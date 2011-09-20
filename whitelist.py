#!/usr/bin/env python

from commands import getstatusoutput
from sys import exit

cmd = "gsettings get com.canonical.Unity.Panel systray-whitelist"
results = getstatusoutput(cmd)

whitelist = []

if not results[0]:
    whitelist = eval(results[1])
else:
    print results[1]
    exit(results[0])

if 'magick-rotation' in whitelist:
    print "magick-rotation has been found"
#    print whitelist
    exit(0)
else:
    cmd = 'gsettings set com.canonical.Unity.Panel systray-whitelist "['
    for index in range(len(whitelist)):
        cmd += "'" + whitelist[index] + "', "
    cmd += "'magick-rotation'" + ']"'
    results = getstatusoutput(cmd)
    exit(results[0])
    exit(0)
