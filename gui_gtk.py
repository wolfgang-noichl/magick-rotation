#!/usr/bin/env python2

import gtk
import pygtk
import gobject
import sys
import os.path
from commands import getstatusoutput

from config import *
from listener import *

# supports threads in pygtk
gobject.threads_init()

import notify2

# to support App Indicator for Ubuntu Raring (13.04) Unity and later
find_distro = "cat /etc/issue"
distro_raw = getstatusoutput(find_distro)
distro = (distro_raw[1].split(' '))[0]
if distro == "Ubuntu":
    version = (distro_raw[1].split(' '))[1]
    major_version = (version).split('.')[0] + "." + (version).split('.')[1]
    in_unity = getstatusoutput("echo $XDG_CURRENT_DESKTOP")[1]
    if float(major_version) >= 13.04 and in_unity == "Unity":
        try:
            import appindicator # should only be available in Unity (and KDE?)
            have_appindicator = True
        except:
            have_appindicator = False
    else:
        have_appindicator = False
else:
    have_appindicator = False

prog_ver="1.7"

class about_dlg(gtk.Dialog):
    def __init__(self, name, version):
        gtk.Dialog.__init__(self, name)
        version = prog_ver
        filepath = os.path.dirname(sys.argv[0]) + "/MagickIcons/"
        image_filename = filepath + "MagickAbout.png"
        HBox = gtk.HBox()
        self.set_resizable(False)
        self.set_border_width(8)
        self.set_has_separator(False)
        self.connect('delete_event', self.close_about)
        about_title=gtk.Label("""<b><span size="22000">Magick Rotation  </span></b>""")
        about_title.set_use_markup(True)
        about_label=gtk.Label("""\nThis program supports Dell, Fujitsu, HP, and Lenovo\nconvertible tablet PC's.\n\nVersion """ + version + """\n\nAuthors:  Jayhawk & Red_Lion\n\nContributor:  Favux""")
        about_label.set_justify(gtk.JUSTIFY_CENTER)
        image = gtk.Image()
        image.set_from_file(image_filename)
        HBox.pack_start(image)
        HBox.pack_start(about_title)
        self.vbox.add(HBox)
        self.vbox.add(about_label)
        # OK button
        ok_button = gtk.Button(stock=gtk.STOCK_OK)
        ok_button.connect("pressed", self.close_about)
        self.action_area.pack_start(ok_button)

    def close_about(self, widget=None, data=None):
        self.destroy()

