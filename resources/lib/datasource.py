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
from globalvars import *
import resources.lib
from resources.lib.listing import *

class DataSource:
    def getListItems(self):
        """
        Generate a list of ListeItem objects for the current data source.
        @abstract
        """
        return [
            # Fernsehkritik-TV
            ListItem(
                ADDON.getLocalizedString(30200),
                'plugin://' + ADDON_ID + '/?cmd=list&module=fktv',
                ADDON_BASE_PATH + '/resources/assets/banner-fktv.png',
                ADDON_BASE_PATH + '/resources/assets/fanart-fktv.jpg',
                {
                    'Title': ADDON.getLocalizedString(30200),
                    'Director':'Holger Kreymeier, Nils Beckmann, Daniel Gusy',
                    'Genre': ADDON.getLocalizedString(30201),
                    'Premiered':'07.04.2007',
                    'Country': ADDON.getLocalizedString(30202),
                    'Plot': ADDON.getLocalizedString(30203)
                }
            ),
            # Pantoffel-TV
            ListItem(
                ADDON.getLocalizedString(30210),
                'plugin://' + ADDON_ID + '/?cmd=list&module=ptv',
                ADDON_BASE_PATH + '/resources/assets/banner-ptv.png',
                ADDON_BASE_PATH + '/resources/assets/fanart-ptv.jpg',
                {
                    'Title': ADDON.getLocalizedString(30210),
                    'Director':'Holger Kreymeier, Jenny von Gagern, Steven Gräwe, Michael Stock',
                    'Genre': ADDON.getLocalizedString(30211),
                    'Premiered':'17.06.2013',
                    'Country': ADDON.getLocalizedString(30212),
                    'Plot': ADDON.getLocalizedString(30213)
                }
            ),
            # Pressesch(l)au
            ListItem(
                ADDON.getLocalizedString(30220),
                'plugin://' + ADDON_ID + '/?cmd=list&module=ps',
                ADDON_BASE_PATH + '/resources/assets/banner-ps.png',
                ADDON_BASE_PATH + '/resources/assets/fanart-ps.jpg',
                {
                    'Title': ADDON.getLocalizedString(30220),
                    'Director':'Holger Kreymeier, Steven Gräwe, Daniel Gusy',
                    'Genre': ADDON.getLocalizedString(30221),
                    'Premiered':'01.08.2013',
                    'Country': ADDON.getLocalizedString(30222),
                    'Plot': ADDON.getLocalizedString(30223)
                }
            ),
            # Massengeschmack-TV
            ListItem(
                ADDON.getLocalizedString(30230),
                'plugin://' + ADDON_ID + '/?cmd=list&module=mgtv',
                ADDON_BASE_PATH + '/resources/assets/banner-mgtv.png',
                ADDON_BASE_PATH + '/resources/assets/fanart-mgtv.jpg',
                {
                    'Title': ADDON.getLocalizedString(30230),
                    'Director':'Holger Kreymeier',
                    'Genre': ADDON.getLocalizedString(30231),
                    'Premiered':'05.08.2013',
                    'Country': ADDON.getLocalizedString(30232),
                    'Plot': ADDON.getLocalizedString(30233)
                }
            ),
        ]

