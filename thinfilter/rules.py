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
# FIXME not needed if module is imported
try:
    import thinfilter.logger as lg
except ImportError:
    print "DEBUG: Import exception, adding cur dir to sys.path"
    sys.path.append("/home/mario/thinetic/dansguardian")
import thinfilter.logger as lg
import thinfilter.config

class DataObj(object):
    def __init__(self, **kwargs):
        lg.debug("DataObj: kwargs=%s" %(kwargs) , __name__)
        self.values=[]
        self.varname=""
        self.itype=""
        self.varname_disabled=""
        for _var in kwargs:
            setattr(self, _var, kwargs[_var])


class rules(object):
    def __init__(self, **kwargs):
        lg.debug("rules::__init__() kwargs=%s"%kwargs)
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
            if type(v) == type({}) or type(v) == type([]):
                lg.debug("printdata() self.%s=%s"%(obj,v) )

    def getdata(self):
        __data=[]
        for obj in dir(self):
            if "__" in obj: continue
            if obj in ['fnames', 'kwargs']: continue
            v=getattr(self, obj)
            if type(v) == type({}) or type(v) == type([]):
                lg.debug("obj=%s v=%s" %(obj, v))
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
            lg.debug("banned: %s"%v)

        for v in self.vars['data']['nobanned']:
            lg.debug("NO banned: %s"%v)

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
            lg.debug("bannedphraselist: %s"%v)

        for v in self.exceptionphraselist:
            lg.debug("exceptionphraselist: %s"%v)

        for v in self.weightedphraselist:
            lg.debug("weightedphraselist: %s"%v)
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
        self.fnames=["squid/squid.conf"]
        self.acl_localnet=[]
        self.http_access=[]
        
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


if __name__ == "__main__":
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
    
    #app=extensions(fname="dansguardian/lists/bannedextensionlist")
    #app.printdata()
    
    #app=ips()
    #app.printdata()
    #for a in app.getdata():
    #    print "%s=%s %s" %(a.varname, a.value, a.itype)
    
    app=phraselist()
    app.printdata()
    for a in app.getdata():
        print "%s=%s %s" %(a.varname, a.value, a.itype)
    