## Advanced Setup Options ##
class advanced_table(gtk.Table):
    def __init__(self):
        gtk.Table.__init__(self)

        # place & warning over command entry boxes
        ampersand_label = gtk.Label('''Do not use '&' in commands.''')
        self.attach(ampersand_label, 1, 2, 2, 3)

        # for shell commands before and after rotation to tablet and laptop mode
        before_tablet_label = gtk.Label("Run before switch to tablet: ")
        before_tablet_label.set_alignment(0, .5)
        self.before_tablet = gtk.Entry()
        self.before_tablet.set_width_chars(25)
        self.attach(before_tablet_label, 0, 1, 3, 4)
        self.attach(self.before_tablet, 1, 2, 3, 4)

        after_tablet_label = gtk.Label("Run after switch to tablet: ")
        after_tablet_label.set_alignment(0, .5)
        self.after_tablet = gtk.Entry()
        self.after_tablet.set_width_chars(25)
        self.attach(after_tablet_label, 0, 1, 4, 5)
        self.attach(self.after_tablet, 1, 2, 4, 5)

        before_normal_label = gtk.Label("Run before switch to normal: ")
        before_normal_label.set_alignment(0, .5)
        self.before_normal = gtk.Entry()
        self.before_normal.set_width_chars(25)
        self.attach(before_normal_label, 0, 1, 5, 6)
        self.attach(self.before_normal, 1, 2, 5, 6)

        after_normal_label = gtk.Label("Run after switch to normal: ")
        after_normal_label.set_alignment(0, .5)
        self.after_normal = gtk.Entry()
        self.after_normal.set_width_chars(25)
        self.attach(after_normal_label, 0, 1, 6, 7)
        self.attach(self.after_normal, 1, 2, 6, 7)

        # spacer
        spacer_label1 = gtk.Label("")
        self.attach(spacer_label1, 0, 1, 8, 9)

        isnotify_label=gtk.Label("Allow notification?")

        self.isnotify_button=gtk.CheckButton()

        self.attach(isnotify_label, 0, 1, 9, 10)
        self.attach(self.isnotify_button, 1, 2, 9, 10)

        # notify timeout
        isnotify_timeout_label=gtk.Label("Notification timeout (msec):")
        self.isnotify_timeout_text=gtk.Entry()
        self.attach(isnotify_timeout_label, 0, 1, 10, 11)
        self.attach(self.isnotify_timeout_text, 1, 2, 10, 11)

        # how long before next poll
        waittime_label=gtk.Label("Information update interval (msec):")
        self.waittime_text=gtk.Entry()
        self.attach(waittime_label, 0, 1, 11, 12)
        self.attach(self.waittime_text, 1, 2, 11, 12)

        # does user want Magick Rotation to autostart; moved from Setup
        autostart_label=gtk.Label("Run Magick Rotation on start?")
        self.autostart=gtk.CheckButton()
        self.attach(autostart_label, 0, 1, 12, 13)
        self.attach(self.autostart, 1, 2, 12, 13)

        # spacer
        spacer_label2 = gtk.Label("")
        self.attach(spacer_label2, 0, 1, 13, 14)

        # debug logging mode checkbox
        debug_log_label = gtk.Label("Debugging tool logging on?")
        self.debug_log_button = gtk.CheckButton()
        self.attach(debug_log_label, 0, 1, 14, 15)
        self.attach(self.debug_log_button, 1, 2, 14, 15)

        # log file name and location
        self.log_label = gtk.Label('''<i><span size="9000">(log printed to:  ~/magick-log_date)</span></i>''')
        self.log_label.set_use_markup(True)
        self.attach(self.log_label, 0, 1, 15, 16)

    def set_before_tablet(self, data):
        self.before_tablet.set_text(data)

    def get_before_tablet(self):
        return self.before_tablet.get_text()

    def set_after_tablet(self, data):
        self.after_tablet.set_text(data)

    def get_after_tablet(self):
        return self.after_tablet.get_text()

    def set_before_normal(self, data):
        self.before_normal.set_text(data)

    def get_before_normal(self):
        return self.before_normal.get_text()

    def set_after_normal(self, data):
        self.after_normal.set_text(data)

    def get_after_normal(self):
        return self.after_normal.get_text()

    def set_isnotify_button(self, data):
        self.isnotify_button.set_active(data)

    def get_isnotify_button(self):
        return self.isnotify_button.get_active()

    def set_isnotify_timeout(self, data):
        self.isnotify_timeout_text.set_text(str(data))

    def get_isnotify_timeout(self):
        return self.isnotify_timeout_text.get_text()

    def set_waittime(self, data):
        self.waittime_text.set_text(str(data))

    def get_waittime(self):
        return self.waittime_text.get_text()

    def set_autostart(self, data):
        self.autostart.set_active(data)

    def get_autostart(self):
        return self.autostart.get_active()

    def set_debug_log(self, data):
        self.debug_log_button.set_active(data)

    def get_debug_log(self):
        return self.debug_log_button.get_active()

