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
import string

version="__VERSION__"
daemon = True
debug = False
name = "thinfilter"
timeout = 8
uid=None
devel=False

DAEMON_LOG_FILE = "/var/log/thinfilter.log"
DAEMON_PID_FILE = "/var/run/thinfilter.pid"
DBNAME = "/var/lib/thinfilter/database.db"
BASE="/usr/share/thinfilter/webpanel/"
VAR="/var/lib/thinfilter/"
SESSIONS_DIR=VAR+"sessions"

#if os.path.isdir("/.dirs/dev/thinfilter"):
#    DAEMON_LOG_FILE = "/.dirs/dev/thinfilter/thinfilter.log"
#    DAEMON_PID_FILE = "/.dirs/dev/thinfilter/thinfilter.pid"
#    DBNAME = "/.dirs/dev/thinfilter/thinfilter.db"


# set BASE in git sources dir to debug
#if os.path.abspath(os.curdir) == "/home/mario/thinetic/git/thinfilter":
#    BASE="/home/mario/thinetic/git/thinfilter/webpanel/"
#    DAEMON_LOG_FILE = "/home/mario/thinetic/git/thinfilter/thinfilter.log"
#    DAEMON_PID_FILE = "/home/mario/thinetic/git/thinfilter/thinfilter.pid"
#    DBNAME = "/home/mario/thinetic/git/thinfilter/thinfilter.db"
#    SESSIONS_DIR="/home/mario/thinetic/git/thinfilter/webpanel/sessions"

if os.path.abspath(os.curdir) == "/mnt/thinetic/git/thinfilter":
    BASE="/mnt/thinetic/git/thinfilter/webpanel/"
#    DAEMON_LOG_FILE = "/mnt/thinetic/git/thinfilter/thinfilter.log"
#    DAEMON_PID_FILE = "/mnt/thinetic/git/thinfilter/thinfilter.pid"
#    DBNAME = "/mnt/thinetic/git/thinfilter/thinfilter.db"
#    SESSIONS_DIR="/mnt/thinetic/git/thinfilter/webpanel/sessions"



IMAGE_EXTENSIONS=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'ppm', 'pcx', 'tiff']
ALLOWED_CHARS=string.letters + string.digits + '-_.'
HIDDEN_INTERFACES=['lo', 'wmaster0', 'pan0', 'vboxnet0']
SERVER_PORT=16895

stop = False


thread_verbose = False
urls=[]
roles=[]
menus=[]
buttons=[]

#print "D: thinblue.config loaded"
