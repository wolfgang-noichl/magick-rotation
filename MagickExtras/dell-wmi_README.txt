
Magick Rotation 1.6						April 27, 2012


The default dell-wmi with the kernel does not report the hinge switch state which Magick Rotation needs in order to work.  What we can do is the use a version modified by Rafi Rubin along with dkms, or a subsequent modification for BIOS A09 or later.  Unfortunately the underlying dell-wmi.c is getting a bit long in the tooth and does not reflect the changes to the dell-wmi.c in newer kernels.  While the dell-wmi.ko versions included here still work, as far as we know, what's needed is for someone with kernel coding skills and a Dell tablet PC for testing to make the KE_SW and SW_TABLET_MODE modifications to a newer dell-wmi.c.  The legacy_keymap we are using needs to be updated to accomodate the sparse-keymap and new dell_bios_hotkey_table.

FIRST check to see if you have the dkms framework installed.  If you have installed a proprietary driver such as a video or wifi driver it likely is.  Otherwise you will need to install it.  Examples:
Ubuntu - in Software Center search 'dkms' or from the command line:
    sudo apt-get install dkms
Fedora - in Add/Remove Software search 'dkms' or from the command line:
    su -c 'yum install dkms'
openSUSE - in Install/Remove Software search 'dkms' or from the command line:
    su -c 'zypper install dkms'


ALL XT BIOS's and XT2 BIOS A08 AND EARLIER
Open a terminal and copy (as root) the dell-wmi-20101214-rafi folder to /usr/src.  Either use the path to the MagickExtras folder (assuming you extracted it onto your Desktop): 
    sudo cp -a /home/yourusername/Desktop/magick-rotation/MagickExtras/dell-wmi-20101214-rafi /usr/src/
or after you change directories into the MagickExtras folder:
    sudo cp -a dell-wmi-20101214-rafi /usr/src/

Then continue with the following:
    sudo dkms add -m dell-wmi -v 20101214-rafi
    sudo dkms build -m dell-wmi -v 20101214-rafi
    sudo dkms install -m dell-wmi -v 20101214-rafi

When you restart, it should now report the swivel hinge state and Magick Rotation should now work.  You should be able to see the information through:
    sudo xxd -g1 /dev/input/magick-rotation

To remove the dkms install the command is:
    sudo dkms remove -m dell-wmi -v 20101214-rafi --all

Then to remove the dkms folder:
    sudo rm -r /usr/src/dell-wmi-20101214-rafi

For those of you wondering why we are using dkms for this, dkms will recompile the modified dell-wmi.ko kernel module every time there is a kernel update.


XT2 BIOS A09 OR LATER
A change in the Dell XT2 BIOS results in Rafi's modified dell-wmi.c no longer working.  This is apparently due to a change in the hex scan codes for the hinge switch.  Both enneract and Michael Knap agree on the new scan codes for tablet rotation, which is our primary concern.  The previous scan codes:
	{KE_SW , 0xe046, SW_TABLET_MODE,1},     /* Going to tablet mode */
	{KE_SW , 0xe047, SW_TABLET_MODE,0},     /* Coming from tablet mode */
are replaced by:
	{KE_SW , 0xffd2, SW_TABLET_MODE,1},     /* Going to tablet mode */
	{KE_SW , 0xffd3, SW_TABLET_MODE,0},     /* Coming from tablet mode */

However enneract goes on to find other scan codes that need to be altered affecting bezel buttons and other things.  Knap doesn't comment on them.  While Knap had the later A11 BIOS for simplicity's sake we'll assume enneract's hp-wmi update for the A09 is more complete and use it.  Some minor editing was done to enneract's comments to document the changes more clearly.  Should make it easier to revert changes that don't work especially since Rafi hasn't vetted these.  See:
enneract - BIOS A09:  http://ubuntuforums.org/showpost.php?p=9780095&postcount=1176
Michael Knap - BIOS A11:  http://ubuntuforums.org/showpost.php?p=11439576&postcount=1587

Open a terminal and copy (as root) the dell-wmi-20120302-A09 folder to /usr/src.  Either use the path to the MagickExtras folder (assuming you extracted it onto your Desktop): 
    sudo cp -a /home/yourusername/Desktop/magick-rotation/MagickExtras/dell-wmi-20120302-A09 /usr/src/
or after you change directories into the MagickExtras folder:
    sudo cp -a dell-wmi-20120302-A09 /usr/src/

Then continue with the following:
    sudo dkms add -m dell-wmi -v 20120302-A09
    sudo dkms build -m dell-wmi -v 20120302-A09
    sudo dkms install -m dell-wmi -v 20120302-A09

When you restart, it should now report the swivel hinge state and Magick Rotation should now work.

To remove the dkms install the command is:
    sudo dkms remove -m dell-wmi -v 20120302-A09 --all

Then to remove the dkms folder:
    sudo rm -r /usr/src/dell-wmi-20120302-A09

