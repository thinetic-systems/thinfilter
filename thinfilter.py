#!/usr/bin/env python
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

import sys
import os
import string
import traceback
import random
from hashlib import sha1







import thinfilter
thinfilter.init()



import thinfilter.config
thinfilter.config.debug=False
if "--debug" in sys.argv:
    thinfilter.config.debug=True
import thinfilter.logger as lg

# load daemonize con configure
import thinfilter.daemonize
lg.old_stderr=sys.stderr
lg.old_stdout=sys.stdout


import web
web.config.debug = False
if "--debug" in sys.argv:
    web.config.debug=True
    thinfilter.config.daemon=False
else:
    sys.stderr = lg.stderr()
    sys.stdout = lg.stdout()

web.config.session_parameters.cookie_name="ThinFilter"


from web import form

def debug(txt):
    lg.debug("thinfilter::debug(): %s" %str(txt), name="thinfilter" )
    #print >> sys.stderr, "DEBUG: %s" %str(txt)



# A simple user object that doesn't store passwords in plain text
# see http://en.wikipedia.org/wiki/Salt_(cryptography)
class PasswordHash(object):
    def __init__(self, password_):
        self.salt = "".join(chr(random.randint(33,127)) for x in xrange(64))
        self.saltedpw = sha1(password_ + self.salt).hexdigest()
    def check_password(self, password_):
        """checks if the password is correct"""
        return self.saltedpw == sha1(password_ + self.salt).hexdigest()

# FIXME: a secure application would never store passwords in plaintext in the source code
users = {'admin' : PasswordHash('admin') } 


#urls = ('/', 'index',
#        '/logout', 'logout',
#        '/main', 'main',
#        '/config', 'config',
#        '/phones', 'phones',
#        '/phones.xml', 'phones_xml',
#        '/files', 'files',
#        '/clear', 'clear',
#        '/re-send', 'resend',
#        '/download', 'download',
#        '/data/([a-zA-Z.]*)', 'static')

urls = ('/', 'index',
        '/logout', 'logout',
        '/main', 'main',
        '/config', 'config',
        '/config/(.*)', 'config',
        
        '/download', 'download',
        #'/data/([a-zA-Z.]*)', 'static',
        '/data/([a-zA-Z0-9-.]*)', 'static',
        )


# global app
app = web.application(urls, globals())
render = web.template.render(thinfilter.config.BASE + 'templates/', base='layout')
db = web.database(dbn='sqlite', db=thinfilter.config.DBNAME)

# from http://webpy.org/cookbook/session_with_reloader
# use only one session instead of debug=True
if web.config.get('_session') is None:
    session = web.session.Session(app, web.session.DiskStore(thinfilter.config.SESSIONS_DIR), {'user': 'anonymous'})
    web.config._session = session
else:
    session = web.config._session

signin_form = form.Form(form.Textbox('username',
                         form.Validator('Unknown username.', lambda x: x in users.keys()),
                         description='Usuario:'),
            form.Password('password', description='Contraseña:'),
            form.Button("submit", type="submit", description="Entrar"),
            validators = [form.Validator("El usuario o la contraseña son incorrectos.",
                          lambda x: users[x.username].check_password(x.password)) ])

class BaseRequest(object):
    """
    Base class to provide some common methods to any URL
    """
    def islogged(self):
        lg.debug("BaseRequest()::authenticate")
        
        if not hasattr(session, "user"):
            session.user="anonymous"
            debug("BaseRequest() GET setting user anonymous")
        if session.user != "anonymous":
            return True
        return False


class index(BaseRequest):
    def GET(self):
        my_signin = signin_form()
        if not self.islogged():
            return render.index(session, my_signin)
        return render.main(session, None)
    
    def POST(self):
        my_signin = signin_form() 
        if not hasattr(session, "user"):
            session.user="anonymous"
            debug("POST setting user anonymous")
        if not my_signin.validates():
            debug("not login valid")
            return render.index(session, my_signin)
        else:
            session.user = my_signin['username'].value
            debug("login OK set session.user to %s" %my_signin['username'].value)
            return render.main(session, None)



class logout(BaseRequest):
    def GET(self):
        session.user=""
        try:
            session.kill()
        except Exception, err:
            debug("Exception logout, error=%s"%err)
            traceback.print_exc(file=sys.stderr)
            pass
        raise web.seeother('/')



class main(BaseRequest):
    def GET(self):
        if not self.islogged():
            raise web.seeother('/')
        
        entries = db.select('config')
        return render.main(session, None)



class config(BaseRequest):
    def GET(self, options=None):
        if not self.islogged():
            raise web.seeother('/')
        
        debug("config::GET() options=%s" %options)
        
#        entries = db.select('config')
#        conf=entries[0]
#        if conf.debug == 1:
#            conf.debugtxt="checked"
#        else:
#            conf.debugtxt=""
        import thinfilter.rules
        conf=[
              thinfilter.rules.DataObj(itype="checkbox", varname="var1", value=1, varnamechecked="checked"),
              thinfilter.rules.DataObj(itype="checkbox", varname="var2", value=2, varnamechecked=""),
              thinfilter.rules.DataObj(itype="checkbox", varname="var3", value=3, varnamechecked="checked"),
              thinfilter.rules.DataObj(itype="text", varname="var4", value="prueba"),
                ]
        
        #conf=thinfilter.rules.ips().getdata()
        conf=thinfilter.rules.squid().getdata()
        return render.config(session, conf)


    def POST(self):
        if not self.islogged():
            raise web.seeother('/')
        
        userdata=web.input(debug=0, concurrent=8, timeout=4)
        debug(userdata)
        _debug = userdata.debug
        _timeout = userdata.timeout
        _concurrent = userdata.concurrent
        debug("debug=%s  timeout=%s  concurrent=%s"%(_debug, _timeout, _concurrent) )
        try:
            # set stop=2 to reload conf from daemon
            db.query("UPDATE config set debug='%s', timeout='%s', concurrent='%s', stop='2'" %(_debug, _timeout, _concurrent))
        except Exception, err:
            debug("Exception save config, error=%s"%err)
            traceback.print_exc(file=sys.stderr)
        return web.seeother('/config')



