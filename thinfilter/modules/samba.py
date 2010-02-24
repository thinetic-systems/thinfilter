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
# openvpn stuff
#

import os
import sys

import glob
import re
import types
import pwd

"""
SAMBA
  list users: pdbedit -L
  delete user: pdbedit -x $USER
  adduser: useradd xxxxx && pdbedit -a -u xxxxx

  list shares: PASSWD=passwd smbclient -L \\\\127.0.0.1 -U user -g
"""


import thinfilter.logger as lg
import thinfilter.config
import thinfilter.common

import web
render = web.template.render(thinfilter.config.BASE + 'templates/')

SMB_RELOAD="/etc/init.d/samba reload"
SMB_PATH="/var/lib/samba/shares"
SMB_MINUSER=2001
SMB_MAXUSER=3000
SMBCONF="/etc/samba/smb.conf"

if thinfilter.config.devel:
    SMBCONF="./smb.conf"


SMB_VARS=[
        'global|workgroup',
]

"""
[share]
  comment = Share folder
  path = /var/lib/samba/shares/share
  browseable = yes
  read only = no
  guest ok = yes
  valid users = xxxxx, yyyyyy, @group
  
  read only = yes
  write list = admin, root, @staff
"""

from configobj import ConfigObj, Section
class MyConfigObj (ConfigObj):

    def _write_line(self, indent_string, entry, this_entry, comment):
        """Write an individual line, for the write method"""
        # NOTE: the calls to self._quote here handles non-StringType values.
        if not self.unrepr:
            val = self._decode_element(self._quote(this_entry))
        else:
            val = repr(this_entry)
        return '%s%s%s%s%s' % (
            indent_string,
            self._decode_element(self._quote(entry, multiline=False)),
            self._a_to_u(' = '),
            val,
            self._decode_element(comment))

    def _parse(self, infile):
        """Actually parse the config file."""
        temp_list_values = self.list_values
        if self.unrepr:
            self.list_values = False
            
        comment_list = []
        done_start = False
        this_section = self
        maxline = len(infile) - 1
        cur_index = -1
        reset_comment = False
        
        while cur_index < maxline:
            if reset_comment:
                comment_list = []
            cur_index += 1
            line = infile[cur_index]
            sline = line.strip()
            # do we have anything on the line ?
            if not sline or sline.startswith('#') or sline.startswith(';'):
                reset_comment = False
                comment_list.append(line)
                continue
            
            if not done_start:
                # preserve initial comment
                self.initial_comment = comment_list
                comment_list = []
                done_start = True
                
            reset_comment = True
            # first we check if it's a section marker
            mat = self._sectionmarker.match(line)
            if mat is not None:
                # is a section line
                (indent, sect_open, sect_name, sect_close, comment) = mat.groups()
                if indent and (self.indent_type is None):
                    self.indent_type = indent
                cur_depth = sect_open.count('[')
                if cur_depth != sect_close.count(']'):
                    self._handle_error("Cannot compute the section depth at line %s.",
                                       NestingError, infile, cur_index)
                    continue
                
                if cur_depth < this_section.depth:
                    # the new section is dropping back to a previous level
                    try:
                        parent = self._match_depth(this_section,
                                                   cur_depth).parent
                    except SyntaxError:
                        self._handle_error("Cannot compute nesting level at line %s.",
                                           NestingError, infile, cur_index)
                        continue
                elif cur_depth == this_section.depth:
                    # the new section is a sibling of the current section
                    parent = this_section.parent
                elif cur_depth == this_section.depth + 1:
                    # the new section is a child the current section
                    parent = this_section
                else:
                    self._handle_error("Section too nested at line %s.",
                                       NestingError, infile, cur_index)
                    
                sect_name = self._unquote(sect_name)
                if parent.has_key(sect_name):
                    self._handle_error('Duplicate section name at line %s.',
                                       DuplicateError, infile, cur_index)
                    continue
                
                # create the new section
                this_section = Section(
                    parent,
                    cur_depth,
                    self,
                    name=sect_name)
                parent[sect_name] = this_section
                parent.inline_comments[sect_name] = comment
                parent.comments[sect_name] = comment_list
                continue
            #
            # it's not a section marker,
            # so it should be a valid ``key = value`` line
            mat = self._keyword.match(line)
            if mat is None:
                # it neither matched as a keyword
                # or a section marker
                self._handle_error(
                    'Invalid line at line "%s".',
                    ParseError, infile, cur_index)
            else:
                # is a keyword value
                # value will include any inline comment
                (indent, key, value) = mat.groups()
                if indent and (self.indent_type is None):
                    self.indent_type = indent
                # check for a multiline value
                if value[:3] in ['"""', "'''"]:
                    try:
                        (value, comment, cur_index) = self._multiline(
                            value, infile, cur_index, maxline)
                    except SyntaxError:
                        self._handle_error(
                            'Parse error in value at line %s.',
                            ParseError, infile, cur_index)
                        continue
                    else:
                        if self.unrepr:
                            comment = ''
                            try:
                                value = unrepr(value)
                            except Exception, e:
                                if type(e) == UnknownType:
                                    msg = 'Unknown name or type in value at line %s.'
                                else:
                                    msg = 'Parse error in value at line %s.'
                                self._handle_error(msg, UnreprError, infile,
                                    cur_index)
                                continue
                else:
                    if self.unrepr:
                        comment = ''
                        try:
                            value = unrepr(value)
                        except Exception, e:
                            if isinstance(e, UnknownType):
                                msg = 'Unknown name or type in value at line %s.'
                            else:
                                msg = 'Parse error in value at line %s.'
                            self._handle_error(msg, UnreprError, infile,
                                cur_index)
                            continue
                    else:
                        # extract comment and lists
                        try:
                            (value, comment) = self._handle_value(value)
                        except SyntaxError:
                            self._handle_error(
                                'Parse error in value at line %s.',
                                ParseError, infile, cur_index)
                            continue
                #
                key = self._unquote(key)
                if this_section.has_key(key):
                    self._handle_error(
                        'Duplicate keyword name at line %s.',
                        DuplicateError, infile, cur_index)
                    continue
                # add the key.
                # we set unrepr because if we have got this far we will never
                # be creating a new section
                this_section.__setitem__(key, value, unrepr=True)
                this_section.inline_comments[key] = comment
                this_section.comments[key] = comment_list
                continue
        #
        if self.indent_type is None:
            # no indentation used, set the type accordingly
            self.indent_type = ''

        # preserve the final comment
        if not self and not self.initial_comment:
            self.initial_comment = comment_list
        elif not reset_comment:
            self.final_comment = comment_list
        self.list_values = temp_list_values



