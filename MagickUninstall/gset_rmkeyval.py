#!/usr/bin/env python

from commands import getstatusoutput, getoutput
from sys import exit
from ast import literal_eval

# Remove Magick Rotation from Ubuntu Unity's system tray whitelist
cmd = "gsettings get com.canonical.Unity.Panel systray-whitelist"
results_wl = getstatusoutput(cmd)

whitelist = []

if not results_wl[0]:
    whitelist = literal_eval(results_wl[1])  # ignore whitelist empty case, highly unlikely
    if 'magick-rotation' not in whitelist:
        print "magick-rotation already removed from whitelist"
    else:
        whitelist_remove = ['magick-rotation']
        whitelist_new = [x for x in whitelist if x not in whitelist_remove]
        command = 'gsettings set com.canonical.Unity.Panel systray-whitelist "' + str(whitelist_new) + '"'
        results = getstatusoutput(command)

# Remove/Disable Magick Rotation's extension in GNOME Shell's enabled extension list
cmd = "gsettings get org.gnome.shell enabled-extensions"
results_ex = getstatusoutput(cmd)

enabled_extensions = []

if not results_ex[0]:
    # has to be Gnome Shell version >= 3.2 for there to be an enabled extension to disable
    gshell_str = getoutput("gnome-shell --version")  # e.g. string:  GNOME Shell 3.4.1
    gshell_ver = gshell_str.split(' ')[2]            # yields 3.4.1
    gshell_subver = int((gshell_ver.split('.'))[1])  # yields 4
    if gshell_subver >= 2:  # yes, 3.2 or better
        if results_ex[1] == "@as []":  # no extension enabled, len(results_ex) = 6
            print "magick-rotation-extension already disabled"
        else:
            enabled_extensions = literal_eval(results_ex[1])
            if 'magick-rotation-extension' not in enabled_extensions:
                print "magick-rotation-extension already disabled"
            elif enabled_extensions == "['magick-rotation-extension']":
                command = 'gsettings set org.gnome.shell enabled-extensions "[]"'
                results = getstatusoutput(command)
            else:
                extension_disable = ['magick-rotation-extension']
                enabled_extensions_new = [x for x in enabled_extensions if x not in extension_disable]
                command = 'gsettings set org.gnome.shell enabled-extensions "' + str(enabled_extensions_new) + '"'
                results = getstatusoutput(command)

exit(0)
