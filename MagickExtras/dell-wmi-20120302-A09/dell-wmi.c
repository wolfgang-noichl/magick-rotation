/*
 * Dell WMI hotkeys
 *
 * Copyright (C) 2008 Red Hat <mjg@redhat.com>
 *
 * Portions based on wistron_btns.c:
 * Copyright (C) 2005 Miloslav Trmac <mitr@volny.cz>
 * Copyright (C) 2005 Bernhard Rosenkraenzer <bero@arklinux.org>
 * Copyright (C) 2005 Dmitry Torokhov <dtor@mail.ru>
 *
 *  This program is free software; you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation; either version 2 of the License, or
 *  (at your option) any later version.
 *
 *  This program is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with this program; if not, write to the Free Software
 *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
 */

#include <linux/kernel.h>
#include <linux/module.h>
#include <linux/init.h>
#include <linux/types.h>
#include <linux/input.h>
#include <acpi/acpi_drivers.h>
#include <linux/acpi.h>
#include <linux/string.h>

/*
 * Addition of KE_SW and SW_TABLET_MODE by Rafi Rubin.
 * Hex scan code changes for Latitude XT2 A09 BIOS by enneract.
 * SW_TABLET_MODE scan code changes confirmed by Michael Knap for the A11 BIOS.
 */

MODULE_AUTHOR("Matthew Garrett <mjg@redhat.com>");
MODULE_DESCRIPTION("Dell laptop WMI hotkeys driver");
MODULE_LICENSE("GPL");

#define DELL_EVENT_GUID "9DBB5994-A997-11DA-B012-B622A1EF5492"

MODULE_ALIAS("wmi:"DELL_EVENT_GUID);

struct key_entry {
	char type;		/* See KE_* below */
	u16 code;
	u16 keycode;
   u8  state;
};

enum { KE_KEY, KE_SW, KE_IGNORE, KE_END };

/*
 * Certain keys are flagged as KE_IGNORE. All of these are either
 * notifications (rather than requests for change) or are also sent
 * via the keyboard controller so should not be sent again.
 */

static struct key_entry dell_wmi_keymap[] = {
	/* scan code changed from 0xe045 to 0x0041 for XT2 A09 BIOS */
	{KE_KEY, 0x0041, KEY_PROG1},
	/* scan code changed from 0xe046 to 0xffd2 for XT2 A09 BIOS */
	{KE_SW , 0xffd2, SW_TABLET_MODE,1},     /* Going to tablet mode */
	/* scan code changed from 0xe047 to 0xffd3 for XT2 A09 BIOS */
	{KE_SW , 0xffd3, SW_TABLET_MODE,0},     /* Coming from tablet mode */
	{KE_KEY, 0xe009, KEY_EJECTCD},

	/* These also contain the brightness level at offset 6 */
	{KE_KEY, 0xe006, KEY_BRIGHTNESSUP},
	{KE_KEY, 0xe005, KEY_BRIGHTNESSDOWN},

	/* Battery health status button */
	/* Fn+F3 on the Latitude XT2-comment added by enneract,
	 * scan code changed from 0xe007 to 0x003d for XT2 A09 BIOS */
	{KE_KEY, 0x003d, KEY_BATTERY}, 
		
	/* This is actually for all radios. Although physically a
	 * switch, the notification does not provide an indication of
	 * state and so it should be reported as a key */
	/* This is not physically a switch on the XT2 (Fn+F9)-comment added by enneract,
	 * scan code changed from 0xe008 to 0x0008 for XT2 A09 BIOS */
	{KE_KEY, 0x0008, KEY_WLAN},

	/* The next device is at offset 6, the active devices are at
	   offset 8 and the attached devices at offset 10 */
	/* scan code changed from 0xe00b to 0x0070 for XT2 A09 BIOS */
	{KE_KEY, 0x0070, KEY_DISPLAYTOGGLE},

	{KE_KEY, 0xe00c, KEY_KBDILLUMTOGGLE},

	/* BIOS error detected */
	{KE_KEY, 0xe00d, KEY_RESERVED},

	/* Wifi Catcher */
	/* Needs to be held down for a second or two-comment added by enneract,
	 * scan code changed from 0xe011 to 0x0011 for XT2 A09 BIOS */
	{KE_KEY, 0x0011, KEY_PROG2},

	/* Ambient light sensor toggle */
	{KE_KEY, 0xe013, KEY_RESERVED},

	{KE_KEY, 0xe020, KEY_MUTE},
	{KE_KEY, 0xe02e, KEY_VOLUMEDOWN},
	{KE_KEY, 0xe030, KEY_VOLUMEUP},
	{KE_KEY, 0xe033, KEY_KBDILLUMUP},
	{KE_KEY, 0xe034, KEY_KBDILLUMDOWN},
	{KE_KEY, 0xe03a, KEY_CAPSLOCK},
	{KE_KEY, 0xe045, KEY_NUMLOCK},
	{KE_KEY, 0xe046, KEY_SCROLLLOCK},
	{KE_END, 0}
};

static struct input_dev *dell_wmi_input_dev;