class Shares(thinfilter.common.Base):
    def __init__(self):
        self.vars={}
        self.varsobj=MyConfigObj( SMBCONF )
        
        self.vars['global|workgroup']=self.varsobj['global']['workgroup']
        self.vars['sections']=[]
        for section in self.varsobj:
            if section not in ['global', 'print$', 'printers', 'homes']:
                self.vars['sections'].append(section)
        try:
            self.vars['users']=self.get_users()
        except Exception, err:
            lg.error("Can't read users: err=%s"%err, __name__)
            self.vars['users']=[]
        self.vars['abspath']=SMB_PATH
        

    def get_users(self):
        data=[]
        allusers=thinfilter.common.run('pdbedit -L && sleep 0.1', verbose=False, _from=__name__)
        for user in allusers:
            userid=int(user.split(':')[1])
            if userid >= SMB_MINUSER and userid < SMB_MAXUSER:
                data.append( user.split(':')[0] )
        return data

    def save(self):
        self.varsobj.write()
        thinfilter.common.run(SMB_RELOAD, verbose=False, _from=__name__)

    def change_workgroup(self, workgroup):
        lg.debug("change_workgroup() workgroup=%s"%workgroup, __name__)
        if re.search('[á|é|í|ó|ú| |\'|\"]', workgroup):
            lg.error("change_workgroup() MATCH=%s"%(re.search('[á|é|í|ó|ú| |\'|\"]', workgroup)), __name__)
            return False
        self.varsobj['global']['workgroup']=workgroup
        self.save()
        return True

    def new_share(self, sharename, shareobj):
        if re.search('[á|é|í|ó|ú| |.|\'|\"]', sharename):
            return False
        newdata={'valid users':[],
                 'browseable': 'no',
                 'guest ok': 'no',
                 'read only': 'no',
                }
        
        # delete share ???
        if shareobj.has_key('delete') and shareobj['delete'] == '1':
            if sharename in self.vars['sections']:
                # load shares, pop it and save
                self.varsobj=MyConfigObj( SMBCONF )
                self.varsobj.pop(sharename)
                self.save()
                return True
            else:
                # unknow user...
                return False
        # add share
        for key in shareobj:
            if key in ['comment', 'path']:
                newdata[key]=shareobj[key]
            elif key in ['browseable', 'guest ok', 'read only']:
                if shareobj[key] == 'on':
                    newdata[key]='yes'
                else:
                    newdata[key]='no'
            elif "user|" in key:
                newdata['valid users'].append(key.split('|')[1])
        self.varsobj[sharename]=newdata
        self.save()
        os.mkdir(newdata['path'])
        return True

    def new_user(self, username, userobj):
        if re.search('[á|é|í|ó|ú| |.|\'|\"]', username):
            return False
        newdata={}
        # delete user???
        if userobj.has_key('delete') and userobj['delete'] == '1':
            if username in self.vars['users']:
                # delete user from samba
                thinfilter.common.run("pdbedit -x %s"%(username), verbose=True, _from=__name__)
                # delete user from UNIX system
                thinfilter.common.run("deluser %s"%(username), verbose=True, _from=__name__)
                return True
            else:
                # unknow user...
                return False
        
        # check password and password2
        if userobj['password'] != userobj['password2']:
            return False
        
        # add system user
        if not self.user_exists(username):
            cmd="useradd -s /bin/false -u %s -d /var/lib/samba/shares -g sambashare %s"%(self.get_last_uid(), username)
            thinfilter.common.run(cmd, verbose=True, _from=__name__)
        
        cmd="echo %s:%s | chpasswd"%(username, userobj['password'])
        thinfilter.common.run(cmd, verbose=True, _from=__name__)
        
        # add samba user
        cmd="cat << EOF| pdbedit -t -a -u %s\n%s\n%s\nEOF"%(username, userobj['password'], userobj['password'])
        thinfilter.common.run(cmd, verbose=True, _from=__name__)
        
        return True


    def get_last_uid(self):
        allusers=pwd.getpwall()
        last=SMB_MINUSER
        for user in allusers:
            if user[2] < SMB_MINUSER: continue
            elif user[2] > SMB_MAXUSER: continue
            elif user[2] > last: last=user[2]
        return last+1

    def user_exists(self, username):
        allusers=pwd.getpwall()
        for user in allusers:
            if user[0] == username: return True
        return False


    def read_share(self, sharename):
        newdata={'sharename': '',
                'sharenamereadonly':'',
                'delete':'Borrar recurso',
                'enabledelete':'',
                'comment': '', 
                'path': '',
                'browseable': ' checked', 
                'guest ok': ' checked', 
                'read only': '',
                'user':{}}
        for user in self.vars['users']:
            newdata['user'][user]=''
        if not self.varsobj.has_key(sharename):
            return newdata
        data=self.varsobj[sharename]
        newdata['sharename']=sharename
        newdata['sharenamereadonly']=' readonly'
        newdata['enabledelete']='1'
        for key in data:
            if key in ['comment', 'path']:
                newdata[key]=data[key]
            elif key in ['browseable', 'guest ok', 'read only']:
                if data[key] == 'yes':
                    newdata[key]=' checked'
                else:
                    newdata[key]=''
            elif key == "valid users":
                if type(data[key]) == types.ListType:
                    for user in data[key]:
                        newdata["user"][user]=" checked"
                elif type(data[key]) == types.StringType:
                    newdata["user"][data[key]]=" checked"
            else:
                lg.error("read_share() unknow key=%s"%key, __name__)
        
        return newdata

    def read_user(self, username):
        newdata={'username': '',
                'usernamereadonly':'',
                'delete':'Borrar usuario',
                'enabledelete':''}
        if username not in self.vars['users']:
            return newdata
        newdata['username']=username
        newdata['usernamereadonly']=' readonly'
        newdata['enabledelete']='1'
        return newdata

