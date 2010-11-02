#!/usr/bin/env python

import os.path
import datetime

class debug:
    def __init__(self, debug_on, win):
        self.win = win
        self.debug_on = debug_on

    def debug(self, data):
        debug_log = self.win.adv_table.get_debug_log()
        log_file = "~/magick-log"

        if self.debug_on:
            print data

        if debug_log:
            curtime = datetime.datetime.today()
            timestamp = curtime.strftime("%Y-%m-%d %H:%M:%S")
            filedatestamp = curtime.strftime("%Y-%m-%d")
            value = "echo \'" + timestamp + ": " + data + "\' >> " + log_file +  "_" + filedatestamp
            os.system(value)
