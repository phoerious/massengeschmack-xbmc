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

class Listing:
    def generate(self, source):
        """
        Generate listing from data source.
        
        @type source: DataSource
        @param source: the data source object
        """
        pass
    
    def show():
        """
        Show the listing after it has been generated.
        """
        pass
    
    def setViewMode(self, id):
        """
        Set the view mode of the current listing.
        
        @type id: int
        @param id: the view mode ID from the current skin
        """
        pass
    
    def __addDir(self, name, url):
        pass