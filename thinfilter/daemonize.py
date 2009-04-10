# -*- coding: UTF-8 -*-
##########################################################################
# ThinFilter writen by MarioDebian <mario.izquierdo@thinetic.es>
#
#    ThinFilter
#
# Copyright (c) 2009 Mario Izquierdo <mario.izquierdo@thinetic.es>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
###########################################################################

import os
import sys
import time
import thinfilter.config
import thinfilter.logger

def daemonize():
    #print "daemonize..."
    # do the UNIX double-fork magic, see Stevens' "Advanced
    # Programming in the UNIX Environment" for details (ISBN 0201563177)
    try:
        pid = os.fork()
        if pid > 0:
            # exit first parent
            sys.exit(0)
    except OSError, e:
        print >> sys.stderr, "fork #1 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)

    # decouple from parent environment
    os.chdir("/")
    os.setsid()
    os.umask(0)
    #print "decouple..."

    # do second fork
    try:
        pid = os.fork()
        if pid > 0:
            # exit from second parent, print eventual PID before
            file(thinfilter.config.DAEMON_PID_FILE, 'w').write('%d'%pid)
            sys.exit(0)
    except OSError, e:
        print >> sys.stderr, "fork #2 failed: %d (%s)" % (e.errno, e.strerror)
        sys.exit(1)


def killall(proc_name):
    os.system("killall %s"%proc_name)    


def start_server():
    #lock for pid
    if os.path.isfile(thinfilter.config.DAEMON_PID_FILE):
        # read PID
        old_pid = open(thinfilter.config.DAEMON_PID_FILE, 'r').read()
        if os.path.isdir("/proc/%d" %int(old_pid)):
            print "daemon already running at PID=%d..." % int(old_pid)
            sys.exit(1)
        else:
            os.remove(thinfilter.config.DAEMON_PID_FILE)
    else:
        daemonize()

def stop_server(proc_name, ignore = False, wait = False):
    if not os.path.exists(thinfilter.config.DAEMON_PID_FILE):
        killall(proc_name)
        if ignore: return
        sys.exit(1)
        
    pid = open(thinfilter.config.DAEMON_PID_FILE, 'r').read().strip()
    os.popen('kill -15 %d' % int(pid))
    os.remove(thinfilter.config.DAEMON_PID_FILE)
    if wait:
        print("waiting for pid %s"%pid)
        while os.path.isdir("/proc/%s"%pid):
            time.sleep(0.5)

def status():
    if not os.path.exists(thinfilter.config.DAEMON_PID_FILE):
        # daemon not running
        sys.exit(1)
    pid = open(thinfilter.config.DAEMON_PID_FILE, 'r').read()
    # if proccess is running will have a /proc/XXX dir
    if os.path.isdir("/proc/%d" %int(pid)):
        sys.exit(0)
    

