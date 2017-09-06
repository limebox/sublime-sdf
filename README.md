# NetSuite SDF

## This requires you to install the NetSuite SDF CLI tool.

You need to install the cli tool manually following the instructions documented here:
https://system.eu1.netsuite.com/app/help/helpcenter.nl?fid=chapter_4779302061.html

Alternatively, you can install SDF on Windows using Chocolatey (you MUST install v17.1.2):
https://chocolatey.org/packages/sdfcli (instructions to install Chocolatey: https://chocolatey.org/install)

(A version of the NetSuite SDF CLI tool will soon be available on Homebrew for Mac)

## Current NetSuite Version (17.1.2)

The currently released version of SDF is 17.1.2. However, the latest version, 17.2.0 will be rolled out to NetSuite customers starting September 15th. Shortly after release, I will update this plugin to use the latest version from NetSuite.

I will be releasing an instructional video after the 17.2 release on how to use this product. In the mean time, you can explore the project by using the shortcut "Ctrl+Alt+D" (Win) or "Cmd+Apple+D" (Mac). In order for this to work, you MUST have a file in your NetSuite project folder called ".sdf" and formatted the same way recommended in the NetSuite help docs (https://system.eu1.netsuite.com/app/help/helpcenter.nl?fid=section_1490561186.html)

```ini
account=
email=
role=
url=
```

For a sample folder structure that works with this plugin, please see the related repository: https://github.com/limebox/framework
