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
                {},
            ),
        }

        super().__init__(*args, **kwargs)

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

    def _invoke_shell_commands(
        self,
        commands: list[str],
        options: dict[str, Any],
    ) -> int:
        """"""
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

    def _install_brew(
        self,
        data: Any,
        options: dict[str, Any],
    ) -> bool:
        """Installs Homebrew"""
        if isinstance(data, dict) or (isinstance(data, bool) and data):
            # Check if Homebrew is already installed
            if Path(
                self._brew_prefix(options["force-intel"], for_cmd=False)
            ).exists():
                self._log.info("Homebrew is already installed")
                return True
            else:
                # Install Homebrew
                return self._invoke_shell_commands(
                    [
                        "arch -x86_64 " if options["force-intel"] else ""
                        "/bin/bash -c "
                        "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)",
                    ],
                    options,
                ) == 0
        else:
            return True
