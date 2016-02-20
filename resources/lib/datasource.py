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
from datetime import datetime
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
            """Feed IDs contained in this submodule."""

            self.feedName = None    # type: str
            """Custom feed name (overrides automatically generated name from feed IDs)"""

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
                # rstrip() for removing workaround white-space for 16 char min-length issue
                # see <http://trac.kodi.tv/ticket/16599>
                title = title.rstrip() + ' ' + ADDON.getLocalizedString(30199)
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

        ds            = cls()
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
            s.feedName = i.get('feed_name', s.feedName)
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
        return 'episodes'

    def getShowTitle(self):
        """
        Get display title for current show.

        @rtype: str
        @return: show title to be displayed in listings
        """
        title = self.showMetaData.get('Title', ADDON.getLocalizedString(30198))
        if not self.isActive:
            # rstrip() for removing workaround white-space for 16 char min-length issue
            # see <http://trac.kodi.tv/ticket/16599>
            title = title.rstrip() + ' ' + ADDON.getLocalizedString(30199)
        return title

    def buildFeedURL(self, submodule, quality):
        """
        Build a feed URL which points to an RSS feed which is filtered by the given IDs.

        This method relies on self.id being set properly in derived classes.

        @type submodule: DataSource.Submodule
        @param submodule: submodule for which to generate the feed URL
        @type quality: str
        @param quality: the movie quality (either 'best', 'hd', 'mobile' or 'audio')
        @rtype: str
        @return feed URL string
        """
        url = HTTP_BASE_FEED_URI + '/'

        if submodule.feedName:
            url += submodule.feedName
        else:
            first = True
            for i in submodule.ids:
                if not first:
                    url += 'x'
                first = False
                url += str(self.id) + '-' + str(i)

        url += '/' + quality + '.xml'
        print(url)
        return url

    def getListItems(self):
        """
        Generate a list of L{resources.lib.listing.ListItem} objects for the current data source.

        @rtype: list of resources.lib.listing.ListItem
        @return: generator object with ListItems
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
        data      = resources.lib.parseRSSFeed(self.buildFeedURL(submodule, self.getQuality()), True)
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
        # create generator object of submodules with inactive submodules coming last
        for active in (True, False):
            for i in (s for s in self.submodules if s.isActive == active):
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


class DataSourceRegistry:
    """
    Decorator for registering custom DataSource classes.
    Any non-bootstrapped DataSource that shall be hooked into the DataSource list, needs to be decorated.
    The only exception is L{OverviewDataSource} which is always the root DataSource and
    therefore registered implicitly.
    """

    __dataSources = {}

    def __init__(self, moduleName):
        """
        Register class as DataSource. The specified moduleName will be used to automatically instantiate
        DataSources when that submodule is called via KODI URI.

        @type moduleName: str
        @param moduleName: module name to register for
        @return: decorated DataSource
        """
        self.__moduleName = moduleName

    def __call__(self, cls):
        if self.__moduleName not in self.__dataSources:
            self.__dataSources[self.__moduleName] = cls
        return self.__dataSources[self.__moduleName]

    @classmethod
    def getDataSources(cls):
        """
        Return a set of registered DataSource classes.

        @rtype: set of DataSource
        @return all registered DataSources
        """
        return set(cls.__dataSources.values())

    @classmethod
    def getDataSourceByName(cls, moduleName):
        """
        Get DataSource class by registered module name.

        @param moduleName: module name the DataSource was registered for
        @rtype DataSource
        @return: the DataSource class or None if no DataSource is registered under moduleName
        """
        return cls.__dataSources.get(moduleName, None)


class OverviewDataSource(DataSource):
    """
    Overview DataSource for displaying an overview of all registered show DataSources.
    This is the root DataSource that is displayed at top level.
    """

    @classmethod
    def bootstrap(cls, jsonFile):
        raise NotImplementedError

    def getListItems(self):
        dataSources = []

        # add all registered DataSources to the list
        for i in DataSourceRegistry.getDataSources():
            dataSources.append(i())

        # boostrap any remaining DataSources from available bootstrap files
        bootstrapFiles = glob.glob(ADDON_BOOTSTRAP_PATH + '/*.json')
        for i in bootstrapFiles:
            dataSources.append(DataSource.bootstrap(i))

        # sort DataSources as defined in each DataSource's sortOrder property
        dataSources.sort(key=lambda x: x.sortOrder)

        # create generator object of shows with inactive submodules coming last
        for active in (True, False):
            for i in (s for s in dataSources if s.isActive == active):
                yield ListItem(
                    i.id,
                    i.getShowTitle(),
                    resources.lib.assembleListURL(i.moduleName),
                    i.bannerPath,
                    i.fanartPath,
                    i.showMetaData
                )

    def getContentMode(self):
        return "tvshows"


@DataSourceRegistry('live')
class LiveDataSource(DataSource):
    """
    Custom DataSource for LIVE streams.
    """

    def __init__(self):
        super(LiveDataSource, self).__init__()

        self.id           = -9999
        self.moduleName   = 'live'
        self.sortOrder    = 600
        self.showMetaData = {
            'Title'    : ADDON.getLocalizedString(30270),
            'Country'  : ADDON.getLocalizedString(30202),
            'Plot'     : ADDON.getLocalizedString(30272)
        }
        self.bannerPath = ADDON_BASE_PATH + '/resources/media/banner-live.png'
        self.fanartPath = ADDON_BASE_PATH + '/resources/media/fanart-live.png'
        self.isActive   = True

        self.isLive     = False

        self.__shows    = resources.lib.getLiveShows()
        self.__current  = []
        self.__upcoming = []

        for i in self.__shows:
            if i['isLive']:
                self.isLive = True
                self.__current.append(i)
            else:
                self.__upcoming.append(i)

        # if there is a show live on air, mark it in the list and move it to the top
        if self.isLive:
            self.sortOrder = -10000
            self.showMetaData['Title'] = self.showMetaData['Title'].rstrip() + ' ' + ADDON.getLocalizedString(30278)

    @classmethod
    def bootstrap(cls, jsonFile):
        raise NotImplementedError

    def getListItems(self):
        if self.__current:
            yield ListItem(
                self.id,
                ADDON.getLocalizedString(30273),
                '#',
                self.__getThumbnailURL(0),
                self.fanartPath,
                {'Plot' : ADDON.getLocalizedString(30274)}
            )

            for i in self.__createShowListing(self.__current, True):
                yield i

        if self.__upcoming:
            yield ListItem(
                self.id,
                ADDON.getLocalizedString(30275),
                '#',
                self.__getThumbnailURL(0),
                self.fanartPath,
                {'Plot' : ADDON.getLocalizedString(30276)}
            )

            for i in self.__createShowListing(self.__upcoming):
                yield i

    def getContentMode(self):
        return 'episodes'

    def __createShowListing(self, shows, isLive=False):
        for i in shows:
            iconimage = self.__getThumbnailURL(i['pid'])
            plot      = i['oneliner']
            time      = datetime.fromtimestamp(float(i['begin'])).strftime('%d.%m.%Y, %H:%M:%S')
            date      = datetime.fromtimestamp(float(i['begin'])).strftime('%d.%m.%Y')
            name      = self.__getShowName(int(i['pid']))

            if not plot:
                plot = ''
            else:
                plot += '\n\n'

            plot += ADDON.getLocalizedString(30277).format(name, time)

            metaData  = {
                'Title'     : name,
                'Date'      : date,
                'Plot'      : plot
            }

            listName   = '    ' + name + ' -> ' + ADDON.getLocalizedString(30279).format(time)
            streamName = name + ' ' + ADDON.getLocalizedString(30278)

            isFolder = True
            if isLive:
                isFolder = False

            yield ListItem(
                self.id,
                listName,
                resources.lib.assemblePlayURL(self.__getStreamURL(i['showid']), streamName, iconimage, metaData),
                iconimage,
                self.fanartPath,
                metaData,
                isFolder=isFolder
            )

    @staticmethod
    def __getShowName(id):
        if -3 == id:
            # Livetalk
            name = ADDON.getLocalizedString(30280)
        elif 0 == id:
            # Massengeschmack-TV
            name = ADDON.getLocalizedString(30230)
        elif 1 == id:
            # FKTV
            name = ADDON.getLocalizedString(30200)
        elif 2 == id:
            # PantoffelTV
            name = ADDON.getLocalizedString(30210)
        elif 3 == id:
            # Pressesch(l)au
            name = ADDON.getLocalizedString(30220)
        elif 4 == id:
            # Pasch-TV
            name = ADDON.getLocalizedString(30240)
        elif 5 == id:
            # Netzprediger
            name = ADDON.getLocalizedString(30250)
        elif 6 == id:
            # Asynchron
            name = ADDON.getLocalizedString(30260)
        elif 7 == id:
            # Tonangeber
            name = ADDON.getLocalizedString(30264)
        elif 8 == id:
            # Hoaxilla-TV
            name = ADDON.getLocalizedString(30400)
        elif 9 == id:
            # Sakura
            name = ADDON.getLocalizedString(30290)
        elif 10 == id:
            # Migropolis
            name = ADDON.getLocalizedString(30410)
        else:
            name = '-'

        return name.rstrip()

    @staticmethod
    def __getStreamURL(showid):
        info = resources.lib.getLiveStreamInfo(showid)
        if not info:
            return '#'
        return info['url']

    @staticmethod
    def __getThumbnailURL(id):
        return HTTP_BASE_URI + '/img/logo' + str(id) + '_feed.jpg'


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
        ds = DataSourceRegistry.getDataSourceByName(module)
        if ds is None:
            raise RuntimeError("Invalid module {}".format(module))
        return ds()