class FKTVDataSource(DataSource):
    def getListItems(self):
        audioOnly = ADDON.getSetting('content.audioOnly')
        
        quality = None
        if 'true' == audioOnly:
            quality = 'audio'
        else:
            if 0 == int(ADDON.getSetting('content.quality')):
                quality = 'best'
            else:
                quality = 'mobile'
        
        submodule = None
        if 'submodule' in ADDON_ARGS and ADDON_ARGS['submodule'] in self.__urls[quality]:
            submodule = ADDON_ARGS['submodule']
        
        if None == submodule:
            return self.__getBaseList()
        
        data      = resources.lib.parseRSSFeed(self.__urls[quality][submodule], True)
        listItems = []
        
        for i in data:
            iconimage = self.__getThumbnailURL(i['guid'])
            print iconimage
            date      = resources.lib.parseUTCDateString(i['pubdate']).strftime('%d.%m.%Y')
            metaData  = {
                'Title'     : i['title'],
                'Genre'     : ADDON.getLocalizedString(30201),
                'Date'      : date,
                'Premiered' : date,
                'Country'   : ADDON.getLocalizedString(30232),
                'Plot'      : i['description'],
                'Duration'  : int(i['duration']) / 60
            }
            streamInfo = {
                'duration' : i['duration']
            }
            
            listItems.append(
                ListItem(
                    i['title'],
                    'plugin://' + ADDON_ID + '/?cmd=play&url=' + urllib.quote(i['url']) +
                        '&name=' + urllib.quote(i['title']) + '&iconimage=' + urllib.quote(iconimage) +
                        '&metadata=' + resources.lib.dictUrlEncode(metaData) +
                        '&streaminfo=' + resources.lib.dictUrlEncode(streamInfo),
                    iconimage,
                    ADDON_BASE_PATH + '/resources/assets/fanart-fktv.jpg',
                    metaData,
                    streamInfo,
                    False
                )
            )
        
        return listItems
    
    def __getThumbnailURL(self, guid):
        basePath1 = 'http://fernsehkritik.tv/images/magazin/'
        basePath2 = 'http://massengeschmack.tv/img/mag/'
        
        if 'fktv' == guid[0:4]:
            return basePath1 + 'folge' + guid[4:] + '@2x.jpg'
        if 'postecke' == guid[0:8]:
            return basePath2 + 'postecke.jpg'
        if 'interview-' == guid[0:10]:
            return basePath2 + guid[10:] + '.jpg'
        
        return basePath2 + guid + '.jpg'
    
    def __getBaseList(self):
        return [
            # All
            ListItem(
                ADDON.getLocalizedString(30300),
                'plugin://' + ADDON_ID + '/?cmd=list&module=fktv&submodule=all',
                ADDON_BASE_PATH + '/resources/assets/banner-fktv.png',
                ADDON_BASE_PATH + '/resources/assets/fanart-fktv.jpg',
                {
                    'Title': ADDON.getLocalizedString(30300),
                    'Country': ADDON.getLocalizedString(30202),
                    'Plot': ADDON.getLocalizedString(30350)
                }
            ),
            # Episodes
            ListItem(
                ADDON.getLocalizedString(30301),
                'plugin://' + ADDON_ID + '/?cmd=list&module=fktv&submodule=episodes',
                ADDON_BASE_PATH + '/resources/assets/banner-fktv.png',
                ADDON_BASE_PATH + '/resources/assets/fanart-fktv.jpg',
                {
                    'Title': ADDON.getLocalizedString(30301),
                    'Country': ADDON.getLocalizedString(30202),
                    'Plot': ADDON.getLocalizedString(30351)
                }
            ),
            # Postecke
            ListItem(
                ADDON.getLocalizedString(30352),
                'plugin://' + ADDON_ID + '/?cmd=list&module=fktv&submodule=postecke',
                ADDON_BASE_PATH + '/resources/assets/banner-fktv.png',
                ADDON_BASE_PATH + '/resources/assets/fanart-fktv.jpg',
                {
                    'Title': ADDON.getLocalizedString(30352),
                    'Country': ADDON.getLocalizedString(30202),
                    'Plot': ADDON.getLocalizedString(30353)
                }
            ),
            # Interviews
            ListItem(
                ADDON.getLocalizedString(30302),
                'plugin://' + ADDON_ID + '/?cmd=list&module=fktv&submodule=interviews',
                ADDON_BASE_PATH + '/resources/assets/banner-fktv.png',
                ADDON_BASE_PATH + '/resources/assets/fanart-fktv.jpg',
                {
                    'Title': ADDON.getLocalizedString(30302),
                    'Country': ADDON.getLocalizedString(30202),
                    'Plot': ADDON.getLocalizedString(30354)
                }
            ),
            # Extras
            ListItem(
                ADDON.getLocalizedString(30303),
                'plugin://' + ADDON_ID + '/?cmd=list&module=fktv&submodule=extras',
                ADDON_BASE_PATH + '/resources/assets/banner-fktv.png',
                ADDON_BASE_PATH + '/resources/assets/fanart-fktv.jpg',
                {
                    'Title': ADDON.getLocalizedString(30303),
                    'Country': ADDON.getLocalizedString(30202),
                    'Plot': ADDON.getLocalizedString(30355)
                }
            )
        ]
    
    __urls = {
        'best' : {
            'all'        : HTTP_BASE_URI + 'feed/1-1x1-2x1-3x1-4/hd.xml',
            'episodes'   : HTTP_BASE_URI + 'feed/1-1/hd.xml',
            'postecke'   : HTTP_BASE_URI + 'feed/1-2/hd.xml',
            'interviews' : HTTP_BASE_URI + 'feed/1-3/hd.xml',
            'extras'     : HTTP_BASE_URI + 'feed/1-4/hd.xml'
        },
        'mobile' : {
            'all'        : HTTP_BASE_URI + 'feed/1-1x1-2x1-3x1-4/mobile.xml',
            'episodes'   : HTTP_BASE_URI + 'feed/1-1/mobile.xml',
            'postecke'   : HTTP_BASE_URI + 'feed/1-2/mobile.xml',
            'interviews' : HTTP_BASE_URI + 'feed/1-3/mobile.xml',
            'extras'     : HTTP_BASE_URI + 'feed/1-4/mobile.xml'
        },
        'audio' : {
            'all'        : HTTP_BASE_URI + 'feed/1-1x1-2x1-3x1-4/audio.xml',
            'episodes'   : HTTP_BASE_URI + 'feed/1-1/audio.xml',
            'postecke'   : HTTP_BASE_URI + 'feed/1-2/audio.xml',
            'interviews' : HTTP_BASE_URI + 'feed/1-3/audio.xml',
            'extras'     : HTTP_BASE_URI + 'feed/1-4/audio.xml'
        }
    }
    __thumbnailURLs = {
        'episodes' : 'http://fernsehkritik.tv/images/magazin/{0}@2x.jpg'
    }

def createDataSource(module=''):
    """
    Create a data source object based on the magazine name.
    If left empty, an overview data source will be generated.
    
    @type module: str
    @keyword module: the magazine name (fktv, ptv, pschlau, mgtv, ...)
    @return: DataSource instance
    """
    if 'fktv' == module:
        return FKTVDataSource()
    else:
        return DataSource()