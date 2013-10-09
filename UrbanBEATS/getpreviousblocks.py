# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 1.0
@section LICENSE

This file is part of UrbanBEATS
Copyright (C) 2013  Peter M Bach

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

#from pyvibe import *
import os
from pydynamind import *
from osgeo import ogr, osr
import sys

class GetPreviousBlocks(Module):
    """Loads the Blocks and Patches Shapefile and transfers all relevant information into
    a suitable data management structure for use in urbplanbb and other modules
        
    Inputs: Either project path or exact filename
	- Obtain file directly from a filename or from an ongoing simulation? - Boolean
            Filename: specify path
            Ongoing simulation: specify project path (it is likely the program will load a text file with information on how to grab the shapefile)
    Outputs: Vector Data containing block attributes (these are used in later modules as a comparison with the newly entered data)
    
    Log of Updates made at each version:
    
    v1.00 (June, 2013):
        - Compatibility with new attributes
        - Repositioned this module along the logic train, it now sits before urbplanbb
             additional parameter self.implementationcycle is a boolean that can be read by urbplanbb
             to determine whether it actually runs through the "block-update" options or not. If True,
             urbplanbb will skip block implementation. When this module is featured in the planning cycle,
             value will be False and urbplanbb will run the update check.
        - ...
    
    v0.80 (July 2012):
        - First created.
        - Can import both blocks and patches shapefiles and transfer every attribute across to a VIBe2.VectorDataOut port. This port can be connected
        to a subsequent module and the attributes recalled. Currently no geometric information is transferred as it is believed that it will not be
        relevant so long as all subsequent maps in the simulation are aligned with each other.
        
        @ingroup UrbanBEATS
	@author Peter M Bach
	"""
        
    def __init__(self):
        Module.__init__(self)
	#homeDir = os.environ['HOME']	#works only in linux
        self.createParameter("ongoing_sim", BOOL,"")
        self.createParameter("implementationcycle", BOOL, "")
        self.createParameter("patchesavailable", BOOL, "")
        self.createParameter("path_name", STRING ,"")
        self.createParameter("block_path_name",FILENAME,"")
        self.createParameter("patch_path_name",FILENAME,"")
        self.ongoing_sim = 0            #Is this module part of an ongoing simulation?
        self.implementationcycle = 0    #Is this module in the implementation cycle? If yes, urbplanbb will not check
        self.patchesavailable = 0
        self.path_name = "D:\\"
        self.block_path_name = "D:\\Screek500m_Blocks.shp"
        self.patch_path_name = "D:\\Screek500m_Patches.shp"

	#Views
	self.blocks = View("PreviousBlocks", COMPONENT, WRITE)	#other because of datatransfer problem with other block view from delinblocks
        
        self.patch = View("PatchAttributes", COMPONENT, WRITE)

	self.mapattributes = View("MasterMapAttributes", COMPONENT, WRITE)	#same thing with the name as with the block
        self.mapattributes.addAttribute("Xmin")
        self.mapattributes.addAttribute("Ymin")
        self.mapattributes.addAttribute("Width")
        self.mapattributes.addAttribute("Height")
        self.mapattributes.addAttribute("BlockSize")
        self.mapattributes.addAttribute("BlocksWidth")
        self.mapattributes.addAttribute("BlocksHeight")
        self.mapattributes.addAttribute("TotalBlocks")
        self.mapattributes.addAttribute("Impl_cycle")
        
	datastream = []
        datastream.append(self.blocks)
        datastream.append(self.mapattributes)
        datastream.append(self.patch)
        self.addData("City", datastream)
        
    def run(self):
	city = self.getData("City")
        map_attr = Component()
        map_attr.addAttribute("Impl_cycle", self.implementationcycle)
        city.addComponent(map_attr, self.mapattributes)
        
        #Get the correct driver (we are working with ESRI Shapefiles)
        driver = ogr.GetDriverByName('ESRI Shapefile')
        
        #default savefile names for ongoing simulations
        blocksave_file = "ubeats_out.shp"
        patchsave_file = "ubeats_outp.shp"
        
        if self.ongoing_sim == True:
            blockfile_name = self.path_name + blocksave_file
            patchfile_name = self.path_name + patchsave_file
        else:
            blockfile_name = self.block_path_name
            patchfile_name = self.patch_path_name
        
        #open data source, check if it exists otherwise quit.
        blockdataSource = driver.Open(blockfile_name, 0)
        patchdataSource = driver.Open(patchfile_name, 0)
        if blockdataSource is None:
            print "Error, could not open Blocks " + blockfile_name
            map_attr.addAttribute("Impl_cycle", 1)      #No data so fake impl_cycle so that urbplanbb does not check redev
            return False
        if self.patchesavailable:
            if patchdataSource is None:
                print "Error, could not open Patches " + patchfile_name
                map_attr.addAttribute("Impl_cycle", 1)      #No data so fake impl_cycle so that urbplanbb does not check redev
                return False
        
        blocklayer = blockdataSource.GetLayer()
        if self.patchesavailable: patchlayer = patchdataSource.GetLayer()
        total_blocks = blocklayer.GetFeatureCount()
        if total_blocks == 0:
            map_attr.addAttribute("Impl_cycle", 1)      #No data so fake impl_cycle so that urbplanbb does not check redev
            blockdataSource.Destroy()
            if self.patchesavailable: patchdataSource.Destroy()
            return False        #No blocks, end function
        blockspatialRef = blocklayer.GetSpatialRef()
        if self.patchesavailable: patchspatialRef = patchlayer.GetSpatialRef()
        print "Spatial Reference (Proj4): " + str(blockspatialRef.ExportToProj4())
        print "Total Blocks in map: " + str(total_blocks)
        
        #Perform some comparison to make sure that the projection of the loaded file is identical to that of the final desired format
        #Code...
        #...
        
        #Get extents of the layer
        extents = blocklayer.GetExtent()     #returns as xmin, xmax, ymin, ymax
        xmin = extents[0]
        ymin = extents[2]
        print str(xmin) + ", " + str(ymin)
        
        #Get some dimensions of the map
        map_width = extents[1] - xmin
        map_height = extents[3] - ymin
        
        #Get block size and number of blocks wide and tall from first block in the shape file
        firstBlock = blocklayer.GetFeature(0)
        centrex = firstBlock.GetField("CentreX")
        block_size = 2*centrex
        blocks_wide = map_width/block_size
        blocks_tall = map_height/block_size
        
        print firstBlock.GetFieldCount()
        
        #Set some global attributes
        map_attr.addAttribute("Xmin", xmin)
        map_attr.addAttribute("Ymin", ymin)
        map_attr.addAttribute("Width", map_width)
        map_attr.addAttribute("Height", map_height)
        map_attr.addAttribute("BlockSize", block_size)
        map_attr.addAttribute("BlocksWidth", blocks_wide)
        map_attr.addAttribute("BlocksHeight", blocks_tall)
        map_attr.addAttribute("TotalBlocks", total_blocks)
        
        #Loop through each Block and obtain all attributes
        for i in range(int(total_blocks)):
            currentID = i+1
            currentBlock = blocklayer.GetFeature(i)          #obtains feature with FID = i
            if self.patchesavailable: currentPatches = patchlayer.GetFeature(i)        #obtains patches from patch file
            
            #Transfer all Block Attributes to Block Output
            block_attr = Component()                         #declares Attribute() vector for VIBe
            city.addComponent(block_attr,self.blocks)
	    total_attrs = currentBlock.GetFieldCount()  #gets total number of attributes
            for j in range(int(total_attrs)):           
                name = str(currentBlock.GetFieldDefnRef(j).GetName())        #Obtain attribute name from FieldDefn object
                value = currentBlock.GetField(j)                        #get the value from the field using the same index
                if value == None:
                    pass
                else:
                    block_attr.addAttribute(str(name), value)                    #assign to block_attr vector

            currentBlock.Destroy()      #destroy to save memory
            
            if self.patchesavailable:
                #Transfer all Patch Attributes to Patch Output
                patch_attr = Component()
                city.addComponent(patch_attr,self.patch)
                total_patchattr = currentPatches.GetFieldCount()
                for j in range(int(total_patchattr)):
                    name = str(currentPatches.GetFieldDefnRef(j).GetName())
                    value = currentPatches.GetField(j)
                    if value == None:
                        pass
                    else:
                        patch_attr.addAttribute(str(name), value)
                
                currentPatches.Destroy()    #destroy to save memory
        
        #Destroy the shapefile
        blockdataSource.Destroy()
        if self.patchesavailable: patchdataSource.Destroy()
        #END OF MODULE
