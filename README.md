This is a fork of the original launchpad project (https://launchpad.net/magick-rotation), which seems to be dead.
The automatic installer isn't working anymore at least on *buntu, at least due to https://bugs.launchpad.net/magick-rotation/+bug/1621026.
*You're probably best off with just following the manual install instructions in ./INSTALLER.txt, which are known to work at least for Xubuntu 18.04 and 19.04.*

-------

Magick Rotation is an application that will help Dell, Fujitsu, HP, and Lenovo convertible tablet PC's automatically rotate screen orientation and devices that use the Wacom or evdev drivers.

To install run the MAGICK-INSTALL file in the unpacked magick-rotation folder. (Fedora ensure 'beesu' package installed. For versions 1.5 and earlier run the magick-rotation file.)
Saucy Unity, maybe also later Unity editions also install 'python-appindicator'.

Note: the xinput utility is required. If 'xinput list' entered in a terminal
produces output it is installed.

Magick Rotation is not a Ubuntu specific application. Versions have worked in Arch, Fedora, Gentoo, Mandriva, and openSUSE among others.

The Magick Rotation Installer possibly currently works with Fedora, LMDE, Mint and openSUSE.
(Other Distros may also be supported if they use the same package manager and library names etc. as one of the supported Distros. Debian may be an example.)

If the automatic installer does not work on your Distro follow the instructions in INSTALLER.txt.

Gentoo ebuild by Vadim Efimov available here (probably outdated, though): http://packages.gentoo.org/package/x11-misc/magick-rotation

Thank you to our testers on Ubuntu forums.
For the Dell XT & XT2's: wildschweini, enneract, Ubuntiac
For the Thinkpads: forti, supr0, linuxd00
For the Fujitsu's: dog-soldier, pvdh, Cobuntu

A special thank you to Robert Gerlach for his assistance in adding Fujitsu tablet PC support.

