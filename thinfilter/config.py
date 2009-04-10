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


daemon = True
debug = False
name = "thinfilter"
timeout = 8
uid=None


DAEMON_LOG_FILE = "/var/log/thinfilter.log"
DAEMON_PID_FILE = "/var/run/thinfilter.pid"
DBNAME = "/var/lib/thinfilter/database.db"
BASE="/usr/share/thinfilter/webpanel/"
SESSIONS_DIR="/var/lib/thinfilter/sessions"

if os.path.isdir("/.dirs/dev/thinfilter"):
    DAEMON_LOG_FILE = "/.dirs/dev/thinblue/thinfilter.log"
    DAEMON_PID_FILE = "/.dirs/dev/thinblue/thinfilter.pid"
    DBNAME = "/.dirs/dev/thinblue/thinfilter.db"


# set BASE in git sources dir to debug
if os.path.abspath(os.curdir) == "/home/mario/thinetic/dansguardian":
    BASE="/home/mario/thinetic/dansguardian/webpanel/"
    DAEMON_LOG_FILE = "/home/mario/thinetic/dansguardian/thinfilter.log"
    DAEMON_PID_FILE = "/home/mario/thinetic/dansguardian/thinfilter.pid"
    DBNAME = "/home/mario/thinetic/dansguardian/thinfilter.db"
    SESSIONS_DIR="/home/mario/thinetic/dansguardian/webpanel/sessions"



IMAGE_EXTENSIONS=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'ppm', 'pcx', 'tiff']
ALLOWED_CHARS=string.letters + string.digits + '-_.'

stop = False


thread_verbose = False

#print "D: thinblue.config loaded"
