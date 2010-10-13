#!/usr/bin/env python
import os.path
import sys
import os
import pickle

class config:
    def __init__(self):
        self.filename = "~/.magick-rotation.conf"

    def load_data(self):
        # Default values
        autostart = True
        rotate_mode = 'right'
        run_tablet = "cellwriter --show-window"
        run_normal = "cellwriter --hide-window"
        run_tablet_before = ""
        run_normal_before = ""
        isnotify = True
        notify_timeout = 3000
        waittime = 0.25
        debug_log = False

        config = os.path.expanduser(self.filename)
        if os.path.exists(config):
            conffd = open(config, "r")
            pick = pickle.Unpickler(conffd)
            try:
                autostart, rotate_mode, run_tablet_before, run_tablet, \
                run_normal_before, run_normal, isnotify, notify_timeout, \
                waittime, debug_log = pick.load()
            except:
                print "Config file invalid, I will delete it and load defaults"
                os.remove(config)

        return [autostart, rotate_mode, run_tablet_before, run_tablet, \
                run_normal_before, run_normal, isnotify, notify_timeout, \
                waittime, debug_log]

    def write_data(self, data):
        config = os.path.expanduser(self.filename)
        conf = open(config, "w")
        pick = pickle.Pickler(conf)
        pick.dump(data)
        # Write to autostart if requested
        self.add_autostart(data[0]    )
        print "Config written to", self.filename

    def add_autostart(self, autostart):
        autostart_desktop="""
[Desktop Entry]
Type=Application
Name = Magick Rotation for HP tablet pc's
Exec=%s
Icon = redo
Comment=Helps with automatic rotation
"""
        autostart_file_path = "~/.config/autostart/magick-rotation.desktop"

        if autostart:
            astfl=os.path.abspath(sys.argv[0])
            if not os.path.isdir(os.path.expanduser('~')+"/.config/autostart/"):
                os.mkdir(os.path.expanduser('~')+"/.config/autostart/")
            wr=open(os.path.expanduser(autostart_file_path), "w")
            wr.write(autostart_desktop % astfl)
            wr.close()
        else:
            if os.path.exists(os.path.expanduser(autostart_file_path)):
                os.remove(os.path.expanduser(autostart_file_path))


