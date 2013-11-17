/* This extension adds the interactive Magick Rotation Icon
 * to the GNOME 3.8 Shell's System Status Area.
 *
 * Code from anarsoul's Gnome 3.8 fork of TopIcons by Adel Gadllah
 * https://github.com/anarsoul/topIcons
 */

const Clutter = imports.gi.Clutter;
const Shell = imports.gi.Shell;

const Lang = imports.lang;
const PanelMenu = imports.ui.panelMenu;
const Panel = imports.ui.panel;
const Main = imports.ui.main;
const Mainloop = imports.mainloop;
const NotificationDaemon = imports.ui.notificationDaemon;

let trayIcon = [];
let trayAddedId = 0;
let trayRemovedId = 0;

// window manager class of Magick's icon is 'magick-rotation'
var wmClassIcon = ['magick-rotation'];

// new for Gnome 3.8
const IndicatorStatusIcon = new Lang.Class({
    Name: 'IndicatorStatusIcon',
    Extends: PanelMenu.Button,

    _init: function(icon){
        this.parent(0.0, _("Tray Indicator StatusIcon"));

        this._trayIcon = icon;
        this.actor.add_actor(icon);
    },

    destroy: function() {
        this.parent();
    },

    getIcon: function() {
        return this._trayIcon;
    },
});

// Callback when a tray icon is added to the tray manager.
// We make a top panel Menu Button for it.
function onTrayIconAdded(o, icon) {
    let wmClass = icon.wm_class ? icon.wm_class.toLowerCase() : '';
    if (wmClass == wmClassIcon) {
        global.log('onTrayIconAdded: ' + wmClass);
        if (NotificationDaemon.STANDARD_TRAY_ICON_IMPLEMENTATIONS[wmClass] !== undefined)
            return;

        icon.height = Panel.PANEL_ICON_SIZE;
        icon.width = Panel.PANEL_ICON_SIZE;

        let indicatorStatusIcon = new IndicatorStatusIcon(icon)

        icon.reactive = true;
        icon._clicked = icon.connect('button-release-event', function(actor, event) {
            icon.click(event);
        });

        if (trayIcon[wmClass] != undefined) {
            let oldIndicator = trayIcon[wmClass];
            trayIcon[wmClass] = null;
            oldIndicator.destroy();
        }

        trayIcon[wmClass] = indicatorStatusIcon;
        Main.panel.addToStatusArea('tray-' + wmClass, indicatorStatusIcon);
    }
}

function onTrayIconRemoved(o, icon) {
    let wmClass = icon.wm_class ? icon.wm_class.toLowerCase() : '';
    if (wmClass == wmClassIcon) {
        let oldIndicator = null;

        global.log('onTrayIconRemoved: ' + wmClass);

        if (trayIcon[wmClass] !== undefined) {
            oldIndicator = trayIcon[wmClass];
            trayIcon[wmClass] = null;
            oldIndicator.destroy();
            return;
        }

        global.log("onTrayIconRemoved: indicator not found!");
    }
}

function moveTrayIconToStatusTray() {
    Main.notificationDaemon._trayManager.disconnect(Main.notificationDaemon._trayIconAddedId);
    Main.notificationDaemon._trayManager.disconnect(Main.notificationDaemon._trayIconRemovedId);
    trayAddedId = Main.notificationDaemon._trayManager.connect('tray-icon-added', onTrayIconAdded);
    trayRemovedId = Main.notificationDaemon._trayManager.connect('tray-icon-removed', onTrayIconRemoved);

    let toDestroy = [];

    // convert Magick's message tray only gtk.StatusIcon to status tray icon.
    for (let i = 0; i < Main.notificationDaemon._sources.length; i++) {
        let source = Main.notificationDaemon._sources[i];
        if (!source.trayIcon)
            continue;
        let icon = source.trayIcon;
        if (icon) {
            let wmClass = icon.wm_class ? icon.wm_class.toLowerCase() : '';
            if (wmClass == wmClassIcon) {
                let parent = source.trayIcon.get_parent();
                parent.remove_actor(source.trayIcon);
                onTrayIconAdded(this, source.trayIcon);
                toDestroy.push(source);
            } 
        }
    }

    for (let i = 0; i < toDestroy.length; i++) {
        toDestroy[i].destroy();
    }
}

function moveTrayIconToMessageTray() {
    if (trayAddedId != 0) {
        Main.notificationDaemon._trayManager.disconnect(trayAddedId);
        trayAddedId = 0;
    }

    if (trayRemovedId != 0) {
        Main.notificationDaemon._trayManager.disconnect(trayRemovedId);
        trayRemovedId = 0;
    }

    Main.notificationDaemon._trayIconAddedId = Main.notificationDaemon._trayManager.connect('tray-icon-added',
                                                Lang.bind(Main.notificationDaemon, Main.notificationDaemon._onTrayIconAdded));
    Main.notificationDaemon._trayIconRemovedId = Main.notificationDaemon._trayManager.connect('tray-icon-removed',
                                                Lang.bind(Main.notificationDaemon, Main.notificationDaemon._onTrayIconRemoved));

    for (var key in trayIcon) {
        let indicator = trayIcon[key];
        let icon = indicator.getIcon();
        icon.disconnect(icon._clicked);
        icon._clicked = undefined;
        indicator.actor.remove_actor(icon);
        indicator.destroy();
        Main.notificationDaemon._onTrayIconAdded(Main.notificationDaemon, icon);
    }

    trayIcon = [];
}

function init() {
}

function enable() {
    moveTrayIconToStatusTray();
}

function disable() {
    moveTrayIconToMessageTray();
}
