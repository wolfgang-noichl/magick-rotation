#!/usr/bin/env python
from commands import getstatusoutput
from hpwmi import *

class hinge:
    def __init__(self, win):
        self.hingelist = {"hpwmi":"/dev/input/hp-wmi"}
        self.win = win

    def get_switch(self):
        ret_switch = None
        for switch, filename in self.hingelist.iteritems():
            command = "stat " + filename
            if not getstatusoutput(command)[0]:
                ret_switch = hpwmi(self.win)
                break
        return ret_switch

if __name__ == "__main__":
    h = hinge()
    switch = h.get_swtich()
        
#vim :set expandtab :set tabstop=4 :set shiftwidth=4
