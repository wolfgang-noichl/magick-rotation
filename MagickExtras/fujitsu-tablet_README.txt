
Magick Rotation 1.6						April 5, 2012


Robert Gerlach's kernel driver fujitsu-tablet.ko or "Fujitsu tablet pc extras driver" was accepted into the 3.3 kernel.  With this addition Fujitsu tablet PCs are now able to report the hinge switch state.  Magick Rotation can then read the reported laptop or tablet state through the magick-rotation symlink created for Fujitsu tablet PCs by the udev rule in 62-magick.rules.  In order to backport hinge switch support to older kernels the module is included as a dkms implementation in MagickExtras.


Open a terminal and copy (as root) the fujitsu-tablet-20120404-gerlach folder to /usr/src.  Either use the path to the MagickExtras folder (assuming you extracted it onto your Desktop): 
    sudo cp -a /home/yourusername/Desktop/magick-rotation/MagickExtras/fujitsu-tablet-20120404-gerlach /usr/src/
or after you change directories into the MagickExtras folder:
    sudo cp -a fujitsu-tablet-20120404-gerlach /usr/src/

Then continue with the following:
    sudo dkms add -m fujitsu-tablet -v 20120404-gerlach
    sudo dkms build -m fujitsu-tablet -v 20120404-gerlach
    sudo dkms install -m fujitsu-tablet -v 20120404-gerlach

When you restart, it should now report the swivel hinge state and Magick Rotation should now work.  You should be able to see the information through:
    sudo xxd -g1 /dev/input/magick-rotation

To remove the dkms install the command is:
    sudo dkms remove -m fujitsu-tablet -v 20120404-gerlach --all

Then to remove the dkms folder:
    sudo rm -r /usr/src/fujitsu-tablet-20120404-gerlach

For those of you wondering why we are using dkms for this, dkms will recompile the fujitsu-tablet.ko kernel module every time there is a kernel update.

