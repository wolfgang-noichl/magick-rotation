#!/usr/bin/env python

import gtk
import pygtk
import gobject
import sys
import thread
import os.path
from commands import getstatusoutput, getoutput
import platform
import pango

# for Magick Rotation's Gnome Shell 3.2 extension (spec.s changed from 3.0) removal
# has to be Gnome Shell >= 3.2 for there to be an extension to remove
if os.path.exists("/usr/bin/gnome-shell"):
    gshell_str = getoutput("gnome-shell --version")  # e.g. string:  GNOME Shell 3.4.1
    gshell_ver = gshell_str.split(' ')[2]            # yields 3.4.1
    gshell_subver = int((gshell_ver.split('.'))[1])  # yields 4
    if gshell_subver >= 2:
        gshell = True  # yes, 3.2 or better and installed

class uninstaller_dialog(gtk.MessageDialog):
    def __init__(self,  parent=None, flags=0, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_NONE, message_format=None):
        gtk.MessageDialog.__init__(self, parent,  flags,  type,  buttons,  message_format)

    def list_packages(self, packages, engine,  win):
        self.add_buttons(gtk.STOCK_OK,  gtk.RESPONSE_ACCEPT,  gtk.STOCK_CANCEL,  gtk.RESPONSE_REJECT)
        self.set_border_width(15)
        message = ""
        message = "Magick Rotation files to be uninstalled.\n"
        
        for package in packages:
            message += " " + str(package) + '\n'
        message += "\nOK to remove the above?\n"
        
        self.set_markup(message)
        engine.log.write(message)
        self.connect("close",  self.close)
        self.connect("response",  self.check_response, engine, win)

        self.show()
    
    def check_response(self,  dialog,  response, engine,  win):
        self.destroy()
        
        if response == gtk.RESPONSE_ACCEPT:
            win.show_all()
            thread.start_new_thread(engine.run_uninstaller,  (None, ))
        else:
            win.close_window()
        
    def close(self,  dialog=None):
        self.destroy()
        return True

class uninstaller_window(gtk.Window):
    def __init__(self,  filepath):
        gtk.Window.__init__(self)
        self.filepath = filepath
        image_filename = filepath + "/UnMagickSplash.png"
        HBox = gtk.HBox()
        VBox = gtk.VBox()

        self.buffer = gtk.TextBuffer()
        self.text_view = gtk.TextView()
        self.text_view.set_editable(False)
        self.text_view.set_buffer(self.buffer)
        self.text_view.set_cursor_visible(False)
        self.text_view.set_wrap_mode(gtk.WRAP_CHAR)
        self.text_win = gtk.ScrolledWindow()
        self.text_win.set_policy(gtk.POLICY_NEVER, gtk.POLICY_AUTOMATIC)
        self.text_win.add(self.text_view)
        self.text_win.set_size_request(250, 100)

        self.pkg_label = gtk.Label()
	self.pkg_label.set_text("")
        self.pkg_label.set_line_wrap(20)

        image = gtk.Image()
        image.set_from_file(image_filename) 

        HBox.pack_start(image)        
        HBox.pack_start(self.text_win)

        VBox.pack_start(HBox)
        VBox.pack_start(self.pkg_label)

        self.add(VBox)
        self.set_position(gtk.WIN_POS_CENTER_ALWAYS)
        self.connect("delete-event", self.close_window)
        self.hide()

    def get_filepath(self):
        return self.filepath

    def add_text(self,  text):
        self.buffer.insert_at_cursor(text)
        #Once we print the information, move the scrollbar where 
        #the last bit of information was written.
        vscroll = self.text_win.get_vscrollbar()
        #The adjustment has the slider values
        vadj = vscroll.get_adjustment()
        #The upper value is the maximum scroll point
        value = vadj.get_upper()
        if value:
            vadj.set_value(value)

    def add_bold_text(self, text):
        self.buffer.create_tag("bold", weight=pango.WEIGHT_BOLD)
        iter = self.buffer.get_end_iter()
        self.buffer.insert_with_tags_by_name(iter, text, "bold")

    def close_window(self, widget=None, data=None):
        self.destroy()
        gtk.main_quit()
        return True

