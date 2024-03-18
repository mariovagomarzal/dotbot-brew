# dotbot-brew

This is a [Dotbot][dotbot] plugin for installing packages and casks with
Homebrew.

## Table of contents

- [Installation](#installation)
- [Usage](#usage)
  - [The `install-brew` directive](#the-install-brew-directive)
  - [The `brew` directive](#the-brew-directive)
  - [The `cask` directive](#the-cask-directive)
  - [The `tap` directive](#the-tap-directive)
  - [The `brewfile` directive](#the-brewfile-directive)
- [Examples](#examples)
  - [Minimal example](#minimal-example)
  - [Complete example](#complete-example)
- [License](#license)

## Installation

To use this plugin in your dotfiles, you need to add it as a submodule with
the following command:

```sh
git submodule add https://github.com/mariovagomarzal/dotbot-brew.git
```

Then, you need to add the plugin when you call the `dotbot` executable.
Typically, this is done in the `install` script of your dotfiles. For
example, in the default `install` script of Dotbot:

```sh
"${BASEDIR}/${DOTBOT_DIR}/${DOTBOT_BIN}" -d "${BASEDIR}" --plugin-dir dotbot-brew -c "${CONFIG}" "${@}"
```

## Usage

The plugin provides five new directives to manage Homebrew operations:

- `install-brew`: Installs Homebrew in your machine if it is not already
  installed.
- `brew`: Installs a package with Homebrew.
- `cask`: Installs a cask with Homebrew.
- `tap`: Adds a tap to Homebrew.
- `brewfile`: Installs packages and casks from a Brewfile.

In the following subsections we will describe each directive in detail and
its available options. Additionally, we have included a section with some
examples of how to use the plugin.

### General options

Every directive has a set of common options which are the following:

- `stdin`: A boolean that indicates if the command stdin should be redirected
  to the terminal.
- `stdout`: A boolean that indicates if the command stdout should be
  redirected to the terminal.
- `stderr`: A boolean that indicates if the command stderr should be
  redirected to the terminal.
- `force-intel`: A boolean that indicates if the command should be executed
  with Rosetta 2 on Apple Silicon Macs.

They can be defined in three ways:

- As a global option for every `dotbot-brew` directive. This can be done by
  setting the defaults of the `homebrew` key. For example:

  ```yaml
  - defaults:
      homebrew:
        # These are the defaults
        stdin: true
        stdout: true
        stderr: true
        forece-intel: false
  ```
- As a global option for every directive of the specified type. For
  example:

  ```yaml
  - defaults:
      install-brew:
        # Same as the global defaults
        stdin: true
        stdout: true
        stderr: true
        forece-intel: false
        # ... other specific options for this directive
  ```
- As a local option for a specific directive. For example:
  
  ```yaml
  - install-brew:
      # Same as the global defaults
      stdin: true
      stdout: true
      stderr: true
      forece-intel: false
      # ... other specific options for this directive
  ```

The order of preference of the options is ascending, meaning that the local
options are prioritized over the globals of the directive, and the globals
of the directive over the globals of the plugin.

The specific options of each directive will be described in the following
subsections.

### The `install-brew` directive 

The `install-brew` directive is used to install Homebrew in your machine if
it is not already installed. It can be used in two ways:

- With a boolean that indicates if Homebrew should be installed. For
  example:

  ```yaml
  - install-brew: true
  ```

- With a dictionary with the general options and/or the specific options of
  the directive. The specific options are the following:

  - `install`: A boolean that indicates if Homebrew should be installed.
  - `force`: A boolean that indicates if Homebrew should be installed even
    if it is already installed.
  - `setup_bash`: A boolean that indicates if the Homebrew post-isntall
    steps for Bash should be executed.
  - `setup_zsh`: A boolean that indicates if the Homebrew post-isntall
    steps for Zsh should be executed.
  - `setup_fish`: A boolean that indicates if the Homebrew post-isntall
    steps for Fish should be executed.

  For example:

  ```yaml
  - install-brew:
      # Same as the global directive defaults
      install: true
      force: false
      # ... other general options
  ```

**Note:** See the `_install_brew` method in the `brew.py` file for more
information about the specific commands that are executed for each
setup-shell option.

### The `brew` directive

The `brew` directive is used to install a package (formula) with Homebrew.
It can be used in two ways:

- With a list of packages to install. For example:

  ```yaml
  - brew:
    - git
    - zsh
  ```

- With a dictionary with the general options and/or the specific options of
  the directive. The specific options are the following:

  - `packages`: A list of packages to install.
  - `force`: A boolean that indicates if the package should be installed
    even if it is already installed.

  For example:

  ```yaml
  - brew:
      packages: # By default it is an empty list
        - git
        - zsh
      force: false # Same as the global directive defaults
      # ... other general options
  ```

### The `cask` directive

The `cask` directive is used to install a cask with Homebrew. It can be
used in two ways:

- With a list of casks to install. For example:

  ```yaml
  - cask:
    - firefox
    - visual-studio-code
  ```

- With a dictionary with the general options and/or the specific options of
  the directive. The specific options are the following:

  - `casks`: A list of casks to install.
  - `force`: A boolean that indicates if the cask should be installed
    even if it is already installed.

  For example:

  ```yaml
  - cask:
      casks: # By default it is an empty list
        - firefox
        - visual-studio-code
      force: false # Same as the global directive defaults
      # ... other general options
  ```

### The `tap` directive

The `tap` directive is used to add a tap to Homebrew. It can be used in two
ways:

- With a list of taps to add. For example:

  ```yaml
  - tap:
    - homebrew/cask-fonts
    - homebrew/cask-drivers
  ```

- With a dictionary with the general options and/or the specific options of
  the directive. The specific options are the following:

  - `taps`: A list of taps to add.

  For example:

  ```yaml
  - tap:
      taps: # By default it is an empty list
        - homebrew/cask-fonts
        - homebrew/cask-drivers
      # ... other general options
  ```

### The `brewfile` directive

The `brewfile` directive is used to install packages and casks from a
Brewfile. It can be used in two ways:

- With a list of Brewfiles to install. For example:

  ```yaml
  - brewfile:
    - Brewfile
    - Brewfile.local
  ```

- With a dictionary with the general options and/or the specific options of
  the directive. The specific options are the following:

  - `brewfiles`: A list of Brewfiles to install.

  For example:

  ```yaml
  - brewfile:
      brewfiles: # By default it is an empty list
        - Brewfile
        - Brewfile.local
      # ... other general options
  ```

## Examples

In this section we will show two examples of how to use the plugin.

### Minimal example

The following example shows how to use the plugin to install Homebrew and
some packages and casks with no fancy options.

```yaml
- defaults:
    homebrew:
      # Disable standard output for all the `dotbot-brew` directives
      stdout: false

- tap:
  - homebrew/cask-fonts

- brew:
  - git
  - fish

- cask:
  - visual-studio-code
  - font-fira-code-nerd-font
```

### Complete example

The following example shows how to use the plugin to install Homebrew and
some packages and casks with some fancy options.

```yaml
- defaults:
    homebrew:
      force-intel: true
      stdin: false
    cask:
      force: true

- tap:
  - homebrew/cask-fonts

- brew:
  - git
  - fish

- cask:
    stdin: true
    casks:
      - mactex
      - karabiner-elements
    
- cask:
  - visual-studio-code

- brewfile:
  - brew/Brewfile
  - brew/Brewfile.local
```

## License

This project is licensed under the [MIT LICENSE](/LICENSE) by Mario Vago
Marzal.

<!-- External links -->
[dotbot]: https://github.com/anishathalye/dotbot
