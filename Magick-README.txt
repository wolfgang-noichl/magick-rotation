
Magick Rotation 1.7						November 30, 2013


NOTE: In the Advanced Setup command boxes do not use '&' after a program. For example adding '&' to Cairo Dock as in "cairo-dock -o &".  Adding the '&' will cause Magick Rotation to "hang".

NOTE (obsolete?): If the stylus and other input tools have right and left orientation reversed when in a portrait tablet mode (cw or ccw), you likely have a known bug in xf86-input-wacom.  The bug caused cw and ccw to be reversed for xsetwacom in versions 0.10.9 through 0.11.0.  It is suggested you update xf86-input-wacom to a later version.  Cloning its git repository to update is described in FAQ #1603.


PRELIMINARIES
First make sure the infrastructure is in place.  If your video driver needs to be configured for rotation ensure that's done.

Magick Rotation requires Python 2 to run.  Some of the Distros are now switching to Python 3 with their new releases.  You may need to install Python 2 from the Distro's official repositories.  Additionally beginning with Magick Rotation 1.6.2 you'll need to ensure a 'python2' symlink is present.  See the "Accommodating the changeover to Python 3" FAQ:  https://answers.launchpad.net/magick-rotation/+faq/2108

Enter "lsmod" (without the quotes) in a terminal.  You should see one of the following:  'hp_wmi' or 'dell_wmi' or 'fujitsu_tablet' or 'thinkpad_acpi'. If the appropriate kernel module for you is not present you'll need to add it to the 'modules' file in "/etc/modules" at the bottom of the list without quotes.  In the case of a Fujitsu tablet PC if your kernel predates 3.4 you'll need to install fujitsu-tablet.ko from the MagickExtras folder.

NOTE:  Dell tablet PC's need to install a modified dell-wmi.ko while Fujitsu tablet PC's may need to install a fujitsu-tablet.ko.  See the dell-wmi_README.txt or the fujitsu-tablet_README.txt in the MagickExtras folder.  Or also the "How do I get my Dell XT or XT2 to work with Magick Rotation?" FAQ:  https://answers.launchpad.net/magick-rotation/+faq/1447  The 3.4 or 3.5 kernel should come with a working fujitsu-table.ko making installing one unnecessary.


INSTALLATION
If you haven't already, install CellWriter through your Software Installer such as Synaptic Package Manager.  CellWriter is Magick Rotation's default onscreen keyboard.  You can use another onscreen keyboard such as Onboard by changing the CellWriter lines in Advanced Setup.

In order for the Installer to work in Fedora the 'beesu' packaged needs to be installed.  Either with Add/Remove Software or from the command line with:
    su - -c "yum install beesu"
In Kubuntu Precise 12.04 the python-gtk2 package is not installed by default.  It is required so install it with the Software Center, Muon, or:  
    sudo apt-get install python-gtk2
Starting in Ubuntu Saucy 13.10 the 'gksu' package needs to be installed and if you are using the Unity Desktop in Saucy the 'python-appindicator' package.  The Installer should pop up the Software Center so you can install them if required before it runs.

If an earlier Magick Rotation is running shut it down by right clicking on it's green rotating arrow icon and clicking on 'Quit'.  To install open the extracted magick-rotation folder and double click on the  MAGICK-INSTALL file and choose 'Run'.  If instead it opens up in your text editor right click on MAGICK-INSTALL (for pre-1.6 versions it's the 'magick-rotation' file) and select 'Properties'. Then click on the 'Permissions' tab. Verify "Allow executing file as a program" is checked, if not check it, and close.  If the executable flag isn't the problem it is likely an issue with the latest Gnome version of Nautilus.  Open Nautilus and click on Files in the top bar and choose Preferences.  In the Behavior tab under 'Executable Text Files' change the new default of 'View executable text files when they are opened' back to the old default of 'Ask each time'.

The Installer will install the libraries needed to compile checkmagick and compile it.  Then it will install the Magick Rotation files to their various locations and delete the now unnecessary install files.  This will be detailed in the install_log which shows which files were installed in what locations.  Reboot and the applet should be installed and working, signified by the green Magick Rotation icon that should appear.  The version number is available if you click the About button.

If the install doesn't work check the install_log and see if there is an explanation.  If there isn't an install_log, only a partial one, or you don't understand it using a terminal you can change directories into the magick-rotation folder and run MAGICK-INSTALL from the command line with:
    ./MAGICK-INSTALL
The output may tell you the problem.  For example Fedora might see an audit conflict between packages when trying to install say gcc.  You can clear that by running:
    su - -c "yum update audit"

The magick-rotation-1.6 folder should, after installation, contain INSTALLER.txt, install_log, Magick-README.txt, and the folders MagickExtras and MagickUninstall.  MagickUninstall lets you uninstall Magick Rotation using MAGICK-UNINSTALL similar to MAGICK-INSTALL.  MagickExtras has the kernel drivers/modules needed by both the Dell and Fujitsu tablet PCs in order to work with Magick Rotation.  It includes the modified dell-wmi.ko dkms and the fujitsu-tablet.ko dkms along with instructions for both.

