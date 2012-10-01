#!/usr/bin/env python2

from time import sleep
import os.path
import sys
from xrotate import *
from commands import getstatusoutput
import platform

import datetime

from debug import *

class xrandr:
    def __init__(self):
        self.display = screen()

    def get_state(self):
        state = self.display.get_cur_value()
        if state == "normal":
            ret_val = 0
        else:
            ret_val = 1
            
        return ret_val

class listener:
    def __init__(self, debug_on, win):
        self.processing = True
        self.polling = True
        self.win = win
        self.debug = debug(debug_on, win)

        randr = xrandr()
        self.listen = randr

    def toggle_polling(self):
        if self.polling:
            self.polling = False
        else:
            self.polling = True

    def get_polling_status(self):
        return self.polling

    def stop_processing(self):
        self.processing = False

    def state_notifier(self, run_func):
        tablet_state = 1
        normal_state = 0
        old_state = None

        while self.processing:
            self.debug.debug("checking for rotation")
            try:
                version = platform.machine()
                check_machine = "checkmagick32"
                if version == "x86_64":
                    check_machine = "checkmagick64"
                if os.path.exists("/usr/bin/" + check_machine):
                    randr_check = "/usr/bin/" + check_machine
                else:
                    randr_check = self.win.get_path() + check_machine
                self.debug.debug(randr_check)
                cur_state = getstatusoutput(randr_check)[0] / 256
                self.debug.debug("cur_state: %s " % cur_state)
                self.debug.debug("old_state: %s " % old_state)
                if (old_state != cur_state):
                    if (cur_state == 0):
                        if self.polling: 
                            run_func(cur_state)
                        else:
                            self.debug.debug("I'm disabled, so do nothing.")
                    elif (cur_state != 0):
                        if self.polling: 
                            run_func(cur_state)
                        else:
                            self.debug.debug("I'm disabled, so do nothing.")
                    else:
                        print "Unknown state:", cur_state
            except:
                self.debug.debug("The try in rotation check failed")

            old_state = cur_state
