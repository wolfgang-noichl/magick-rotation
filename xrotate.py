#!/usr/bin/env python

from sys import argv, exit
from commands import getstatusoutput, getoutput

debug = 0

## get current USB device information ##
class devices:
    def __init__(self):
        # list usb devices with 'xinput list'
#        device_list = getoutput("xinput --list").split("\n")
        # Sort 1:  keep Virtual core pointer (pen, touch) devices and discard Virtual core
        # keyboard devices
        pointer_devices = getoutput("xinput --list").split("Virtual core keyboard")[0]
        device_list = pointer_devices.split("\n")
        # get ID number associated with each pointer device from the device strings
        id_list = []
        for device in device_list:
            if "id=" in device:
                id_list.append(device.split("id=")[1].split()[0])

        # populate devices with tuple items:  device name, ID number, device properties
        self.devices = []
        # run 'xinput list-props' with id_list ID numbers
        for id_val in id_list:
            command = "xinput list-props " + id_val
            prop_list = getoutput(command).split("\n")
            device_name = prop_list[0]
            id_num = id_val
            device_props = []
            for index in range(1, len(prop_list)):
                # add property list to devices device_props tupple value
#                device_props.append(prop_list[index])
                # Sort 2 (optional, improves readability): only interested in certain properties
                # any pointer device - Device Enabled, Coordinate Transformation Matrix
                # wacom devices - Wacom Rotation, Wacom Tool Type
                # evdev devices - Evdev Axis Inversion, Evdev Axes Swap, Evdev Axis Calibration
                if "Device Enabled" in prop_list[index]:
                    device_props.append(prop_list[index])
                elif "Coordinate Transformation Matrix" in prop_list[index]:
                    device_props.append(prop_list[index])
                elif "Wacom Rotation" in prop_list[index]:
                    device_props.append(prop_list[index])
                elif "Wacom Tool Type" in prop_list[index]:
                    device_props.append(prop_list[index])
                elif "Evdev Axis Inversion" in prop_list[index]:
                    device_props.append(prop_list[index])
                elif "Evdev Axes Swap" in prop_list[index]:
                    device_props.append(prop_list[index])
                elif "Evdev Axis Calibration" in prop_list[index]:
                    device_props.append(prop_list[index])
            # add to devices the tupple for each device
            self.devices.append([device_name, id_num, device_props])

    def num_devices(self):
        return len(self.devices)

    def get_device(self, id_val):
        idx = self.get_id_num(id_val)
        return self.devices[idx]

    def get_device_name(self, id_val):
        idx = self.get_id_num(id_val)
        return self.devices[idx][0].split("\':")[0].split("Device \'")[1]

    def get_id(self, idx):
        return int(self.devices[idx][1])

    def get_id_num(self, idx):
        for index in range(self.num_devices()):
            if int(self.devices[index][1]) == idx:
                return index
        return -1

    def find_id(self, name):
        for index in range(self.num_devices()):
            cur_name = self.devices[index][0].split("\':")[0].split("Device \'")[1]
            if cur_name == name:
                return self.devices[index][1]
        return -1

    def get_id_list(self):
        idx_list = []
        for device in self.devices:
            idx_list.append(int(device[1]))

        return idx_list

    # check if the device is using the evdev driver
    def is_evdev(self, id_val):
        idx = self.get_id_num(id_val)
        for prop in self.devices[idx][2]:
            prop_info = prop.split("\t")
            for prop_data in prop_info:
                if prop_data.startswith("Evdev"):
                    return 1
        return 0

    # check if touch device is on the evdev driver
    def is_evdev_touch(self, id_val):
        idx = self.get_id_num(id_val)
        if self.is_evdev(id_val):
            if "Touch" in self.devices[idx][0]:
                return 1
        return 0

    # check if the device is using the wacom driver
    def is_wacom(self, id_val):
        idx = self.get_id_num(id_val)
        for prop in self.devices[idx][2]:
            prop_info = prop.split("\t")
            for prop_data in prop_info:
                if prop_data.startswith("Wacom"):
                    return 1
        return 0

# for class wacom, class evdev
class driver:
    def __init__(self, device):
        self.device = device
