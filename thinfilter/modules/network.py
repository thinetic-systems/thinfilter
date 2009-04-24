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
import netifaces
import urllib


import thinfilter.logger as lg
import thinfilter.config

import thinfilter.common
import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

HIDDEN_INTERFACES=['lo', 'wmaster0']

class Interfaces(object):
    def __init__(self, **kwargs):
        self.__GetAllNetworkInterfaces__()

    def get_ip_address(self, ifname):
        lg.debug("get_ip_address() ifname=%s" %(ifname) , __name__)
        if not ifname in netifaces.interfaces():
            return None
        ip=netifaces.ifaddresses(ifname)
        if ip.has_key(netifaces.AF_INET):
            return ip[netifaces.AF_INET][0]['addr']
        return None

    def __getLink__(self, iface):
        try:
            f=open("/sys/class/net/%s/carrier"%iface, 'r')
        except:
            lg.error("Can't read /sys/class/net/%s/carrier"%iface, __name__)
            return False
        try:
            link=f.readline().strip()
        except:
            lg.error("Can't read /sys/class/net/%s/carrier"%iface, __name__)
            link=0
        f.close()
        if link == "1":
            return True
        else:
            return False

    def __getGateway__(self, iface):
        data=[]
        try:
            f=open("/proc/net/route", 'r')
        except:
            lg.error("/proc/net/route is not readable", __name__)
            return None
        for l in f.readlines():
            if l.startswith(iface):
                tmp=l.strip().split()
                if tmp[1] == "00000000":
                    data.append(self.__hex2dec__(tmp[2]))
                    break
        f.close()
        if len(data) < 1:
            lg.warning("WARNING: iface='%s' no gateway"%iface, __name__)
            return None
        else:
            return data[0]

    def __hex2dec__(self, s):
        out=[]
        for i in range(len(s)/2):
            out.append( str(int(s[i*2:(i*2)+2],16)) )
        # data in /proc/net/route is reversed
        out.reverse()
        return ".".join(out)

    def __GetAllNetworkInterfaces__(self):
        self.allnetworkinterfaces=[]
        for dev in netifaces.interfaces():
            if not dev in HIDDEN_INTERFACES:
                ip=netifaces.ifaddresses(dev)
                if ip.has_key(netifaces.AF_INET):
                    data=ip[netifaces.AF_INET][0]
                    data['iface']=dev
                    data['gateway']=self.__getGateway__(dev)
                    if not data['gateway']:
                        data['readonly']="readonly"
                    else:
                        data['readonly']=""
                    data['link']=self.__getLink__(dev)
                    self.allnetworkinterfaces.append(data)
        lg.debug ( "GetAllNetworkInterfaces() %s" %( self.allnetworkinterfaces ), __name__ )
        return self.allnetworkinterfaces

    def get(self):
        return self.allnetworkinterfaces

class network(object):
    @thinfilter.common.islogged
    @thinfilter.common.layout(body='', title='Configuración Red')
    def GET(self, options=None):
        lg.debug("network::GET() options=%s" %options)
        ifaces=Interfaces().get()
        return render.settings_net(ifaces, action='Guardar')

    @thinfilter.common.islogged
    def POST(self):
        ifaces=Interfaces().get()
        formdata=web.input()
        lg.debug("formdata=%s"%formdata, __name__)
        for i in range(len(ifaces)):
            iface=ifaces[i]['iface']
        #FIXME not finished
#        netdata=web.input()
#        lg.debug(netdata)
#        _debug = userdata.debug
#        _timeout = userdata.timeout
#        _concurrent = userdata.concurrent
#        lg.debug("debug=%s  timeout=%s  concurrent=%s"%(_debug, _timeout, _concurrent) )
#        try:
#            # set stop=2 to reload conf from daemon
#            #db.query("UPDATE config set debug='%s', timeout='%s', concurrent='%s', stop='2'" %(_debug, _timeout, _concurrent))
#        except Exception, err:
#            lg.error("Exception save config, error=%s"%err)
#            traceback.print_exc(file=sys.stderr)
        return web.seeother('/network')


