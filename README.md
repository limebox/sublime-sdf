# Sublime SDF

### Authors Note
Please use the github Issues tab if you are having any issues using this product.

### Thank you
Thank you PackageControl.io for listing the NetSuite SDF package:
https://packagecontrol.io/packages/NetSuite%20SDF

If you find any bugs, feel free to report them in the issues section of github.

# SDFCLI

> ## JAVA 9 NOTE
>
> Java 9 is not currently supported by the NetSuite SDF CLI tool. If you have Java 9 you will need to uninstall it and proceed with the following steps to install Java 8. I will update this tool when support for Java 9 is added.

This plugin requires you to install the SDFCLI tool from NetSuite.
The source for Chocolatey and Brew can be found here: https://github.com/limebox/sdf

## Windows
Install via [Chocolatey](https://chocolatey.org)
```bash
choco install sdfcli # This installs Java 8 and Maven 3.5
```

## Mac
Install via [Homebrew](https://brew.sh)
```bash
brew cask install caskroom/versions/java8 # Unless you already have Java 8 installed.
brew install limebox/netsuite/sdfcli
```
