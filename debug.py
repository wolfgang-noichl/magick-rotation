#!/usr/bin/env python

import os.path
import datetime

class debug:
    def __init__(self, debug_on, win):
        self.win = win
        self.debug_on = debug_on

    def debug(self, data):
        debug_log = self.win.adv_table.get_debug_log()
        curtime = datetime.datetime.today()
        filedatestamp = curtime.strftime("%m-%d-%Y")
        log_file = "~/magick-log_" + filedatestamp

        if self.debug_on:
            print data

        if debug_log:
            timestamp = curtime.strftime("%H:%M:%S")
            value = "echo \'" + timestamp + ": " + data + "\' >> " + log_file
            os.system(value)
