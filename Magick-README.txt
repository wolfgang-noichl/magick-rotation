
Magick Rotation 1.7						June 02, 2020


NOTE: In the Advanced Setup command boxes do not use '&' after a program. For example adding '&' to Cairo Dock as in "cairo-dock -o &".  Adding the '&' will cause Magick Rotation to "hang".

NOTE (obsolete?): If the stylus and other input tools have right and left orientation reversed when in a portrait tablet mode (cw or ccw), you likely have a known bug in xf86-input-wacom.  The bug caused cw and ccw to be reversed for xsetwacom in versions 0.10.9 through 0.11.0.  It is suggested you update xf86-input-wacom to a later version.  Cloning its git repository to update is described in FAQ #1603.


PRELIMINARIES
First make sure the infrastructure is in place.  If your video driver needs to be configured for rotation ensure that's done.

Magick Rotation requires Python 3 to run.

Enter "lsmod" (without the quotes) in a terminal.  You should see one of the following:  'hp_wmi' or 'dell_wmi' or 'fujitsu_tablet' or 'thinkpad_acpi'. If the appropriate kernel module for you is not present you'll need to add it to the 'modules' file in "/etc/modules" at the bottom of the list without quotes.  In the case of a Fujitsu tablet PC if your kernel predates 3.4 you'll need to install fujitsu-tablet.ko from the MagickExtras folder.

NOTE:  Dell tablet PC's need to install a modified dell-wmi.ko while Fujitsu tablet PC's may need to install a fujitsu-tablet.ko.  See the dell-wmi_README.txt or the fujitsu-tablet_README.txt in the MagickExtras folder.  Or also the "How do I get my Dell XT or XT2 to work with Magick Rotation?" FAQ:  https://answers.launchpad.net/magick-rotation/+faq/1447  The 3.4 or 3.5 kernel should come with a working fujitsu-table.ko making installing one unnecessary.


INSTALLATION
If you haven't already, install CellWriter through your Software Installer such as Synaptic Package Manager.  CellWriter is Magick Rotation's default onscreen keyboard.  You can use another onscreen keyboard such as Onboard by changing the CellWriter lines in Advanced Setup.

Then, follow ./INSTALLER.txt.

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


##############################################################
##  This program is free software; you can redistribute it  ##
##  and/or modify it under the terms of the GNU General     ##
##  Public license as published by the Free Software        ##
##  Foundation; either version 2 of the License, or (at     ## 
##  your option) any later version.                         ##
##############################################################
