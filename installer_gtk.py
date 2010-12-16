#!/usr/bin/env python

import gtk
import pygtk
import gobject
import sys
import thread
try:
    from apt_pm import *
    apt_installed = True
except ImportError:
    apt_installed = False
    
import os.path
from commands import getstatusoutput
import platform
import pango

class installer_dialog(gtk.MessageDialog):
    def __init__(self,  parent=None, flags=0, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_NONE, message_format=None):
        gtk.MessageDialog.__init__(self, parent,  flags,  type,  buttons,  message_format)

    def list_packages(self, packages, engine,  win):
        self.add_buttons(gtk.STOCK_OK,  gtk.RESPONSE_ACCEPT,  gtk.STOCK_CANCEL,  gtk.RESPONSE_REJECT)
        message = ""
        
        if len(packages) > 1:
            message = "The following packages are going to be installed:\n"
        for package in packages:
            message += " " + str(package) + '\n'
        message += "\nOk to install?\n"
        
        self.set_markup(message)
        engine.log.write(message)
        self.connect("close",  self.close)
        self.connect("response",  self.check_response, engine, win)

        self.show()
        
    def no_installer(self,  engine,  win):
        self.add_buttons(gtk.STOCK_CLOSE,  gtk.RESPONSE_CLOSE)
        message = "There are no package managers that are compatible\n"
        message += "with this installer.  Please read INSTALLER.txt\n"
        message += "for manual installation instructions.\n"
        
        self.set_markup(message)
        engine.log.write(message)
        self.connect("close",  self.close)
        self.connect("response",  self.check_response, engine, win)

        self.show()
        
    def missing_packages(self, packages, engine,  win):
        self.add_buttons(gtk.STOCK_CLOSE,  gtk.RESPONSE_CLOSE)
        message = "The following packages are missing:\n"
        for package in packages:
            message += " " + str(package) + '\n'
        message += "\nInstallation cannot be completed.\n"
        message += "Please read INSTALLER.txt for manual\n"
        message += "installation instructions.\n"
        
        self.set_markup(message)
        engine.log.write(message)
        self.connect("close",  self.close)
        self.connect("response",  self.check_response, engine, win)

        self.show()
    
    def check_response(self,  dialog,  response, engine,  win):
        self.destroy()
        
        if response == gtk.RESPONSE_ACCEPT:
            win.show_all()
            thread.start_new_thread(engine.run_installer,  (None, ))
        else:
            win.close_window()
        
    def close(self,  dialog=None):
        self.destroy()
        return True

class installer_window(gtk.Window):
    def __init__(self,  filepath):
        gtk.Window.__init__(self)
        self.filepath = filepath
        image_filename = filepath + "/MagickIcons/MagickSplash.png"
        HBox = gtk.HBox()
        VBox = gtk.VBox()

        self.fetching = False
        self.installing = False

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
        self.progress_bar = gtk.ProgressBar()
        self.pkg_label.set_line_wrap(20)

        image = gtk.Image()
        image.set_from_file(image_filename) 

        HBox.pack_start(image)        
        HBox.pack_start(self.text_win)

        VBox.pack_start(HBox)
        VBox.pack_start(self.pkg_label)
        VBox.pack_start(self.progress_bar)

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
        # Prevent the window from closing when the system is
        # installing the packages
        if self.installing and not self.fetching:
            pass
        else:
            self.destroy()
            gtk.main_quit()
        return True

class installer_engine:
    def __init__(self,  path):
        self.win = installer_window(path)
        self.filepath = path
        logfile = self.filepath + "/install_log"
        self.log = open(logfile,  "w")

    def compile_checkmagick(self):
        version = platform.machine()
        if version == "x86_64":
            version = "/checkmagick64"
        else:
            version = "/checkmagick32"

        command = "gcc -lX11 -lXrandr " +  self.filepath + "/check.c -o " + self.filepath + version
        self.log.write("Compiling check.c\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def install_udev_rules(self):
        command = "cp 62-magick.rules /etc/udev/rules.d/"
        self.log.write("Copying\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_install_check(self):
        command = "rm " + self.filepath + "/firstrun"
        self.log.write("Removing installed filecheck\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def execute_steps(self,  data=None):
        dialog = installer_dialog(self.win,  0, gtk.MESSAGE_INFO,  gtk.BUTTONS_NONE,  None)
        if not apt_installed:
            dialog.no_installer(self,  self.win)
            return -1
        self.apt = apt_pm()

        packages = self.apt.find_uninstalled(["libx11-dev", "libxrandr-dev"])
        
        if packages[1]:
            dialog.missing_packages(packages[1],  self,  self.win)
            self.remove_install_check()
            return -1
        else:
            # Ask the user if they want to install the package
            # If they don't, then exit installer and do not 
            # launch magick-rotation
            
            package_string = ""
            package_list = []
            self.packages_to_install = False
            if packages[0]:
                for package in packages[0]:
                    if not package_string:
                        package_string += package
                    else:
                        package_string += (" " + package)
                self.apt.mark_packages(packages[0])
                self.packages_to_install = True

                packages = self.apt.list_packages()
                
                for package in packages:
                    package_list.append(package.name)
                    
            package_list.append("\n\nFile to install in /etc/udev/rules.d:\n62-magick.rules\n")
            dialog.list_packages(package_list,  self,  self.win)
                
    def close_dialog(self,  dialog=None):
        self.win.add_text("Canceling installation.")
        dialog.close()
        return True

    def run_installer(self,  data=None):
            if self.packages_to_install:
                self.log.write("Installing packages\n")
                self.apt.install(self.win)
                self.win.progress_bar.hide()
                self.win.pkg_label.hide()
            self.win.add_text("Compiling check.c\n")
            success = self.compile_checkmagick()
            self.win.add_text("Installing udev rules\n")
            success = self.install_udev_rules()
            success = self.remove_install_check()
            self.win.add_bold_text("\n\n\nINSTALLATION COMPLETE")
            self.win.add_text("\nA system restart is \nrequired to ensure that \n")
            self.win.add_text("magick-rotation will work.\n")

    def run(self):
        gobject.threads_init()
        #self.win.show_all()
        thread.start_new_thread(self.execute_steps, (None, ))
        gtk.main()

if __name__ == "__main__" :
    path = os.path.dirname(sys.argv[0])
#    if not path or path == ".":
  #      path = "./"
    if not path:
        path = "."

    i = installer_engine(path)
    i.run()
