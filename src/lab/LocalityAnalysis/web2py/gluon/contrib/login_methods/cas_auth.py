#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
This file is part of web2py Web Framework (Copyrighted, 2007-2009).
Developed by Massimo Di Pierro <mdipierro@cs.depaul.edu>.
License: GPL v2

Tinkered by Szabolcs Gyuris < szimszo n @ o regpreshaz dot eu>
"""

class CasAuth( object ):
    """
    Login will be done via Web2py's CAS application, instead of web2py's
    login form.
    
    Include in your model (eg db.py)::
        
        from gluon.contrib.login_methods.cas_auth import CasAuth
        auth.define_tables(username=True)
        auth.settings.login_form=CasAuth(
            globals(),
            urlbase = "https://web2py.com/cas/cas",
                 actions=['login','check','logout'])

    where urlbase is the actual CAS server url without the login,logout...
    Enjoy.
    """
    def __init__(self, g, 
                 urlbase = "https://web2py.com/cas/cas",
                 actions=['login','check','logout'],
                 maps=dict(username=lambda v:v[2],
                           email=lambda v:v[1],
                           user_id=lambda v:v[0])):
        self.urlbase=urlbase
        self.cas_login_url="%s/%s"%(self.urlbase,actions[0])
        self.cas_check_url="%s/%s"%(self.urlbase,actions[1])
        self.cas_logout_url="%s/%s"%(self.urlbase,actions[2])
        self.globals=g
        self.request=self.globals['request']
        self.session=self.globals['session']
        self.maps=maps
        http_host=self.request.env.http_x_forwarded_for
        if not http_host: http_host=self.request.env.http_host
        self.cas_my_url='http://%s%s'%( http_host, self.request.env.path_info )
    def login_url( self, next = "/" ):
        self.session.token=self._CAS_login()
        return next
    def logout_url( self, next = "/" ):
        self.session.token=None
        self.session.auth=None
        self._CAS_logout()
        return next
    def get_user( self ):
        user=self.session.token
        if user:
            d = {'source':'web2py cas'}
            for key in self.maps:
                d[key]=self.maps[key](user)
            return d
        return None
    def _CAS_login( self ):
        """
        exposed as CAS.login(request)
        returns a token on success, None on failed authentication
        """
        import urllib
        self.ticket=self.request.vars.ticket
        if not self.request.vars.ticket:
            self.globals['redirect']( "%s?service=%s"%( self.cas_login_url,
                                          self.cas_my_url ) )
        else:
            url="%s?service=%s&ticket=%s"%\
                                                           ( self.cas_check_url,
                                                            self.cas_my_url,
                                                            self.ticket )
            data=urllib.urlopen( url ).read().split( '\n' )
            if data[0]=='yes': return data[1].split( ':' )
        return None

    def _CAS_logout( self ):
        """
        exposed CAS.logout()
        redirects to the CAS logout page
        """
        import urllib
        self.globals['redirect']( "%s?service=%s"%( 
                                                  self.cas_logout_url,
                                                  self.cas_my_url ) )