#        self.get_property(None)

    def get_property(self, prop):
        for property in self.device[2]:
            prop_data = property.split("\t")
            prop_name = prop_data[1].split(":")[0].split(" (")[0]
            prop_value = prop_data[2]
            if prop_name == prop:
                return prop_value
        if debug:
            print prop, "property not found"
        return None

class wacom:
    def __init__(self, device, id_val):
        self.dev = driver(device)
        self.id_val = id_val

        self.wacom_table = ["none", "cw", "ccw", "half"]
        self.wac_to_randr = {"none":"normal", "ccw":"left", "half":"inverted", "cw":"right"}
        self.randr_to_wac = {"normal":"none", "left":"ccw", "inverted":"half", "right":"cw"}
        self.rotate_order = ["normal", "left", "inverted", "right"]

    def is_touch(self):
        dev_type = self.dev.get_property("Wacom Tool Type")

        if "TOUCH" in dev_type:
                return 1
        return 0

    def toggle_touch(self, toggle):
        if toggle:
#            switch = str(1)
            switch = "on"
        else:
#            switch = str(0)
            switch = "off"

        # the command string to toggle touch
#        val_string = 'xinput set-prop ' + str(self.id_val) + ' "Device Enabled" ' + switch
        # use xsetwacom for touch toggle to accommodate serial tablet PC's
        val_string = 'xsetwacom set "' + str(self.id_val) + '" Touch ' + switch
        if debug:
            print val_string

        # the system call to toggle touch
        result =  getstatusoutput(val_string)[1]
        if debug:
            if result:
                print result
            print

    def get_next_rotation(self):

        # Find current direction
        wacom_rotate_val = int(self.dev.get_property("Wacom Rotation"))

        # Change the wacom rotation name to the randr naming convention
        randr_name = self.wac_to_randr[self.wacom_table[wacom_rotate_val]]
        # Find out the actual rotation value
        randr_val = self.rotate_order.index(randr_name)
        # Find the next rotation value
        new_rotated_val = (randr_val + 1) % 4
        # Get the randr name of the value
        new_randr_name = self.rotate_order[new_rotated_val]

        # Translate it back to the wacom convention
        return self.randr_to_wac[new_randr_name]

    def rotate(self, direction):
        if direction:
            if debug:
                print "skipping next rotation check"
            new_dir = self.randr_to_wac[direction]
        else:
            new_dir = self.get_next_rotation()

        # The command string to rotate
        val_string = "xsetwacom set " + str(self.id_val) + " rotate " + new_dir
        if debug:
            print val_string

        # The actual system call to rotate
        result =  getstatusoutput(val_string)[1]
        if debug:
            if result:
                print result
            print

class linuxwacom:
    def __init__(self):
        pass

    def toggle_touch(self, name, toggle):
        # some versions of xsetwacom are case sensitive, use "o" instead of "O"
        if toggle:
            switch = "on"
        else:
            switch = "off"

        val_string = 'xsetwacom set "' + str(name) + '" Touch ' + switch
        if debug:
            print val_string

        result =  getstatusoutput(val_string)[1]
        if debug:
            if result:
                print result
            print

    def rotate(self, name, direction):
        self.randr_to_wac = {"normal":"none", "left":"ccw", "inverted":"half", "right":"cw"}
        new_dir = self.randr_to_wac[direction]
        # The command string to rotate
        val_string = 'xsetwacom set "' + str(name) + '" rotate ' + new_dir
        if debug:
            print val_string

        # The actual system call to rotate
        result =  getstatusoutput(val_string)[1]
        if debug:
            if result:
                print result
            print

