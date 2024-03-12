# dotbot-brew


This is a [Dotbot][dotbot] plugin for installing packages and casks with
Homebrew.

## Installation

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
- As a gloval option for every directive of the specified type. For
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

### The `install-brew` directive 

The `install-brew` directive is used to install Homebrew in your machine if
it is not already installed. The contents of this directive can be either a
bool indicating if Homebrew should be installed or a dictionary with the
general options, in which case the installation will be performed.

### The `brew` directive

Hi.

## Examples

## License

This project is licensed under the [MIT LICENSE](/LICENSE) by Mario Vago
Marzal.

<!-- External links -->
[dotbot]: https://github.com/anishathalye/dotbot
