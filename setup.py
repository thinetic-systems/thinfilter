#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 
# This script is inspired by the debian package python-chardet
import os
import glob
from distutils.core import setup
from distutils.command.build import build
from distutils.dir_util import copy_tree

data_files = []


def get_files(ipath):
    files = []
    for afile in glob.glob('%s/*'%(ipath) ):
        if os.path.isfile(afile):
            files.append(afile)
    return files

def get_recursive(ipath, dest):
    fileList=[]
    for root, subFolders, files in os.walk(ipath):
        for f in files:
            print "%s => %s"%(os.path.join(root,f), os.path.join(dest,root))
            fileList.append( (os.path.join(dest,root) ,[os.path.join(root,f)]) )
    return fileList


data_files.append(('share/thinfilter/static', get_files("webpanel/static") ))
data_files.append(('share/thinfilter/templates', get_files("webpanel/templates") ))
#for f in get_recursive("webpanel/", 'share/thinfilter/'):
#    data_files.append(f)

# openvpn easy-rsa2.0
data_files.append(('/var/lib/thindistro/changes/etc/openvpn', get_files("openvpn") ))

# dnsmasq
data_files.append(('/var/lib/thindistro/changes/etc/dnsmasq/', ['dnsmasq/dnsmasq.conf'] ))
data_files.append(('/var/lib/thindistro/changes/etc/', ['resolv.conf.dnsmasq'] ))


# squid3
data_files.append(('/var/lib/thindistro/changes/etc/squid3/', ['squid3/squid.conf'] ))

# squid logrotate
data_files.append(('/var/lib/thindistro/changes/etc/logrotate.d/', ['logrotate.d/squid3'] ))

# dansguardian
#for f in get_recursive("dansguardian/", '/var/lib/thindistro/changes/etc/dansguardian/'):
#    data_files.append(f)


# firewall
data_files.append(('/var/lib/thindistro/changes/etc/thinfilter/', get_files("firewall/") ))



setup(name='ThinFilter',
      description = 'Easy and small proxy distro',
      version='0.1.1',
      author = 'Mario Izquierdo',
      author_email = 'mario.izquierdo@thinetic.es',
      url = 'http://www.thinetic.es',
      license = 'GPLv2',
      platforms = ['linux'],
      keywords = ['proxy', 'squid', 'vpn'],
      packages=['thinfilter' , 'thinfilter.modules', 'thinfilter.server'],
      package_dir = {'':''},
      scripts=['thinfilter.py', 'thinfilter-cron.py', 'thinfiltersrv.py'],
      data_files=data_files
      )

