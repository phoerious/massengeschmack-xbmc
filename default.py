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
import urllib2

from globalvars import *
import resources.lib as lib

ok = True

# show warning and open settings if login data have not been configured or if the credentials are invalid
if '' == ADDON.getSetting('account.username').strip() or '' == ADDON.getSetting('account.password').strip():
    dialog = xbmcgui.Dialog()
    dialog.ok(ADDON.getLocalizedString(30100), ADDON.getLocalizedString(30101))
    ok = False
elif not lib.probeLoginCrendentials(ADDON.getSetting('account.username'), ADDON.getSetting('account.password')):
    dialog = xbmcgui.Dialog()
    dialog.ok(ADDON.getLocalizedString(30102), ADDON.getLocalizedString(30103))
    ok = False
    
if not ok:
    ADDON.openSettings()
else:
    xbmcplugin.endOfDirectory(ADDON_HANDLE)
    xbmcplugin.setContent(ADDON_HANDLE, 'movies')
    xbmc.executebuiltin('Container.SetViewMode(503)')

