/*
 * This extension adds the interactive Magick Rotation Icon
 * to the GNOME 3.6 Shell's System Status Area.
 *
 * Code from EvilStatusIconForever fork for Gnome 3.6 by mathematicalcoffee
 * https://github.com/mathematicalcoffee/EvilStatusIconForever
 * Original EvilStatusIconForever for Gnome 3.2 by Brian Hsu
 * https://github.com/brianhsu/EvilStatusIconForever
 */

const Shell = imports.gi.Shell;
const PanelMenu = imports.ui.panelMenu;
const Panel = imports.ui.panel;
const Main = imports.ui.main;
const STANDARD_TRAY_ICON_IMPLEMENTATIONS = imports.ui.notificationDaemon.STANDARD_TRAY_ICON_IMPLEMENTATIONS;
let trayManager, addedID;
let statusArea;

var notification = ['magick-rotation']

/*
 * Hide built-in status icon.
 *
 * Note: in 3.6 the top-level actor for a status button in
 * _rightBox.get_children() doesn't have a ._delegate; its first child does.
 * So instead we just remove from the status area directly.
 */
function hideStatusIcon(name)
{
    if (statusArea[name]) {
        statusArea[name].actor.hide();
    }
}

/*
 * Show built-in status icon again.
 */
function showStatusIcon(name)
{
    if (statusArea[name]) {
        statusArea[name].actor.show();
    }
}

/*
 * Callback when a tray icon is added to the tray manager.
 * We make a panel button for the top panel for it.
 */
function _onTrayIconAdded(o, icon) {
    let wmClass = icon.wm_class ? icon.wm_class.toLowerCase() : '';
    if (notification.indexOf(wmClass) === -1) {
        // skip it
        return;
    }

    icon.height = Panel.PANEL_ICON_SIZE;
    let buttonBox = new PanelMenu.Button();
    let box = buttonBox.actor;
    box.add_actor(icon);

    Main.panel._addToPanelBox(wmClass, buttonBox, 0, Main.panel._rightBox);
}

/*
 * STANDARD_TRAY_ICON_IMPLEMENTATIONS is necessary for 3.6
 * to stop the message tray also making an icon for it.
 */
function removeFromTopBar(wmClass)
{
    delete STANDARD_TRAY_ICON_IMPLEMENTATIONS[wmClass];
    if (statusArea[wmClass]) {
        statusArea[wmClass].destroy();
    }
}

function addToTopBar(wmClass)
{
    STANDARD_TRAY_ICON_IMPLEMENTATIONS[wmClass] = wmClass;
}

function init() {
}

function enable() {
    statusArea = Main.panel.statusArea;
    trayManager = Main.notificationDaemon._trayManager;
    addedID = trayManager.connect('tray-icon-added', _onTrayIconAdded);

    for (var i = 0; i < notification.length; i++) {
        global.log('Add ' + notification[i] + " to top bar");
        addToTopBar(notification[i]);
    }

}

function disable() {
    trayManager.disconnect(addedID);
    addedID = 0;

    for (var i = 0; i < notification.length; i++) {
        global.log('Remove ' + notification[i] + " from top bar");
        removeFromTopBar(notification[i]);
    }

}
