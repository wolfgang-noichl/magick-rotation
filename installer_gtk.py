#!/usr/bin/env python

import gtk
import pygtk
import gobject
import sys
import thread
import os.path
from commands import getstatusoutput
import platform
import pango

sys.dont_write_bytecode = True

# for Fedora
if os.path.exists("/usr/bin/yum"):
    packman = "YUM"
# for openSUSE
elif os.path.exists("/usr/bin/zypper"):
    packman = "YaST"
# for Ubuntu and to tell non-supported Distros to manually install
else:
    try:
        from apt_pm import *
        apt_installed = True
    except ImportError:
        apt_installed = False
    packman = "APT"

class installer_dialog(gtk.MessageDialog):
    def __init__(self,  parent=None, flags=0, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_NONE, message_format=None):
        gtk.MessageDialog.__init__(self, parent,  flags,  type,  buttons,  message_format)

    def list_packages(self, packages, engine,  win):
        self.add_buttons(gtk.STOCK_OK,  gtk.RESPONSE_ACCEPT,  gtk.STOCK_CANCEL,  gtk.RESPONSE_REJECT)
        self.set_border_width(15)
        message = ""

        if packman == "APT":
            if len(packages) > 1:
                message = "APT packages to be installed:\n"
            for package in packages:
                message += " " + str(package) + '\n'
        elif packman == "YUM":
            if len(packages) > 1:
                message = "YUM packages to be installed:\n"
            for package in packages:
                message += " " + str(package) + '\n'
        elif packman == "YaST":
            if len(packages) > 1:
                message = "YaST packages to be installed:\n"
            for package in packages:
                message += " " + str(package) + '\n'
        message += "\nOK to install the above?\n"
        
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
        if packman == "APT":
            self.progress_bar = gtk.ProgressBar()
        self.pkg_label.set_line_wrap(20)

        image = gtk.Image()
        image.set_from_file(image_filename) 

        HBox.pack_start(image)        
        HBox.pack_start(self.text_win)

        VBox.pack_start(HBox)
        VBox.pack_start(self.pkg_label)
        if packman == "APT":
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
    def __init__(self,  path, usr_name=None):
        self.usr_name = usr_name
        self.win = installer_window(path)
        self.filepath = path
        logfile = self.filepath + "/install_log"
        self.log = open(logfile,  "w")

    if packman == "YUM":
        def install_yum_packages(self):
            packages = {"yum_packages":["gcc", "libX11-devel", "libXrandr-devel"]}
            for yum_packages, package_list in packages.iteritems():
                for package in package_list:
                    command = "yum install " + package
                    self.log.write(command)
                    success = getstatusoutput(command)
                    self.log.write("\n")
                    self.log.write(str(success[0]))
                    self.log.write("\n")
                    self.log.write(str(success[1]))
            return success

    if packman == "YaST":
        def install_zypper_packages(self):
            packages = {"zypper_packages":["gcc", "xorg-x11-libX11-devel", "xorg-x11-devel"]}
            for zypper_packages, package_list in packages.iteritems():
                for package in package_list:
                    command = "zypper --non-interactive install " + package
                    self.log.write(command)
                    success = getstatusoutput(command)
                    self.log.write("\n")
                    self.log.write(str(success[0]))
                    self.log.write("\n")
                    self.log.write(str(success[1]))
            return success

    def compile_checkmagick(self):
        version = platform.machine()
        if version == "x86_64":
            version = "checkmagick64"
        else:
            version = "checkmagick32"
        self.bit_ver = version

        # The new toolchain in Oneiric requires the linked libraries at the end of the compile command
