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

from subprocess import Popen, PIPE, STDOUT

import thinfilter.logger as lg
import thinfilter.config

class link(object):
    def __init__(self, **kwargs):
        lg.debug("link: kwargs=%s" %(kwargs) , __name__)
        self.text=""
        self.link=""
        self.cssclass=""
        for _var in kwargs:
            setattr(self, _var, kwargs[_var])
        #lg.debug("link: text='%s'" %self.text, __name__)
        #lg.debug("link: link='%s'" %self.link, __name__)
        #lg.debug("link: cssclass='%s'" %self.cssclass, __name__)

class DataObj(object):
    def __init__(self, **kwargs):
        #lg.debug("DataObj: kwargs=%s" %(kwargs) , __name__)
        self.values=[]
        self.varname=""
        self.itype=""
        self.varname_disabled=""
        self.extra=link()
        for _var in kwargs:
            setattr(self, _var, kwargs[_var])



class rules(object):
    def __init__(self, **kwargs):
        lg.debug("rules::__init__() kwargs=%s"%kwargs, __name__)
        self.kwargs=kwargs
        self.fnames=[]
        self.init()

    def init(self):
        pass

    def _read(self, fname):
        if not os.path.isfile(fname):
            raise "rules:: filenotfound"
            return
        f=open(fname, 'r')
        for line in f.readlines():
            self.foreachline( line.replace('\n', ''), fname=fname )

    def foreachline(self, *args):
        raise "rules::foreachline not defined"

#    def printdata(self):
#        for v in self.vars['data']:
#            lg.debug("data: %s"%v)

    def printdata(self):
        for obj in dir(self):
            if "__" in obj: continue
            v=getattr(self, obj)
            if type(v) == type({}) or type(v) == type([]) or type(v) == type(""):
                lg.debug("printdata() self.%s=%s"%(obj,v) , __name__)

    def _pregetdata(self):
        pass

    def getdata(self):
        self._pregetdata()
        __data=[]
        for obj in dir(self):
            if "__" in obj: continue
            if obj in ['fnames', 'kwargs']: continue
            v=getattr(self, obj)
            if type(v) == type({}) or type(v) == type([]):
                lg.debug("obj=%s v=%s" %(obj, v), __name__)
                __data.append( self._reprdata(obj, v)  )
        return __data

    def _reprdata(self, obj, v):
        return DataObj(varname=obj, value=v, itype="")
###########################################################

class extensions(rules):
    def init(self):
        self.vars['data']['banned']=[]
        self.vars['data']['nobanned']=[]

    def foreachline(self, line):
        if line.strip() == "":
            # empty line
            pass
        elif line.startswith("."):
            self.vars['data']['banned'].append(line)
        elif line.startswith("#.") or line.startswith("# ."):
            self.vars['data']['nobanned'].append(line)

    def printdata(self):
        for v in self.vars['data']['banned']:
            lg.debug("banned: %s"%v, __name__)

        for v in self.vars['data']['nobanned']:
            lg.debug("NO banned: %s"%v, __name__)

###########################################################


class ips(rules):
    """
    Read and parse this files:
        dansguardian/lists/exceptioniplist
        dansguardian/lists/bannediplist
    """
    def init(self):
        self.fnames=["dansguardian/lists/exceptioniplist",
                     "dansguardian/lists/bannediplist"]
        self.exceptioniplist=[]
        self.bannediplist=[]
        
        for f in self.fnames:
            self._read(f)
    
    def foreachline(self, line, fname=None):
        if fname:
            fname=fname.split("/")[-1]
        
        if line.strip() == "":
            # empty line
            pass
        elif line[0].isdigit():
            getattr(self, fname).append( [line] )
    
    def _reprdata(self, obj, v):
        return DataObj(varname=obj, value=v, itype="multiselect")

###########################################################


