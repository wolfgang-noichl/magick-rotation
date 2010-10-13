#!/usr/bin/env python

from time import sleep
import os.path
from config import *
from xrotate import *

import datetime

from debug import *

class hp_wmi:
    def __init__(self, debug_on, win):
        self.debug = debug(debug_on, win)
        state_hp_wmi="/sys/devices/platform/hp-wmi/dock"
        state_hp_wmi_patched="/sys/devices/platform/hp-wmi/tablet"

        self.capable = False

        if os.path.exists(state_hp_wmi_patched):
            self.stfile=open(state_hp_wmi_patched, "r")
            self.debug.debug("Use patched hp_wmi 'tablet' event file")
            self.capable = True
        elif os.path.exists(state_hp_wmi):
            self.stfile=open(state_hp_wmi, "r")
            self.debug.debug("Use native hp_wmi 'dock' event file")
            self.capable = True

    def is_capable(self):
        return self.capable

    def get_tablet_state(self):
        return self.tablet_state

    def get_normal_state(self):
        return self.normal_state

    def get_state(self):
        self.debug.debug("opening status file")
        data = self.stfile.read()
        self.stfile.seek(0)
        self.debug.debug("file opened successfully")
        if data == "4\n" or data == "1\n":
            data = 1
        else:
            data = 0
        return data

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
        # tablet/normal state files from hp_wmi
        self.processing = True
        self.polling = True
        self.win = win
        self.debug = debug(debug_on, win)

        hp = hp_wmi(debug_on, self.win)
        self.has_hp_wmi = hp.is_capable()
        if self.has_hp_wmi:
            self.listen = hp
        else:
            randr = xrandr()
            self.listen = randr

    # Tells the engine if the screen should be rotated
    def rotate_screen(self):
        return self.has_hp_wmi

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
                cur_state=self.listen.get_state()
                self.debug.debug("cur_state: %s " % cur_state)
                self.debug.debug("old_state: %s " % old_state)
                if (old_state != cur_state):
                    if (cur_state == normal_state):
                        if self.polling: 
                            run_func(True)
                        else:
                            self.debug.debug("I'm disabled, so do nothing.")
                    elif (cur_state == tablet_state):
                        if self.polling: 
                            run_func(False)
                        else:
                            self.debug.debug("I'm disabled, so do nothing.")
                    else:
                        print "Unknown state:", cur_state
            except:
                self.debug.debug("The try in rotation check failed")

            old_state=cur_state
            waittime = float(self.win.adv_table.get_waittime())
            
            sleep(waittime)