static struct key_entry *dell_wmi_get_entry_by_scancode(int code)
{
	struct key_entry *key;

	for (key = dell_wmi_keymap; key->type != KE_END; key++)
		if (code == key->code)
			return key;

	return NULL;
}

static struct key_entry *dell_wmi_get_entry_by_keycode(int keycode)
{
	struct key_entry *key;

	for (key = dell_wmi_keymap; key->type != KE_END; key++)
		if (key->type == KE_KEY && keycode == key->keycode)
			return key;

	return NULL;
}

static int dell_wmi_getkeycode(struct input_dev *dev, int scancode,
			       int *keycode)
{
	struct key_entry *key = dell_wmi_get_entry_by_scancode(scancode);

	if (key && key->type == KE_KEY) {
		*keycode = key->keycode;
		return 0;
	}

	return -EINVAL;
}

static int dell_wmi_setkeycode(struct input_dev *dev, int scancode, int keycode)
{
	struct key_entry *key;
	int old_keycode;

	if (keycode < 0 || keycode > KEY_MAX)
		return -EINVAL;

	key = dell_wmi_get_entry_by_scancode(scancode);
	if (key && key->type == KE_KEY) {
		old_keycode = key->keycode;
		key->keycode = keycode;
		set_bit(keycode, dev->keybit);
		if (!dell_wmi_get_entry_by_keycode(old_keycode))
			clear_bit(old_keycode, dev->keybit);
		return 0;
	}
	return -EINVAL;
}

static void dell_wmi_notify(u32 value, void *context)
{
	struct acpi_buffer response = { ACPI_ALLOCATE_BUFFER, NULL };
	static struct key_entry *key;
	union acpi_object *obj;

	wmi_get_event_data(value, &response);

	obj = (union acpi_object *)response.pointer;

	if (obj && obj->type == ACPI_TYPE_BUFFER) {
		int *buffer = (int *)obj->buffer.pointer;
		printk("dell wmi got code %x\n",value);
		/*
		 *  The upper bytes of the event may contain
		 *  additional information, so mask them off for the
		 *  scancode lookup
		 */
		key = dell_wmi_get_entry_by_scancode(buffer[1] & 0xFFFF);
		if (key) {
         switch (key->type) {
         case KE_KEY:
				input_report_key(dell_wmi_input_dev, key->keycode, 1);
				input_sync(dell_wmi_input_dev);
				input_report_key(dell_wmi_input_dev, key->keycode, 0);
				input_sync(dell_wmi_input_dev);
            break;
         case KE_SW:
            input_report_switch(dell_wmi_input_dev, key->keycode, key->state);
            input_sync(dell_wmi_input_dev);
            break;
         }
		} else if (buffer[1] & 0xFFFF)
			printk(KERN_INFO "dell-wmi: Unknown key %x pressed\n",
			       buffer[1] & 0xFFFF);
	}
}

static int __init dell_wmi_input_setup(void)
{
	struct key_entry *key;
	int err;

	dell_wmi_input_dev = input_allocate_device();

	if (!dell_wmi_input_dev)
		return -ENOMEM;

	dell_wmi_input_dev->name = "Dell WMI hotkeys";
	dell_wmi_input_dev->phys = "wmi/input0";
	dell_wmi_input_dev->id.bustype = BUS_HOST;
	dell_wmi_input_dev->getkeycode = dell_wmi_getkeycode;
	dell_wmi_input_dev->setkeycode = dell_wmi_setkeycode;

	for (key = dell_wmi_keymap; key->type != KE_END; key++) {
		switch (key->type) {
		case KE_KEY:
			set_bit(EV_KEY, dell_wmi_input_dev->evbit);
			set_bit(key->keycode, dell_wmi_input_dev->keybit);
			break;
		case KE_SW:
			set_bit(EV_SW, dell_wmi_input_dev->evbit);
			set_bit(key->keycode, dell_wmi_input_dev->swbit);
			break;
		}
	}

	err = input_register_device(dell_wmi_input_dev);

	if (err) {
		input_free_device(dell_wmi_input_dev);
		return err;
	}

	return 0;
}

static int __init dell_wmi_init(void)
{
	int err;

	if (wmi_has_guid(DELL_EVENT_GUID)) {
		err = dell_wmi_input_setup();

		if (err)
			return err;

		err = wmi_install_notify_handler(DELL_EVENT_GUID,
						 dell_wmi_notify, NULL);
		if (err) {
			input_unregister_device(dell_wmi_input_dev);
			printk(KERN_ERR "dell-wmi: Unable to register"
			       " notify handler - %d\n", err);
			return err;
		}

	} else
		printk(KERN_WARNING "dell-wmi: No known WMI GUID found\n");

	return 0;
}

static void __exit dell_wmi_exit(void)
{
	if (wmi_has_guid(DELL_EVENT_GUID)) {
		wmi_remove_notify_handler(DELL_EVENT_GUID);
		input_unregister_device(dell_wmi_input_dev);
	}
}

module_init(dell_wmi_init);
module_exit(dell_wmi_exit);
