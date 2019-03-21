# Sublime Text 3 - Limebox NetSuite SDF Plugin

## Changelog
All notable changes to this project will be documented in this file.

## 1.1910.15 - 2019-03-20
- Fixed path issue in context menu for Windows vs Mac
- Fixed issue when executing certain commands from the sidebar, then executing other commands from the command palette
- Fixed issue with "Save Token" calling the wrong function to confirm which version the request is being made from
- Initial groundwork for "Upload Folder" and "Upload File" commands
- Hid "Install Limebox Framework" for non-empty folders to avoid confusion

## 1.1910.14 - 2019-03-14
- Removed "bad filenames" check as the CLI allows importing files via quotes (though this is broken in Linux at the moment)
- Removed debug print lines
- Changed "Yes" response checker to match new confirmation from 19.1 when importing objects
- Added "Done" checker to determine when the CLI has completed (new for 19.1.0)
- Fixed "Version Checker" from 1.1910.12

## 1.1910.13 - 2019-03-13
- Fixed list length assumptions by first checking if a list has items
- Added a try catch around the create project code in the event the user clicks a phantom file in Sublime

## 1.1910.12 - 2019-03-13
- CLI changed how output is displayed. Plugin adjusted to get new version number for >19.1.0
- Upon opening, a check is made to see if the .sdf file is listed in the File Excluse Pattern, if so, the plugin removes it
- Added version check on "Save Token" since 18.2.1 used "tokenkey" but 19.2.0 used "tokenid"
- If you are still using the 18.2.0 CLI, hide the "Save Token" function
- Removed the reset environment function when CLI is upgraded

## 1.1910.11 - 2019-03-12
- Fixed createproject issue in Windows
- Initial 19.1 fixes for both Windows and Mac given the cli changes

## 1.1910.1 Release Info
For SDF projects, a new right click menu has been added to give you more control over your project
Versioning is as such:
[plugin major release].[NetSuite Release].[plugin patch release]

### [1.1910.1] - 2019-02-20
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