class phraselist(rules):
    """
    Read and parse this files:
        dansguardian/lists/bannedphraselist
        dansguardian/lists/exceptionphraselist
        dansguardian/lists/weightedphraselist
    """
    def init(self):
        self.fnames=["dansguardian/lists/bannedphraselist",
                     "dansguardian/lists/exceptionphraselist",
                     "dansguardian/lists/weightedphraselist"]
        self.bannedphraselist=[]
        self.exceptionphraselist=[]
        self.weightedphraselist=[]
        
        for f in self.fnames:
            self._read(f)

    def foreachline(self, line, fname=None):
        if fname:
            fname=fname.split("/")[-1]
        
        if line.strip() == "":
            # empty line
            pass
        elif line.startswith(".Include"):
            a=line.split('<')[1].split('>')[0]
            getattr(self, fname).append( DataObj(varname=a, value=1, itype="checkbox") )
        elif line.startswith("#.Include"):
            a=line.split('<')[1].split('>')[0]
            getattr(self, fname).append( DataObj(varname=a, value=0, itype="checkbox") )

    def printdata(self):
        for v in self.bannedphraselist:
            lg.debug("bannedphraselist: %s"%v, __name__)

        for v in self.exceptionphraselist:
            lg.debug("exceptionphraselist: %s"%v, __name__)

        for v in self.weightedphraselist:
            lg.debug("weightedphraselist: %s"%v, __name__)
"""
dansguardian/lists/filtergroupslist


dansguardian/lists/logsitelist
dansguardian/lists/exceptionsitelist

dansguardian/lists/logregexpurllist
dansguardian/lists/contentregexplist
dansguardian/lists/bannedregexpurllist
dansguardian/lists/exceptionregexpurllist

dansguardian/lists/urlregexplist


dansguardian/lists/exceptionfileurllist
dansguardian/lists/greyurllist
dansguardian/lists/exceptionurllist
dansguardian/lists/logurllist

dansguardian/lists/bannedextensionlist
dansguardian/lists/exceptionextensionlist


dansguardian/lists/greysitelist
dansguardian/lists/bannedurllist
dansguardian/lists/bannedsitelist
dansguardian/lists/exceptionfilesitelist



dansguardian/lists/bannedmimetypelist
dansguardian/lists/exceptionmimetypelist

dansguardian/lists/pics

dansguardian/lists/headerregexplist
dansguardian/lists/bannedregexpheaderlist

"""


