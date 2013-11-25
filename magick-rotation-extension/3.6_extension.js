/* This extension adds the interactive Magick Rotation Icon
 * to the GNOME 3.6 Shell's System Status Area.
 *
 * Code from mathematicalcoffee's Gnome 3.6 fork of EvilStatusIconForever by Brian Hsu
 * https://github.com/mathematicalcoffee/EvilStatusIconForever
 */

const Clutter = imports.gi.Clutter;
const Shell = imports.gi.Shell;

const PanelMenu = imports.ui.panelMenu;
const Panel = imports.ui.panel;
const Main = imports.ui.main;
const STANDARD_TRAY_ICON_IMPLEMENTATIONS = imports.ui.notificationDaemon.STANDARD_TRAY_ICON_IMPLEMENTATIONS;

let trayManager, addedID, fullScreenChangedId;
let statusArea;
let trayIcon = {};

// window manager class of Magick's icon is 'magick-rotation'
var wmClassIcon = ['magick-rotation'];

function LOG(message) {
    //log(message);
}

// Hide built-in status icon.
  // Note: in 3.6 the top-level actor for a status button in
  // _rightBox.get_children() doesn't have a ._delegate; its first child
  // does. So instead we just remove from the status area directly.
function hideStatusIcon(name)
{
    if (statusArea[name]) {
        statusArea[name].actor.hide();
    }
}

// Show built-in status icon again.
function showStatusIcon(name)
{
    if (statusArea[name]) {
        statusArea[name].actor.show();
    }
}

// Callback when a tray icon is added to the tray manager.
// We make a panel button for the top panel for it.
function _onTrayIconAdded(o, icon) {
    let wmClass = icon.wm_class ? icon.wm_class.toLowerCase() : '';
    if (wmClassIcon.indexOf(wmClass) === -1) {
        // skip it
        return;
    }

    icon.height = Panel.PANEL_ICON_SIZE;
    icon.width = Panel.PANEL_ICON_SIZE;
    let buttonBox = new PanelMenu.Button();
    let box = buttonBox.actor;
    box.add_actor(icon);

    Main.panel._addToPanelBox(wmClass, buttonBox, 0, Main.panel._rightBox);
    trayIcon[wmClass] = icon;
}

// STANDARD_TRAY_ICON_IMPLEMENTATIONS is necessary for 3.6
// to stop the message tray also making an icon for it.
function removeFromStatusTray(wmClass)
{
    delete STANDARD_TRAY_ICON_IMPLEMENTATIONS[wmClass];
    if (trayIcon[wmClass]) {
        trayIcon[wmClass].unparent();
    }
    if (statusArea[wmClass]) {
        statusArea[wmClass].destroy();
    }
}

function addToStatusTray(wmClass)
{
    STANDARD_TRAY_ICON_IMPLEMENTATIONS[wmClass] = wmClass;
}

function _moveTrayIconToStatusTray() {
    LOG('Add ' + wmClassIcon + " to top bar");
    addToStatusTray(wmClassIcon);

    let i;

    // convert Magick's message tray only gtk.StatusIcon to status tray icon.
    for (i = 0; i < Main.notificationDaemon._sources.length; ++i) {
        let source = Main.notificationDaemon._sources[i],
            icon = source.trayIcon;
        if (icon) {
            let wmClass = icon.wm_class ? icon.wm_class.toLowerCase() : '';
            if (wmClassIcon.indexOf(wmClass) > -1) {
                // NOTE: if I use icon.unparent() it segfaults, but if I use
                // parent.remove_actor(icon) it's fine.
                // Weird!
                icon.get_parent().remove_actor(icon);
                source.destroy();

                // add back to the tray
                _onTrayIconAdded(trayManager, icon);
            }
        }
    }
}

function _moveTrayIconToMessageTray() {
    removeFromStatusTray(wmClassIcon);
    let icon = trayIcon[wmClassIcon];
    if (icon) {
        LOG('Remove ' + wmClassIcon + " from top bar");
        // add back to message tray
        Main.notificationDaemon._onTrayIconAdded(Main.notificationDaemon, icon);
        delete trayIcon[wmClassIcon];
    }

    trayIcon = {};
}

function init() {
}

function enable() {
    statusArea = Main.panel.statusArea;
    trayManager = Main.notificationDaemon._trayManager;
    addedID = trayManager.connect('tray-icon-added', _onTrayIconAdded);

    _moveTrayIconToStatusTray();
    // StatusIcon = wmClassIcon = 'magick-rotation'
    LOG('Remove ' + wmClassIcon + " from top bar");
    hideStatusIcon(wmClassIcon);

    // NOTE: this fix (for icons turning into white squares) from TopIcons:
    // https://extensions.gnome.org/extension/495/topicons/
      // TrayIcons do not survive leaving the stage (they end up as
      // whitesquares), so work around this by temporarily move them back
      // to the message tray while we are in fullscreen.
    fullScreenChangedId = Main.layoutManager.connect(
        'primary-fullscreen-changed', function (o, state) {
            if (state) {
                _moveTrayIconToMessageTray();
            } else {
                _moveTrayIconToStatusTray();
            }
        });
}

function disable() {
    trayManager.disconnect(addedID);
    addedID = 0;

    _moveTrayIconToMessageTray();
    LOG('Restore ' + wmClassIcon + " to top bar");
    showStatusIcon(wmClassIcon);

    Main.layoutManager.disconnect(fullScreenChangedId);
}