#        command = "gcc -lX11 -lXrandr " +  self.filepath + "/check.c -o " + self.filepath + "/" + version
        # Fortunately the syntax is backwards compatible obviating a major headache
        command = "gcc " +  self.filepath + "/check.c -o " + self.filepath + "/" + version + " -lX11 -lXrandr"
        self.log.write("\n\n")
        self.log.write("Compiling check.c\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def install_checkmagick(self):
        command = "mv "  +  self.filepath + "/" + str(self.bit_ver) + " /usr/bin/"
        self.log.write("Moving checkmagick\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def install_udev_rules(self):
        command = "mv "  +  self.filepath + "/" + "62-magick.rules /etc/udev/rules.d/"
        self.log.write("Moving 62-magick.rules\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def add_group(self):
        command = "groupadd magick"
        self.log.write("Add magick group\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def add_user(self):
        username = self.usr_name
        if packman == "YaST":
            command = "usermod -A magick " + str(username)
        else:
            command = "gpasswd -a " + username + " magick"
        self.log.write("Add user to magick group\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def create_magick_folder(self):
        if os.path.exists("/usr/share/magick-rotation"):
            command = ""
        else:
            command = "mkdir /usr/share/magick-rotation"
        self.log.write("\n")
        self.log.write("Create folder magick-rotation in /usr/share\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def install_readme(self):
        command = "cp " + self.filepath + "/" + "Magick-README.txt /usr/share/magick-rotation/"
        self.log.write("Copying Magick-README\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def install_magick_files(self):
        magick_filename = {"magick_files":["ChangeLog", "config.py", "debug.py", "gui_gtk.py", "hinge.py", "listener.py", "magick-rotation", "xrotate.py"]}
        self.log.write("Moving magick-rotation files\n")
        for magick_files, filename_list in magick_filename.iteritems():
            for filename in filename_list:
                command = "mv " + self.filepath + "/" + filename + " /usr/share/magick-rotation/" + filename
                self.log.write(command)
                success = getstatusoutput(command)
                self.log.write("\n")
                self.log.write(str(success[0]))
                self.log.write("\n")
                self.log.write(str(success[1]))
        return success

    def create_magickicons_folder(self):
        if os.path.exists("/usr/share/magick-rotation/MagickIcons"):
            command = ""
        else:
            command = "mkdir /usr/share/magick-rotation/MagickIcons"
        self.log.write("\n")
        self.log.write("Create folder MagickIcons in /usr/share/magick-rotation\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def install_magick_icons(self):
        icon_filename = {"magick_icons":["MagickAbout.png", "magick-rotation-disabled.png", "magick-rotation-disabled-touchoff.png", "magick-rotation-enabled.png", "magick-rotation-enabled-touchoff.png"]}
        self.log.write("Moving MagickIcon files\n")
        for magick_icons, filename_list in icon_filename.iteritems():
            for filename in filename_list:
                command = "mv " + self.filepath + "/MagickIcons/" + filename + " /usr/share/magick-rotation/MagickIcons/" + filename
                self.log.write(command)
                success = getstatusoutput(command)
                self.log.write("\n")
                self.log.write(str(success[0]))
                self.log.write("\n")
                self.log.write(str(success[1]))
        return success

    def remove_splashicon(self):
        command = "rm " + self.filepath + "/MagickIcons/MagickSplash.png"
        self.log.write("\n")
        self.log.write("Removing MagickSplash.png\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        return success

    def remove_magickicons(self):
        command = "rmdir " + self.filepath + "/MagickIcons"
        self.log.write("\n")
        self.log.write("Removing MagickIcons folder\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_install_files(self):
        install_filename = {"install_files":["apt_installprogress_gtk.py", "apt_pm.py", "check.c", "firstrun", "installer_gtk.py", "whitelist.py"]}
        self.log.write("Removing uneeded install files\n")
        for install_files, filename_list in install_filename.iteritems():
            for filename in filename_list:
                command = "rm " + self.filepath + "/" + filename
                self.log.write(command)
                success = getstatusoutput(command)
                self.log.write("\n")
                self.log.write(str(success[0]))
                self.log.write("\n")
                self.log.write(str(success[1]))
        return success

    def execute_steps(self,  data=None):
        dialog = installer_dialog(self.win,  0, gtk.MESSAGE_INFO,  gtk.BUTTONS_NONE,  None)

        if packman == "APT":
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
        elif packman == "YUM":
            package_string = ""
            package_list = []
            self.packages_to_install = False
            packages = ["gcc", "libX11-devel", "libXrandr-devel"]
            for package in packages:
                package_list.append(package)
        elif packman == "YaST":
            package_string = ""
            package_list = []
            self.packages_to_install = False
            packages = ["gcc", "xorg-x11-libX11-devel", "xorg-x11-devel"]
            for package in packages:
                package_list.append(package)

        package_list.append("\nMagick Rotation install changes.\n\nFile to install in /usr/bin:\n checkmagick")
        package_list.append("\nFolder to install in /usr/share:\n magick-rotation\n\nFile to install in /etc/udev/rules.d:\n 62-magick.rules\n\nAdd group:\n magick\n")
        dialog.list_packages(package_list,  self,  self.win)
                
    def close_dialog(self,  dialog=None):
        self.win.add_text("Canceling installation.")
        dialog.close()
        return True

    def run_installer(self,  data=None):
            if packman == "APT":
                if self.packages_to_install:
                    self.log.write("\nInstalling APT packages\n")
                    self.apt.install(self.win)
                    self.win.progress_bar.hide()
                    self.win.pkg_label.hide()
                else:
                    self.log.write("\n\nAPT packages already installed\n")
            if packman == "YUM":
                self.log.write("\n\nInstalling YUM packages\n")
                success = self.install_yum_packages()
            if packman == "YaST":
                self.log.write("\n\nInstalling YaST packages\n")
                success = self.install_zypper_packages()
            self.win.add_text("Compiling check.c\n")
            success = self.compile_checkmagick()
            self.win.add_text("Installing checkmagick\n")
            success = self.install_checkmagick()
            self.win.add_text("Installing udev rules\n")
            success = self.install_udev_rules()
            self.win.add_text("Creating magick group\n")
            success = self.add_group()
            self.win.add_text("Installing user in magick group\n")
            success = self.add_user()
            self.win.add_text("Creating magick-rotation folder\n")
            success = self.create_magick_folder()
            self.win.add_text("Moving magick-rotation files\n")
            success = self.install_readme()
            success = self.install_magick_files()
            self.win.add_text("Creating MagickIcons folder\n")
            success = self.create_magickicons_folder()
            self.win.add_text("Moving MagickIcons files\n")
            success = self.install_magick_icons()
            self.win.add_text("Removing uneeded files\n")
            success = self.remove_splashicon()
            success = self.remove_magickicons()
            success = self.remove_install_files()
            self.win.add_bold_text("\nINSTALLATION COMPLETE")
            self.win.add_text("\nA system restart is \nrequired to ensure that \n")
            self.win.add_text("magick-rotation will work.\n")

    def run(self):
        gobject.threads_init()
        #self.win.show_all()
        thread.start_new_thread(self.execute_steps, (None, ))
        gtk.main()

if __name__ == "__main__" :
    path = os.path.dirname(sys.argv[0])
    if len(sys.argv) > 1:
        usr_name = sys.argv[1]
    else:
        usr_name = None
#    if not path or path == ".":
  #      path = "./"
    if not path:
        path = "."

    # pass username unchanged to class installer_engine
    if usr_name:
        i = installer_engine(path, usr_name)
    else:
        i = installer_engine(path)
    i.run()
