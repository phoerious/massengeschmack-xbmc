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
import urllib
import urllib2
import email.utils
import datetime
import json
from xml.dom import minidom
from HTMLParser import HTMLParser

from globalvars import *
from resources.lib.listing import Listing, ListItem
from resources.lib.datasource import DataSource, FKTVDataSource

# helper functions

def openHTTPConnection(uri):
    """
    Open an HTTP(S) connection and return the connection handle.
    
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
    
    if not 'cmd' in ADDON_ARGS:
        dialog = xbmcgui.DialogProgress()
        dialog.create(ADDON.getLocalizedString(30104))
    
    ok = False
    passwordManager = urllib2.HTTPPasswordMgrWithDefaultRealm()
    passwordManager.add_password(None, HTTP_BASE_URI, username, password)
    authHandler = urllib2.HTTPBasicAuthHandler(passwordManager)
    opener = urllib2.build_opener(authHandler)
    urllib2.install_opener(opener)
    
    if not 'cmd' in ADDON_ARGS:
        dialog.update(50)
    
    try:
        handle = openHTTPConnection(HTTP_BASE_URI + 'feed/all/hd.xml')
    except IOError, e:
        pass
    else:
        handle.close()
        ok = True
    
    if not 'cmd' in ADDON_ARGS:
        dialog.update(100)
        del dialog
    
    return ok

def parseRSSFeed(feed, fetch=False):
    """
    Parse an RSS feed and create a list of dicts from the XML data.
    This function is necessary because we can't rely on any third-party
    RSS modules.
    
    if fetch is true, feed is assumed to be a URI to an RSS feed instead of
    its XML contents.
    
    The returned list has to following format:
    [
        {
            'title'       : summary1,
            'subtitle'    : subtitle1,
            'pubdate'     : pubdate1,
            'description' : description1,
            'link'        : link1,
            'guid'        : guid1,
            'url'         : url1,
            'duration'    : duration1
        },
        {
            'title'       : summary2,
            'subtitle'    : subtitle2,
            'pubdate'     : pubdate2,
            'description' : description2,
            'link'        : link2,
            'guid'        : guid2,
            'url'         : url2,
            'duration'    : duration2
        },
        ...
    ]
    
    @type feed: str
    @param feed: the RSS feed as XML string or a URI if fetch is true
    @type fetch: bool
    @param fetch: True if feed is a URI, default is false
    @return a list of dicts with the parsed feed data
    """
    if fetch:
        response = None
        try:
            response = openHTTPConnection(feed)
        except IOError, e:
            xbmcgui.Dialog().ok(ADDON.getLocalizedString(39902), ADDON.getLocalizedString(39903) + '[CR]Error: {0}'.format(e.strerror))
            return domDict
        feed = response.read()
    
    dom = minidom.parseString(feed)
    
    data   = []
    parser = HTMLParser()
    for node in dom.getElementsByTagName('item'):
        # convert duration string to seconds
        duration = node.getElementsByTagName('itunes:duration')[0].firstChild.nodeValue
        h, m, s  = map(int, duration.split(':'))
        duration = datetime.timedelta(hours=h, minutes=m, seconds=s).seconds
        
        data.append({
            'title'       : parser.unescape(node.getElementsByTagName('title')[0].firstChild.nodeValue),
            'subtitle'    : parser.unescape(node.getElementsByTagName('itunes:subtitle')[0].firstChild.nodeValue),
            'pubdate'     : parser.unescape(node.getElementsByTagName('pubDate')[0].firstChild.nodeValue),
            'description' : parser.unescape(node.getElementsByTagName('description')[0].firstChild.nodeValue),
            'link'        : parser.unescape(node.getElementsByTagName('link')[0].firstChild.nodeValue),
            'guid'        : parser.unescape(node.getElementsByTagName('guid')[0].firstChild.nodeValue),
            'url'         : parser.unescape(node.getElementsByTagName('enclosure')[0].getAttribute('url')),
            'duration'    : duration
        })
    
    return data

def parseUTCDateString(date):
    """
    Parse an RFC 2822 date format to a datetime object.
    
    @type date: str
    @param date: the date string
    @return a datetime object
    """
    return datetime.datetime.fromtimestamp(email.utils.mktime_tz(email.utils.parsedate_tz(date)))

def dictUrlEncode(data):
    """
    Create a URL encoded JSON string from a given dict or list.
    
    @type data: dict
    @param data: the data structure
    """
    return urllib.quote(json.dumps(data, separators=(',', ':')))

def assembleListURL(module=None, submodule=None, mode=None):
    """
    Assemble a plugin:// url with a list command.
    
    @type module: str
    @param module: the name of the module to list
    @type submodule: str
    @param submodule: the name of the sub module to list (requires module to be set)
    @type mode: str
    @param mode: a mode for a submodule (requires submodule to be set)
    """
    url = 'plugin://' + ADDON_ID + '/?cmd=list'
    if None == module:
        return url
    
    url += '&module=' + urllib.quote(module)
    if None != submodule:
        url += '&submodule=' + urllib.quote(submodule)
    if None != submodule and None != mode:
        url += '&mode=' + urllib.quote(mode)
    
    return url
    

def assemblePlayURL(url, name='', iconImage='', metaData={}, streamInfo={}):
    """
    Assemble a plugin:// URL with a play command for a given URL.
    
    @type url: str
    @param url: the real URL of the media file
    @type name: str
    @param name: a nice human-readable name
    @type iconImage: str
    @param iconImage: a URL to a thumbnail image
    @type metaData: dict
    @param metaData: metaData for the media file
    @type streamInfo: dict
    @param: streamInfo: technical info about the stream (such as the duration or resolution)
    """
    return 'plugin://' + ADDON_ID + '/?cmd=play&url=' + urllib.quote(url) + \
           '&name=' + urllib.quote(name) + '&iconimage=' + urllib.quote(iconImage) + \
           '&metadata=' + dictUrlEncode(metaData) + \
           '&streaminfo=' + dictUrlEncode(streamInfo)