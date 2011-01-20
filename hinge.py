#!/usr/bin/env python

from commands import getstatusoutput

from oem_wmi import *

class hinge:
    def __init__(self, win):
        self.hingelist = {"oem_wmi":["/dev/input/hp-wmi", "/dev/input/dell-wmi", "/dev/input/lenovo-acpi"]}
        self.win = win

    def get_switch(self):
        ret_switch = None
        for switch, filename_list in self.hingelist.iteritems():
            for filename in filename_list:
                command = "stat " + filename
                if not getstatusoutput(command)[0]:
                    ret_switch = oem_wmi(filename=filename, win=self.win)
                    break
        return ret_switch

if __name__ == "__main__":
    h = hinge()
    switch = h.get_switch()
        
#vim :set expandtab :set tabstop=4 :set shiftwidth=4
