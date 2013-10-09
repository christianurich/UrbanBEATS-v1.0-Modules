# -*- coding: utf-8 -*-
"""
@file
@author Peter M Bach <peterbach@gmail.com>
@version 0.5
@section LICENSE

This file is part of VIBe2
Copyright (C) 2011 Peter M Bach

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
"""

#from pyvibe import *
from pydynamind import *
from osgeo import ogr, osr
import sys
import os

class GetSystems(Module):
    """Loads the Points Shapefile and transfers all relevant information about water management systems into
a suitable data management structure for use in implementation modules
Inputs: Either project path or exact filename
- Obtain file directly from a filename or from an ongoing simulation? - Boolean
Filename: specify path
Ongoing simulation: specify project path (it is likely the program will load a text file with information on how to grab the shapefile)
Outputs: Vector Data containing block attributes (these are used in later modules as a comparison with the newly entered data)
Log of Updates made at each version:
v0.80 (March 2012):
- First created. Imports a systems shape file, containing points of each system
- Future work: To make sure the projection is adjusted if the file was not created by UrbanBEATS
@ingroup UrbanBEATS
@author Peter M Bach
"""

    def __init__(self):
        Module.__init__(self)
        
        self.createParameter("ubeats_file", BOOL,"")
        self.createParameter("ongoing_sim", BOOL,"")
        self.createParameter("path_name", FILENAME,"")
	self.ubeats_file = 1 #Was this file created by UrbanBEATS or is it man-made?
        self.ongoing_sim = 0 #Is this module part of an ongoing simulation?
	#homeDir = os.environ['HOME']
	#self.path_name = homeDir + '/Documents/UrbanBEATS/UrbanBeatsModules/data/0_screek-500msys-1970impl_points.shp'
        self.path_name = "D:\\Screek500m_PlannedWSUD1.shp" #specify C-drive as default value

	#Views
	self.sysGlobal = View("SystemGlobal",COMPONENT,WRITE)
	self.sysGlobal.addAttribute("TotalSystems")

	self.sysAttr = View("SystemAttribute",COMPONENT,WRITE)
	self.sysAttr.addAttribute("StrategyID")
        self.sysAttr.addAttribute("posX")
        self.sysAttr.addAttribute("posY")
	self.sysAttr.addAttribute("BasinID")
	self.sysAttr.addAttribute("Location")
	self.sysAttr.addAttribute("Scale")
	self.sysAttr.addAttribute("Type")
        self.sysAttr.addAttribute("Qty")
	self.sysAttr.addAttribute("GoalQty")
	self.sysAttr.addAttribute("SysArea")
	self.sysAttr.addAttribute("Status")
	self.sysAttr.addAttribute("Year")
	self.sysAttr.addAttribute("EAFact")
	self.sysAttr.addAttribute("ImpT")
	self.sysAttr.addAttribute("CurImpT")
	self.sysAttr.addAttribute("Upgrades")
	self.sysAttr.addAttribute("WDepth")
	self.sysAttr.addAttribute("FDepth")
	
	datastream = []
        datastream.append(self.sysGlobal)
	datastream.append(self.sysAttr)
        self.addData("City", datastream)
        
    def run(self):
	city = self.getData("City")
        sys_global = Component() #write all general attributes in here
        city.addComponent(sys_global, self.sysGlobal)
        #Get the correct driver (we are working with ESRI Shapefiles)
        driver = ogr.GetDriverByName('ESRI Shapefile')
        
        #Use the following file for testing: C:/UBEATS/0_UrbanBEATS-SC-500m_points.shp
        #self.path_name = "C:/UBEATS/Replicate100/0_SCreekTest1-500msys-1970_points.shp"
        save_file = "ubeats_out.shp"
        if self.ongoing_sim == True:
            file_name = self.path_name + save_file
        else:
            file_name = self.path_name
        
        print file_name
        
        #open data source, check if it exists otherwise quit.
        dataSource = driver.Open(file_name, 0)
        if dataSource is None:
            print "Error, could not open "+file_name
            sys_global.addAttribute("TotalSystems", 0)
            return False
        
        layer = dataSource.GetLayer()
        total_systems = layer.GetFeatureCount()
        spatialRef = layer.GetSpatialRef()
        print "Spatial Reference (Proj4): " + str(spatialRef.ExportToProj4())
        
        #Perform some comparison to make sure that the projection of the loaded file is identical to that of the final desired format
        #Code...
        #...
        
        #add global attributes
        sys_global.addAttribute("TotalSystems", total_systems)
        print "Total Systems in Map: ", total_systems
        sys_global.addAttribute("UBFile", self.ubeats_file)
        
        #Loop through each feature and grab all the relevant information
        for i in range(int(total_systems)):
            feature = layer.GetFeature(i)
            sys_attr = Component()
            city.addComponent(sys_attr,self.sysAttr)
            
            total_attrs = feature.GetFieldCount()  #gets total number of attributes
            for j in range(int(total_attrs)):           
                name = str(feature.GetFieldDefnRef(j).GetName())        #Obtain attribute name from FieldDefn object
                value = feature.GetField(j)                        #get the value from the field using the same index
                if value == None:
                    pass
                else:
                    sys_attr.addAttribute(str(name), value)                    #assign to block_attr vector

            feature.Destroy()      #destroy to save memory
            
        #Destroy the shapefile to free up memory
        dataSource.Destroy()
        #END OF MODULE
