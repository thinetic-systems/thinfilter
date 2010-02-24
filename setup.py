#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 
# This script is inspired by the debian package python-chardet
import os
import sys
import glob
from distutils.core import setup
from distutils.command.build import build
from distutils.dir_util import copy_tree

#from setuptools.command.build_ext import build_ext
#from setuptools import Extension

data_files = []


def get_files(ipath, exclude=None):
    files = []
    for afile in glob.glob('%s/*'%(ipath) ):
        if os.path.isfile(afile):
            if exclude and exclude in afile:
                continue
            files.append(afile)
    return files


def get_recursive(ipath, dest, exclude=None):
    fileList=[]
    for root, subFolders, files in os.walk(ipath):
        for f in files:
            if exclude and exclude in f:
                continue
            #print "%s => %s"%(os.path.join(root,f), os.path.join(dest,root))
            fileList.append( (os.path.join(dest,root) ,[os.path.join(root,f)]) )
    return fileList


data_files.append(('share/thinfilter/webpanel/static', get_files("webpanel/static") ))
data_files.append(('share/thinfilter/webpanel/templates', get_files("webpanel/templates") ))
#for f in get_recursive("webpanel/", 'share/thinfilter/'):
#    data_files.append(f)

# openvpn easy-rsa2.0
for f in get_recursive("openvpn/", "/etc/"):
    data_files.append(f)


# dnsmasq
data_files.append(('share/thinfilter/config/', ['dnsmasq/dnsmasq.conf'] ))
data_files.append(('share/thinfilter/config/', ['resolv.conf.dnsmasq'] ))

# squidGuard
for f in get_recursive("squidGuard/", "/var/lib/thinfilter/", exclude='.db'):
    data_files.append(f)

# squid3
data_files.append(('share/thinfilter/config/squid3/', get_files("squid3")))

# squid logrotate
data_files.append(('share/thinfilter/config/logrotate.d/', ['logrotate.d/squid3'] ))

# openvpn
data_files.append(('share/thinfilter/config/logrotate.d/', ['logrotate.d/openvpn'] ))

## dansguardian
##for f in get_recursive("dansguardian/", '/var/lib/thinfilter/changes/etc/dansguardian/'):
3#    data_files.append(f)


# firewall
data_files.append(('/etc/thinfilter/', ["firewall/firewall.conf"] ))
data_files.append(('sbin/', ["firewall/thinfilter.fw"] ))

# thinfilter-cron
data_files.append(('/etc/cron.d/', ["cron.d/thinfilter-cron"] ))

#procname_mod=Extension('thinfilter.procname', sources=['procname/procnamemodule.c'])

setup(name='ThinFilter',
      description = 'Easy and small proxy distro',
      version='0.1.1',
      author = 'Mario Izquierdo',
      author_email = 'mario.izquierdo@thinetic.es',
      url = 'http://www.thinetic.es',
      license = 'GPLv2',
      platforms = ['linux'],
      keywords = ['proxy', 'squid', 'vpn', 'samba'],
      packages=['thinfilter' , 'thinfilter.modules', 'thinfilter.server'],
      package_dir = {'':'./'},
      scripts=['thinfilter.py', 'thinfilter-cron.py', 'thinfiltersrv.py'],
      data_files=data_files,
      #ext_modules=[procname_mod]
      )

