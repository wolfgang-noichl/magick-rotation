The default dell-wmi with the kernel does not report the hinge switch state which Magick Rotation needs in order to work.  What we can do is the use this version modified by Rafi Rubin along with dkms.

Open a terminal and copy the dell-wmi-20101214-rafi folder to /usr/src.  Either use the path to the MagickExtras folder (assuming you extracted it onto your Desktop): 

    sudo cp -a /home/yourusername/Desktop/magick-rotation/MagickExtras/dell-wmi-20101214-rafi /usr/src/

or after you change directories into the MagickExtras folder:

    sudo cp -a dell-wmi-20101214-rafi /usr/src/

Then continue with the following:

    sudo dkms add -m dell-wmi -v 20101214-rafi
    sudo dkms build -m dell-wmi -v 20101214-rafi
    sudo dkms install -m dell-wmi -v 20101214-rafi

When you restart, it should now report the swivel hinge.  You should be able to see the information through:

    sudo xxd -g1 /dev/input/dell-wmi

For those of you wondering why we are using dkms for this, dkms will recompile the modified dell-wmi kernel module every time for you when there is a kernel change.
