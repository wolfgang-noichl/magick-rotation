
Magick Rotation 1.0						September  25, 2010

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

Enter "lsmod" (without the quotes) in a terminal. In Jaunty, Karmic, Lucid, and Maverick you should see 'hp-wmi' or 'hp_wmi'. If 'hp_wmi' is not present you'll need to add to the 'modules' file in "/etc/modules".

The above is described in more detail in the "Auto-magic Rotation HOW TO" post #225:  http://ubuntuforums.org/showthread.php?t=996830&page=23


Installation:

If you haven't already, install CellWriter through Synaptic Package Manager.

If an earlier Magick Rotation is running shut it down by right clicking on it's green rotating arrow icon and clicking on 'Quit'.  Drag and drop the Magick_Rotation_1.0 folder onto 'yourusername' in the left column of 'Places' (/home/yourusername). To install open the folder and right click on 'magick-rotation-1.0' and select 'Properties'. Then click on the 'Permissions' tab. Check "Allow executing file as a program" and close. Now double click on 'magick-rotation-1.0' and choose 'Run'. The applet is installed.


Setup:  Before rotating for the first time.

Right click on the Magick Rotation icon (green arrow), located in the notification area in the top panel (right side), and chose 'Setup'.  Chose if you want Magick to "Run on start?" (you do) and which direction to rotate to.  Remember to 'Save' the direction if you changed it.  Then go into "Advanced Setup" and make any other changes you want (commands to run before and after rotation, etc.) and then click on 'Save'. You are ready to rotate.

If you check your "/home/username/" directory you'll see the Magick_Rotation-1.0 folder. In "System > Preferences > Sessions" or "Startup Applications" you'll see an entry called "Magick Rotation" etc.. The .conf file is named 'magick-rotation.conf'. To see it click "Show Hidden Files" in 'View' in 'Places' (Nautilus).


Debugging Tool Use:

Terminal:  To run the command line 'debug' version quit Magick (if running) and open a terminal. To see the debugging output in the terminal use:

Magick_Rotation_1.0/magick-rotation-1.0 debug

To stop make either right click on the Magick green arrow icon and choose 'Quit' or be sure the terminal is in focus and use ctrl + C (or Z). You'll see a python traceback after stopping.

Or you could use in a terminal:

python Magick_Rotation_1.0/magick-rotation-1.0 debug

To stop make sure the terminal is in focus and use ctrl + Z.

This option let's you quickly eyeball the problem. Remember you have a limited amount of time to swivel into tablet mode and back before the terminal will overflow and you'll lose the beginning of the debug output.

Log file:  This option allows you to print the output to the text file 'magick-log_date' in "/home/yourusername/" directory for more detailed study.  Go into "Advanced Setup" and check the "Debugging tool logging on?" check box then 'Save'.  Remember the log will keep filling until you uncheck the check box and hit 'Save' again.

Looking at the output should help pin the problem down for you. And you have the option of posting it as an attachement if you need help.


Ayuthia's xrotate.py:

You can use this python script to rotate without Magick Rotation.  Right click on 'xrotate.py' and select 'Properties'. Then click on the 'Permissions' tab. Check "Allow executing file as a program" and close.  You can now place it in a launcher.  The command for use is:  ./xrotate.py  That will rotate the tablet counterclockwise in 90 degree steps.  To specify direction use either normal | left | right | inverted  as in:  ./xrotate.py right

To turn debugging on in xrotate.py change at about line #6:  debug = 0
to:  debug = 1


##############################################################
##  This program is free software; you can redistribute it  ##
##  and/or modify it under the terms of the GNU General     ##
##  Public license as published by the Free Software        ##
##  Foundation; either version 2 of the License, or (at     ## 
##  your option) any later version.                         ##
##############################################################
