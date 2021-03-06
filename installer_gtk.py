#!/usr/bin/env python2

import gtk
import pygtk
import gobject
import sys
import _thread
import os.path
from subprocess import getstatusoutput, getoutput
import platform
import pango
import datetime

sys.dont_write_bytecode = True

# Determine Distro #
find_distro = "cat /etc/issue"
# another option is 'cat /etc/*release'; outputs for 'cat /etc/issue':
#   Ubuntu 12.04.1 LTS \n \l
#   Linux Mint 12 Lisa \n \l
#   Linux Mint Debian Edition \n \l
#   Debian GNU/Linux 4.0 \n \l
#   Fedora release 16 (Verne)
#   Kernel \r on an \m (\l)
#   Red Hat Enterprise Linux AS release 3 (Taroon)
#   Kernel \r on an \m
#   CentOS release 5.4 (Final)
#   Kernel \r on an \m
#   Welcome to openSUSE Linux 12.1 "Asparagus" - Kernel \r (\l).
distro_raw = getstatusoutput(find_distro)
distro_split = distro_raw[1].split(' ')  # index 1 has string containing Distro name

# Determine Distro Package Manager #
# for Fedora
if os.path.exists("/usr/bin/yum"):
    packman = "YUM"
# for openSUSE
elif os.path.exists("/usr/bin/zypper"):
    packman = "YaST"
# for Debian and LMDE
elif distro_split[0] == "Debian" or distro_split[2] == "Debian":
    packman = "APT_DEB"
# for Ubuntu, Mint, and to tell non-supported Distros to manually install
else:
    try:
        from apt_pm import *
        apt_installed = True
    except ImportError:
        apt_installed = False
    packman = "APT"

# Determine if Gnome Shell installed and version #
# install Magick Rotation's extension if Gnome Shell is installed and version 3.2
# (extension spec.s changed after 3.0) or better
if os.path.exists("/usr/bin/gnome-shell"):
    gshell_str = getoutput("gnome-shell --version")  # e.g. string:  GNOME Shell 3.2.1
    gshell_ver = gshell_str.split(' ')[2]            # yields 3.2.1
    gshell_subver = int((gshell_ver.split('.'))[1])  # yields 2
    if gshell_subver >= 2:
        gshell = True  # Gnome shell installed and 3.2 or better
    else:
        gshell = False  # use for Gnome Shell 3.0
else:
    gshell = False  # Gnome Shell not installed

