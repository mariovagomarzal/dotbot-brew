"""Brew plugin for Dotbot"""
import os
import subprocess
from pathlib import Path
from typing import Any, Callable

from dotbot import Plugin


class Brew(Plugin):
    """Brew plugin, a subclass of the base Plugin class"""
    _global_defaults: dict[str, Any]
    _directives: dict[str, tuple[Callable, dict[str, Any]]]

    def __init__(self, *args, **kwargs):
        # The global defaults of all the directives
        self._global_defaults = {
            "stdin": True,
            "stdout": True,
            "stderr": True,
            "force-intel": False,
        }

        # A dictionary of the directives, where each item contains a tuple with
        # the callable that handles the directive and a dict with its specific
        # default options.
        self._directives = {
            # The `install-brew` directive
            "install-brew": (
                self._install_brew,
                {
                    "install": True,
                    "force": False,
                },
            ),
            "brew": (
                self._brew,
                {
                    "packages": [],
                    "force": False,
                }
            ),
            "cask": (
                self._cask,
                {
                    "casks": [],
                    "force": False,
                }
            ),
            "tap": (
                self._tap,
                {
                    "taps": [],
                }
            ),
            "brewfile": (
                self._brewfile,
                {
                    "brewfiles": [],
                }
            ),
        }

        super().__init__(*args, **kwargs)

    # Directive management methods
    def can_handle(self, directive: str) -> bool:
        """Returns wether the directive can be handled by this plugin"""
        return directive in self._directives.keys()

    def _get_directive_options(
        self,
        directive: str,
        data: Any,
    ) -> dict[str, Any]:
        """Returns the default options for the directive"""
        options = self._global_defaults.copy()

        # If the configuration has specific defaults for the plugin, we
        # update the options dictionary with them
        options.update(self._context.defaults().get("homebrew", {}))

        # If the directive has specific global defaults, we update the
        # options dictionary with them
        global_directive_defaults = self._directives[directive][1]
        global_directive_defaults.update(
            self._context.defaults().get(directive, {})
        )
        options.update(global_directive_defaults)

        # If the directive has specific defaults in the data, we update the
        # options dictionary with them
        if isinstance(data, dict):
            options.update(data)

        return options

    def handle(self, directive: str, data: Any) -> bool:
        """Handles the directive and returns wether it was successful or
        not"""
        # First, we build the options dictionary for the directive
        options = self._get_directive_options(directive, data)

        # Now, we can assume that the options contains all the keys of the
        # global defaults and the specific defaults of the directive.
        # Each directive has to handle the `data` depending on its specific
        # type and the options.
        return self._directives[directive][0](data, options)

    # Auxiliary methods
    def _invoke_shell_commands(
        self,
        commands: list[str],
        options: dict[str, Any],
    ) -> int:
        """Invokes a list of shell commands with the given options and
        returns the exit code of the last command executed."""
        commands_str = " && ".join(commands)
        return subprocess.call(
            commands_str,
            shell=True,
            cwd=self._context.base_directory(),
            stdin=subprocess.PIPE if not options["stdin"] else None,
            stdout=subprocess.PIPE if not options["stdout"] else None,
            stderr=subprocess.PIPE if not options["stderr"] else None,
        )

    def _brew_prefix(
        self,
        force_intel: bool,
        for_cmd: bool = True
    ) -> str:
        """Returns the Homebrew prefix based on the OS and the
        architecture"""
        os_name = os.uname().sysname
        os_arch = os.uname().machine

        if os_name == "Darwin":
            if os_arch == "arm64" and force_intel:
                if for_cmd:
                    return "arch -x86_64 /usr/local/bin/brew"
                else:
                    return "/usr/local/bin/brew"
            elif os_arch == "arm64" and not force_intel:
                return "/opt/homebrew/bin/brew"
            else:
                return "/usr/local/bin/brew"
        elif os_name == "Linux":
            return "/home/linuxbrew/.linuxbrew/bin/brew"
        else:
            raise ValueError(f"Unsupported OS: {os_name}")

    def _list_packages(
        self,
        package_type: str,
        force_intel: bool,
    ) -> list[str]:
        """Returns a list of the installed formulae"""
        result = subprocess.run(
            self._brew_prefix(force_intel) + f" list --{package_type} -1",
            shell=True,
            stdin=subprocess.PIPE,
            capture_output=True,
        )

        if result.returncode != 0:
            raise RuntimeError(
                f"Error listing formulae: {result.stderr.decode()}"
            )
        else:
            return result.stdout.decode().split("\n")

    # Directive methods
    def _install_brew(
        self,
        data: Any,
        options: dict[str, Any],
    ) -> bool:
        """Installs Homebrew"""
        # Check validity of the data type
        install = True
        if isinstance(data, dict):
            install = options["install"]
        elif isinstance(data, bool):
            install = data
        else:
            self._log.error("Invalid data for the `install-brew` directive")
            return False

        if install:
            if Path(
                self._brew_prefix(options["force-intel"], for_cmd=False)
            ).exists() and not options["force"]:
                self._log.info("Homebrew is already installed")
                return True
            else:
                self._log.info("Installing Homebrew")
                if self._invoke_shell_commands(
                    [
                        ("arch -x86_64 " if options["force-intel"] else "") + \
                        "/bin/bash -c "
                        "\"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"",
                    ],
                    options,
                ) == 0:
                    self._log.info("Homebrew installed")
                    return True
                else:
                    self._log.error("Error installing Homebrew")
                    return False
        else:
            self.info("Skipping Homebrew installation")
            return True

    def _brew(
        self,
        data: Any,
        options: dict[str, Any],
    ) -> bool:
        """Installs Homebrew packages (formulae)"""
        # Check validity of the data type
        packages = []
        if isinstance(data, dict):
            packages = options["packages"]
        elif isinstance(data, list):
            packages = data
        else:
            self._log.error("Invalid data for the `brew` directive")
            return False

        # Check validity of the packages type
        if not isinstance(packages, list):
            self._log.error("Invalid packages for the `brew` directive")
            return False

        # Install the packages
        all_success = True
        for package in packages:
            install_package = True
            reinstall = False
            if package in self._list_packages(
                "formulae", options["force-intel"]
            ):
                if options["force"]:
                    self._log.info(f"Reinstalling {package}")
                    reinstall = True
                else:
                    self._log.info(f"{package} is already installed")
                    install_package = False
            else:
                self._log.info(f"Installing {package}")

            if install_package:
                success = self._invoke_shell_commands(
                    [
                        self._brew_prefix(options["force-intel"]) +
                        " " + ("reinstall" if reinstall else "install") +
                        f" {package}",
                    ],
                    options,
                ) == 0
                all_success = all_success and success

                if success:
                    self._log.info(f"{package} installed")
                else:
                    self._log.error(f"Error installing {package}")

        if all_success:
            self._log.info("All packages installed successfully")
        else:
            self._log.error("Some packages failed to install")

        return all_success

    def _cask(
        self,
        data: Any,
        options: dict[str, Any],
    ) -> bool:
        """Installs Homebrew casks"""
        # Check validity of the data type
        casks = []
        if isinstance(data, dict):
            casks = options["casks"]
        elif isinstance(data, list):
            casks = data
        else:
            self._log.error("Invalid data for the `cask` directive")
            return False

        # Check validity of the casks type
        if not isinstance(casks, list):
            self._log.error("Invalid casks for the `cask` directive")
            return False

        # Install the casks
        all_success = True
        for cask in casks:
            install_cask = True
            reinstall = False
            if cask in self._list_packages(
                "casks", options["force-intel"]
            ):
                if options["force"]:
                    self._log.info(f"Reinstalling {cask}")
                    reinstall = True
                else:
                    self._log.info(f"{cask} is already installed")
                    install_cask = False
            else:
                self._log.info(f"Installing {cask}")

            if install_cask:
                success = self._invoke_shell_commands(
                    [
                        self._brew_prefix(options["force-intel"]) +
                        " " + ("reinstall" if reinstall else "install") +
                        f" --cask {cask}",
                    ],
                    options,
                ) == 0
                all_success = all_success and success

                if success:
                    self._log.info(f"{cask} installed")
                else:
                    self._log.error(f"Error installing {cask}")

        if all_success:
            self._log.info("All casks installed successfully")
        else:
            self._log.error("Some casks failed to install")

        return all_success

    def _tap(
        self,
        data: Any,
        options: dict[str, Any],
    ) -> bool:
        """Taps a Homebrew repository"""
        # Check validity of the data type
        taps = []
        if isinstance(data, dict):
            taps = options["taps"]
        elif isinstance(data, list):
            taps = data
        else:
            self._log.error("Invalid data for the `tap` directive")
            return False

        # Check validity of the taps type
        if not isinstance(taps, list):
            self._log.error("Invalid taps for the `tap` directive")
            return False

        # Tap the repositories
        all_success = True
        for tap in taps:
            self._log.info(f"Tapping {tap}")
            success = self._invoke_shell_commands(
                [
                    self._brew_prefix(options["force-intel"]) +
                    f" tap {tap}",
                ],
                options,
            ) == 0
            all_success = all_success and success

            if success:
                self._log.info(f"{tap} tapped")
            else:
                self._log.error(f"Error tapping {tap}")

        if all_success:
            self._log.info("All taps were successful")
        else:
            self._log.error("Some taps failed")

        return all_success

    def _brewfile(
        self,
        data: Any,
        options: dict[str, Any],
    ) -> bool:
        """Installs Homebrew packages and casks from a Brewfile"""
        # Check validity of the data type
        brewfiles = []
        if isinstance(data, dict):
            brewfiles = options["brewfiles"]
        elif isinstance(data, list):
            brewfiles = data
        else:
            self._log.error("Invalid data for the `brewfile` directive")
            return False

        # Check validity of the brewfiles type
        if not isinstance(brewfiles, list):
            self._log.error("Invalid brewfiles for the `brewfile` directive")
            return False

        # Install the packages and casks
        all_success = True
        for brewfile in brewfiles:
            self._log.info(f"Installing packages and casks from {brewfile}")
            success = self._invoke_shell_commands(
                [
                    self._brew_prefix(options["force-intel"]) +
                    f" bundle --verbose --file={brewfile}",
                ],
                options,
            ) == 0
            all_success = all_success and success

            if success:
                self._log.info(f"Installed packages and casks from {brewfile}")
            else:
                self._log.error(f"Error installing packages and casks from {brewfile}")

        if all_success:
            self._log.info("All Brewfiles were successful")
        else:
            self._log.error("Some Brewfiles failed")

        return all_success
