# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 0.5
@section LICENSE

This file is part of UrbanBEATS
Copyright (C) 2012  Peter M Bach

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import osr

def convertUTM2geographic(east, north, zone):    
    """Converts easting and northing to geographic coordinates based on the specific UTM zone"""
    utm_coords = osr.SpatialReference()
    utm_coords.SetWellKnownGeogCS("WGS84")
    if north > 0:
        isNorth = True
    else:
        isNorth = False
    utm_coords.SetUTM(zone, isNorth)
    
    geo_coords = utm_coords.CloneGeoCS()
    
    #Create transform component
    coordinate_transformation = osr.CoordinateTransformation(utm_coords, geo_coords)
    
    return coordinate_transformation.TransformPoint(east, north, 0)
    

def convertGeographic2UTM(longitude, latitude):
    """Sets up the UTM coordinate system and converts input longitude and latitude to UTM coordinates"""
    utm_coords = osr.SpatialReference()
    utm_coords.SetWellKnownGeogCS("WGS84")      #Creates geographic coordinate system

    utm_coords.SetUTM(getUTMzone(longitude), checkUTMsuffix(latitude))

    geo_coords = utm_coords.CloneGeogCS()       #Create a new geographic coordinate system by cloning the geoCS of the UTM system

    #create transform component
    coordinate_transformation = osr.CoordinateTransformation(geo_coords, utm_coords) #(<from>, <to>)
    
    return coordinate_transformation.TransformPoint(longitude, latitude, 0) # returns easting, northing, altitude    

def getUTMzone(longitude):
    """Returns the Zone that of the UTM projection to be used"""
    zone = int(1+(longitude + 180.0) / 6.0)
    return zone

def checkUTMsuffix(latitude):
    """Checks for whether UTM Zone lies North or South or Equator"""
    if latitude < 0.0:       #South of Equator
        return False
    else:               #North of Equator
        return True
