# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 0.5
@section LICENSE

This file is part of UrbanBEATS v1.0
Copyright (C) 2011,2012  Peter M Bach

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
from osgeo import ogr, osr
import os, sys

def getFileName(typemap):
    if typemap == "Lo":
        filename = "LocalityMap_UTM.shp"
    elif typemap == "La":
        filename = "Lakes.shp"
    elif typemap == "Ri":
        filename = "Rivers_UTM.shp"
    return filename


def getSpatialRefDataSource(layer):
    spatialRef = layer.GetSpatialRef()
    utmzone = spatialRef.GetUTMZone()   #in case this is needed returns +/- Zone Number (sign tells N/S)
    print "Spatial Reference (Proj4): " + str(spatialRef.ExportToProj4())
    return spatialRef, utmzone


def runLocalityImport(*args):
    if len(args) == 2:    
        filename = args[0]
        currentdir = args[1]
        os.chdir(currentdir)
    else:
        filename = args[0]
        currentdir = ""
    #filename = getFileName("Lo")    
    #currentdir = "C:/UrbanBEATSv1CaseStudies/"

    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    dataSource = driver.Open(filename, 0)
    if dataSource is None:
        print "Error, could not open file"
        sys.exit(1)
    layer = dataSource.GetLayer()    
    totfeatures = layer.GetFeatureCount()
    spatialRef = getSpatialRefDataSource(layer)    
    
    facilities = []    
    
    for i in range(totfeatures):
        #(1) Get the feature
        currentfeature = layer.GetFeature(i)
        geometryref = currentfeature.GetGeometryRef()        
        
        #(2) Obtain coordinates and attributes        
        code = currentfeature.GetFieldAsString("Fcode")
        area = currentfeature.GetFieldAsDouble("Area")
        imp = currentfeature.GetFieldAsDouble("Total_impe")/area
        roof = currentfeature.GetFieldAsDouble("Roof_area")
        demand = currentfeature.GetFieldAsDouble("Average_Wa")
        xpos = geometryref.GetX()
        ypos = geometryref.GetY()

        facil_prop = [code, xpos, ypos, area, imp, roof, demand]        

        #(3) Write to the dictionary
        facilities.append(facil_prop)
    return facilities


def runLakesImport(*args):
    if len(args) == 2:    
        filename = args[0]
        currentdir = args[1]
        os.chdir(currentdir)
    else:
        filename = args[0]
        currentdir = ""
    
    #filename = getFileName("La")    
    #currentdir = "C:/UrbanBEATSv1CaseStudies/"

    os.chdir(currentdir)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    dataSource = driver.Open(filename, 0)
    if dataSource is None:
        print "Error, could not open file"
        sys.exit(1)
    layer = dataSource.GetLayer()
    totfeatures = layer.GetFeatureCount()
    print totfeatures
    spatialRef = getSpatialRefDataSource(layer)
    print spatialRef    
    
    lakepoints = []     #centroid x, y, surface area of the lake
    
    for i in range(totfeatures):
        #(1) Get the feature
        currentfeature = layer.GetFeature(i)
        geometryref = currentfeature.GetGeometryRef()
        
        #(2) Obtain Centroid and Area
        centroid = geometryref.Centroid()   #ccccccc----<<<<
        centreX = centroid.GetX()        
        centreY = centroid.GetY()
        area = geometryref.GetArea()
        
        #(3) Write to output vector
        lakepoints.append([centreX, centreY, area])        
        
    return lakepoints


def runRiverImport(*args):
    if len(args) == 2:    
        filename = args[0]
        currentdir = args[1]
        os.chdir(currentdir)
    else:
        filename = args[0]
        currentdir = ""
        
    #filename = getFileName("Ri")    
    #currentdir = "C:/UrbanBEATSv1CaseStudies/"

    os.chdir(currentdir)
    driver = ogr.GetDriverByName('ESRI Shapefile')
    
    dataSource = driver.Open(filename, 0)
    if dataSource is None:
        print "Error, could not open file"
        sys.exit(1)
    layer = dataSource.GetLayer()
    totfeatures = layer.GetFeatureCount()
    print totfeatures    
    spatialRef = getSpatialRefDataSource(layer)
    print spatialRef    
    
    riverpoints = []    
    for i in range(totfeatures):
        currentfeature = layer.GetFeature(i)
        geometrydetail = currentfeature.GetGeometryRef()    
        if geometrydetail.GetGeometryType() == 2:
            print geometrydetail.GetPointCount()
            getAllPointsInRiverFeature(riverpoints, geometrydetail)
        elif geometrydetail.GetGeometryType() == 5:
            print geometrydetail.GetGeometryCount()
            linestrings = disassembleMultiDataSource(geometrydetail)
            for j in range(len(linestrings)):
                getAllPointsInRiverFeature(riverpoints, linestrings[j])
    return riverpoints
    

def getAllPointsInRiverFeature(riverpoints, geometrydetail):
    point_count = geometrydetail.GetPointCount()
    for i in range(point_count):
        x = geometrydetail.GetX(i)
        y = geometrydetail.GetY(i)
        riverpoints.append([x, y])
    return riverpoints


def disassembleMultiDataSource(multigeometry):
    multigeomarray = []
    geom_count = multigeometry.GetGeometryCount()
    for i in range(geom_count):
        multigeomarray.append(multigeometry.GetGeometryRef(i))
    return multigeomarray