## Setup Options ##
class main_table(gtk.Table):
    def __init__(self):
        gtk.Table.__init__(self)

        # select tablet mode orientation
        swivel_label = gtk.Label("Rotation state in tablet mode?")
        swivel_label.set_alignment(0, .5)

        self.swivel_option = gtk.combo_box_new_text()
        self.swivel_option.append_text("right")
        self.swivel_option.append_text("inverted")
        self.swivel_option.append_text("left")
        self.swivel_option.append_text("normal")

        self.attach(swivel_label, 0, 1, 0, 1)
        self.attach(self.swivel_option, 1, 2, 0, 1)

        # spacer
        self.spacer_label1 = gtk.Label("")
        self.attach(self.spacer_label1, 0, 1, 1, 2)
 
        # enable/disable left click of tray icon to toggle touch; enabled by default
        self.touch_toggle = gtk.CheckButton("Click tray icon to turn on/off touch?")
        self.attach(self.touch_toggle, 0, 1, 2, 3)

        # spacer
        self.spacer_label2 = gtk.Label("")
        self.attach(self.spacer_label2, 0, 1, 3, 4)

        # Added for HP models Compaq TC4200 & 4400
        self.hingevalue_toggle = gtk.CheckButton("BIOS hinge switch values reversed?")
        self.attach(self.hingevalue_toggle, 0, 1, 4, 5)
        self.hingevalue_label = gtk.Label('''<i><span size="9000">(Check if HP Compaq model TC4200 or TC4400.)</span></i>''')
        self.hingevalue_label.set_use_markup(True)
        self.attach(self.hingevalue_label, 0, 1, 5, 6)

    def set_swivel_option(self, data):
        option_table = ["right", "inverted", "left", "normal"]
        self.swivel_option.set_active(option_table.index(data))

    def get_swivel_option(self):
        option_table = ["right", "inverted", "left", "normal"]
        return option_table[self.swivel_option.get_active()]

    def set_touch_toggle(self, data):
        self.touch_toggle.set_active(data)

    def get_touch_toggle(self):
        return self.touch_toggle.get_active()

    def set_hingevalue_toggle(self, data):
        self.hingevalue_toggle.set_active(data)

    def get_hingevalue_toggle(self):
        return self.hingevalue_toggle.get_active()

class btn_box(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)

class magick_gui(gtk.Window):
    def __init__(self, title=""):
        gtk.Window.__init__(self)
        dir_name = os.path.dirname(sys.argv[0])
        if not dir_name:
            dir_name = "."
        self.path = dir_name + "/"

	self.set_title("Magick Rotation Setup")  # title bar default is 'magick-rotation'
        self.set_position(gtk.WIN_POS_CENTER)  # positions Setup window in center of screen
        self.set_resizable(False)
        self.set_border_width(12)

        self.connect("delete-event", self.close_window)

        box = gtk.VBox(spacing=12)

        self.basic_table = main_table()

        adv_expander = gtk.Expander("<b>Advanced Setup</b>")
        adv_expander.set_use_markup(True)

        self.adv_table = advanced_table()
        adv_expander.add(self.adv_table)

        button_box = gtk.HBox()

        # Save button
        save_button = gtk.Button(stock=gtk.STOCK_SAVE)
        save_button.connect('pressed', self.save_data)
        button_box.pack_start(save_button)

        # About button
        about_button =gtk.Button(stock=gtk.STOCK_ABOUT)
        about_button.connect("pressed", self.show_about)
        button_box.pack_start(about_button)

        # Close button
        close_button = gtk.Button(stock=gtk.STOCK_CLOSE)
        close_button.connect("pressed", self.close_window)
        button_box.pack_start(close_button)

        box.pack_start(self.basic_table)
        box.pack_start(adv_expander)
        box.pack_start(button_box)

        self.load_xml()
 
        self.add(box)

    def get_path(self):
        return self.path

    def load_xml(self):
        cfg = config()
        data = cfg.load_xml()
        self.basic_table.set_swivel_option(data[0])
        self.basic_table.set_touch_toggle(data[1])
        self.basic_table.set_hingevalue_toggle(data[2])
        self.adv_table.set_before_tablet(data[3])
        self.adv_table.set_after_tablet(data[4])
        self.adv_table.set_before_normal(data[5])
        self.adv_table.set_after_normal(data[6])
        self.adv_table.set_isnotify_button(data[7])
        self.adv_table.set_isnotify_timeout(data[8])
        self.adv_table.set_waittime(data[9])
        self.adv_table.set_autostart(data[10])
        self.adv_table.set_debug_log(data[11])
        self.version = data[12]

    def show_about(self, widget=None):
        about = about_dlg("About", self.version)
        about.show_all()

    def save_data(self, widget=None):
        cfg = config()
        cfg.write_data([self.basic_table.get_swivel_option(), \
                        self.basic_table.get_touch_toggle(), \
                        self.basic_table.get_hingevalue_toggle(), \
                        self.adv_table.get_before_tablet(), \
                        self.adv_table.get_after_tablet(), \
                        self.adv_table.get_before_normal(), \
                        self.adv_table.get_after_normal(), \
                        self.adv_table.get_isnotify_button(), \
                        self.adv_table.get_isnotify_timeout(), \
                        self.adv_table.get_waittime(), \
                        self.adv_table.get_autostart(), \
                        self.adv_table.get_debug_log(), \
                        self.version])

    def close_window(self, widget=None, data=None):
        self.hide()
        return True