class evdev:
    def __init__(self, device, id_val):
        self.dev = driver(device)
        self.id_val = id_val

        # Needed for Axis Inversion and Axes Swap if Axis Calibration prop unavailable.
        # Would need to change if not a HP TX2z, Dell XT, or XT2 screen.  HP and Dell screens
        # are all 1280x800, but there might be a difference between their N-Trig digitizer
        # calibration values.
        self.top_x = 0
        self.top_y = 0
        self.bottom_x = 9600
        self.bottom_y = 7200

    def toggle_touch(self, toggle):
        val_string = "xinput set-prop " + str(self.id_val) + " 'Device Enabled' " + str(toggle)
        if debug:
            print val_string

        result =  getstatusoutput(val_string)[1]
        if debug:
            if result:
                print result
            print

    def get_next_rotation(self, inv_x, inv_y):
        inv_dict = {(0,0):"normal", (1,0):"left", (1,1):"inverted", (0,1):"right"}
        rotate_order = ["normal", "left", "inverted", "right"]

        randr_name = inv_dict[(inv_x, inv_y)]
        
        # Find out the actual rotation value
        randr_val = rotate_order.index(randr_name)
        # Find the next rotation value
        new_rotated_val = (randr_val + 1) % 4

        # Return the randr name of the value
        return rotate_order[new_rotated_val]

    def rotate_ctm(self, direction):
        # get CTM property from class devices device_props tuple item
        cur_ctm = self.dev.get_property("Coordinate Transformation Matrix").split(", ") 
        # Do not run the method if the property does not exist
        if not cur_ctm:
        # to disable CTM comment out above line and uncomment line below