class samba(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('samba.samba')
    @thinfilter.common.layout(body='', title='Configuración de recursos compartidos')
    def GET(self, options=None):
        sobj=Shares()
        samba_vars=sobj.vars
        formdata=web.input()
        if formdata.has_key('error'):
            samba_vars['error']=formdata['error']
        lg.debug("samba::main::GET() samba=%s" %samba_vars, __name__)
        return render.shares(samba_vars, 'Guardar grupo de trabajo')

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('samba.samba')
    def POST(self):
        sobj=Shares()
        formdata=web.input()
        lg.debug("samba()::main::formdata=%s"%formdata, __name__)
        if thinfilter.config.demo:
            return web.seeother('/shares?error=ERROR:Modo%20demo')
        try:
            if not sobj.change_workgroup( str(formdata['global|workgroup']) ):
                return web.seeother('/shares?error=Grupo%20incorrecto')
        except:
            return web.seeother('/shares?error=Grupo%20incorrecto')
        return web.seeother('/shares')


class shares(object):
    @thinfilter.common.islogged
    @thinfilter.common.isinrole('samba.shares')
    @thinfilter.common.layout(body='', title='Nuevo recurso compartido')
    def GET(self, options=None):
        """
        share/sharename
        share/new
        =========================
        user/username
        user/new
        """
        if not "/" in options:
            return web.seeother('/shares')
        
        sobj=Shares()
        data=sobj.vars
        formdata=web.input()
        if formdata.has_key('error'):
            data['error']=formdata['error']
        
        action=options.split('/')
        if action[0] == "share":
            data['form']=sobj.read_share(action[1])
            return render.shares_new(data, 'Guardar')
        elif action[0] == "user":
            data['form']=sobj.read_user(action[1])
            return render.shares_newuser(data, 'Guardar')
        else:
            return web.seeother('/shares')

    @thinfilter.common.islogged
    @thinfilter.common.isinrole('samba.shares')
    def POST(self, options=None):
        """
        share/sharename
        share/new
        =========================
        user/username
        user/new
        """
        if not "/" in options:
            return web.seeother('/shares')
        
        sobj=Shares()
        formdata=web.input()
        lg.debug("samba()::shares()::formdata=%s"%formdata, __name__)
        
        if thinfilter.config.demo:
            return web.seeother('/shares/share/?error=ERROR:Modo%20demo')
        
        action=options.split('/')
        if action[0] == "share":
            # save share
            if not sobj.new_share(formdata['sharename'], formdata):
                return web.seeother('/shares/share/?error=Parametros%20incorrectos')
            
        elif action[0] == "user":
            # save user
            if not sobj.new_user(formdata['username'], formdata):
                return web.seeother('/shares/user/?error=Parametros%20incorrectos')
        
        #sobj=Shares()
        #if not sobj.new_share(formdata['sharename'], formdata):
        #    return web.seeother('/shares/newshare?error=Parametros%20incorrectos')
        return web.seeother('/shares')








def init():
    if thinfilter.config.devel or os.path.isfile('/usr/sbin/smbd'):
        lg.debug("samba::init()", __name__)
        thinfilter.common.register_url('/shares',                          'thinfilter.modules.samba.samba')
        thinfilter.common.register_url('/shares/([a-zA-Z0-9-./]*)',  'thinfilter.modules.samba.shares')
        
        menu=thinfilter.common.Menu("", "Compartidos", order=70)
        menu.appendSubmenu("/shares", "Configuración", role='samba.samba')
        menu.appendSubmenu("/shares/share/new", "Nuevo recurso", role='samba.shares')
        menu.appendSubmenu("/shares/user/new", "Nuevo usuario", role='samba.shares')
        thinfilter.common.register_menu(menu)
        
        thinfilter.common.register_role_desc('samba.samba', "Ver recursos compartidos")
        thinfilter.common.register_role_desc('samba.shares', "Modificar recursos compartidos")
        
        # create shares path
        if not os.path.isdir(SMB_PATH):
            os.mkdir(SMB_PATH)
            os.chmod(SMB_PATH, 0755)
            os.chown(SMB_PATH, 0, 0)
        
    else:
        lg.info("samba not found, disabling it", __name__)





