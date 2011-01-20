
Magick Rotation 1.2						December 3, 2010

ChangeLog:
1.2 - Removed hp-wmi out of magick-rotation, changed magick-rotation to listen to xrandr events, added installer to help get dependencies and compile check.c
1.1 - Added touch on/off feature with associated icons, changed config file from .conf to .xml, removed separator line above buttons, modified About dialog label, changed description box in magick-rotation
1.0 - Major code reorganization by Ayuthia - converted scripts to be object oriented and separated out the notifier, configuration file, GUI, and main sections
0.5 - Added Ayuthia's evdev rotation support
0.4 - Added Lucid/Xserver 1.7 support courtesy of Ayuthia.
0.3-3-Added GPL, check for dir. "~/.config/autostart/" if not make it, removed separator line in About.
0.3.2-Added gtk stock buttons, moved About button back to setup.
0.3.1-Added borders to Setup and About windows.  Moved OK button into About.
0.3 - This version incorporates Ayuthia's debugging code and more cosmetic improvments.  In addition we've verified that the HP 2700 series tablet pc's (2710p and most likely 2730p) are supported, thanks to zoomy942.

Note: Do no use '&' after a program. For example adding '&' to Cairo Dock as in "cairo-dock -o &".  Adding the '&' will cause Magick Rotation to "hang".


Preliminaries:  First make sure the infrastructure is in place.

If your video card needs to be configured for rotation make sure that's done.  Nvidia and ATI cards see Appendix 1 in the Rotation HOW TO:  http://ubuntuforums.org/showthread.php?p=6274392

Enter "lsmod" (without the quotes) in a terminal. In Jaunty, Karmic, Lucid, and Maverick you should see 'hp-wmi' or 'hp_wmi'. If 'hp-wmi' is not present you'll need to add to the 'modules' file in "/etc/modules".

The above is described in more detail in the "Auto-magic Rotation HOW TO" post #225:  http://ubuntuforums.org/showthread.php?t=996830&page=23


Installation:

If you haven't already, install CellWriter through Synaptic Package Manager.

If an earlier Magick Rotation is running shut it down by right clicking on it's green rotating arrow icon and clicking on 'Quit'.  Drag and drop the magick-rotation folder onto 'yourusername' in the left column of 'Places' (/home/yourusername).  If it asks if you want to replace the magick-rotation folder say "Yes to all".  To install open the folder and right click on 'magick-rotation' and select 'Properties'. Then click on the 'Permissions' tab. Verify "Allow executing file as a program" is checked, if not check it, and close. Now double click on 'magick-rotation' and choose 'Run'. The applet is installed.  The version number is available if you click the About button.


Setup:  Before rotating for the first time.

Right click on the Magick Rotation icon (green arrow), located in the notification area in the top panel (right side), and chose 'Setup'.  Chose if you want Magick to "Run on start?" (you do) and which direction to rotate to.  Remember to 'Save' the direction if you changed it.  Then go into "Advanced Setup" and make any other changes you want (commands to run before and after rotation, etc.) and then click on 'Save'. You are ready to rotate.

Advanced Setup command examples (note use of semi-colon to separate commands).
[Run before switch to tablet:]
killall -9 cairo-dock; gconftool-2 --set /apps/panel/toplevels/top_panel_screen0/size --type integer 42

[Run after switch to tablet:]
cellwriter --show-window; cairo-dock -o

[Run before switch to normal:]
killall -9 cairo-dock; gconftool-2 --set /apps/panel/toplevels/top_panel_screen0/size --type integer 24

[Run after switch to normal:]
cellwriter --hide-window; cairo-dock -o

CellWriter is included by default; the commands show it in portrait and hide it in landscape.  The Cairo (or Glx) Dock commands are to close the dock and restart it after rotation so it resizes correctly.  The gconftool command resizes the top panel to a larger size (from the default 24) in portrait so it is more touch friendly.

If you check your "/home/username/" directory you'll see the magick-rotation folder. In "System > Preferences > Sessions" or "Startup Applications" you'll see an entry called "Magick Rotation for HP tablet pc's". The associated file is in ".config > autostart" and is called "magick-rotation.desktop".  The configuration settings are in a file named 'magick-rotation.conf' in version 1.0. In version 1.1 and up it's a .xml file named magick-rotation.xml.  To see either click "Show Hidden Files" in 'View' in 'Places' (Nautilus).


Turning Touch On or Off:

Simply left click on the Magick tray icon.  A red T will appear in the Magick Rotation icon when touch is off along with a notification pop-up.  To turn touch back on left click on the icon again.  To disable the feature uncheck the "Click tray icon on/off touch?" check box in 'Setup'.  That will turn the touch toggle option off.


Debugging Tool Use:

Terminal:  To run the command line 'debug' version quit Magick (if running) and open a terminal. To see the debugging output in the terminal use:

magick-rotation/magick-rotation debug

To stop make either right click on the Magick green arrow icon and choose 'Quit' or be sure the terminal is in focus and use ctrl + C (or Z). You'll see a python traceback after stopping.

Or you could use in a terminal:

python magick-rotation/magick-rotation debug

To stop make sure the terminal is in focus and use ctrl + Z.

This option let's you quickly eyeball the problem. Remember you have a limited amount of time to swivel into tablet mode and back before the terminal will overflow and you'll lose the beginning of the debug output.

Log file:  This option allows you to print the output to the text file 'magick-log_date' in "/home/yourusername/" directory for more detailed study.  Go into "Advanced Setup" and check the "Debugging tool logging on?" check box then 'Save'.  Remember the log will keep filling until you uncheck the check box and hit 'Save' again.

Looking at the output should help pin the problem down for you. And you have the option of posting it as an attachement if you need help.


xrotate.py:

You can use this python script to rotate without Magick Rotation as a stand alone rotation script.  Right click on 'xrotate.py' and select 'Properties'. Then click on the 'Permissions' tab. Check "Allow executing file as a program" and close.  You can now place it in a launcher.  The command for use is:  ./xrotate.py  That will rotate the tablet counterclockwise in 90 degree steps.  To specify direction use either normal | left | right | inverted  as in:  ./xrotate.py right

To turn debugging on in xrotate.py change at about line #6:  debug = 0
to:  debug = 1


##############################################################
##  This program is free software; you can redistribute it  ##
##  and/or modify it under the terms of the GNU General     ##
##  Public license as published by the Free Software        ##
##  Foundation; either version 2 of the License, or (at     ## 
##  your option) any later version.                         ##
##############################################################