#        if cur_ctm:
            return None

        # Coordinate Transformation Matrix equation #
        # used to translate the currently assigned pixel coordinate vector X,Y
        # of your tablet PC's input tool to a new pixel coordinate vector X',Y'

        # [ x' ]   [ cosA*ctm[0] -sinA*ctm[1]  ctm[2] ]   [ x ]
        # [ y' ] = [ sinA*ctm[3]  cosA*ctm[4]  ctm[5] ] * [ y ]
        # [ 1  ]   [      ctm[6]       ctm[7]  ctm[8] ]   [ w ]

        # directional CTM matrices for tablet PC screen #
        normal_ctm   = [1.000000, 0.000000, 0.000000, \
                        0.000000, 1.000000, 0.000000, \
                        0.000000, 0.000000, 1.000000]

        left_ctm     = [0.000000, -1.000000, 1.000000, \
                        1.000000, 0.000000, 0.000000, \
                        0.000000, 0.000000, 1.000000]

        inverted_ctm = [-1.000000, 0.000000, 1.000000, \
                        0.000000, -1.000000, 1.000000, \
                        0.000000, 0.000000, 1.000000]

        right_ctm    = [0.000000, 1.000000, 0.000000, \
                        -1.000000, 0.000000, 1.000000, \
                        0.000000, 0.000000, 1.000000]

        # call class monitor for monitor information
        mon = monitor()

        # get tablet PC info from class monitor method get_monitor
        tablet = mon.get_monitor()

        if not tablet:
            return None

        # establish requested rotation direction
        cur_dir = tablet.direction

        # select directional CTM for requested rotation direction
        ctm = []
        if (cur_dir == 'normal'):
            ctm = normal_ctm
        elif (cur_dir == 'left'):
            ctm = left_ctm
        elif (cur_dir == 'inverted'):
            ctm = inverted_ctm
        elif (cur_dir == 'right'):
            ctm = right_ctm
        else:
            print "Unable to select directional CTM."

        if debug:
            print "directional CTM selected -> %s:" % direction, ctm
            print "tablet.x:", tablet.x
            print "tablet.y:", tablet.y

        # TODO: add connected monitor support feature for evdev and Wacom X drivers?
        # Partially implemented connected monitor scaling calculation code removed in Magick
        # Rotation 1.6.2.
        # 1. The monitor screen is disabled when 'xrandr -o direction' applied.  So a xrandr
        # command to re-enable the connected monitor is needed, e.g.:
        #  "xrandr --output VGA-1 --auto --mode 1920x1080 --right-of LVDS-1 --rotate normal".
        # Add it to class screen after the xrandr screen orientation command otherwise monitor
        # scaling values are not available plus the monitor is black.
        # 2. A connected monitor feature should also support Wacom input tools.  The xsetwacom
        # MapToOutput parameter is available with X Server 1.8 and xf86-input-wacom-0.10.9
        # (Natty 11.04 or later).  NVIDIA binary requires at least xf86-input-wacom-0.11.99.1
        # (Precise 12.04).
        # 3. Does this belong in Magick?  Would need display options in Advanced Settings.
        # FAQ for xrandr commands or Disper might be better choice.

        # the tablet PC xinput CTM command string
        val_string = "xinput set-prop " + str(self.id_val) + " 'Coordinate Transformation Matrix' " + str(ctm[0]) + " " + str(ctm[1]) + " " + str(ctm[2]) + " " + str(ctm[3]) + " " + str(ctm[4]) + " " + str(ctm[5]) + " " + str(ctm[6]) + " " + str(ctm[7]) + " " + str(ctm[8])

        print "val_string:", val_string

        # the system call for xinput CTM rotation
        result =  getstatusoutput(val_string)[1]
        if debug:
            if result:
                print result

        return 1

    def rotate(self, direction):
        direction_dict = {"normal":[0,0,0], "left":[1,0,1], \
                          "inverted":[1,1,0], "right":[0,1,1]}
        # Inversion tells us which direction we are facing
        # (0, 0) - Normal
        # (1, 0) - Left
        # (1, 1) - Inverted
        # (0, 1) - Right
        if debug:
            print "checking axis inversion"
        inv_val = self.dev.get_property("Evdev Axis Inversion")
        if not inv_val:
            if debug:
                print "no value for inv_val"
            return
        inv_val = inv_val.split(", ")
        inv_x = int(inv_val[0])
        inv_y = int(inv_val[1])

        # swap tells if the screen is sideways (1) or normal (0)
        if debug:
            print "checking swap"
        swap_val = int(self.dev.get_property("Evdev Axes Swap"))
        if (not swap_val and swap_val != 0):
            if debug:
                print "skiping no swap"
            return

        if debug:
            print "checking calibration"
        calib_val = self.dev.get_property("Evdev Axis Calibration")
        if debug:
            print calib_val
        if not calib_val:
            if debug:
                print "No calibration property.  Skipping"
            return
        elif calib_val == "<no items>":
            calib_top_x = self.top_x
            calib_top_y = self.top_y
            calib_bottom_x = self.bottom_x
            calib_bottom_y = self.bottom_y
        elif calib_val == None:
            if debug:
                print "skiping no calib"
            return
        else:
            calib_val = calib_val.split(", ")
            if (len(calib_val) == 4 and
                calib_val[0].isdigit() and
                calib_val[1].isdigit() and
                calib_val[2].isdigit() and
                calib_val[3].isdigit()):
                calib_top_x = int(calib_val[0])
                calib_bottom_x = int(calib_val[1])
                calib_top_y = int(calib_val[2])
                calib_bottom_y = int(calib_val[3])
            else:
                if (len(calib_val) == 4):
                    if debug:
                        print "invalid calib values ", calib_val[0], \
                            calib_val[1],\
                            calib_val[2],\
                            calib_val[3]
                else:
                    if debug:
                        print "invalid value: ", len(calib_val)
                return

        if direction:
            new_dir = direction
        else:
            new_dir = self.get_next_rotation(inv_x, inv_y)

        new_inv_x = direction_dict[new_dir][0]
        new_inv_y = direction_dict[new_dir][1]
        new_swap_val = direction_dict[new_dir][2]

        if swap_val != new_swap_val:
            new_top_y = calib_top_x
            new_bottom_y = calib_bottom_x
            new_top_x = calib_top_y
            new_bottom_x = calib_bottom_y
        else:
            new_top_y = calib_top_y
            new_bottom_y = calib_bottom_y
            new_top_x = calib_top_x
            new_bottom_x = calib_bottom_x

        if inv_x != new_inv_x:
            temp = new_top_x
            new_top_x = new_bottom_x
            new_bottom_x = temp

        if inv_y != new_inv_y:
            temp = new_top_y
            new_top_y = new_bottom_y
            new_bottom_y = temp

        val_string = "xinput set-prop " + str(self.id_val) + " 'Evdev Axis Inversion' " +\
                     str(new_inv_x) + " " + str(new_inv_y)
        if debug:
            print val_string

        result =  getstatusoutput(val_string)[1]
        if debug:
            if result:
                print result

        val_string = "xinput set-prop " + str(self.id_val) + " 'Evdev Axes Swap' " +\
                     str(new_swap_val)
        if debug:
            print val_string
        result =  getstatusoutput(val_string)[1]
        if debug:
            if result:
                print result

        if new_swap_val:
            val_string = "xinput set-prop " + str(self.id_val) + " 'Evdev Axis Calibration' " +\
                        str(self.top_x) + " " +\
                        str(self.bottom_y) + " " +\
                        str(self.top_y) + " " +\
                        str(self.bottom_x)
        else:
            val_string = "xinput set-prop " + str(self.id_val) + " 'Evdev Axis Calibration' " +\
                        str(self.top_x) + " " +\
                        str(self.bottom_x) + " " +\
                        str(self.top_y) + " " +\
                        str(self.bottom_y)
        if debug:
            print val_string
        result =  getstatusoutput(val_string)[1]
        if debug:
            if result:
                print result
            print

        if debug:
            print "direction: ", new_dir
            print "inv_x: ", inv_x, "    ", new_inv_x
            print "inv_y: ", inv_y, "    ", new_inv_y
            print "swap_val: ", swap_val, "    ", new_swap_val
            print calib_top_x, "    ", new_top_x
            print calib_bottom_x, "    ", new_bottom_x
            print calib_top_y, "    ", new_top_y
            print calib_bottom_y, "    ", new_bottom_y

