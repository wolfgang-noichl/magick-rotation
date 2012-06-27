#!/usr/bin/env python

import sys
import pickle
from xml.dom import minidom
import os.path
from commands import getoutput

class config:
    def __init__(self):
        self.filename = "~/.magick-rotation.xml"
        self.old_filename = "~/.magick-rotation.conf"
        self.option = {}

    def load_data(self):
        #test to see if the xml file exists.  
        #If it does, use it, otherwise, try to load the old.
        config = os.path.expanduser(self.filename)
        if os.path.exists(config):
            return self.load_xml()
        else:
            return self.load_old_data()

    def load_old_data (self):
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
        touch_toggle = True
        hingevalue_toggle = False
        version = "1.1"

        config = os.path.expanduser(self.old_filename)
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

        return [bool(autostart), rotate_mode, run_tablet_before, run_tablet, \
                run_normal_before, run_normal, bool(isnotify), int(notify_timeout), \
                float(waittime), bool(debug_log), bool(touch_toggle), \
                bool(hingevalue_toggle), version]

    def load_xml(self):
        # Default values
        self.option["autostart"] = True
        self.option["rotate_mode"] = 'right'
        self.option["run_tablet"] = "cellwriter --show-window"
        self.option["run_normal"] = "cellwriter --hide-window"
        self.option["run_tablet_before"] = ""
        self.option["run_normal_before"] = ""
        self.option["isnotify"] = True
        self.option["notify_timeout"] = 3000
        self.option["waittime"] = 0.25
        self.option["debug_log"] = False
        self.option["touch_toggle"] = True
        self.option["hingevalue_toggle"] = False
        self.option["version"] = "1.6"

        config = minidom.parse(os.path.expanduser(self.filename))

        for node in config.getElementsByTagName("option"):
            # Get the name of the option attribute
            name = str(node.getAttribute("name"))
            # Read through the value that is a child node of option
            values = node.getElementsByTagName("value")
            for node2 in values:
                # Each child node in the value is a text that contains the 
                # option value
                for node3 in node2.childNodes:
                    if node3.nodeType == minidom.Node.TEXT_NODE:
                        opt_val = str(node3.data).strip('"')
                        if opt_val == "False":
                            opt_val = False
                        elif opt_val == "True":
                            opt_val = True
                        self.option[name] = opt_val

        return [self.option["autostart"], self.option["rotate_mode"], self.option["run_tablet_before"], \
                self.option["run_tablet"], self.option["run_normal_before"], self.option["run_normal"], \
                self.option["isnotify"], int(self.option["notify_timeout"]), float(self.option["waittime"]), \
                self.option["debug_log"], self.option["touch_toggle"],  self.option["hingevalue_toggle"], \
                self.option["version"]]

    def write_data(self, data):
        self.option["autostart"] = data[0]
        self.option["rotate_mode"] = data[1]
        self.option["run_tablet_before"] = data[2]
        self.option["run_tablet"] = data[3]
        self.option["run_normal_before"] = data[4]
        self.option["run_normal"] = data[5]
        self.option["isnotify"] = data[6]
        self.option["notify_timeout"] = data[7]
        self.option["waittime"] = data[8]
        self.option["debug_log"] = data[9]
        self.option["touch_toggle"] = data[10]
        self.option["hingevalue_toggle"] = data[11]
        self.option["version"] = data[12]

        # Convert back to xml format
        write_str = "<magick-rotation>\n"
        write_str += '    <version>"' + data[12] + '"</version>\n'
        for name, value in self.option.iteritems():
            if name != "version":
                write_str += '    <option name="' + str(name) + '">\n' + \
                            '        <value>"' + str(value) + '"</value>\n' + \
                            '    </option>\n'
        write_str += "</magick-rotation>\n"

        config = os.path.expanduser(self.filename)
        conf = open(config, "w")
        conf.write(write_str)
        self.add_autostart(data[0])
        print "Config written to", self.filename


    def add_autostart(self, autostart):
        # uninstalled - run from folder .desktop file
        autostart_desktop="""
[Desktop Entry]
Type=Application
Name=Magick Rotation for tablet PC's
Exec=%s
Comment=Tablet PC automatic rotation
Icon=redo
"""
        # installed - use /usr/share path in magick-rotation.desktop
        autostart_desktop_inst="""
[Desktop Entry]
Type=Application
Name=Magick Rotation for tablet PC's
Exec=/usr/share/magick-rotation/magick-rotation
Comment=Tablet PC automatic rotation
Icon=/usr/share/magick-rotation/MagickIcons/magick-rotation-enabled.png
Path=/usr/share/magick-rotation/
"""
        # check if Magick Rotation installed by Installer
        if os.path.exists("/usr/share/magick-rotation/magick-rotation"):
            installed = True
        else:
            installed = False

        autostart_dsktop_path = "~/.config/autostart/magick-rotation.desktop"

        # check if autostart is also installed
        if os.path.exists(os.path.expanduser(autostart_dsktop_path)):
            inst_autostart = True
        else:
            inst_autostart = False

        # for Gnome Shell 3.4 autostart bug
        if os.path.exists("/usr/bin/gnome-shell"):
            gshell_str = getoutput("gnome-shell --version")  # e.g. string:  GNOME Shell 3.4.1
            gshell_ver = gshell_str.split(' ')[2]            # yields 3.4.1
            gshell_subver = int((gshell_ver.split('.'))[1])  # yields 4
        else:
            gshell_subver = 2  # i.e. no Gnome Shell or version < 3.4

        # based on the .magick-rotation.xml autostart entry and the above either
        # write, leave alone, or remove the magick-rotation.desktop file
        if autostart:
            if not os.path.isdir(os.path.expanduser('~')+"/.config/autostart/"):
                os.mkdir(os.path.expanduser('~')+"/.config/autostart/")

            if not installed:  # run from folder, wherever it is
                folder_path = os.path.abspath(sys.argv[0])
                if gshell_subver >= 4:
                    wr = open(os.path.expanduser(autostart_dsktop_path), "w")
                    # append the Gnome Shell 3.4 bug work around
                    wr.write(autostart_desktop % folder_path + "X-GNOME-Autostart-Delay=3")
                else:
                    wr = open(os.path.expanduser(autostart_dsktop_path), "w")
                    wr.write(autostart_desktop % folder_path)
                wr.close()
            else:
                if not inst_autostart:  # re-install removed Installer autostart
                    if gshell_subver >= 4:
                        wr=open(os.path.expanduser(autostart_dsktop_path), "w")
                        # append the Gnome Shell 3.4 bug work around
                        wr.write(autostart_desktop_inst + "X-GNOME-Autostart-Delay=3")
                    else:
                        wr=open(os.path.expanduser(autostart_dsktop_path), "w")
                        wr.write(autostart_desktop_inst)
                    wr.close()
        else:
            if os.path.exists(os.path.expanduser(autostart_dsktop_path)):
                os.remove(os.path.expanduser(autostart_dsktop_path))

if __name__ == "__main__":
    c = config()
    c.write_data(c.load_data())
