# -*- coding: utf-8 -*-
# 
# Massengeschmack Kodi add-on
# Copyright (C) 2013-2016 by Janek Bevendorff
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

import json
import os
import glob
from resources.lib.listing import *


class DataSource(object):
    """
    Generic DataSource class.
    This class can either be subclassed or bootstrapped with a JSON definition
    for creating a custom DataSource.
    """

    class Submodule:
        """
        DataSource submodule DTO.
        """
        def __init__(self):
            self.name = None    # type: str
            """Name of the submodule."""

            self.ids = []   # type: list of int
            """Feed ids contained in this submodule."""

            self.moduleMetaData = {}    # type: dict
            """Metadata for the submodule (int values can be used to reference i18n strings)."""

            self.isActive = True    # type: bool
            """Whether this submodule is currently active."""

        def __eq__(self, other):
            if type(other) is str:
                return self.name == other
            return self.name == other.name

        def __hash__(self):
            return self.name.__hash__()

        def getModuleTitle(self):
            """
            Get display title for current submodule.

            @rtype: str
            @return: submodule title to be displayed in listings
            """
            title = self.moduleMetaData.get('Title', ADDON.getLocalizedString(30198))
            if not self.isActive:
                title += ' ' + ADDON.getLocalizedString(30199)
            return title

    def __init__(self):
        self.id = None  # type: int
        """Numeric ID of the show."""

        self.moduleName = None  # type: str
        """Internal module name."""

        self.sortOrder = 0  # type: int
        """Show listing sort order."""

        self.showMetaData = {}    # type: dict
        """Global meta data for the show  (int values can be used to reference i18n strings)."""

        self.availableQualities = []    # type: list
        """Available quality settings for this DataSource."""

        self.bannerPath = None  # type: str
        """Path to banner image file."""

        self.fanartPath = None  # type: str
        """Path to fanart image file."""

        self.isActive = True    # type: bool
        """Whether the show is currently active."""

        self.submodules = []    # type: list of DataSource.Submodule
        """Available submodules."""

    def __eq__(self, other):
        return self.id == other.id

    def __hash__(self):
        return self.id.__hash__()

    def __getitem__(self, item):
        return self.submodules[item]

    @classmethod
    def bootstrap(cls, jsonFile):
        """
        Bootstrap new DataSource instance from given JSON definition file.

        @type jsonFile: str
        @param jsonFile: path to JSON bootstrap file
        @rtype: DataSource
        @return bootstrapped DataSource
        """

        def __localizeDict(d):
            for k in d:
                d[k] = ADDON.getLocalizedString(d[k]) if type(d[k]) is int else d[k]
            return d

        with open(jsonFile, 'r') as f:
            jd = json.load(f, 'utf-8')

        ds = cls()

        ds.moduleName = os.path.basename(jsonFile).replace('.json', '')
        ds.id         = jd.get('id', ds.id)
        ds.sortOrder  = jd.get('order', ds.sortOrder)
        ds.isActive   = jd.get('active', ds.isActive)

        ds.availableQualities.extend(jd.get('qualities', []))
        ds.showMetaData.update(__localizeDict(jd.get('metadata', {})))

        if 'banner' in jd:
            ds.bannerPath = ADDON_BASE_PATH + '/resources/media/' + jd['banner']
        if 'fanart' in jd:
            ds.bannerPath = ADDON_BASE_PATH + '/resources/media/' + jd['fanart']

        sm = jd.get('submodules', [])
        for i in sm:
            s = cls.Submodule()
            s.name     = i.get('name', s.name)
            s.isActive = i.get('active', s.isActive)
            s.ids.extend(i.get('ids', []))
            s.moduleMetaData.update(__localizeDict(i.get('metadata', {})))
            ds.submodules.append(s)

        return ds

    def getQuality(self):
        """
        Get currently selected quality setting.

        @rtype: str
        @return: quality identifier (best, hd, mobile, audio), None if no quality settings available
        """
        audioOnly = ADDON.getSetting('content.audioOnly')

        quality = None
        if 'true' == audioOnly and 'audio' in self.availableQualities:
            quality = 'audio'
        else:
            qualitySetting = int(ADDON.getSetting('content.quality'))
            if 0 == qualitySetting:
                quality = 'best'
            elif 1 == qualitySetting:
                quality = 'hd'
            elif 2 == qualitySetting:
                quality = 'mobile'

            if quality not in self.availableQualities:
                quality = self.availableQualities[0] if self.availableQualities else None

        return quality

    def getCurrentSubmoduleName(self):
        """
        Get the name of the current submodule.

        @rtype: str
        @return: submodule name or None if we're not in a submodule
        """
        submodule = None
        if 'submodule' in ADDON_ARGS and ADDON_ARGS['submodule'] in self.submodules:
            submodule = ADDON_ARGS['submodule']
        return submodule
    
    def getContentMode(self):
        """
        Get the view mode for the listing content.
        
        Content mode is usually either 'tvshows' or 'episodes', but can
        also be any other valid value for xbmcplugin.setContent().

        @rtype: bool
        @return content mode
        """
        if self.getCurrentSubmoduleName():
            return 'episodes'
        return 'tvshows'

    def getShowTitle(self):
        """
        Get display title for current show.

        @rtype: str
        @return: show title to be displayed in listings
        """
        title = self.showMetaData.get('Title', ADDON.getLocalizedString(30198))
        if not self.isActive:
            title += ' ' + ADDON.getLocalizedString(30199)
        return title

    def buildFeedURL(self, ids, quality):
        """
        Build a feed URL which points to an RSS feed which is filtered by the given IDs.

        This method relies on self.id being set properly in derived classes.

        @type ids: list
        @param ids: a list of numeric IDs of all sub shows to filter by
        @type quality: str
        @param quality: the movie quality (either 'best', 'hd', 'mobile' or 'audio')
        @rtype: str
        @return feed URL string
        """
        url = HTTP_BASE_FEED_URI

        first = True
        for i in ids:
            if not first:
                url += 'x'
            first = False
            url += str(self.id) + '-' + str(i)

        url += '/' + quality + '.xml'

        return url

    def getListItems(self):
        """
        Generate a list of L{resources.lib.listing.ListItem} objects for the current data source.

        @rtype: list of resources.lib.listing.ListItem
        @return: generated ListItems
        """
        submoduleName = self.getCurrentSubmoduleName()

        # show selection list if there are several submodules and we're not inside one already
        if len(self.submodules) > 1 and not submoduleName:
            for i in self.__getBaseList():
                yield i
            return

        # if there is only one submodule, don't show a selection list
        if len(self.submodules) == 1 and not submoduleName:
            submoduleName = self.submodules[0].name

        # shouldn't happen
        if submoduleName is None:
            raise RuntimeError("No valid submodule given.")

        submodule = next(s for s in self.submodules if s.name == submoduleName)
        data      = resources.lib.parseRSSFeed(self.buildFeedURL(submodule.ids, self.getQuality()), True)
        for i in data:
            iconimage = i["thumbUrl"]
            date      = resources.lib.parseUTCDateString(i['pubdate']).strftime('%d.%m.%Y')
            metaData  = {
                'Title'     : i['title'],
                'Genre'     : self.showMetaData.get('Genre', ''),
                'Date'      : date,
                'Country'   : self.showMetaData.get('Country', ''),
                'Plot'      : i['description'],
                'Duration'  : int(i['duration']) / 60
            }
            streamInfo = {
                'duration' : i['duration']
            }

            yield ListItem(
                self.id,
                i['title'],
                resources.lib.assemblePlayURL(i['url'], i['title'], iconimage, metaData, streamInfo),
                iconimage,
                self.fanartPath,
                metaData,
                streamInfo,
                False
            )

    def __getBaseList(self):
        for i in self.submodules:
            yield ListItem(
                self.id,
                i.getModuleTitle(),
                resources.lib.assembleListURL(self.moduleName, i.name),
                self.bannerPath,
                self.fanartPath,
                {
                    'Title': i.moduleMetaData.get('Title', ''),
                    'Plot': i.moduleMetaData.get('Plot', '')
                }
            )


