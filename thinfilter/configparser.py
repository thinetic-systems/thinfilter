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

import thinfilter.logger as lg
import thinfilter.config



class ConfigParser:
    def __init__(self, fname=None):
        self.fname=fname
        self.values={}
        self.__rawdata=None
        self.__modified=False
        self.__newdata={}
        self.readtemplate()

    def readtemplate(self):
        if not self.fname or not os.path.exists(self.fname):
            lg.error("readtemplate() template %s not found, returning empty dictionary"%self.fname, __name__)
            return
        f=open(self.fname, 'r')
        self.__rawdata=f.readlines()
        f.close()
        
        for line in self.__rawdata:
            sline=line.strip()
            if sline == "": continue
            if sline.startswith('#'): continue
            if "=" in sline:
                self.values[sline.split('=')[0].strip()]=sline.split('=')[1].replace('"','').replace("'","").strip()

    def printdata(self):
        lg.debug("printdata(): %s"%self.values, __name__)


    def setvar(self, varname, newvalue):
        if self.values.has_key(varname):
            self.__newdata[varname]=newvalue
            self.values[varname]=newvalue
            self.__modified=True
        else:
            lg.info("setvar() varname=%s not found in self.values"%varname, __name__)

    def getvar(self, varname):
        if self.values.has_key(varname):
            lg.debug("getvar() varname='%s' value='%s'" %(varname, self.values[varname]), __name__ )
        else:
            lg.info("getvar() varname=%s not found in self.values"%varname, __name__)

    def savetofile(self):
        if not self.__modified:
            lg.info("savetofile() not saving, self.__modified=False", __name__)
            return
        for i in range(len(self.__rawdata)):
            sline=self.__rawdata[i].strip()
            if "=" in sline:
                varname=sline.split('=')[0].strip()
                if sline.startswith(varname) and self.__newdata.has_key(varname):
                    line="%s = %s\n"%(varname, self.__newdata[varname])
                    self.__rawdata[i]=line
                    
        f=open(self.fname, 'w')
        for l in self.__rawdata:
            if "filterport" in l: print l
            f.write(l)
        f.close()
        lg.info("savetofile() saved file \"%s\""%self.fname, __name__)


if __name__ == "__main__":
    thinfilter.config.daemon=False
    thinfilter.config.debug=True
    
    app=ConfigParser(fname="dansguardian/dansguardianf1.conf")
    app.printdata()
    app.getvar("filterport")
    app.setvar("filterport", "8080")
    app.getvar("filterport")
    app.savetofile()
