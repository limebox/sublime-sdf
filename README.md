# Sublime SDF

### Authors Note
Please forgive how bad the code is. I was focused on getting it out quickly more than making it look pretty. Making it prettier will be a priority after official release.

### Thank you
Thank you PackageControl.io for listing the NetSuite SDF package:
https://packagecontrol.io/packages/NetSuite%20SDF

If you find any bugs, feel free to report them in the issues section of github.

# SDFCLI

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
brew cask install caskroom/versions/java8 # Unless you already have Java installed. Note, Java 9 is not yet supported.
brew install limebox/netsuite/sdfcli
```
