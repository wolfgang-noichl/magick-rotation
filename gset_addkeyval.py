#!/usr/bin/env python2

from subprocess import getstatusoutput, getoutput
from sys import exit
from ast import literal_eval
import os

# Add Magick Rotation to Ubuntu Unity's system tray whitelist
cmd = "gsettings get com.canonical.Unity.Panel systray-whitelist"
results_wl = getstatusoutput(cmd)

whitelist = []

if not results_wl[0]:
    whitelist = literal_eval(results_wl[1])  # ignore whitelist empty case, highly unlikely
    if 'magick-rotation' in whitelist:
        print("magick-rotation has been found")
    else:
        cmd = 'gsettings set com.canonical.Unity.Panel systray-whitelist "['
        for index in range(len(whitelist)):
            cmd += "'" + whitelist[index] + "', "
        cmd += "'magick-rotation'" + ']"'
        results = getstatusoutput(cmd)

# Add/Enable Magick Rotation's extension to GNOME Shell's enabled extension list
cmd = "gsettings get org.gnome.shell enabled-extensions"
results_ex = getstatusoutput(cmd)

enabled_extensions = []

if not results_ex[0]:
    # determine if Gnome Shell version >= 3.2 before enabling extension
    gshell_str = getoutput("gnome-shell --version")  # e.g. string:  GNOME Shell 3.4.1
    gshell_ver = gshell_str.split(' ')[2]            # yields 3.4.1
    gshell_subver = int((gshell_ver.split('.'))[1])  # yields 4
    if gshell_subver >= 2:  # yes, 3.2 or better
        # create the 'extensions' directory if it does not already exist
        if not os.path.isdir(os.path.expanduser('~')+"/.local/share/gnome-shell/extensions"):
            os.mkdir(os.path.expanduser('~')+"/.local/share/gnome-shell/extensions")
        else:
            print("extensions folder already exists")
        if results_ex[1] == "@as []":  # no extension enabled, len(results_ex) = 6
            command = '''gsettings set org.gnome.shell enabled-extensions "['magick-rotation-extension']"'''
            results = getstatusoutput(command)
        else:
            enabled_extensions = literal_eval(results_ex[1])
            if 'magick-rotation-extension' in enabled_extensions:
                print("magick-rotation-extension already enabled")
            else:  # add 'magick-rotation-extension' to extension(s) in list
                command = 'gsettings set org.gnome.shell enabled-extensions "['
                for index in range(len(enabled_extensions)):
                    command += "'" + enabled_extensions[index] + "', "
                command += "'magick-rotation-extension'" + ']"'
                results = getstatusoutput(command)

exit(0)
