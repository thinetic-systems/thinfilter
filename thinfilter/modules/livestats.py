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
# live stats
#

import sys
import os
import time
import netifaces
from glob import glob

sys.path.append('/home/mario/thinetic/git/thinfilter')
sys.path.append('/mnt/thinetic/git/thinfilter')

import thinfilter.logger as lg
import thinfilter.config

import thinfilter.common
import web
render = web.template.render(thinfilter.config.BASE + 'templates/')


class CPU(object):
    def __init__(self):
        self.interval = 1

    def getTimeList(self, ):
        statFile = file("/proc/stat", "r")
        timeList = statFile.readline().split(" ")[2:6]
        statFile.close()
        for i in range(len(timeList)) :
            timeList[i] = int(timeList[i])
        return timeList

    def deltaTime(self, interval) :
        x = self.getTimeList()
        time.sleep(interval)
        y = self.getTimeList()
        for i in range(len(x)) :
            y[i] -= x[i]
        return y

    def get(self):
        dt = self.deltaTime(self.interval)
        cpuPct = 100 - (dt[len(dt) - 1] * 100.00 / sum(dt))
        return str('%.2f' %cpuPct)


class NET(object):
    def __init__(self, iface):
        self.iface=iface
    
    def get(self):
        # read /sys/class/net/IFACE/statistics/[rt]x_bytes
        rx=open("/sys/class/net/%s/statistics/rx_bytes"%self.iface, 'r').read().strip()
        tx=open("/sys/class/net/%s/statistics/tx_bytes"%self.iface, 'r').read().strip()
        return "%s|%s|%s"%(time.time(), rx, tx)

class stats_svg:
    #@thinfilter.common.islogged
    def GET(self, sfile, extension):
        action="%s%s"%(sfile, extension)
        #lg.debug("stats_svg::GET() action=%s" %(action), __name__)
        if action == "cpu.svg":
            web.header("Content-type", "image/svg+xml")
            return render.cpu_svg()
        elif action == "cpu.update":
            cpu=CPU()
            return ( cpu.get() )
        ############################################
        elif sfile == "net.update":
            net=NET( extension.replace('.','') )
            return ( net.get() )
        elif sfile == "net.svg":
            web.header("Content-type", "image/svg+xml")
            return render.net_svg(extension.replace('.',''))



class DISK(object):
    def __init__(self):
        self.hdd=self.__search_all__()

    def __get_mnt__(self, dev, column):
        # read /proc/mounts
        f=open("/proc/mounts", 'r')
        data=f.readlines()
        f.close()
        for line in data:
            if line.startswith("/dev/%s "%dev):
                return line.split()[column]


    def __dev_info__(self, dev):
        data={}
        bevorbose=False
        out=thinfilter.common.run("/bin/df /dev/%s"%dev, verbose=bevorbose, _from=__name__)
        for line in out:
            if line.startswith("/dev/%s "%(dev)):
                data['used']=int(line.split()[2])
                data['free']=int(line.split()[3])
                data['size']=int(line.split()[1])
                data['mnt']=self.__get_mnt__(dev, 1)
                data['type']=self.__get_mnt__(dev, 2)
        return data

    def __search_all__(self):
        devs={}
        # read /proc/partitions
        f=open("/proc/partitions", 'r')
        data=f.readlines()
        f.close()
        for line in data:
            if "major" in line: continue
            if line.strip() == '': continue
            
            # dev is column 4
            _dev=line.split()
            data=self.__dev_info__(_dev[3])
            #lg.debug("DISK::__search_all__ dev=%s data=%s" %(line.split()[3], data), __name__)
            if len(data) > 0:
                devs[_dev[3]]=data
        
        return devs

class livestats:
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('livestats.livestats')
    @thinfilter.common.layout(body='', title='Estadísticas de red en vivo')
    def GET(self):
        ifaces=[]
        for dev in netifaces.interfaces():
            if not dev in thinfilter.config.HIDDEN_INTERFACES:
                ifaces.append(dev)
        hdd=DISK().hdd
        return render.livestats( ifaces, hdd )


def init():
    # nothing to check
    lg.debug("livestats::init()", __name__)
    
    thinfilter.common.register_url('/livestats', 'thinfilter.modules.livestats.livestats')
    thinfilter.common.register_url('/livestats/(.+?)(?:(\.[^.]*$)|$)$', 'thinfilter.modules.livestats.stats_svg')

    menu=thinfilter.common.Menu("/livestats", "Estado", order=15, role='livestats.livestats')
    thinfilter.common.register_menu(menu)

if __name__ == "__main__":
    thinfilter.config.debug=True
    thinfilter.config.daemon=False
    app=DISK()
    print app.hdd
