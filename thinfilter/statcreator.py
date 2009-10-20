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

#
# network stuff
#

import os
import sys
import rrdtool
import time
import random
import netifaces


import thinfilter.config
GRAPH_PATH=os.path.join( thinfilter.config.BASE, "graphs")

import thinfilter.logger as log


class CPU(object):
    def __init__(self):
        self.fname="%s/cpu"%(GRAPH_PATH)

    def create(self):
        rrdtool.create("%s.rrd"%(self.fname),
                "--step=300",
                "DS:load1:GAUGE:180:0:U",
                "DS:load5:GAUGE:180:0:U",
                "DS:load15:GAUGE:180:0:U",
                "DS:user:GAUGE:180:0:100",
                "DS:nice:GAUGE:180:0:100",
                "DS:system:GAUGE:180:0:100",
                "RRA:AVERAGE:0.5:1:1440",
                "RRA:AVERAGE:0.5:1440:1",
                "RRA:MIN:0.5:1440:1",
                "RRA:MAX:0.5:1440:1")


    def update(self):
        if not os.path.isfile("%s.rrd"%self.fname):
            self.create()
        # open /proc/loadavg
        f=open("/proc/loadavg", 'r')
        line=f.readline()
        f.close()
        (load1, load5, load15, nop1, nop2)=line.split()
        
        # open /proc/stat ans proccess it
        f=open("/proc/stat", 'r')
        for line in f.readlines():
            if line.startswith("cpu "):
                #cpu  2527278 23868 2818517 28868419 634076 128825 70912 0 0
                (cpu, user, nice, system, iddle, iowait, irq, softirq, tmp1, tmp2)=line.split()
        f.close()
        
        rrdtool.update("%s.rrd"%self.fname,
                       "-t", "load1:load5:load15:user:nice:system",
                       "N:%s:%s:%s:%s:%s:%s"%(load1, load5, load15, user, nice, system)
                    )
        log.info( "CPU update ===> (N:%s:%s:%s:%s:%s:%s)"%(load1, load5, load15, user, nice, system), __name__ )

    def graph(self):
        rrdtool.graph("%s.png"%self.fname,
                      #"--start", "day", 
                      "--imgformat", "PNG",
                      "--width", "700", "--height", "300",
                      "--start", "-1day",
                      "--end", "-1",
                      #"-aPNG", "-i", "-z",
                      #"--alt-y-grip", "-w 600", "-h 100", "-l 0",
                      #"-u 100", "-r",
                      "--color", "SHADEA#EAE9EE",
                      "--color", "SHADEB#EAE9EE",
                      "--color", "BACK#EAE9EE",
                      "-t cpu usage per day",
                      "DEF:load1=%s.rrd:load1:AVERAGE"%self.fname,
                      "DEF:load5=%s.rrd:load5:AVERAGE"%self.fname,
                      "DEF:load15=%s.rrd:load15:AVERAGE"%self.fname,
                      "DEF:user=%s.rrd:user:AVERAGE"%self.fname,
                      "DEF:nice=%s.rrd:nice:AVERAGE"%self.fname,
                      "DEF:system=%s.rrd:system:AVERAGE"%self.fname,
                      ####################
                      "CDEF:cpu=user,nice,system,+,+", 
                      "CDEF:reluser=load15,user,100,/,*", 
                      "CDEF:relnice=load15,nice,100,/,*", 
                      "CDEF:relsys=load15,system,100,/,*",
                      "CDEF:idle=load15,100,cpu,-,100,/,*",
                      "HRULE:1#000000",
                      "COMMENT:	",
                      "AREA:reluser#FF0000:CPU user",
                      "STACK:relnice#00AAFF:CPU nice",
                      "STACK:relsys#FFFF00:CPU system",
                      "STACK:idle#00FF00:CPU idle",
                      "COMMENT:	\\j",
                      "COMMENT:	",
                      "LINE1:load1#000FFF:Load average 1 min",
                      "LINE2:load5#000888:Load average 5 min",
                      "LINE3:load15#000000:Load average 15 min",
                      "COMMENT:	\\j",
                      "COMMENT:	\\j",
                      "COMMENT:\\j",
                      #"COMMENT:	",
                      "GPRINT:load15:MIN:Load 15 min minimum\: %lf",
                      "GPRINT:load15:MAX:Load 15 min maximum\: %lf",
                      "GPRINT:load15:AVERAGE:Load 15 min average\: %lf",
                      "COMMENT:	\\j",
                      "COMMENT:	",
                      "GPRINT:cpu:MIN:CPU usage minimum\: %lf%%",
                      "GPRINT:cpu:MAX:CPU usage maximum\: %lf%%",
                      "GPRINT:cpu:AVERAGE:CPU usage average\: %lf%%",
                      "COMMENT:	\\j")
        log.info("updated %s.png"%self.fname, __name__)
                    #### old
