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
GRAPH_PATH=os.path.join( thinfilter.config.VAR, "graphs")

import thinfilter.logger as log


class CPU(object):
    def __init__(self):
        self.fname="%s/cpu"%(GRAPH_PATH)
        if not os.path.isfile(self.fname + ".rrd"):
            self.create()

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
        log.info( "CPU create (%s)"%self.fname, __name__ )
#/usr/bin/rrdtool create /www/htdocs/rrd/logs/localhost_stats/cpu.rrd \
#    --step 300 \
#    DS:user:COUNTER:600:0:U \
#    DS:system:COUNTER:600:0:U \
#    DS:nice:COUNTER:600:0:U \
#    DS:idle:COUNTER:600:0:U \
#    DS:iowait:COUNTER:600:0:U \
#    RRA:AVERAGE:0.5:1:800 \
#    RRA:AVERAGE:0.5:6:800 \
#    RRA:AVERAGE:0.5:24:800 \
#    RRA:AVERAGE:0.5:288:800 \
#    RRA:MAX:0.5:1:800 \
#    RRA:MAX:0.5:6:800 \
#    RRA:MAX:0.5:24:800 \
#    RRA:MAX:0.5:288:800


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
        log.info( "CPU update (%s) ===> (N:%s:%s:%s:%s:%s:%s)"%(self.fname, load1, load5, load15, user, nice, system), __name__ )

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
                      "-t Uso de CPU por día",
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
                      "AREA:reluser#FF0000:CPU usuario",
                      "STACK:relnice#00AAFF:CPU nice",
                      "STACK:relsys#FFFF00:CPU sistema",
                      "STACK:idle#00FF00:CPU ocioso",
                      "COMMENT:	\\j",
                      "COMMENT:	",
                      "LINE1:load1#000FFF:Carga media 1 min",
                      "LINE2:load5#000888:Carga media 5 min",
                      "LINE3:load15#000000:Carga media 15 min",
                      "COMMENT:	\\j",
                      "COMMENT:	\\j",
                      "COMMENT:\\j",
                      #"COMMENT:	",
                      "GPRINT:load15:MIN:Carga en 15 min mínimo\: %lf",
                      "GPRINT:load15:MAX:Carga en 15 min máximo\: %lf",
                      "GPRINT:load15:AVERAGE:Carga en 15 min media\: %lf",
                      "COMMENT:	\\j",
                      "COMMENT:	",
                      "GPRINT:cpu:MIN:Uso de CPU mínimo\: %lf%%",
                      "GPRINT:cpu:MAX:Uso de CPU máximo\: %lf%%",
                      "GPRINT:cpu:AVERAGE:Uso de CPU media\: %lf%%",
                      "COMMENT:	\\j")
        log.info("updated %s.png"%self.fname, __name__)


################################################################################


class Net(object):
    def __init__(self, iface="eth0"):
        self.iface=iface
        secure_iface=iface.replace(':', '_')
        self.fname="%s/%s"%(GRAPH_PATH, secure_iface)
        if not os.path.isfile(self.fname + ".rrd"):
            self.create()
        
    def create(self):
        rrdtool.create("%s.rrd"%self.fname,
                "--step=300",
                "DS:incoming:DERIVE:600:0:12500000",
                "DS:outgoing:DERIVE:600:0:12500000",
                "RRA:AVERAGE:0.5:1:576",
                "RRA:AVERAGE:0.5:6:672",
                "RRA:AVERAGE:0.5:24:732",
                "RRA:AVERAGE:0.5:144:1460")
        log.info( "CPU create (%s)"%self.fname, __name__ )

#/usr/bin/rrdtool create /www/htdocs/rrd/logs/localhost_stats/eth0.rrd \
#    --step 300 \
#    DS:in:COUNTER:600:0:1250000 \
#    DS:out:COUNTER:600:0:1250000 \
#    RRA:AVERAGE:0.5:1:800 \
#    RRA:AVERAGE:0.5:6:800 \
#    RRA:AVERAGE:0.5:24:800 \
#    RRA:AVERAGE:0.5:288:800 \
#    RRA:MAX:0.5:1:800 \
#    RRA:MAX:0.5:6:800 \
#    RRA:MAX:0.5:24:800 \
#    RRA:MAX:0.5:288:800



    def update(self):
        if not os.path.isfile("%s.rrd"%self.fname):
            self.create()
        data={}
        f=open("/proc/net/dev", 'r')
        for line in f.readlines():
            if "%s:"%self.iface in line:
                #if "%s: " in line.split()[0]:
                if len(line.split()) == 17:
                    tx=int(line.split()[9])
                    rx=int(line.split()[1])
                    #print "tx at 9"
                else:
                    tx=int(line.split()[8])
                    rx=line.split()[0].replace("%s:"%self.iface, "")
                
                f.close()
                rrdtool.update("%s.rrd"%self.fname,
                        "-t", "incoming:outgoing", 
                        "N:%s:%s"%(rx, tx)
                    )
                log.info( "NET update (%s)===> (N:%s:%s)"%(self.fname, rx, tx), __name__ )
                return

#/usr/bin/rrdtool update \
#    /www/htdocs/rrd/logs/localhost_stats/eth0.rrd \
#    --template \
#    in:out \
#    N:$output


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
                    "-t Tráfico en interfaz %s (diario)"%self.iface,
                    "-v KB por seg",
                    "DEF:in=%s.rrd:incoming:AVERAGE"%self.fname,
                    "DEF:out=%s.rrd:outgoing:AVERAGE"%self.fname,
                    "CDEF:out_neg=out,-1,*",
                    "AREA:in#11EE11:Descarga",
                    "LINE1:in#009900",
                    "GPRINT:in:MAX:Max\: %3.2lf %SB/s",
                    "GPRINT:in:AVERAGE:Media\: %3.2lf %SB/s",
                    "GPRINT:in:LAST:Actual\: %3.2lf %SB/s\\j",
                    "AREA:out_neg#0000FF:Subida ",
                    "LINE1:out_neg#000088",
                    "GPRINT:out:MAX:Max\: %3.2lf %SB/s",
                    "GPRINT:out:AVERAGE:Media\: %3.2lf %SB/s",
                    "GPRINT:out:LAST:Actual\: %3.2lf %SB/s",
                    "HRULE:0#000000")
        log.info( "updated %s.png"%self.fname, __name__ )

#Graph[eth0]:
#    --rigid
#    --base=1000
#    --alt-autoscale-max
#    -v "Bytes Per Second"
#    DEF:a=eth0.rrd:in:AVERAGE
#    DEF:b=eth0.rrd:out:AVERAGE
#    CDEF:cdefe=b,-1,*
#    AREA:a#eacc00:Inbound
#    GPRINT:a:LAST:" Cur\:%8.2lf %s"
#    GPRINT:a:AVERAGE:"Ave\:%8.2lf %s"
#    GPRINT:a:MAX:"Max\:%8.2lf %s\n"
#    LINE1:a#000001:
#    AREA:cdefe#da4725:Outbound
#    GPRINT:b:LAST:"Cur\:%8.2lf %s"
#    GPRINT:b:AVERAGE:"Ave\:%8.2lf %s"
#    GPRINT:b:MAX:"Max\:%8.2lf %s\n"
#    LINE1:cdefe#000001:
#    HRULE:0#000000



