#!/usr/bin/env python

import gtk
import pygtk
import gobject
import sys
import os.path

from config import *
from listener import *

#prog_ver="1.0"

# supports threads in pygtk
gobject.threads_init()

try:
    import pynotify
    pynotify_support = True
except:
    print "Please install pynotify.  It is not required but it makes the experience better."
    pynotify_support = False

class about_dlg(gtk.Dialog):
    def __init__(self, name, version):
        gtk.Dialog.__init__(self, name)
        self.set_resizable(False)
        self.set_border_width(8)
        self.set_has_separator(False)
        self.connect('delete_event', self.close_about)
        about_title=gtk.Label("""
        <b><span size="22000">Magick Rotation</span></b>""")
        about_title.set_use_markup(True)
        about_label=gtk.Label("""\nThis program supports HP's Pavilion TX2000 & TX2500 series, \nTouchSmart TX2z series, Elitebook 2700p series, & \nTouchSmart TM2 series tablet pc's\n\nVersion """ + version + """\n\nAuthors:  Red_Lion (red_lion@inbox.ru)\njayhawk\n\nContributor:  Favux\n\nAlso see http://ubuntuforums.org/showthread.php?t=996830""")
        about_label.set_justify(gtk.JUSTIFY_CENTER)

        self.vbox.add(about_title)
        self.vbox.add(about_label)
        # OK button
        ok_button = gtk.Button(stock=gtk.STOCK_OK)
        ok_button.connect("pressed", self.close_about)
        self.action_area.pack_start(ok_button)

    def close_about(self, widget=None, data=None):
        self.destroy()

class advanced_table(gtk.Table):
    def __init__(self):
        gtk.Table.__init__(self)

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

        ampersand_label = gtk.Label("""(Do no use '&' in above commands.) """)
        self.attach(ampersand_label, 0, 1, 7, 8)

        # spacer
        spacer_label1 = gtk.Label("")
        self.attach(spacer_label1, 0, 1, 8, 9)

        # notify about switch
        if pynotify_support:
            isnotify_label=gtk.Label("Allow notification?")
        else:
            isnotify_label=gtk.Label("Allow notification? (pynotify not found)")

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

        # spacer
        spacer_label2 = gtk.Label("")
        self.attach(spacer_label2, 0, 1, 12, 13)

        # debug logging mode checkbox
        debug_log_label = gtk.Label("Debugging tool logging on?")
        self.debug_log_button = gtk.CheckButton()
        self.attach(debug_log_label, 0, 1, 13, 14)
        self.attach(self.debug_log_button, 1, 2, 13, 14)

        # log file name and location
        log_label = gtk.Label("(log printed to:  ~/magick-log_date)")
        self.attach(log_label, 0, 1, 14, 15)

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

    def set_debug_log(self, data):
        self.debug_log_button.set_active(data)

    def get_debug_log(self):
        return self.debug_log_button.get_active()

class main_table(gtk.Table):
    def __init__(self):
        gtk.Table.__init__(self)

        self.autostart = gtk.CheckButton("Run on start?")
        self.attach(self.autostart, 0, 1, 0, 1)

        swivel_label = gtk.Label("Rotation state in tablet mode?")
        swivel_label.set_alignment(0, .5)

        self.swivel_option = gtk.combo_box_new_text()
        self.swivel_option.append_text("right")
        self.swivel_option.append_text("inverted")
        self.swivel_option.append_text("left")
        self.swivel_option.append_text("normal")

        self.attach(swivel_label, 0, 1, 1, 2)
        self.attach(self.swivel_option, 1, 2, 1, 2)

        self.touch_toggle = gtk.CheckButton("Click tray icon to turn on/off touch?")
        self.attach(self.touch_toggle, 0, 1, 2, 3)

    def set_autostart(self, data):
        self.autostart.set_active(data)

    def get_autostart(self):
        return self.autostart.get_active()

    def set_touch_toggle(self, data):
        self.touch_toggle.set_active(data)

    def get_touch_toggle(self):
        return self.touch_toggle.get_active()

    def set_swivel_option(self, data):
        option_table = ["right", "inverted", "left", "normal"]
        self.swivel_option.set_active(option_table.index(data))

    def get_swivel_option(self):
        option_table = ["right", "inverted", "left", "normal"]
        return option_table[self.swivel_option.get_active()]

class btn_box(gtk.HBox):
    def __init__(self):
        gtk.HBox.__init__(self)

class magick_gui(gtk.Window):
    def __init__(self, title=""):
        gtk.Window.__init__(self)
        self.set_resizable(False)
        self.set_border_width(5)

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

        self.load_data()
 
        self.add(box)

    def load_data(self):
        cfg = config()
        data = cfg.load_data()

        self.basic_table.set_autostart(data[0])
        self.basic_table.set_swivel_option(data[1])
        self.adv_table.set_before_tablet(data[2])
        self.adv_table.set_after_tablet(data[3])
        self.adv_table.set_before_normal(data[4])
        self.adv_table.set_after_normal(data[5])
        self.adv_table.set_isnotify_button(data[6])
        self.adv_table.set_isnotify_timeout(data[7])
        self.adv_table.set_waittime(data[8])
        self.adv_table.set_debug_log(data[9])
        self.basic_table.set_touch_toggle(data[10])
        self.version = data[11]

    def show_about(self, widget=None):
        about = about_dlg("About", self.version)
        about.show_all()

    def save_data(self, widget=None):
        cfg = config()
        cfg.write_data([self.basic_table.get_autostart(),\
                        self.basic_table.get_swivel_option(), \
                        self.adv_table.get_before_tablet(), \
                        self.adv_table.get_after_tablet(), \
                        self.adv_table.get_before_normal(), \
                        self.adv_table.get_after_normal(), \
                        self.adv_table.get_isnotify_button(), \
                        self.adv_table.get_isnotify_timeout(), \
                        self.adv_table.get_waittime(), \
                        self.adv_table.get_debug_log(), \
                        self.basic_table.get_touch_toggle(), \
                        self.version])

    def close_window(self, widget=None, data=None):
        self.hide()
        return True

class tray_gui(gtk.StatusIcon):
    def __init__(self, engine):
        gtk.StatusIcon.__init__(self)
        self.set_tooltip("Loading...")
        self.path = os.path.dirname(sys.argv[0]) + "/"
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

      
class tray_menu_gui(gtk.Menu):
    def __init__(self, engine):
        gtk.Menu.__init__(self)

        # Start the polling
        self.option_enable = gtk.CheckMenuItem("Enable")
        self.option_enable.set_active(True)
        self.option_enable.connect("activate", engine.toggle_rotate, self.option_enable)

        # Calls the configuration window
        option_setup = gtk.MenuItem("Setup")
        option_setup.connect("activate", engine.display_config_window)

        # Stops the application
        option_exit = gtk.MenuItem("Quit")
        option_exit.connect("activate", engine.quit)

        self.append(self.option_enable)
        self.append(option_setup)
        self.append(option_exit)

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