## change screen orientation ##
class screen:
    name = ""
    x = 0
    y = 0
    x_offset = 0
    y_offset = 0
    direction = ""

    def __init__(self, new_name=None, new_x=None, new_y=None, new_x_offset=None, new_y_offset=None, new_direction=None):
        screen.name = new_name
        screen.x = new_x
        screen.y = new_y
        screen.x_offset = new_x_offset
        screen.y_offset = new_y_offset
        screen.direction = new_direction

    def get_next_rotation(self, direction):
        rotate_order = ["normal", "left", "inverted", "right"]
        randr_name = direction
   
        randr_val = rotate_order.index(randr_name)
        # Add one to get the next rotation value and
        # do a modulo (gets the remainder) to get the next value
        new_rotated_val = (randr_val + 1) % 4

        return rotate_order[new_rotated_val]
    
    def rotate(self, direction):
        if direction:
            new_dir = direction
        else:
            new_dir = self.get_next_rotation()

        # the xrandr screen orientation command string
        val_string = "xrandr -o " + new_dir
        if debug:
            print " Rotating screen"
            print val_string

        # the system call to change screen orientation
        result =  getstatusoutput(val_string)[1]
        screen.direction = new_dir
        if debug:
            if result:
                print result
            print

        return new_dir

class monitor:
    monitor_list = []
    count = 0

    def __init__(self):
        # find connnected monitors in xrandr output
        cmd = "xrandr -q --verbose 2>/dev/null|grep connected|grep -v disconnected"
        connected_monitor_data = getoutput(cmd)
        monitor_data = connected_monitor_data.split("\n")
        monitor_count = len(monitor_data)
        print "class monitor monitor_count:", monitor_count

# current connected resolution marked with an asterix in xrandr, so: xrandr | grep '*'

        # extract the monitor name, resolution, offsets, and direction
        for index in range(monitor_count):
            resolution  = monitor_data[index].split("connected ")[1].split(" (")[0]
            if resolution.startswith("("):
                # if it starts with a '(' then the monitor is plugged in but disabled
                pass
            else:
                x_coord = resolution.split("x")[0]
                y_coord = resolution.split("x")[1].split('+')[0]
                off_x = resolution.split("x")[1].split('+')[1]
                off_y = resolution.split("x")[1].split('+')[2]

                direction = monitor_data[index].split(") ")[1].split(" (")[0]
                name = monitor_data[index].split(" ")[0]

                monitor.monitor_list.append(screen())
                monitor.monitor_list[monitor.count].name = name
                monitor.monitor_list[monitor.count].x = x_coord
                monitor.monitor_list[monitor.count].y = y_coord
                monitor.monitor_list[monitor.count].x_offset = off_x
                monitor.monitor_list[monitor.count].y_offset = off_y
                monitor.monitor_list[monitor.count].direction = direction
