#!/usr/bin/python

import apt
import sys
import thread
import gobject
from apt.progress import InstallProgress

# tried try/except for LMDE, running into a threading bug in 2.7.3rc?
#try:
#    from apt.progress import InstallProgress  # ImportError: cannot import name InstallProgress
#except ImportError:
#    from apt.progress.base import InstallProgress  # Fatal Python error: PyEval_RestoreThread: NULL tstate
#    from apt.progress.old import InstallProgress  # Fatal Python error: PyEval_RestoreThread: NULL tstate
#    from apt.progress.gtk2 import InstallProgress  # ImportError: cannot import name InstallProgress

from apt_installprogress_gtk import *

class TextInstallProgress(InstallProgress):
    def __init__(self):
        apt.progress.InstallProgress.__init__(self)
        self.last = 0.0

    def updateInterface(self):
        InstallProgress.updateInterface(self)
        if self.last >= self.percent:
            return
        sys.stdout.write("\r[%s] %s\n" %(self.percent, self.status))
        sys.stdout.flush()
        self.last = self.percent

    def conffile(self, current, new):
        print "conffile prompt: %s %s" % (current, new)

    def error(self, errorstr):
        print "got dpkg error: '%s'" % errorstr

class apt_pm:
    def __init__(self):
        self.cache = apt.Cache()
        
    def find_uninstalled(self,  package_list):
        packages_found = []
        packages_missing = []
                
        for package in package_list:
            try:
                pkg = self.cache[package]
                try:
                    if not pkg.is_installed:
                        packages_found.append(package)
                except:
                    if not pkg.installed:
                        packages_found.append(package)
            except KeyError:
                packages_missing.append(package)
            
            
        return [packages_found,  packages_missing]
    
    def mark_packages(self,  package_list):
        for package in package_list:
            pkg = self.cache[package]
            try:
                pkg.mark_install()
            except:
                pkg.markInstall()
            
    def list_packages(self):
        package_list = []
        try:
            for package in self.cache.get_changes():
                package_list.append(package)
        except:
            for package in self.cache.getChanges():
                package_list.append(package)

        return package_list
    
    def install(self,  win=None):
        fprogress = FetchProgressGTK(win)
        iprogress = InstallProgressGTK(win)
        win.installing = True

        if not iprogress :
            fprogress = TextFetchProgress()
            progress_widget = TextInstallProgress()

        res = self.cache.commit(fprogress, iprogress)
        win.installing = False

if __name__ == "__main__":
    a = apt_pm()
    packages = a.find_uninstalled(["wesnoth"])
    a.mark_packages(packages[0])
