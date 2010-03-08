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
daemon = False
debug = False
name = "thinfilter"
timeout = 8
uid=None
devel=False
demo=False
ssl=False
#seconds (10 minutes)
sessiontimeout=600

DAEMON_LOG_FILE = "/var/log/thinfilter.log"
DAEMON_PID_FILE = "/var/run/thinfilter.pid"
DBNAME = "/var/lib/thinfilter/database.db"
BASE="/usr/share/thinfilter/webpanel/"
VAR="/var/lib/thinfilter/"

SESSIONS_DIR=VAR+"sessions"
SQUIDGUARD_PATH=VAR+"/squidGuard/db/"
SQUIDGUARD_CONF="/etc/squid3/squidGuard.conf"
SQUIDGUARD_FILES=['domains', 'urls', 'expressions']
SQUIDGUARD_EDIT_RULES=['lista-blanca', 'lista-negra']

OPENVPN_DIR="/etc/openvpn"

# set BASE in git sources dir to debug
if os.path.isfile('debian/thinfilter.install'):
    BASE=os.path.abspath('./') + "/webpanel/"
    DAEMON_LOG_FILE = os.path.abspath('./') + "/thinfilter.log"
    DAEMON_PID_FILE = os.path.abspath('./') + "/thinfilter.pid"
    DBNAME = os.path.abspath('./') + "/thinfilter.db"
    SESSIONS_DIR=os.path.abspath('./') + "/webpanel/sessions"
    #SQUIDGUARD_PATH=os.path.abspath('./') +"/squidGuard/db/"
    #SQUIDGUARD_CONF=os.path.abspath('./') + "/squid3/squidGuard.conf.demo"


IMAGE_EXTENSIONS=['png', 'jpg', 'jpeg', 'gif', 'bmp', 'ppm', 'pcx', 'tiff']
ALLOWED_CHARS=string.letters + string.digits + '-_.'
HIDDEN_INTERFACES=['lo', 'wmaster0', 'pan0', 'vboxnet0']

SERVER_PORT=16895
WEB_PORT=9090
WEB_IP="10.0.0.1"
FORCE_IP=""

stop = False


thread_verbose = False
urls=[]
roles=[]
menus=[]
buttons=[]
role_desc=[]
users={}

#print "D: thinblue.config loaded"