class installer_dialog(gtk.MessageDialog):
    def __init__(self,  parent=None, flags=0, type=gtk.MESSAGE_INFO, buttons=gtk.BUTTONS_NONE, message_format=None):
        gtk.MessageDialog.__init__(self, parent,  flags,  type,  buttons,  message_format)

    def list_packages(self, packages, engine,  win):
        self.add_buttons(gtk.STOCK_OK,  gtk.RESPONSE_ACCEPT,  gtk.STOCK_CANCEL,  gtk.RESPONSE_REJECT)
        self.set_border_width(15)
        message = ""

        if len(packages) > 1:
            message = packman + " packages to be installed:\n"
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
            _thread.start_new_thread(engine.run_installer,  (None, ))
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
        curtime = datetime.datetime.today()
        datetimestamp = curtime.strftime("%m-%d-%Y_%H:%M")
        logfile = self.filepath + "/install-log_" + datetimestamp
        self.log = open(logfile,  "w")

    if packman == "YUM":
        def install_yum_packages(self):
            packages = {"yum_packages":["gcc", "libX11-devel", "libXrandr-devel"]}
            for yum_packages, package_list in packages.items():
                for package in package_list:
                    command = "yum -y install " + package
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
            for zypper_packages, package_list in packages.items():
                for package in package_list:
                    command = "zypper --non-interactive install " + package
                    self.log.write(command)
                    success = getstatusoutput(command)
                    self.log.write("\n")
                    self.log.write(str(success[0]))
                    self.log.write("\n")
                    self.log.write(str(success[1]))
            return success

    if packman == "APT_DEB":
        def install_aptd_packages(self):
            packages = {"aptd_packages":["gcc", "libx11-dev", "libxrandr-dev"]}
            for aptd_packages, package_list in packages.items():
                for package in package_list:
                    command = "apt-get -y install " + package
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
            command = "gpasswd -a " + str(username) + " magick"
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
        for magick_files, filename_list in magick_filename.items():
            for filename in filename_list:
                self.log.write("\n")
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
        for magick_icons, filename_list in icon_filename.items():
            for filename in filename_list:
                self.log.write("\n")
                command = "mv " + self.filepath + "/MagickIcons/" + filename + " /usr/share/magick-rotation/MagickIcons/" + filename
                self.log.write(command)
                success = getstatusoutput(command)
                self.log.write("\n")
                self.log.write(str(success[0]))
                self.log.write("\n")
                self.log.write(str(success[1]))
        return success

    # The Gnome Shell Message Tray auto-hides and obscures touch-on/off icons with its message
    # number.  This installs an extension that moves the Magick icon to System Status Area.
    if gshell == True:  # Gnome Shell installed and 3.2 or better
        def move_magickextension_folder(self):
            username = self.usr_name
            if os.path.exists("/home/" + str(username) + "/.local/share/gnome-shell/extensions/magick-rotation-extension"):
                command = 'print "magick-rotation-extension folder already exists\n"'
            elif gshell_subver == 6:  # use 3.6 extension
                # rename 3.6_extension.js to extension.js
                getoutput("mv " + self.filepath + "/magick-rotation-extension/3.6_extension.js " + self.filepath + "/magick-rotation-extension/extension.js")
                # rename 3.6_metadata.json to metadata.json
                getoutput("mv " + self.filepath + "/magick-rotation-extension/3.6_metadata.json " + self.filepath + "/magick-rotation-extension/metadata.json")
                # remove 3.8_extension.js & 3.8_metadata.json
                getoutput("rm " + self.filepath + "/magick-rotation-extension/3.8_extension.js")
                getoutput("rm " + self.filepath + "/magick-rotation-extension/3.8_metadata.json")
                # install 3.6 magick-rotation-extension
                command = "mv " + self.filepath + "/magick-rotation-extension /home/" + str(username) + "/.local/share/gnome-shell/extensions/magick-rotation-extension"
                self.log.write("Move 3.6 magick-rotation-extension folder to ~/.local/share/gnome-shell/extensions\n")
            elif gshell_subver >= 8:  # use 3.8 and later extension
                # rename 3.8_extension.js to extension.js
                getoutput("mv " + self.filepath + "/magick-rotation-extension/3.8_extension.js " + self.filepath + "/magick-rotation-extension/extension.js")
                # rename 3.8_metadata.json to metadata.json
                getoutput("mv " + self.filepath + "/magick-rotation-extension/3.8_metadata.json " + self.filepath + "/magick-rotation-extension/metadata.json")
                # remove 3.6_extension.js & 3.6_metadata.json
                getoutput("rm " + self.filepath + "/magick-rotation-extension/3.6_extension.js")
                getoutput("rm " + self.filepath + "/magick-rotation-extension/3.6_metadata.json")
                # install 3.8 magick-rotation-extension
                command = "mv " + self.filepath + "/magick-rotation-extension /home/" + str(username) + "/.local/share/gnome-shell/extensions/magick-rotation-extension"
                self.log.write("Move 3.8 magick-rotation-extension folder to ~/.local/share/gnome-shell/extensions\n")
            else:  # use 3.2 and 3.4 extension
                # remove 3.6_extension.js & 3.6_metadata.json
                getoutput("rm " + self.filepath + "/magick-rotation-extension/3.6_extension.js")
                getoutput("rm " + self.filepath + "/magick-rotation-extension/3.6_metadata.json")
                # remove 3.8_extension.js & 3.8_metadata.json
                getoutput("rm " + self.filepath + "/magick-rotation-extension/3.8_extension.js")
                getoutput("rm " + self.filepath + "/magick-rotation-extension/3.8_metadata.json")
                # install magick-rotation-extension
                command = "mv " + self.filepath + "/magick-rotation-extension /home/" + str(username) + "/.local/share/gnome-shell/extensions/magick-rotation-extension"
                self.log.write("Move 3.2 magick-rotation-extension folder to ~/.local/share/gnome-shell/extensions\n")
            self.log.write(command)
            success = getstatusoutput(command)
            self.log.write("\n")
            self.log.write(str(success[0]))
            self.log.write("\n")
            self.log.write(str(success[1]))
            self.log.write("\n")
            return success

    # Clean up
    def remove_splashicon(self):
        command = "rm " + self.filepath + "/MagickIcons/MagickSplash.png"
        self.log.write("Removing MagickSplash.png\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        return success

    def remove_magickicons_folder(self):
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

    def remove_magickextension_folder(self):
        if os.path.exists(self.filepath + "/magick-rotation-extension"):
            command = "rm -rf " + self.filepath + "/magick-rotation-extension"
            self.log.write("\n")
            self.log.write("Removing magick-rotation-extension folder\n")
        else:
            command = ""
            self.log.write("Magick extension folder already removed\n")
        self.log.write(command)
        success = getstatusoutput(command)
        self.log.write("\n")
        self.log.write(str(success[0]))
        self.log.write("\n")
        self.log.write(str(success[1]))
        self.log.write("\n")
        return success

    def remove_install_files(self):
        install_filename = {"install_files":["apt_installprogress_gtk.py", "apt_pm.py", "check.c", "installer_gtk.py", "MAGICK-INSTALL", "gset_addkeyval.py"]}
        self.log.write("Removing uneeded install files\n")
        for install_files, filename_list in install_filename.items():
            for filename in filename_list:
                self.log.write("\n")
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

            # determine if in Linux Mint - python apt module apt.cache is case sensitive 
            # exclude LMDE, it and Debian use libx11-dev along with Ubuntu
            if distro_split[1] == "Mint" and not distro_split[2] == "Debian":
                packages = self.apt.find_uninstalled(["libX11-dev", "libxrandr-dev"])
            else:
                packages = self.apt.find_uninstalled(["libx11-dev", "libxrandr-dev"])
            # TODO:  make apt_pm.py and apt_installprogress_gtk.py compatible with LMDE
            # and Debian APT flavor.

            if packages[1]:
                dialog.missing_packages(packages[1],  self,  self.win)
                self.remove_install_check()
                return -1
            else:
                # Ask the user if they want to install the package.
                # If they don't, then exit installer and do not 
                # launch magick-rotation.

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
            # TODO:  add YUM to apt_pm.py and apt_installprogress_gtk.py?  YUM is written
            # in Python like APT.  YUM API seems to indicate this may be possible.
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
        elif packman == "APT_DEB":
            package_string = ""
            package_list = []
            self.packages_to_install = False
            packages = ["gcc", "libx11-dev", "libxrandr-dev"]
            for package in packages:
                package_list.append(package)

        # Ask the user if they want to install Magick Rotation files and folders.
        package_list.append("\nMagick Rotation install changes.\n\nFile to install in /usr/bin:\n checkmagick")
        package_list.append("\nFolder to install in /usr/share:\n magick-rotation\n\nFile to install in /etc/udev/rules.d:\n 62-magick.rules\n\nAdd group:\n magick\n")
        # Ask the user if they want to install the Magick extension for Gnome Shell 3.2 or better.
        if gshell == True:
            package_list.append("Shell extension to install:\n magick-rotation-extension\n")
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
            if packman == "APT_DEB":
                self.log.write("\n\nInstalling APT_DEB packages\n")
                success = self.install_aptd_packages()
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
            if gshell == True:
                self.win.add_text("Enabled Magick extension\n")
                self.win.add_text("Moving Magick extension folder\n")
                success = self.move_magickextension_folder()
            self.win.add_text("Removing uneeded files and folders\n")
            success = self.remove_splashicon()
            success = self.remove_magickicons_folder()
            success = self.remove_magickextension_folder()
            success = self.remove_install_files()

            self.win.add_bold_text("\nINSTALLATION COMPLETE")
            self.win.add_text("\nA system restart is required to\n")
            self.win.add_text("ensure Magick Rotation will work.\n")

    def run(self):
        gobject.threads_init()
        #self.win.show_all()
        _thread.start_new_thread(self.execute_steps, (None, ))
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