#class phones(BaseRequest):
#    def GET(self):
#        if not self.islogged():
#            raise web.seeother('/')
#        
#        entries = db.select('phones')
#        return render.phones(session, entries)



#class phones_xml(BaseRequest):
#    def GET(self):
#        # local render engine (not use layout.html)
#        lrender = web.template.render(thinfilter.config.BASE + 'templates')
#        web.header('Content-Type', 'text/xml')
#        if session and session.user != "anonymous":
#            entries = db.select('phones')
#            return lrender.phones_xml(entries)
#        else:
#            # return empty XML if no auth
#            return lrender.phones_xml([])



class FileData(object):
    def __init__(self):
        entries = db.select('config')[0]
        self.absname=os.path.join( entries.file_path , entries.sendfile)
        self.fname=entries.sendfile
        self.b64=""
        self.isimage=False
        self.ext=self.fname.split('.')[-1]
        if self.ext in thinfilter.config.IMAGE_EXTENSIONS:
            self.isimage=True
            import base64
            if os.path.isfile(self.absname):
                self.b64=base64.b64encode( open(self.absname, 'r').read() )

    def download(self):
        web.header('Content-Type', 'image/%s' %(self.ext) )
        return open(self.absname, 'r').read()



class FileUpload(object):
    def __init__(self, _form):
        self.raw=_form['myfile'].value
        self.filename=_form['myfile'].filename
        for c in range(len(self.filename)):
            print "c=%s   self.filename[c]=%s" %(c, self.filename[c])
            if self.filename[c] not in ALLOWED_CHARS:
                self.filename=self.filename.replace(self.filename[c],'_')

    def isallowed(self):
        if not self.filename.split('.')[-1] in thinfilter.config.IMAGE_EXTENSIONS:
            return False
        return True

    def save(self):
        entries = db.select('config')[0]
        self.absname=os.path.join( entries.file_path , self.filename)
        try:
            f=open(self.absname, 'wb')
            f.write(self.raw)
            f.close()
            return True
        except Exception, err:
            debug("Exception save config, error=%s"%err)
            traceback.print_exc(file=sys.stderr)
            return False



#class files:
#    def GET(self):
#        if session and session.user != "anonymous":
#            return render.files(session, FileData() )
#        raise web.seeother('/')

#    def POST(self):
#        if session and session.user != "anonymous":
#            upload = FileUpload( web.input(myfile={}) )
#            
#            if not upload.isallowed():
#                # extension not allowed
#                return render.files(session, FileData() )
#            if upload.save():
#                # configure database
#                db.query("UPDATE config set sendfile='%s', stop='2'" %(upload.filename))
#            
#            return render.files(session, FileData() )
#        raise web.seeother('/')



#class download:
#    def GET(self):
#        if session and session.user != "anonymous":
#            data=FileData()
#            return data.download()
#        raise web.seeother('/')



#class clear:
#    def GET(self):
#        if session and session.user != "anonymous":
#            # clear phone table
#            try:
#                db.query("DELETE from phones")
#            except Exception, err:
#                debug("Exception clear, error=%s"%err)
#                traceback.print_exc(file=sys.stderr)
#            raise web.seeother('/phones')
#        raise web.seeother('/')



#class resend:
#    def GET(self):
#        if session and session.user != "anonymous":
#            # set 'seen1' to all
#            try:
#                db.query("UPDATE phones set status='seen1', date_send=''")
#            except Exception, err:
#                debug("Exception resend, error=%s"%err)
#                traceback.print_exc(file=sys.stderr)
#            raise web.seeother('/phones')
#        raise web.seeother('/')


class static:
    def GET(self, sfile):
        #debug(os.path.join(thinfilter.config.BASE, 'static' , sfile))
        if not os.path.isfile( os.path.join(thinfilter.config.BASE, 'static' , sfile) ):
            # return 404
            return web.notfound()

        # set headers (javascript, css, or images)
        extension = sfile.split('.')[-1]
        if extension == "css":
            web.header("Content-Type","text/css; charset=utf-8")
        elif extension == "js":
            web.header("Content-Type","text/javascript; charset=utf-8")
        elif extension in thinfilter.config.IMAGE_EXTENSIONS:
            web.header('Content-Type', 'image/%s' %(extension) )
        return open(os.path.join(thinfilter.config.BASE, 'static', sfile)).read()


if __name__ == "__main__":
    args=[]
    for arg in sys.argv[1:]:
        args.append(arg)
    sys.argv=[sys.argv[0], '9090']
    debug("main() sys.argv=%s args=%s" %(sys.argv,args) )
    if "--start" in args:
        debug("daemonize....")
        #thinblue.daemonize.start_server()
        app.run()
    
    elif "--stop" in args:
        #thinblue.daemonize.stop_server(sys.argv[0])
        pass
    
    else:
        print >> lg.old_stderr , """
thinfilter:
        --start    - start web daemon
        --stop     - stop daemon

    You can access interface in http://localhost:9090
"""