NOTE:  You can still run Magick Rotation from the magick-rotation folder without installing it or if the Installer fails.  This is no longer true for Ubuntu Raring 13.04 and later with the Unity Desktop due to the peculiarities of how the App. Indicator API handles icons.  For pre-1.6 versions rename or remove the file firstrun.  You will then need to manually compile checkmagic and install the udev rules.  If you have Gnome Shell 3.2 or better you may want to implement the extension.  See the INSTALLER.txt file for instructions.  Then double click on the 'magick-rotation' file and choose 'Run'.


SETUP - BEFORE ROTATING FOR THE FIRST TIME
Right click on the Magick Rotation icon (green arrow), located in the notification area in the top panel (right side), and choose 'Setup'.  Choose which direction to rotate to.  Remember to 'Save' the direction if you changed it.  Then go into "Advanced Setup" and make any other changes you want such as commands to run before and after rotation, etc.  The check box option  "Run on start?" (you do) was moved to Advanced Setup a while ago.  (If you uncheck it to start Magick again you'll need to run it from /usr/share/magick-rotation with './magick-rotation' or the folder by double-clicking on magick-rotation.)  Then after any changes click on 'Save'. You are ready to rotate.

NOTE:  HP Compaq TC4200 & TC4400's.  Your hinge switch values are reversed from other models.  Check the "BIOS hinge switch values reversed?" check box in Setup and then click on Save before first rotation.


ADVANCED SETUP
Command examples (note use of semi-colon to separate commands).
[Run before switch to tablet:]
killall -9 cairo-dock; gconftool-2 --set /apps/panel/toplevels/top_panel_screen0/size --type integer 42

[Run after switch to tablet:]
cellwriter --show-window; cairo-dock -o

[Run before switch to normal:]
killall -9 cairo-dock; gconftool-2 --set /apps/panel/toplevels/top_panel_screen0/size --type integer 24

[Run after switch to normal:]
cellwriter --hide-window; cairo-dock -o

CellWriter is included by default; the commands show it in portrait and hide it in landscape.  The Cairo (or Glx) Dock commands are to close the dock and restart it after rotation so it resizes correctly.  Recent versions of Glx Dock resize correctly and no longer need these commands.  The gconftool command resizes the top panel to a larger size (from the default 24) in portrait so it is more touch friendly.  This is no longer useful in Unity but still helpful in Classic mode.


TURNING TOUCH ON & OFF
Simply left click on the Magick tray icon.  A red T will appear in the Magick Rotation icon when touch is off along with a notification pop-up.  To turn touch back on left click on the icon again.  To disable the feature uncheck the "Click tray icon on/off touch?" check box in 'Setup'.  That will turn the touch toggle option off.


DEBUGGING TOOL USE
Terminal:  To run the command line 'debug' version quit Magick (if running) and open a terminal. To see the debugging output in the terminal change directory to the magick-rotation directory that contains the magick-rotation file and use:
    ./magick-rotation debug
or
    python magick-rotation debug
Go ahead and rotate the tablet PC from laptop to tablet mode and back.  To stop either right click on the Magick green arrow icon and choose 'Quit' or be sure the terminal is in focus and use ctrl + C (or Z). You may see a python traceback after stopping.  This option lets you quickly eyeball the problem.

Log file:  This option allows you to print debug output to a text file called 'magick-log_date' (where 'date' is the current date) in your "/home/yourusername/" directory.  Go into "Advanced Setup" and check the "Debugging tool logging on?" check box then 'Save'.  Go ahead and rotate the tablet PC from laptop to tablet mode and back.  Remember to uncheck the check box and hit 'Save' again after you finish.

Looking at either output should help pin the problem down for you. And you have the option of posting it if you need help.


XROTATE.PY
You can use this python script to rotate without Magick Rotation as a stand alone rotation script.  Right click on 'xrotate.py' and select 'Properties'. Then click on the 'Permissions' tab. Check "Allow executing file as a program" and close.  You can now place it in a launcher.  The command for use is:  ./xrotate.py  That will rotate the tablet counterclockwise in 90 degree steps.  To specify direction use either normal | left | right | inverted  as in:
    ./xrotate.py right

To turn debugging on in xrotate.py change at about line #6:  debug = 0
to:  debug = 1


INSTALLED FILES
As mentioned before the install_log will show you the files and their locations.  In "System > Preferences > Sessions" or "Startup Applications" you'll see an entry called "Magick Rotation for tablet PC's". The associated file is in "~/.config/autostart" and is called "magick-rotation.desktop".  The configuration settings are in a .xml file at "~/.magick-rotation.xml".  To see it "Show Hidden Files" in 'View' in 'Places' (Nautilus or Dophin).  The Gnome Shell 3.2 or better extension folder will be at "~/.local/gnome-shell/extensions/magick-rotation-extension".


UNINSTALL MAGICK ROTATION
Open the MagickUninstall folder and double click on the  MAGICK-UNINSTALL file and choose 'Run'.  If instead it opens up in your text editor right click on MAGICK-UNINSTALL and select 'Properties'. Then click on the 'Permissions' tab.  Verify "Allow executing file as a program" is checked, if not check it, and close.  This will remove everything but the packages used to compile check.c (in case another application is now also using them).


##############################################################
##  This program is free software; you can redistribute it  ##
##  and/or modify it under the terms of the GNU General     ##
##  Public license as published by the Free Software        ##
##  Foundation; either version 2 of the License, or (at     ## 
##  your option) any later version.                         ##
##############################################################