#                      "CDEF:total=user,system,idle,+,+",
#                      "CDEF:userpct=100,user,total,/,*",
#                      "CDEF:systempct=100,system,total,/,*",
#                      "CDEF:idlepct=100,idle,total,/,*",
#                      "AREA:userpct#0000FF:user cpu usage\\j",
#                      "STACK:systempct#FF0000:system cpu usage\\j",
#                      "STACK:idlepct#00FF00:idle cpu usage\\j",
#                      "GPRINT:userpct:MAX:maximal user cpu\\:%3.2lf%%",
#                      "GPRINT:userpct:AVERAGE:average user cpu\\:%3.2lf%%",
#                      "GPRINT:userpct:LAST:current user cpu\\:%3.2lf%%\\j",
#                      "GPRINT:systempct:MAX:maximal system cpu\\:%3.2lf%%",
#                      "GPRINT:systempct:AVERAGE:average system cpu\\:%3.2lf%%",
#                      "GPRINT:systempct:LAST:current system cpu\\:%3.2lf%%\\j",
#                      "GPRINT:idlepct:MAX:maximal idle cpu\\:%3.2lf%%",
#                      "GPRINT:idlepct:AVERAGE:average idle cpu\\:%3.2lf%%",
#                      "GPRINT:idlepct:LAST:current idle cpu\\:%3.2lf%%\\j"
#                    )
#                    /usr/bin/rrdtool graph /var/www/localhost/htdocs/stats/load.png \
#                    -Y -u 1.1 -l 0 -L 5 -v "Load" -w 700 -h 300 -t "Load & CPU stats - `/bin/date`" \
#                    -c ARROW\#000000 -x MINUTE:30:MINUTE:30:HOUR:1:0:%H \
#                    DEF:load1=/usr/share/rrdtool/load.rrd:load1:AVERAGE \
#                    DEF:load5=/usr/share/rrdtool/load.rrd:load5:AVERAGE \
#                    DEF:load15=/usr/share/rrdtool/load.rrd:load15:AVERAGE \
#                    DEF:user=/usr/share/rrdtool/load.rrd:cpuuser:AVERAGE \
#                    DEF:nice=/usr/share/rrdtool/load.rrd:cpunice:AVERAGE \
#                    DEF:sys=/usr/share/rrdtool/load.rrd:cpusystem:AVERAGE \
#                    CDEF:cpu=user,nice,sys,+,+ \
#                    CDEF:reluser=load15,user,100,/,* \
#                    CDEF:relnice=load15,nice,100,/,* \
#                    CDEF:relsys=load15,sys,100,/,* \
#                    CDEF:idle=load15,100,cpu,-,100,/,* \
#                    HRULE:1\#000000 \
#                    COMMENT:"	" \
#                    AREA:reluser\#FF0000:"CPU user" \
#                    STACK:relnice\#00AAFF:"CPU nice" \
#                    STACK:relsys\#FFFF00:"CPU system" \
#                    STACK:idle\#00FF00:"CPU idle" \
#                    COMMENT:"	\j" \
#                    COMMENT:"	" \
#                    LINE1:load1\#000FFF:"Load average 1 min" \
#                    LINE2:load5\#000888:"Load average 5 min" \
#                    LINE3:load15\#000000:"Load average 15 min" \
#                    COMMENT:"	\j" \
#                    COMMENT:"\j" \
#                    COMMENT:"	" \
#                    GPRINT:load15:MIN:"Load 15 min minimum\: %lf" \
#                    GPRINT:load15:MAX:"Load 15 min maximum\: %lf" \
#                    GPRINT:load15:AVERAGE:"Load 15 min average\: %lf" \
#                    COMMENT:"	\j" \
#                    COMMENT:"	" \
#                    GPRINT:cpu:MIN:"CPU usage minimum\: %lf%%" \
#                    GPRINT:cpu:MAX:"CPU usage maximum\: %lf%%" \
#                    GPRINT:cpu:AVERAGE:"CPU usage average\: %lf%%" \
#                    COMMENT:"	\j";
#                    #
#                    /usr/bin/rrdtool graph /var/www/localhost/htdocs/stats/cpu.png \
#                    -Y -r -u 100 -l 0 -L 5 -v "CPU usage" -w 700 -h 300 -t "Bifroest CPU stats - `/bin/date`" \
#                    -c ARROW\#000000 -x MINUTE:30:MINUTE:30:HOUR:1:0:%H \
#                    DEF:user=/usr/share/rrdtool/load.rrd:cpuuser:AVERAGE \
#                    DEF:nice=/usr/share/rrdtool/load.rrd:cpunice:AVERAGE \
#                    DEF:sys=/usr/share/rrdtool/load.rrd:cpusystem:AVERAGE \
#                    CDEF:idle=100,user,nice,sys,+,+,- \
#                    COMMENT:"	" \
#                    AREA:user\#FF0000:"CPU user" \
#                    STACK:nice\#000099:"CPU nice" \
#                    STACK:sys\#FFFF00:"CPU system" \
#                    STACK:idle\#00FF00:"CPU idle" \
#                    COMMENT:"	\j";;