class squid(rules):
    """
    Read and parse this files:
        dansguardian/lists/exceptioniplist
        dansguardian/lists/bannediplist
    """
    def init(self):
        self.fnames=["/etc/squid3/squid.conf"]
        self.http_port=[]
        self.acl=[]
        self.http_access=[]
        
        
        for f in self.fnames:
            self._read(f)
    
    def foreachline(self, line, fname=None):
        if fname:
            fname=fname.split("/")[-1]
        
        if line.strip() == "":
            # empty line
            pass
        elif line.startswith("acl"):
            line=line.split('\t#')[0]
            self.acl.append(line)
        elif line.startswith("http_access"):
            line=line.split('\t#')[0]
            self.http_access.append(line)
        elif line.startswith("http_port"):
            line=line.split('\t#')[0]
            self.http_port.append(line)
        #else:
        #    lg.debug("foreachline() '%s'"%line, __name__)
    
    def _reprdata(self, obj, v):
        if obj == "http_port" and not "transparent" in v:
            lg.debug( dir(link(text="Set transparent")) , __name__)
            return DataObj(varname=obj, value=v, itype="raw", extra=link(text="Set transparent") )
        elif obj == "http_port" and "transparent" in v:
            lg.debug( dir(link(text="Set transparent")) , __name__)
            return DataObj(varname=obj, value=v, itype="raw", extra=link(text="Disable transparent") )
        return DataObj(varname=obj, value=v, itype="raw")

    def _pregetdata(self):
        self.acl.reverse()
        self.http_access.reverse()

    def mgrinfo(self):
        # FIXME remove IP argument
        cmd="squidclient mgr:info"
        p = Popen(cmd, shell=True, bufsize=0, stdout=PIPE, stderr=STDOUT, close_fds=True)
        
        mode=None
        for _line in p.stdout.readlines():
            line=_line.replace('\n','')
            #lg.debug("line: %s"%line, __name__)
            if line.startswith("Current Time:"):
                self.time=line.replace("Current Time:",'').strip()
            if line.startswith("Server:"):
                self.version=line.replace("Server:",'').strip()
            
            elif line.startswith("Connection information for squid:"):
                mode="connection"
                continue
            elif line.startswith("Cache information for squid:"):
                mode="cache"
                continue
            elif line.startswith("Median Service Times"):
                mode="service-times"
                continue
            elif line.startswith("Resource usage for squid:"):
                mode="resources"
                continue
            elif line.startswith("Memory usage for squid via mallinfo():"):
                mode="memory-usage"
                continue
            elif line.startswith("Memory accounted for:"):
                mode="memory-accounted"
                continue
            elif line.startswith("File descriptor usage for squid:"):
                mode="file-descriptor"
                continue
            elif line.startswith("Internal Data Structures:"):
                mode="internal-data"
                continue
            ######################
            # save some things
            ########################
            # connection data
            elif "Number of clients" in line and mode == "connection":
                self.clients=line.strip().split()[-1]
            elif "Number of HTTP requests" in line and mode == "connection":
                self.http_requests=line.strip().split()[-1]
            elif "Average HTTP requests per minute" in line and mode == "connection":
                self.http_avg_requests=line.strip().split()[-1]
            
            elif "Storage Swap capacity:" in line and mode == "cache":
                self.cache_swap_usage=line.strip().split()[3]
            elif "Storage Swap size:" in line and mode == "cache":
                self.cache_swap_size=" ".join(line.strip().split()[3:])
            
            elif "Storage Mem capacity:" in line and mode == "cache":
                self.cache_mem_usage=line.strip().split()[3]
            elif "Storage Mem size:" in line and mode == "cache":
                self.cache_mem_size=" ".join(line.strip().split()[3:])
            
            elif "Total in use:" in line and mode == "memory-usage":
                self.mem_total=" ".join(line.strip().split()[3:5])
                self.mem_total_percent=line.strip().split()[5]
            
            elif "Total accounted:" in line and mode == "memory-accounted":
                self.mem_ac_total=" ".join(line.strip().split()[2:4])
                self.mem_ac_total_percent=line.strip().split()[4]
        
        
        cmd="squidclient mgr:delay"
        p = Popen(cmd, shell=True, bufsize=0, stdout=PIPE, stderr=STDOUT, close_fds=True)
        
        pool=None
        pool_type=None
        self.delay_pools_data={}
        for _line in p.stdout.readlines():
            line=_line.replace('\n','')
            #lg.debug("line: %s"%line, __name__)
            if line.startswith("Delay pools configured:"):
                self.delay_pools=line.split()[-1]
            
            elif line.startswith("Pool:"):
                pool=line.split()[-1]
                self.delay_pools_data[pool]={}
                continue
            
            elif "Class:" in line and pool:
                self.delay_pools_data[pool]['class']=line.split()[-1]
            
            elif "Aggregate:" in line and pool:
                self.delay_pools_data[pool]['aggregate']={}
                pool_type="aggregate"
            elif "Individual:" in line and pool:
                self.delay_pools_data[pool]['individual']={}
                pool_type="individual"
            elif "Max:" in line and pool:
                self.delay_pools_data[pool][pool_type]['max']=line.split()[-1]
            elif "Restore:" in line and pool:
                self.delay_pools_data[pool][pool_type]['restore']=line.split()[-1]
            elif "Current:" in line and pool:
                self.delay_pools_data[pool][pool_type]['current']=line.replace('Current: ','').strip()
        
        pools_data=""
        for pool in self.delay_pools_data:
            pools_data+="uno<br/>"
        
        self.delay_pools_data=pools_data
        
        values=[]
        del(self.acl)
        del(self.kwargs)
        del(self.http_access)
        del(self.http_port)
        del(self.fnames)
        for obj in dir(self):
            if "__" in obj: continue
            v=getattr(self, obj)
            if type(v) == type("") or type(v) == type([]) or type(v) == type({}):
                lg.debug("printdata() self.%s=%s"%(obj,v) , __name__)
                values.append( DataObj(varname=obj, value=v, itype="plain") )
        return values



if __name__ == "__main__":
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
    
    #app=extensions(fname="dansguardian/lists/bannedextensionlist")
    #app.printdata()
    
    #app=ips()
    #app.printdata()
    #for a in app.getdata():
    #    print "%s=%s %s" %(a.varname, a.value, a.itype)
    
    #app=phraselist()
    #app.printdata()
    #for a in app.getdata():
    #    print "%s=%s %s" %(a.varname, a.value, a.itype)
    
    app=squid()
    #print app.getdata()
    print app.mgrinfo()
