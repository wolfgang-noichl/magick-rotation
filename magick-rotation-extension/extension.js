/*
 * This extension adds the interactive Magick Rotation Icon
 * to the GNOME 3.2 Shell's System Status Area.
 */

const StatusIconDispatcher = imports.ui.statusIconDispatcher;

// window manager class of Magick's icon is 'magick-rotation'
var wmClassIcon = ['magick-rotation'];

function enable() {
    StatusIconDispatcher.STANDARD_TRAY_ICON_IMPLEMENTATIONS[wmClassIcon] = wmClassIcon;
}

function disable() {
    StatusIconDispatcher.STANDARD_TRAY_ICON_IMPLEMENTATIONS[wmClassIcon] = '';
}

function init(metadata) {
}