## Adds Magick Rotation App Indicator to Ubuntu Unity's System Tray. ##
# System Tray icons not conforming to the App Indicator spec. deprecated starting with Raring 13.04.
if have_appindicator:
    class ind_gui(gtk.Menu):
        def __init__(self, engine):
            gtk.Menu.__init__(self)
            # App Indicator spec. does not support tool tips
            self.menu = tray_menu_gui(engine)
            self.connect('popup-menu', self.menu.popup_menu, self.menu)
            self.menu.show_all() # otherwise menus not visible
            self.engine = engine

            # create App Indicator object, make icon visible in tray, attach menus
            self.ind = appindicator.Indicator ("Magick_Rotation",
                                "/usr/share/magick-rotation/MagickIcons/magick-rotation-enabled.png",
                                appindicator.CATEGORY_APPLICATION_STATUS)
            self.ind.set_status(appindicator.STATUS_ACTIVE) # equivalent to gtk.StatusIcon's set_visible(True)
            self.ind.set_menu(self.menu)

# TODO: Need to verify the following for certain. Apparently complete path string required to access
# Magick icon using indicator object's icon parameter.  Originally could only use theme icons!  So
# can only use Magick installed, not from folder, with Unity Raring and later.  Additionally:
#     self.path = os.path.abspath(sys.argv[0]) + "/MagickIcons/"
#     self.ind.set_icon(self.path + "magick-rotation-enabled.png")
# doesn't work to set the icons either.  So the app indicator .set_icon also can only handle a string.
# This is weird unexpected behavior.

# App Indicator API doesn't support gtk.StatusIcon's set_from_file attribute.
#                self.set_from_file(self.path + "magick-rotation-disabled.png")
# Able to use App Indicator API supported set_icon to change icons.  But using set_attention_icon, also supported,
# doesn't seem to work.
#     API e.g.:  self.ind.set_icon("distributor-logo") # not deprecated for set_icon_full in Raring at least
#     API e.g.:  self.ind.set_attention_icon("new-messages-red")

        # added update_poll_status to toggle_touch in magick-rotation to detect when touch toggled
        # in pop-up menu, consolidates update_touch_status here
        def update_poll_status(self, polling):
            touch_on = self.engine.get_touch_status()
            if polling == True and touch_on == True:
                self.ind.set_icon("/usr/share/magick-rotation/MagickIcons/magick-rotation-enabled.png")
            elif polling == False and touch_on == True:
                self.ind.set_icon("/usr/share/magick-rotation/MagickIcons/magick-rotation-disabled.png")
            elif polling == True and touch_on == False:
                self.ind.set_icon("/usr/share/magick-rotation/MagickIcons/magick-rotation-enabled-touchoff.png")
            else:
                self.ind.set_icon("/usr/share/magick-rotation/MagickIcons/magick-rotation-disabled-touchoff.png")

# Right and left click are identical on an Application Indicator by design.  Can't left click Magick
# icon to toggle touch on and off and use right click to access Setup.  Changing touch toggle to a
# MenuItem in class tray_menu_gui only reasonable alternative.

        print "Magick is using an App Indicator."