class DnsMasq(object):
    def __init__(self):
        self.conf="/etc/dnsmasq.conf"
        f=open(self.conf, 'r')
        self.listen_address=""
        self.dhcp_range=""
        self.dhcp_option=""
        self.dns=""
        self.dnsfile=""
        self.rawdata=[]
        for _line in f.readlines():
            self.rawdata.append(_line)
            line=_line.strip()
            if not line == "" and not line.startswith("#"):
                lg.debug("DnsMasq() append line '%s'"%line)
                if line.startswith("listen-address="):
                    self.listen_address=line.split('=')[1]
                elif line.startswith("dhcp-range="):
                    self.dhcp_range=line.split('=')[1]
                elif line.startswith("dhcp-option="):
                    self.dhcp_option=line.split('=')[1]
                elif line.startswith("resolv-file="):
                    self.dnsfile=line.split('=')[1]
                    self.dns=",".join(self.__read_dns__())

    def __read_dns__(self):
        #resolv-file=/etc/resolv.conf.primary
        f=open(self.dnsfile, 'r')
        dns=[]
        for line in f.readlines():
            if line.startswith("nameserver"):
                dns.append(line.strip().split()[1])
        return dns

    def get(self):
        return {#'listen-address':self.listen_address, 
                'dhcp-range': self.dhcp_range,
                #'dhcp-option': self.dhcp_option,
                'dns': self.dns
                }
        
    def save(self, data):
        f=open(self.conf, 'w')
        for line in self.rawdata:
            if line.startswith("dhcp-range="):
                f.write("dhcp-range=%s\n"%(data['dhcp-range']) )
            #elif line.startswith("listen-address="):
            #    f.write("listen-address=%s\n"%(data['listen-address']) )
            #elif line.startswith("dhcp-option="):
            #    f.write("dhcp-option=%s\n"%(data['dhcp-option']) )
            else:
                f.write(line)
        f.close()
        # save DNS resolv-file=/etc/resolv.conf.primary
        f=open(self.dnsfile, 'w')
        for dns in self.dns.strip().split(','):
            f.write("nameserver %s\n" %(dns) )
        f.close()
        # save /etc/resolv.conf
        f=open("/etc/resolv.conf", 'w')
        f.write("nameserver 10.0.0.1\n")
        for dns in self.dns.strip().split(','):
            f.write("nameserver %s\n" %(dns) )
        f.close()
        # restart dnsmasq
        os.system("/usr/sbin/invoke-rc.d dnsmasq restart")
        
class dhcp(object):
    @thinfilter.common.islogged
    @thinfilter.common.layout(body='', title='Configuración DHCP')
    def GET(self, options=None):
        lg.debug("dhcp::GET() options=%s" %options)
        data=DnsMasq().get()
        lg.debug("dhcp::GET() dnsmasq=%s" %data)
        return render.settings_dhcp(data, action='Guardar')

    @thinfilter.common.islogged
    def POST(self):
        dnsmasq=DnsMasq()
        data=dnsmasq.get()
        formdata=web.input()
        lg.debug("dhcp()::formdata=%s"%formdata, __name__)
        for param in data:
            lg.debug("dhcp::POST() param=%s old=%s"%(param, data[param]) )
            lg.debug("dhcp::POST() param=%s new=%s"%(param, getattr(formdata, param.replace('_','-')) ) )
            data[param]=getattr(formdata, param.replace('_','-'))
        lg.debug("dhcp::POST() data=%s"%data)
        dnsmasq.save(data)
        return web.seeother('/network/dhcp')

class netStats(object):
    def __init__(self):
        self.ifaces=[]
        for dev in Interfaces().get():
            if not dev['iface'] in HIDDEN_INTERFACES:
                tx_and_rx=self.__get_data__(dev)
                self.ifaces.append(tx_and_rx)

    def __get_data__(self, _dev):
        data={'iface':_dev['iface'], 'link':_dev['link'], 'gateway':_dev['gateway'], 'tx':0, 'rx':0}
        dev=_dev['iface']
        f=open("/proc/net/dev", 'r')
        for line in f.readlines():
            if "%s:"%dev in line:
                tx=int(line.split()[8]) or 0
                rx=line.split()[0].replace("%s:"%dev, "")
                if rx == "":
                    rx=int(line.split()[1])
                data['tx']="%.2f MiB" %( float(tx)/(1024*1024) )
                data['rx']="%.2f MiB" %( float(rx)/(1024*1024) )
                return data

    def get(self):
        return self.ifaces




class extraStats(object):
    def __init__(self):
        raw=open("/proc/uptime", 'r').readline()
        self.uptime=self.fractSec(float(raw.split()[0]))
        self.public_ip=self.__get_public_ip__()

    def fractSec(self, s):
        years, s = divmod(s, 31556952)
        _min, s = divmod(s, 60)
        h, _min = divmod(_min, 60)
        d, h = divmod(h, 24)
        txtdate=""
        if int(years) > 0:
            txtdate+="%s años, "%int(years)
        txtdate+="%s días %s horas %s minutos %s segundos" %( int(d), int(h), int(_min), int(s))
        return txtdate

    def __get_public_ip__(self):
        try:
            raw = urllib.urlopen("http://dynupdate.no-ip.com/ip.php", proxies={})
            public_ip=raw.readline().strip()
            raw.close()
            return public_ip
        except:
            return "[no disponible]"
        

    def get(self):
        return [self.uptime, self.public_ip]

class netstats(object):
    @thinfilter.common.islogged
    @thinfilter.common.layout(body='', title='Estadísticas de red')
    def GET(self, options=None):
        data=netStats().get()
        extra=extraStats().get()
        lg.debug("netstats::GET() dnsmasq=%s" %data)
        lg.debug("netstats::GET() extra=%s" %extra)
        return render.net_stats(data, extra)

    @thinfilter.common.islogged
    def POST(self):
        return web.seeother('/network/stats')




def init():
    # nothing to check
    lg.debug("network::init()", __name__)
    """
        '/network', 'network',
        '/network/dhcp', 'dhcp',
        '/network/stats', 'netstats',
    """
    thinfilter.common.register_url('/network',      'thinfilter.modules.network.network')
    thinfilter.common.register_url('/network/dhcp',  'thinfilter.modules.network.dhcp')
    thinfilter.common.register_url('/network/stats', 'thinfilter.modules.network.netstats')




if __name__ == "__main__":
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
    
    print extraStats().get()
