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
import xbmcgui
import xbmcaddon
import xbmcplugin
import json

from globalvars import *
import resources.lib as lib

ok = True

# show warning and open settings if login data have not been configured or if the credentials are invalid
if '' == ADDON.getSetting('account.username') or '' == ADDON.getSetting('account.password'):
    dialog = xbmcgui.Dialog()
    dialog.ok(ADDON.getLocalizedString(30100), ADDON.getLocalizedString(30101))
    ok = False
elif not lib.probeLoginCrendentials(ADDON.getSetting('account.username'), ADDON.getSetting('account.password')):
    dialog = xbmcgui.Dialog()
    dialog.ok(ADDON.getLocalizedString(30102), ADDON.getLocalizedString(30103))
    ok = False
    
if not ok:
    ADDON.openSettings()
    exit()

print ADDON_ARGS

# analyze URL
if not 'cmd' in ADDON_ARGS:
    ADDON_ARGS['cmd'] = 'list'

if 'list' == ADDON_ARGS['cmd']:
    listing    = lib.Listing()
    datasource = lib.datasource.createDataSource()
    if 'module' in ADDON_ARGS:
        datasource = lib.datasource.createDataSource(ADDON_ARGS['module'])
    listing.generate(datasource)
    listing.show()
    
elif 'play' == ADDON_ARGS['cmd']:
    name       = ''
    iconImage  = ''
    metaData   = {}
    streamInfo = {}
    if 'name' in ADDON_ARGS:
        name = ADDON_ARGS['name']
    if 'iconimage' in ADDON_ARGS:
        iconImage = ADDON_ARGS['iconimage']    
    if 'metadata' in ADDON_ARGS:
        metaData = json.loads(ADDON_ARGS['metadata'])
    if 'streaminfo' in ADDON_ARGS:
        streamInfo = json.loads(ADDON_ARGS['streaminfo'])
    
    listitem = xbmcgui.ListItem(name, iconImage=iconImage, thumbnailImage=iconImage)
    listitem.setInfo('video', metaData)
    listitem.addStreamInfo('video', streamInfo)
    playlist = xbmc.PlayList(1)
    playlist.clear()
    playlist.add(ADDON_ARGS['url'], listitem)
    xbmc.Player().play(playlist)
    playlist.clear()
    
else:
    raise RuntimeError(ADDON_ARGS['cmd'] + ': ' + ADDON.getLocalizedString(39901)) 