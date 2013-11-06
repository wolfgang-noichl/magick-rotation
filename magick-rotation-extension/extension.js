/*
 * This extension adds the interactive Magick Rotation Icon
 * to the GNOME 3.2 Shell's System Status Area.
 */

const StatusIconDispatcher = imports.ui.statusIconDispatcher;

function enable() {
    StatusIconDispatcher.STANDARD_TRAY_ICON_IMPLEMENTATIONS['magick-rotation'] = 'magick-rotation';
}

function disable() {
    StatusIconDispatcher.STANDARD_TRAY_ICON_IMPLEMENTATIONS['magick-rotation'] = '';
}

function init(metadata) {
}
