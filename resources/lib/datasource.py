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
                '',
                ADDON_BASE_PATH + '/resources/assets/banner-fktv.png',
                ADDON_BASE_PATH + '/resources/assets/logo-fktv.png',
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
                '',
                ADDON_BASE_PATH + '/resources/assets/banner-ptv.png',
                ADDON_BASE_PATH + '/resources/assets/logo-ptv.png',
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
                '',
                ADDON_BASE_PATH + '/resources/assets/banner-ps.png',
                ADDON_BASE_PATH + '/resources/assets/logo-ps.png',
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
                '',
                ADDON_BASE_PATH + '/resources/assets/banner-mgtv.png',
                ADDON_BASE_PATH + '/resources/assets/logo-mgtv.png',
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
        pass

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