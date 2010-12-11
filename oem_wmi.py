#!/usr/bin/env python

import struct
import os.path
from commands import getoutput
from config import *

class oem_wmi:
    def __init__(self, win=None):
        dev_node = os.path.exists("/dev/input/hp-wmi")
        if dev_node == True:
            filepath = "/dev/input/hp-wmi"
        else:
            filepath = "/dev/input/dell-wmi"
        self.filename = filepath
        self.win = win

    def run(self, data=None):
        fd = open(self.filename, "r")

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
                    if ev_val:
                        rotate = ROTATE_TABLET
                    else:
                        rotate = ROTATE_LAPTOP
                    command = "xrandr -o " + rotate
        #            print command
                    getoutput(command)

if __name__ == "__main__":
    h = oem_wmi(None)
    h.run()
