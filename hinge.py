#!/usr/bin/env python2

# For tablet PC's with switches that transmit hinge state (laptop or tablet)
# through an oem-wmi or oem-acpi, permitting a 'magick-rotation' symlink to be
# created for them in 62-magick.rules.  Currently supported examples include
# the hp-wmi, dell-wmi (modified version in MagickExtras), fujitsu-tablet
# (Fujitsu FUJ02BD, Fujitsu FUJ02BF), and lenovo-acpi.

import struct
import os.path
from commands import getstatusoutput, getoutput

from config import *

class hinge:
    def __init__(self, win=None, filename=None):
        self.magick_symlink = "/dev/input/magick-rotation"
        self.win = win

    def get_switch(self):
        ret_switch = None
        command = "stat " + self.magick_symlink
        if not getstatusoutput(command)[0]:
            ret_switch = hinge(win=self.win, filename=self.magick_symlink)
        return ret_switch

    def run(self, listener=None):
        fd = open(self.magick_symlink, "r")

        while True:
            EV_SW = 5
            SW_TABLET_MODE = 1
                # Originally was at 48, but found that if laptop is
                # suspended, the data gets offset too much.  If it is
                # at 8, it appears that it is able to find the value
                # more consistently.
            input = fd.read(8)
            ev_type = struct.unpack("H", input[0:2])[0]
            ev_code = struct.unpack("H", input[2:4])[0]
            ev_val  = struct.unpack("H", input[4:6])[0]
#            ev_type = struct.unpack("H", input[16:18])[0]
#            ev_code = struct.unpack("H", input[18:20])[0]
#            ev_val  = struct.unpack("H", input[20:22])[0]
            print "type %x " % ev_type,
            print "code %x " % ev_code, 
            print "value %x" % ev_val

            
            if self.win:
                ROTATE_TABLET = self.win.basic_table.get_swivel_option()
            else:
                ROTATE_TABLET = "right"
            ROTATE_LAPTOP = "normal"
        
            rotate = ROTATE_LAPTOP
            if ev_type == EV_SW:
                if ev_code == SW_TABLET_MODE:
                    hingevalue_toggle = self.win.basic_table.get_hingevalue_toggle()
                    if hingevalue_toggle == False:
                        if ev_val:
                            rotate = ROTATE_TABLET
                        else:
                            rotate = ROTATE_LAPTOP
                    # Added for HP models Compaq TC4200 & 4400
                    else:
                        if ev_val:
                            rotate = ROTATE_LAPTOP
                        else:
                            rotate = ROTATE_TABLET
                    command = "xrandr -o " + rotate
#                    print command
                    run_command = True
                    # This is to turn off rotation if the user
                    # turns off the polling
                    if listener:
                        if not listener.get_polling_status():
                            run_command = False
                    if run_command:
                        getoutput(command)

if __name__ == "__main__":
    h = hinge()
    switch = h.get_switch()

#vim :set expandtab :set tabstop=4 :set shiftwidth=4
