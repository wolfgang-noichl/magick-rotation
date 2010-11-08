#include <stdio.h>
#include <X11/Xlib.h>
#include <X11/extensions/Xrandr.h>

int main(void) {
	XEvent event;
	int ret_val = -1;
	Rotation rotation, rot_val;

	Display *dpy = XOpenDisplay(NULL);
	Window root = RootWindow(dpy, 0);

	XRRSelectInput(dpy, DefaultRootWindow(dpy), RRScreenChangeNotifyMask);

	XNextEvent(dpy, (XEvent *) &event);

	XRRScreenConfiguration *conf = XRRGetScreenInfo(dpy, root);

	rot_val = XRRConfigRotations(conf, &rotation);

	switch (rotation) {
		case RR_Rotate_0:
			ret_val = 0;
			break;
		case RR_Rotate_90:
			ret_val = 1;
			break;
		case RR_Rotate_180:
			ret_val = 3;
			break;
		case RR_Rotate_270:
			ret_val = 2;
			break;
	}

	return ret_val;

}