class uninstaller_engine:
    def __init__(self,  path, usr_name=None):
        self.usr_name = usr_name
        self.win = uninstaller_window(path)
        self.filepath = path
        logfile = self.filepath + "/uninstall_log"
        self.log = open(logfile,  "w")

    def remove_checkmagick(self):
        version = platform.machine()
        if version == "x86_64":
            version = "checkmagick64"
        else:
            version = "checkmagick32"
        command = "rm /usr/bin/" + version
        self.log.write("\n\n")
        self.log.write("Removing checkmagick\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_udev_rules(self):
        command = "rm /etc/udev/rules.d/62-magick.rules"
        self.log.write("Removing 62-magick.rules\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_user(self):
        username = self.usr_name
        if os.path.exists("/usr/bin/zypper"):
            command = "usermod -R magick " + str(username)
        else:
            command = "gpasswd -d " + str(username) + " magick"
        self.log.write("Remove user in magick group\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_group(self):
        command = "groupdel magick"
        self.log.write("\n")
        self.log.write("Removing magick group\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_magick_icons(self):
        icon_filename = {"magick_icons":["MagickAbout.png", "magick-rotation-disabled.png", "magick-rotation-disabled-touchoff.png", "magick-rotation-enabled.png", "magick-rotation-enabled-touchoff.png"]}
        self.log.write("Removing MagickIcon files\n")
        for magick_icons, filename_list in icon_filename.iteritems():
            for filename in filename_list:
                self.log.write("\n")
                command = "rm /usr/share/magick-rotation/MagickIcons/" + filename
                self.log.write(command)
                success = getstatusoutput(command)
                self.log.write("\n")
                self.log.write(str(success[0]))
                self.log.write("\n")
                self.log.write(str(success[1]))
        return success

    def remove_magickicons_folder(self):
        command = "rmdir /usr/share/magick-rotation/MagickIcons"
        self.log.write("\n")
        self.log.write("Removing folder MagickIcons from /usr/share/magick-rotation\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_magick_files(self):
        magick_filename = {"magick_files":["ChangeLog", "config.py", "debug.py", "gui_gtk.py", "hinge.py", "listener.py", "Magick-README.txt", "magick-rotation", "xrotate.py"]}
        self.log.write("Removing magick-rotation files\n")
        for magick_files, filename_list in magick_filename.iteritems():
            for filename in filename_list:
                self.log.write("\n")
                command = "rm /usr/share/magick-rotation/" + filename
                self.log.write(command)
                success = getstatusoutput(command)
                self.log.write("\n")
                self.log.write(str(success[0]))
                self.log.write("\n")
                self.log.write(str(success[1]))
        return success

    def remove_magick_folder(self):
#        command = "rmdir /usr/share/magick-rotation"
        command = "rm -rf /usr/share/magick-rotation"
        self.log.write("\n")
        self.log.write("Removing folder magick-rotation from /usr/share\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_xml_config(self):
        username = self.usr_name
        command = "rm /home/" + str(username) + "/.magick-rotation.xml"
        self.log.write("Removing file magick-rotation.xml from /home/username\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_autostart_config(self):
        username = self.usr_name
        command = "rm /home/" + str(username) + "/.config/autostart/magick-rotation.desktop"
        self.log.write("Removing file magick-rotation.desktop from /home/username/.config/autostart\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    if gshell == True:
        def remove_magickextension_folder(self):
            username = self.usr_name
            command = "rm -rf /home/" + str(username) + "/.local/share/gnome-shell/extensions/magick-rotation-extension"
            self.log.write("Removing magick-rotation-extension folder in ~/.local/share/gnome-shell/extensions\n")
            self.log.write(command)
            success = getstatusoutput(command)
            self.log.write("\n")
            self.log.write(str(success[0]))
            self.log.write("\n")
            self.log.write(str(success[1]))
            self.log.write("\n")
            return success

    def execute_steps(self,  data=None):
        dialog = uninstaller_dialog(self.win,  0, gtk.MESSAGE_INFO,  gtk.BUTTONS_NONE,  None)
        package_list = []
        # Ask the user if they want to uninstall Magick Rotation files and folders.
        package_list.append("\nFile to remove in /usr/bin:\n checkmagick\n\nFile to remove in /etc/udev/rules.d:\n 62-magick.rules\n\nRemove group:\n magick\n\nFolder to remove in /usr/share:\n magick-rotation\n\nFiles to remove in /home/username\n .magick-rotation.xml\n magick-rotation.desktop\n")
        # Ask the user if they want to uninstall the Magick extension for Gnome Shell.
        if gshell == True:
            package_list.append("Shell extension to remove:\n magick-rotation-extension\n")
        dialog.list_packages(package_list,  self,  self.win)

    def run_uninstaller(self,  data=None):
            self.win.add_text("Removing checkmagick\n")
            success = self.remove_checkmagick()
            self.win.add_text("Removing udev rules\n")
            success = self.remove_udev_rules()
            self.win.add_text("Removing user in magick group\n")
            success = self.remove_user()
            self.win.add_text("Removing magick group\n")
            success = self.remove_group()
            self.win.add_text("Removing MagickIcons files\n")
            success = self.remove_magick_icons()
            self.win.add_text("Removing MagickIcons folder\n")
            success = self.remove_magickicons_folder()
            self.win.add_text("Removing magick-rotation files\n")
            success = self.remove_magick_files()
            self.win.add_text("Removing magick-rotation folder\n")
            success = self.remove_magick_folder()
            self.win.add_text("Removing Magick .xml file\n")
            success = self.remove_xml_config()
            self.win.add_text("Removing Magick .desktop file\n")
            success = self.remove_autostart_config()
            if gshell == True:
                self.win.add_text("Disabled Magick extension\n")
                self.win.add_text("Removing Magick extension folder\n")
                success = self.remove_magickextension_folder()
            self.win.add_bold_text("\nUNINSTALL COMPLETE")
            self.win.add_text("\nA system restart is required to\n")
            self.win.add_text("ensure Magick Rotation is removed.\n")

    def run(self):
        gobject.threads_init()
        thread.start_new_thread(self.execute_steps, (None, ))
        gtk.main()

if __name__ == "__main__" :
    path = os.path.dirname(sys.argv[0])
    if len(sys.argv) > 1:
        usr_name = sys.argv[1]
    else:
        usr_name = None
    if not path:
        path = "."

    # pass username unchanged to class uninstaller_engine
    if usr_name:
        i = uninstaller_engine(path, usr_name)
    else:
        i = uninstaller_engine(path)
    i.run()