#                mon = screen(name, x_coord, y_coord, off_x, off_y, direction)
#                monitor.monitor_list.append(mon)
#                monitor.monitor_list.append([mon.name, mon.x, mon.y, mon.x_offset, mon.y_offset, mon.direction])
                monitor.count += 1

# monitor_types = ["CRT", "DVI", "VGA"]
# less common monitor types: "DP1", "S-video", "TMDS", "TV"
# monitor_types = ["CRT", "DP1", "DVI", "S-video", "TMDS", "TV", "VGA"]

    # determine which monitor is the tablet PC screen
    def get_monitor(self):
#        tablet_list = ["LVDS", "DFP"]
        # nVidia proprietary driver xrandr output uses 'default' for monitor name(s)
        # whether or not a second monitor is connected.  So xrotate.py will not work as
        # a stand alone script for nVidia proprietary driver unless "default" is added.
        tablet_list = ["LVDS", "DFP", "default"]
        for mon in monitor.monitor_list:
            for check in tablet_list:
                if mon.name.startswith(check):
                    return mon
        return None

class rotate:
    def __init__(self):
        self.dev = devices()
        self.top_x = 0
        self.top_y = 0
        self.bottom_x = 9600
        self.bottom_y = 7200

        self.rotate_order = ["normal", "left", "inverted", "right"]
        self.lid_order = ["normal", "right"]

        self.direction = "normal"
        self.wacom_count = 0

    def rotate_device(self, direction, device):
        id_val = 0
        if not str(device).isdigit():
            id_val = self.dev.find_id(device)
        else:
            id_val = device

        id_val = int(id_val)

        if self.dev.is_evdev(id_val):
            processing = "rotating evdev device "
            if debug:
                print processing + self.dev.get_device_name(id_val)
            evdev_dev = evdev(self.dev.get_device(id_val), id_val)
            # This will try to rotate using the Coordinate
            # Transformation Matrix but if it cannot, then
            # it will fall back to other rotation method
            print "going: %s" % direction
            if not evdev_dev.rotate_ctm(direction):
                evdev_dev.rotate(direction)
        elif self.dev.is_wacom(id_val):
            self.wacom_count += 1
            processing = "rotating wacom device "
            if debug:
                print processing + self.dev.get_device_name(id_val)
            wacom_dev = wacom(self.dev.get_device(id_val), id_val)
            wacom_dev.rotate(direction)
        else:
            processing = "skipping "
#            if debug:
#                print processing + self.dev.get_device_name(id_val)

    def rotate_ctm_device(self, direction, device):
        id_val = 0
        if not str(device).isdigit():
            id_val = self.dev.find_id(device)
        else:
            id_val = device

        id_val = int(id_val)

        if self.dev.is_evdev(id_val):
            processing = "rotating evdev device "
            if debug:
                print processing + self.dev.get_device_name(id_val)
            evdev_dev = evdev(self.dev.get_device(id_val), id_val)
            evdev_dev.rotate_ctm(direction)
#        elif self.dev.is_wacom(id_val):
#            self.wacom_count += 1
#            processing = "rotating wacom device "
#            if debug:
#                print processing + self.dev.get_device_name(id_val)
#            wacom_dev = wacom(self.dev.get_device(id_val), id_val)
#            wacom_dev.rotate(direction)
        else:
            processing = "skipping "
#            if debug:
#                print processing + self.dev.get_device_name(id_val)

    # To rotate only the devices and not the screen
    def rotate_devices(self, direction):
        if debug:
            print "Entered rotate_devices"
        dev_list = self.dev.get_id_list()
        self.wacom_count = 0
        for id_val in dev_list:
            self.rotate_device(direction, id_val)

        if debug:
            print "wacom count: ", self.wacom_count
            print "direction: " + direction

        # for versions less than Lucid we will check 
        # xsetwacom to see if there are any devices to 
        # rotate
        if self.wacom_count == 0:
            wacom_dev = linuxwacom()
            devices = getoutput("xsetwacom list")
            if devices:
                devices = devices.split("\n")
                for item in devices:
                    name = ""
                    item_list = item.split()
                    # Rebuild the device name with spaces but
                    # skip the last word because it is the tool type
                    for index in range(len(item_list) - 1):
                        name += item_list[index]
                        if index != (len(item_list) - 2):
                            name += " "
                    if debug:
                        print "name: " + name + " direction: " + direction
                    wacom_dev.rotate(name, direction)


    def rotate(self, direction):
        dev_list = self.dev.get_id_list()

        mon = monitor()
        display = mon.get_monitor()

        if not display:
            if debug:
                print "No tablet monitor found"
                return None

