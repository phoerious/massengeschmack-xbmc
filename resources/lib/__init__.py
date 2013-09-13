# -*- coding: utf-8 -*-
# 
# Massengeschmack XBMC add-on
# Copyright (C) 2013 by Janek Bevendorff
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

import xbmcgui
import urllib2

from globalvars import *
from resources.lib.listing import Listing, ListItem
from resources.lib.datasource import DataSource, FKTVDataSource

# helper functions

def openHTTPConnection(uri):
    """
    Open an HTTP connection and return the connection handle.
    
    @type uri: str
    @param uri: the request URI
    @return: urllib2 request handle
    """
    request = urllib2.Request(uri)
    request.add_header('User-Agent', HTTP_USER_AGENT)
    return urllib2.urlopen(request)

def probeLoginCrendentials(username, password):
    """
    Test if the given login credentials are correct by sending a test request
    and install HTTP authentication handler.
    
    @type username: str
    @type password: str
    @return: true if login was successful
    """
    
    dialog = xbmcgui.DialogProgress()
    dialog.create(ADDON.getLocalizedString(30104))
    
    ok = False
    passwordManager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passwordManager.add_password(None, HTTP_BASE_URI, username, password)
    authHandler = urllib2.HTTPBasicAuthHandler(passwordManager)
    opener = urllib2.build_opener(authHandler)
    urllib2.install_opener(opener)
    
    dialog.update(50)
    
    try:
        handle = openHTTPConnection(HTTP_BASE_URI + 'feed/all/hd.xml')
    except IOError, e:
        print e
    else:
        handle.close()
        ok = True
    
    dialog.update(100)
    del dialog
    
    return ok