## Adds Magick Rotation icon to System Tray. ##
else:
    class tray_gui(gtk.StatusIcon):
        def __init__(self, engine):
            gtk.StatusIcon.__init__(self)
            self.set_tooltip("Loading...")
            self.path = os.path.dirname(sys.argv[0]) + "/MagickIcons/"
            self.set_from_file(self.path + "magick-rotation-enabled.png")
            self.set_visible(True)
            self.menu = tray_menu_gui(engine)
            self.connect('popup-menu', self.menu.popup_menu, self.menu)
            self.connect('activate', self.update_touch_status)
            self.engine = engine

        def update_poll_status(self, polling):
            touch_on = self.engine.get_touch_status()
            if not polling:
                if touch_on:
                    self.set_from_file(self.path + "magick-rotation-disabled.png")
                else:
                    self.set_from_file(self.path + "magick-rotation-disabled-touchoff.png")
            else:
                if touch_on:
                    self.set_from_file(self.path + "magick-rotation-enabled.png")
                else:
                    self.set_from_file(self.path + "magick-rotation-enabled-touchoff.png")

        def update_touch_status(self, data=None):
            if self.engine.win.basic_table.get_touch_toggle():
                self.engine.toggle_touch()
                touch_on = self.engine.get_touch_status()
                if touch_on:
                    if self.menu.option_enable.get_active():
                        self.set_from_file(self.path + "magick-rotation-enabled.png")
                    else:
                        self.set_from_file(self.path + "magick-rotation-disabled.png")
                else:
                    if self.menu.option_enable.get_active():
                        self.set_from_file(self.path + "magick-rotation-enabled-touchoff.png")
                    else:
                        self.set_from_file(self.path + "magick-rotation-disabled-touchoff.png")

        print "Magick is using a gtk.StatusIcon."

class tray_menu_gui(gtk.Menu):
    def __init__(self, engine):
        gtk.Menu.__init__(self)

        # Toggles touch when using App Indicator
        if have_appindicator:
            self.option_touch = gtk.CheckMenuItem("Touch")
            self.option_touch.set_active(True)
            self.option_touch.connect("activate", engine.toggle_touch, self.option_touch)

        # Rotates screen - submitted by gco, see magick-rotation module
        option_rotate = gtk.MenuItem("Rotate")
        option_rotate.connect("activate", engine.force_rotate)

        # Calls the configuration window
        option_setup = gtk.MenuItem("Setup")
        option_setup.connect("activate", engine.display_config_window)

        # Start the polling
        self.option_enable = gtk.CheckMenuItem("Enable")
        self.option_enable.set_active(True)
        self.option_enable.connect("activate", engine.toggle_rotate, self.option_enable)

        # Stops the application
        option_exit = gtk.MenuItem("Quit")
        option_exit.connect("activate", engine.quit)

        # Add tray menu items in order
        if have_appindicator: # adds 'Touch' when using App Indicator
            self.append(self.option_touch)
            self.append(gtk.SeparatorMenuItem())
        if "gnome-shell" in str(getstatusoutput("ps ax | grep -v grep | grep gnome-shell")):
            # so Rotate isn't obscured by some versions of gnome-shell's top panel
#            self.append(gtk.MenuItem(""))  # maybe a bit much
            self.append(gtk.SeparatorMenuItem())
        self.append(option_rotate)
        self.append(gtk.SeparatorMenuItem())  # adds dividing line
        self.append(option_setup)
        self.append(gtk.SeparatorMenuItem())
        self.append(self.option_enable)
        self.append(gtk.SeparatorMenuItem())
        self.append(option_exit)

    # With App Indicator right or left click opens the popup menu
    def popup_menu(self, menu, button, time, data = None):
        # button 3 is right click
        if button == 3:
            if data:
                data.show_all()
                data.popup(None, None, None, 3, time)

if __name__ == "__main__":
    win = magick_gui()
    win.show()
    gtk.main()