#        direction = display.direction
        if not direction:
            direction = display.get_next_rotation(display.direction)
        display.direction = display.rotate(direction)

        direction = display.direction
        self.wacom_count = 0
        for id_val in dev_list:
            if debug:
                print "testing " , id_val
            self.rotate_device(direction, id_val)

        # for versions less than Lucid we will check 
        # xsetwacom to see if there are any devices to 
        # rotate
        if self.wacom_count == 0:
            wacom_dev = linuxwacom()
            devices = getoutput("xsetwacom list")
            if devices:
                devices = devices.split("\n")
                for item in devices:
                    name = ""
                    item_list = item.split()
                    # Rebuild the device name with spaces but
                    # skip the last word because it is the tool type
                    for index in range(len(item_list) - 1):
                        name += item_list[index]
                        if index != (len(item_list) - 2):
                            name += " "
                    wacom_dev.rotate(name, direction)

class touch:
    def __init__(self):
        self.dev = devices()

    def toggle_touch(self, toggle):
        toggle = int(toggle)
        dev_list = self.dev.get_id_list()
        wacom_count = 0
        for id_val in dev_list:
            if self.dev.is_evdev_touch(id_val):
                ev_touch = evdev(self.dev.get_device(id_val), id_val)
                ev_touch.toggle_touch(toggle)
            if self.dev.is_wacom(id_val):
                wac = wacom(self.dev.get_device(id_val), id_val)
                if wac.is_touch():
                    wacom_count += 1
                    wac.toggle_touch(toggle)

        if wacom_count == 0:
            wacom_dev = linuxwacom()
            devices = getoutput("xsetwacom list")
            if devices:
                devices = devices.split("\n")
                for item in devices:
                    name = ""
                    item_list = item.split()
                    # Rebuild the device name with spaces but
                    # skip the last word because it is the tool type
                    for index in range(len(item_list) - 1):
                        name += item_list[index]
                        if index != (len(item_list) - 2):
                            name += " "
                    tool_type = item_list[len(item_list) - 1]
#                if len(tool_type) == 3:
#                    tool_type = tool_type[2]
                    if tool_type in ["TOUCH", "touch"]:
                           wacom_dev.toggle_touch(name, toggle)

if __name__ == "__main__":
    r = rotate()
    d = devices()
#    d.find_id('N-Trig MultiTouch')

#    t = touch()
#    t.toggle_touch(1)

# Remember to uncomment this so that it will work properly
    if (len(argv) == 2):
        direction = argv[1]
        r.rotate(direction)
    elif (len(argv) == 1):
        r.rotate(None)
    elif (len(argv) == 3):
        direction = argv[1]
        device = argv[2]
        r.rotate_device(direction, device)
    else:
        print "xrotate.py needs the direction.\n",
        print "xrotate.py <normal/left/inverted/right>\n",
        print "Example: xrotate.py left'"
        exit(0)

# These three lines are for testing the ctm rotation
#    direction = argv[1]
#    r.rotate_ctm_device(direction, d.find_id('Logitech USB Mouse'))
#    r.rotate_ctm_device(direction, d.find_id('N-Trig MultiTouch'))

#    if (len(argv) == 3):
#        direction = argv[1]
#        device = argv[2]
##        r.rotate_device(direction, device)
#        r.rotate(direction)
#    else:
#        print "xrotate.py needs the direction and device name/id.\n",
#        print "xrotate.py <normal/left/inverted/right> <device name/id>\n",
#        print "Example: xrotate.py left 'N-Trig MultiTouch'"
#        exit(0)