class Net():
    def __init__(self, iface="eth0"):
        self.iface=iface
        self.fname="%s/%s"%(GRAPH_PATH, iface)
        
    def create(self):
        rrdtool.create("%s.rrd"%self.fname,
                "--step=300",
                "DS:incoming:DERIVE:600:0:12500000",
                "DS:outgoing:DERIVE:600:0:12500000",
                "RRA:AVERAGE:0.5:1:576",
                "RRA:AVERAGE:0.5:6:672",
                "RRA:AVERAGE:0.5:24:732",
                "RRA:AVERAGE:0.5:144:1460")

    def update(self):
        if not os.path.isfile("%s.rrd"%self.fname):
            self.create()
        data={}
        f=open("/proc/net/dev", 'r')
        for line in f.readlines():
            if "%s:"%self.iface in line:
                #print line.split()
                if "%s: " in line.split()[0]:
                    tx=int(line.split()[9])
                    #print "tx at 9"
                else:
                    tx=int(line.split()[8])
                    #print "tx at 8"
                rx=line.split()[0].replace("%s:"%self.iface, "")
                if rx == "":
                    rx=int(line.split()[1])
                data['tx']="%s" %( int(tx) )
                data['rx']="%s" %( int(rx) )
                f.close()
                rrdtool.update("%s.rrd"%self.fname,
                        "-t", "incoming:outgoing", 
                        "N:%s:%s"%(data['tx'], data['rx'])
                    )
                log.info( "NET update (%s)===> (N:%s:%s)"%(self.iface, data['tx'], data['rx']), __name__ )
                return

    def graph(self):
        rrdtool.graph("%s.png"%self.fname,
                    "--imgformat", "PNG",
                    "--width", "600", "--height", "100",
                    "--start", "-1day",
                    "--end", "-1",
                    "-i", "-z", "--alt-y-grid",
                    "--color", "SHADEA#EAE9EE",
                    "--color", "SHADEB#EAE9EE",
                    "--color", "BACK#EAE9EE",
                    "-t trafico en %s (diario)"%self.iface,
                    "-v KB por seg",
                    "DEF:in=%s.rrd:incoming:AVERAGE"%self.fname,
                    "DEF:out=%s.rrd:outgoing:AVERAGE"%self.fname,
                    "CDEF:out_neg=out,-1,*",
                    "AREA:in#11EE11:Descarga",
                    "LINE1:in#009900",
                    "GPRINT:in:MAX:Max\: %3.2lf %SB/s",
                    "GPRINT:in:AVERAGE:Media\: %3.2lf %SB/s",
                    "GPRINT:in:LAST:Actual\: %3.2lf %SB/s\\j",
                    "AREA:out_neg#0000FF:Subida  ",
                    "LINE1:out_neg#000088",
                    "GPRINT:out:MAX:Max\: %3.2lf %SB/s",
                    "GPRINT:out:AVERAGE:Media\: %3.2lf %SB/s",
                    "GPRINT:out:LAST:Actual\: %3.2lf %SB/s",
                    "HRULE:0#000000")
        log.info( "updated %s.png"%self.fname, __name__ )
#                    "LINE1:outgoing#0000FF:subida en bytes por seg\\j",
#                    "GPRINT:incoming:MAX:max in \\:%10.2lf %sBps",
#                    "GPRINT:incoming:AVERAGE:med in \\:%10.2lf %sBps",
#                    "GPRINT:incoming:LAST: cur in\\:%10.2lf %sBps\\j",
#                    "GPRINT:outgoing:MAX:max out\\:%10.2lf %sBps",
#                    "GPRINT:outgoing:AVERAGE: med out\\:%10.2lf %sBps",
#                    "GPRINT:outgoing:LAST: cur out\\:%10.2lf %sBps\\j"
#                    )




