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

import xbmc
import xbmcplugin
import xbmcgui
import json
import urllib

from globalvars import *

class Listing:
    def generate(self, source):
        """
        Generate listing from data source.
        
        @type source: DataSource
        @param source: the data source object
        """
        items = source.getListItems()
        for i in items:
            self.__addDir(i)
    
    def show(self):
        """
        Show the listing after it has been generated.
        """
        xbmcplugin.endOfDirectory(ADDON_HANDLE)
        xbmcplugin.setContent(ADDON_HANDLE, 'movies')
        self.setViewMode(503)
    
    def setViewMode(self, id):
        """
        Set the view mode of the current listing.
        
        @type id: int
        @param id: the view mode ID from the current skin
        """
        xbmc.executebuiltin('Container.SetViewMode(' + str(id) + ')')
    
    def __addDir(self, listItem):
        xbmcListItem = xbmcgui.ListItem(listItem.getData('name'), iconImage=listItem.getData('thumbnail'), thumbnailImage=listItem.getData('thumbnail'))
        xbmcListItem.setInfo(type='video', infoLabels=listItem.getData('metaData'))
        xbmcListItem.setProperty('fanart_image', listItem.getData('fanart'))
        xbmcplugin.addDirectoryItem(ADDON_HANDLE, url=listItem.getData('url'), listitem=xbmcListItem, isFolder=listItem.getData('isFolder'))


class ListItem:
    def __init__(self, name='', url='', thumbnail='', fanart='', metaData={}, isFolder=True):
        """
        Generate list item from given parameters.
        
        @type name: str
        @param name: the display name of the list item
        @type url: str
        @param url: the addon URL this item points to (should not be a real Internet URL)
        @type thumbnail: str
        @param thumbnail: the path/URL to a thumbnail image
        @type fanart: str
        @param fanart: the path/URL to a fanart image
        @type metaData: dict
        @param metaData: meta data for this list item as passed to xbmcgui.ListItem()
        @type isFolder: bool
        @param isFolder: True if this item is a folder
        """
        self.__data = {
            'name'      : name,
            'url'       : url,
            'thumbnail' : thumbnail,
            'fanart'    : fanart,
            'metaData'  : metaData,
            'isFolder'  : isFolder
        }
    
    def setData(self, key, value):
        """
        Set a value for this list item.
        
        @type key: str
        @param key: the name of the data record
        @type value: mixed
        @param value: the data (either a string, a dict or a bool)
        """
        self.__data[key] = value
    
    def getData(self, key):
        """
        Get specific data from this list item.
        
        @type key: str
        @param key: which data to retrieve (name, url, iconImage, metaData)
        @return mixed: the data or '' if nothing has been set or key is invalid
        """
        if key in self.__data:
            return self.__data[key]
        
        return ''
    
    def getURLData(self, key):
        """
        Get specific URL encoded data from this list item.
        
        @type key: str
        @param key: which data to retrieve (name, url, iconImage, metaData)
        @return str: the data or '' if nothing has been set of key is invalid
                     (non-string data will be JSON encoded)
        """
        
        if key in self.__data:
            if type(self.__data[key]) == dict:
                return urllib.quote(self.__JSONEncode(self.__data[key]))
            if type(self.__data[key]) == bool:
                return '1' if True == self.__data[key] else '0'
            
            return urllib.quote(self.__data[key])
        
        return ''
    
    def getJSONMetaDataString(self):
        """
        Return a JSON encoded string of all meta data.
        
        @return: the encoded data
        """
        return self.__JSONEncode(self.metaData)
    
    def __JSONEncode(self, data):
        return json.dumps(data, separators=(',', ':'))