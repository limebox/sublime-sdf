# Sublime Text 3 - Limebox NetSuite SDF Plugin

## Changelog
All notable changes to this project will be documented in this file.

## New
For SDF projects, a new right click menu has been added to give you more control over your project
Versioning is as such:
[plugin major release].[NetSuite Release].[plugin patch release]

### [1.1901.2] - 2019-03-
#### Added
- Package Manager library for control of the SDF SDK from Sublime Text
- "Manage SDF SDK" submenu when using brew/choco as a package manager
- sdfscli version switch for brew/choco if using either package manager
- "Update SDF SDK" option to "Manage SDF" submenu
- "Install SDF SDK" option to "Manage SDF" submenu
- Finalized feature hiding when using an older version of the sdfcli than the feature supports

### [1.1901.1] - 2019-02-20
#### Added
- Updated for 19.1 support
- Support for "Save Token" function from 18.2.1
- New file context menu
- "Add to Deploy" and "Remove From Deploy" context menus will modify your deploy.xml file
- "Reset Deploy.xml" to set to default minimum and add default files / folders
- Ignore password input when token is used
- More suitescript snippets
- Support to install the Limebox Framework directly from context menu
- Plugin specific settings
- Invalid token handling
- General Quality of Life improvements
- Multi-environment support
- Multi-client support
- Initial support for SDF SDFK version awareness to disable memu items if not supported by the current version of the SDK