class OverviewDataSource(DataSource):
    """
    Overview DataSource for displaying an overview of all available shows.
    This is the root DataSource that is displayed at top level.
    """

    @classmethod
    def bootstrap(cls, jsonFile):
        raise NotImplementedError

    def getListItems(self):
        dataSources = []

        # create instances of all DataSource subclasses (except this one)
        subclasses = DataSource.__subclasses__()
        for i in (s for s in subclasses if s is not self.__class__):
            dataSources.append(i())

        # boostrap any other DataSources from available bootstrap files
        bootstrapFiles = glob.glob(ADDON_BOOTSTRAP_PATH + '/*.json')
        for i in bootstrapFiles:
            dataSources.append(DataSource.bootstrap(i))

        # sort DataSources as defined in each DataSource's sortOrder property
        dataSources.sort(key=lambda x: x.sortOrder)

        for i in dataSources:
            yield ListItem(
                i.id,
                i.getShowTitle(),
                resources.lib.assembleListURL(i.moduleName),
                i.bannerPath,
                i.fanartPath,
                i.showMetaData
            )


def createDataSource(module=None):
    """
    Create a L{DataSource} object based on the given module name.
    If no module name is given, an overview DataSource will be generated.
    
    @type module: str
    @keyword module: the magazine name, None or empty string for overview
    @rtype: DataSource
    @return: generated DataSource
    """
    if not module:
        return OverviewDataSource()

    bootstrapFile = ADDON_BOOTSTRAP_PATH + '/' + module + '.json'
    if os.path.isfile(bootstrapFile):
        return DataSource.bootstrap(bootstrapFile)
    else:
        raise RuntimeError("Invalid module {}".format(module))

