#!/usr/bin/env python

import gtk
import pygtk
import apt
#try:
#    from apt.progress import base
#    old_apt = False
#except ImportError:
#    old_apt = True
import apt_pkg

try:
    from apt.progress.old import FetchProgress,  InstallProgress
except ImportError:
    from apt.progress import FetchProgress,  InstallProgress

#from apt.progress.old import FetchProgress,  InstallProgress
import sys

class FetchProgressGTK(FetchProgress):
    def __init__(self,  widget):
        FetchProgress.__init__(self)
        self.widget = widget
        self.items = {}

    def updateStatus(self, uri, descr, short_descr, status):
        """Called when the status of an item changes.

        This happens eg. when the downloads fails or is completed.
        """
	uri_text = "Downloading " + short_descr
        if status != self.dlQueued:
            print "\r%s %s" % (self.dlStatusStr[status], descr)
            self.widget.pkg_label.set_text(uri_text)
        self.items[uri] = status

    def pulse(self):
        """Called periodically to update the user interface.

        Return True to continue or False to cancel.
        """
        FetchProgress.pulse(self)
        if self.currentCPS > 0:
            try:
                s = "[%2.f%%] %sB/s %s" % (self.percent,
                                        apt_pkg.size_to_str(int(self.currentCPS)),
                                        apt_pkg.time_to_str(int(self.eta)))
            except:
                s = "[%2.f%%] %sB/s %s" % (self.percent,
                                        apt_pkg.SizeToStr(int(self.currentCPS)),
                                        apt_pkg.TimeToStr(int(self.eta)))
        else:
            s = "%2.f%% [Working]" % (self.percent)
        progress = float(float(self.percent)/float(100))
        self.widget.progress_bar.set_text(s)
        self.widget.progress_bar.set_fraction(progress)
        #print "\r%s" % (s),
        #sys.stdout.flush()
        return True
    
    def start(self):
        """Called when all files have been fetched."""
        self.widget.fetching = True

    def stop(self):
        """Called when all files have been fetched."""
        self.widget.fetching = False
        self.widget.progress_bar.set_text(" ")
        self.widget.pkg_label.set_text(" ")

    def mediaChange(self, medium, drive):
        """react to media change events."""
        print ("Media change: please insert the disc labeled "
               "'%s' in the drive '%s' and press enter") % (medium, drive)

        return raw_input() not in ('c', 'C')


class InstallProgressGTK(InstallProgress):
    def __init__(self,  widget):
        #apt.progress.InstallProgress.__init__(self)
        InstallProgress.__init__(self)
        self.last = 0.0        
        self.widget = widget
        
#    def processing(self, pkg, stage):
#	message = "Installing " + pkg 
#        self.widget.pkg_label.set_text(message)
     #   apt.base.InstallProgress.processing(pkg, stage)
        
    def statusChange(self, pkg, percent, status):
        InstallProgress.statusChange(self,  pkg,  percent,  status)
	message = "Installing " + pkg 
        
        progress_value = float(float(percent) / float(100))
        
        self.widget.progress_bar.set_fraction(progress_value)
        self.widget.progress_bar.set_text(message)
#        self.widget.pkg_label.set_text(message)
#        percent_msg = str(percent) + "%"
#        self.widget.progress_bar.set_text(percent_msg)

    def updateInterface(self):
        InstallProgress.updateInterface(self)

        if self.last >= self.percent:
            return
        progress_value = float(float(self.percent) / float(100))
        
        #self.widget.progress_bar.set_fraction(progress_value)
        #self.widget.pkg_label.set_text(self.status)

        self.last = self.percent        
        
    def conffile(self, current, new):
        print "conffile prompt: %s %s" % (current, new)

    def error(self, errorstr):
        print "got dpkg error: '%s'" % errorstr
