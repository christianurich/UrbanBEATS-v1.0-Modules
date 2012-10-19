# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 0.5
@section LICENSE

This file is part of VIBe2
Copyright (C) 2011  Peter M Bach

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
from delinblocksguic import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pydynamind import *
import math
import ubpatchdelin as ubpat
import ubconvertcoord as ubcc
import ubvectormapload as ubvmap

class delinblocks(Module):
    """Processes information from either UrbanSim or four input biophysical rasters
    and an optional two social-economic rasters and creates a preliminary grid of
    building blocks. 
	
	A coarser resolution grid of the input raster is output
	- block
            contains N number of cells depending on user-specified resolution
            and input raster size, note that all four layers need to match up
            in size, this can be prepared in GIS software.
        - inputs:
            BlockSize = size of cell, model assumes square cells, specify size
                in metres [m]
	- code is split into two possible options based on whether the data is derived
            from UrbanSim or not.
    
    Log of Updates made at each version:
    
    v1.0 update (October 2012) - Post Dynamind Conversion:
        - Full revision and restructuring of parameter list for module, addition of new Regional Geography Parameters
        - Commenting out of UrbanSim Algorithms in the modules. These are not part of UrbanBEATS, but DAnCE4Water
        - 
    
    v0.75 update (October 2011):
        - Added neighbourhood --> block searches all 8 neighbours to get IDs
        - Added terrain delineation --> D8 method only with edge drawing
        - Added additional inputs (planning map, locality map and road network map)
        - Cleaned up code a bit with extra headings and better differentiation between
          UrbanSim Forks and other code
        - Updated GUI with new inputs
        - Does Moore/vonNeumann differentiation now in block flow directions
        - Can account for sinks, but only within existing neighbourhood.
        - Writes attributes to the extracted drainage network
        - Receives and processes Planner's Map, mapping it onto the relevant land uses
        - Implemented calculation of four diversity metrics: richness, Shannon's Diversity, Dominance and Evenness
        Future work:
            - add processing of locality map
            - add processing of natural sink map
            - add processing of road network map
            - Make code more modular, perhaps splitting terrain delineation with rest
            - Implement hexagonal blocks
    
    v0.5 update (August 2011):
        - implemented UrbanSim forks, labelled in the code at five locations
        - implemented additional raster inputs: social parameters 1 and 2 with naming
          treats these as probabilities and returns the average probability for the area
        - processes either the land use, population rasters OR UrbanSim data
        - updated GUI for delinblocks to include UrbanSim and social parameter inputs
        
    v0.5 first (July 2011):
        - implemented block delineation algorithm for basic parameters
        - looks for von Neplan_mapumann neighbourhood and returns Block IDs, writes to Shp file output
        - draws the grid of blocks
        - designed GUI for delinblocks
	
	@ingroup DAnCE4Water
	@author Peter M Bach
	"""

    def __init__(self):
        Module.__init__(self)  
        
        #PARAMETER LIST START
        #-----------------------------------------------------------------------
        
        #General Simualtion Parameters
        self.createParameter("BlockSize", DOUBLE, "")
        self.createParameter("blocksize_auto", BOOL, "")
        self.BlockSize = 500                    #size of the blocks (in m)
	self.blocksize_auto = False             #should the size be chosen automatically?
        
        #Processing Input Data
        self.createParameter("popdatatype", STRING, "")
        self.createParameter("soildatatype", STRING, "")
        self.createParameter("soildataunits", STRING, "")
        self.createParameter("elevdatadatum", STRING, "")
        self.createParameter("elevdatacustomref", DOUBLE, "")
        
        self.createParameter("include_plan_map", BOOL ,"")
        self.createParameter("include_local_map", BOOL,"")
        self.createParameter("include_employment", BOOL, "")
        self.createParameter("jobdatatype", STRING, "")
        
        self.createParameter("include_rivers", BOOL, "")
        self.createParameter("include_lakes", BOOL, "")
        self.createParameter("include_groundwater", BOOL, "")
        self.createParameter("groundwater_datum", STRING, "")
        
        self.createParameter("include_road_net", BOOL,"")
        self.createParameter("include_supply_net", BOOL, "")
        self.createParameter("include_sewer_net", BOOL, "")
        
        self.createParameter("include_soc_par1", BOOL,"")
        self.createParameter("include_soc_par2", BOOL,"")
        self.createParameter("social_par1_name", STRING,"")
        self.createParameter("social_par2_name", STRING,"")
        self.createParameter("socpar1_type", STRING, "")
        self.createParameter("socpar2_type", STRING, "")

        self.createParameter("patchdelin", BOOL, "")
        self.createParameter("spatialmetrics", BOOL, "")

        self.popdatatype = "D"                  #population data type: D = density, C = count
        self.soildatatype = "I"                 #I = infiltration rates, C = classification
        self.soildataunits = "hrs"              #sec = m/s, hrs = mm/hr
        self.elevdatadatum = "S"                #S = sea level, C = custom
        self.elevdatacustomref = 0              #reference above sea level for custom elevation
        self.include_plan_map = False           #planner's map displaying typology distributions
        self.include_local_map = False          #locality map displaying location of centres
        self.include_employment = False         #include employment data for industrial land uses?
        self.jobdatatype = "D"                  #employment data type: D = density, C = count
        self.include_rivers = False             #include river systems
        self.include_lakes = False              #include lake systems
        self.include_groundwater = False        #include groundwater table
        self.groundwater_datum = "Sea"          #"Sea" = Sea level, "Surf" = Surface level
        
        self.include_road_net = False           #road network map not working yet
        self.include_supply_net = False       #include water supply mains
        self.include_sewer_net = False        #include sewer mains
        
        self.include_soc_par1 = True            #include a social parameter in the simulation?
        self.include_soc_par2 = True            #include a social parameter in the simulation?
        self.social_par1_name = "unnamed1"      #name of social parameter1
        self.social_par2_name = "unnamed2"      #name of social parameter2
        self.socpar1_type = "B"                 #B = Binary, P = Proportionate
        self.socpar2_type = "B"
        
        self.patchdelin = True                  #perform patch delineation? All subsequent algorithms will need to consider this
        self.spatialmetrics = True              #perform calculation of spatial metrics? Just an additional feature
        
        #Local Extents and Map Connectivity                   
        self.createParameter("Neighbourhood", STRING,"")
        self.createParameter("vn4FlowPaths", BOOL,"")
        self.createParameter("vn4Patches", BOOL,"")
                
        self.createParameter("flow_method", STRING,"")
        self.createParameter("demsmooth_choose", BOOL,"")
        self.createParameter("demsmooth_passes", DOUBLE,"")
         
        self.Neighbourhood = "M"                #three options: M = Moore, N = von Neumann
        self.vn4FlowPaths = False
        self.vn4Patches = False
               
        self.flow_method = "D8"                 #three options: DI = D-infinity (Tarboton), D8 = D8 (O'Callaghan & Mark) and MS = Divergent (Freeman)
        self.demsmooth_choose = False
        self.demsmooth_passes = 1
        
        #Regional Geography
        self.createParameter("considerCBD", BOOL, "")
        self.createParameter("locationOption", STRING, "")
        self.createParameter("locationCity", DOUBLE, "")
        self.createParameter("locationLong", DOUBLE, "")
        self.createParameter("locationLat", DOUBLE, "")
        self.createParameter("marklocation", BOOL, "")
                
        self.considerCBD = False
        self.locationOption = "S"       #method for setting location option: S = selection, C = coordinates
        self.locationCity = 0           #index of the combobox, it returns the city name in a different vector
        self.locationLong = 0           #longitude of the location
        self.locationLat = 0            #latitude of the location
        self.marklocation = False       #should this CBD location be marked on the map as a point? If yes, it will be saved to the Block Centre Points
        
        #-----------------------------------------------------------------------
        #END OF INPUT PARAMETER LIST


        #DEFINE VIEWS
        #-----------------------------------------------------------------------
        
        #Input Data
	self.elevation = View("Elevation", RASTERDATA, READ)            #<-- BASE INPUTS
        self.soil = View("Soil", RASTERDATA, READ)
        self.landuse = View("LandUse", RASTERDATA, READ)
        self.population = View("Population", RASTERDATA, READ)
        #self.urbansim = View("GRID", FACE, READ)                       #<-- UrbanSim derived data, not active yet
        
        self.plan_map = View("PlanMap", RASTERDATA, READ)               #<-- ADDITIONAL INPUTS
        #self.local_map = View("LocalMap", VECTORDATA, READ)
        self.employment = View("Employment", RASTERDATA, READ)
        #self.rivers = View("Rivers", VECTORDATA, READ)
        #self.lakes = View("Lakes", VECTORDATA, READ)
        self.groundwater = View("Groundwater", RASTERDATA, READ)
        
        #self.road_map = View("RoadMap", VECTORDATA, READ)
        #self.supply_net = View("SupplyMains", VECTORDATA, READ)
        #self.sewer_net = View("SewerMains", VECTORDATA, READ)
        
        self.socpar1 = View("SocialParam1", RASTERDATA, READ)
        self.socpar2 = View("SocialParam2", RASTERDATA, READ)
        
        #Global Attributes View
        self.mapattributes = View("GlobalMapAttributes", COMPONENT, WRITE)
        self.mapattributes.addAttribute("NumBlocks")                  #Number of blocks in the grid
        self.mapattributes.addAttribute("WidthBlocks")                #Width of simulation area in # of blocks
        self.mapattributes.addAttribute("HeightBlocks")               #Height of simulation area in # of blocks
        self.mapattributes.addAttribute("BlockSize")                  #Size of block [m]
        self.mapattributes.addAttribute("InputReso")                  #Resolution of the input data [m]
        self.mapattributes.addAttribute("Neigh_Type")
        self.mapattributes.addAttribute("ConsiderCBD")
        self.mapattributes.addAttribute("CBDLocationLong")
        self.mapattributes.addAttribute("CBDLocationLat")
        #self.mapattributes.addAttribute("UrbanSimData")             #"Yes" or "no" as to whether input derived from UrbanSim
        
        #Block Data View
        self.block = View("Block", FACE, WRITE)
        self.block.addAttribute("BlockID")              #ID of the Block (different from UUID)
        self.block.addAttribute("LocateX")             #x location of bottom-left corner of block (for drawing)
        self.block.addAttribute("LocateY")             #y location of bottom-right corner of block (for drawing)
        self.block.addAttribute("CentreX")             #centre x location of block
        self.block.addAttribute("CentreY")              #centre y location of block
        self.block.addAttribute("OriginX")
        self.block.addAttribute("OriginY")             
        self.block.addAttribute("Status")               #Status: 1 = part of simulation, 0 = not part of simulation
        self.block.addAttribute("Activity")             #Degree to which block is active in simulation (how much data is available)
        self.block.addAttribute("Nhd_N")             #North neighbour Block ID
        self.block.addAttribute("Nhd_S")             #South neighbour Block ID
        self.block.addAttribute("Nhd_W")             #West neighbour Block ID
        self.block.addAttribute("Nhd_E")             #East neighbour Block ID
        self.block.addAttribute("Nhd_NE")            #Northeast neighbour Block ID
        self.block.addAttribute("Nhd_NW")            #Northwest neighbour Block ID
        self.block.addAttribute("Nhd_SE")            #Southeast neighbour Block ID
        self.block.addAttribute("Nhd_SW")            #Southwest neighbour Block ID
        self.block.addAttribute("Soil_k")               #Soil infiltration rate [mm/hr]
        self.block.addAttribute("AvgElev")              #Average elevation of Block [m]

        self.block.addAttribute("pLU_RES")             #Land use proportions in block (multiply with block area to get Area
        self.block.addAttribute("pLU_COM")             #RES = Residential      RD = Road
        self.block.addAttribute("pLU_ORC")             #COM = Commercial       TR = Transport facility
        self.block.addAttribute("pLU_LI")              #ORC = Offices & Res    PG = Parks & Gardens
        self.block.addAttribute("pLU_HI")              #LI = Light Industry    REF = Reserves & Floodways
        self.block.addAttribute("pLU_CIV")             #HI = Heavy Industry    UND = Undeveloped
        self.block.addAttribute("pLU_SVU")             #CIV = Civic Facilities NA = Unclassified
        self.block.addAttribute("pLU_RD")              #SVU = Services & Utility
        self.block.addAttribute("pLU_TR")
        self.block.addAttribute("pLU_PG")
        self.block.addAttribute("pLU_REF")
        self.block.addAttribute("pLU_UND")
        self.block.addAttribute("pLU_NA")
        
        self.block.addAttribute("Population")           #Total people LIVING in block
        self.block.addAttribute("Employment")           #Total people EMPLOYED in block
        self.block.addAttribute("SocPar1")
        self.block.addAttribute("SocPar2")
        self.block.addAttribute("PM_RES")
        self.block.addAttribute("PM_COM")
        self.block.addAttribute("PM_LI")
        self.block.addAttribute("PM_HI")
        
        self.block.addAttribute("TotPatches")           #Total Patches in Block
        self.block.addAttribute("PatchIDs")             #List of Patch IDs to match up with Patch Map
        self.block.addAttribute("Richness")             #Richness of Land use mix in Block
        self.block.addAttribute("ShannonDIV")           #Shannon Diversity Index
        self.block.addAttribute("ShannonDOM")           #Shannon Dominance Index
        self.block.addAttribute("ShannonEVEN")          #Shannon Evenness Index
        
        self.block.addAttribute("downstrID")            #ID block water flows to naturally
        self.block.addAttribute("max_Zdrop")            #maximum drop in elevation
        self.block.addAttribute("avg_slope")            #average slope
        self.block.addAttribute("drainto_ID")           #ID block drains to if a sink
        self.block.addAttribute("h_pond")               #height of ponding before sink can drain

        self.block.addAttribute("CBDdistance")          #Distance from CBD [km]
        self.block.addAttribute("CBDdirection")         #Which direction to travel from CBD to get to Block? Specified as an angle in degrees
        
        #Patch Data View
        self.patch = View("Patch", FACE, WRITE)
        self.patch.addAttribute("LandUse")              #Land use of the patch
        self.patch.addAttribute("Area")                 #Area of the patch
        self.patch.addAttribute("AvgElev")              #Average elevation of the patch
        self.patch.addAttribute("SoilK")
        self.patch.addAttribute("BlockID")              #Block ID that patch belongs to
        
        #Network Data View
        self.network = View("Network", EDGE, WRITE)
        self.network.addAttribute("NetworkID")
        self.network.addAttribute("BlockID")
        self.network.addAttribute("Z_up")
        self.network.addAttribute("Z_down")
        self.network.addAttribute("max_Zdrop")
        self.network.addAttribute("Type")
        self.network.addAttribute("avg_slope")
        
        #Node Data View
        self.blocknodes = View("BlockNodes", NODE, WRITE)
        self.blocknodes.addAttribute("BlockID")         #Holds the Block ID or -1 for CBD location
        
        #Append all views to the data stream
        datastream = []
        datastream.append(self.elevation)
        datastream.append(self.soil)
        datastream.append(self.landuse)
        datastream.append(self.population)
        #datastream.append(self.urbansim)
        
        datastream.append(self.plan_map)
        #datastream.append(self.local_map)
        datastream.append(self.employment)
        #datastream.append(self.rivers)
        #datastream.append(self.lakes)
        datastream.append(self.groundwater)
        
        #datastream.append(self.road_map)
        #datastream.append(self.supply_net)
        #datastream.append(self.sewer_net)
        
        datastream.append(self.socpar1)
        datastream.append(self.socpar2)
        
        datastream.append(self.mapattributes)
        datastream.append(self.block)
        datastream.append(self.patch)
        datastream.append(self.network)
        datastream.append(self.blocknodes)
        
        self.addData("City", datastream)
  
        #Define dictionary to hold Block ID - UUID relationship
	self.BlockIDtoUUID = {}
        self.CBDcoordinates = {
                    "Adelaide" : [280780.0759095973, 6132244.023877329],
                    "Brisbane" : [502317.812981302, 6961397.420122750],
                    "Cairns" : [369106.391411321, 8128447.001515380],
                    "Canberra" : [693122.206993260, 6090719.284280210],
                    "Copenhagen" : [347093.425724650, 6172710.918933620],
                    "Innsbruck" : [681848.057202314, 5237885.440371720],
                    "Kuala Lumpur" : [799755.394164082, 348044.713410070],
                    "London" : [699324.171955045, 5710156.274752980],
                    "Melbourne" : [321467.336657357, 5813188.082041830],
                    "Munich" : [691723.398045385, 5334697.280393150],
                    "Perth" : [392423.697319843, 6466441.091644930],
                    "Singapore" : [372162.693079949, 141518.167286989],
                    "Sydney" : [334154.239302794, 6251091.03554923],
                    "Vienna" : [602067.456062062, 5340352.522405760]    }
        self.soildictionary = [180, 36, 3.6, 0.36]    #mm/hr - 1=sand, 2=sandy clay, 3=medium clay, 4=heavy clay
        
    def run(self):
        city = self.getData("City")     #Get the datastream containing all the info
        cs = self.BlockSize             #set blocksize to a local variable with a short name cs = cell size
                
        if self.Neighbourhood == "N":           #Set neighbourhood Type
            neighbourhood_type = 4              #von Neumann = 4 neighbours
        else: 
            neighbourhood_type = 8              #Moore = 8 neighbours
        
        #Retrieve the data into local variables
        ### 4 BASIC INPUTS ###
        elevationraster = self.getRasterData("City", self.elevation)                   #ELEVATION AND SOIL DATA ARE NOT URBANSIM DEPENDENT!
        soilraster = self.getRasterData("City", self.soil)
        landuseraster = self.getRasterData("City", self.landuse)
        population = self.getRasterData("City", self.population)
        
        ### 7 ADDITIONAL INPUTS ###
        #(1) - Planner's Map
        if self.include_plan_map: 
            plan_map = self.getRasterData("City", self.plan_map)
        else: 
            plan_map = 0
        
        #(2) - Locality Map
        #if include_local_map: local_map = get data
        
        #(3) - Employment Map
        if self.include_employment: 
            employment = self.getRasterData("City", self.employment)
        else: 
            employment = 0
        
        #(4) - Rivers Map
        #if include_rivers: river_map = self.get data
        
        #(5) - Lakes Map
        #if include_lakes: lakes_map = self.get data
        
        #(6) - Groundwater Map
        if self.include_groundwater: 
            groundwater = self.getRasterData("City", self.groundwater)
        else:
            groundwater = 0
        
        #(7) - Social Parameters
        if self.include_soc_par1: 
            socpar1 = self.getRasterData("City", self.socpar1)
        else:
            socpar1 = 0
        if self.incldue_soc_par1: 
            socpar2 = self.getRasterData("City", self.socpar2)
        else:
            socpar2 = 0
        
        #road_net, supply_net and sewer_net = coming in future versions
        
        inputres = landuseraster.getCellSize()                                #input data resolution [m]
        width =  elevationraster.getWidth() * elevationraster.getCellSize()     #"getWidth" syntax returns no. of cells
        height =  elevationraster.getHeight() * elevationraster.getCellSize()   #to get actual width, need to multiply by cell size [m]         
        
        ### AUTO SIZE BLOCKS ###
        if self.blocksize_auto == True:
            cs = self.autosizeBlocks(width, height)
        else:
            cs = self.BlockSize                                                 #BlockSize stored locally [m]
        cellsinblock = int(cs/inputres)                                         #tells us how many smaller cells are in one length of block  
        print "Width", width
        print "Height", height
        print "Block Size: ", cs
        print "Cells in Block: ", cellsinblock
        
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        # ###########################
        # ###URBANSIM FORK #1     ###
        # ###########################
        # if self.input_from_urbansim == True:                     
        #     urbansimdata = "Yes"                                #global attribute for later modules
        #     urbansim_out = self.urbansim_out.getItem()          #get the UrbanSim vector data
        #     USinputres = 200                                    #at moment cell size is fixed but this line needs to be changed in future when urban sim resolution is different
        #     if float(cs/USinputres) > float(int(cs/USinputres)):
        #         print "WARNING, UrbanSim resolution and Block Size conflict"
        #     UScellsinblock = int(cs/USinputres)
        #     numUScells = int(UScellsinblock*width/cs * UScellsinblock*height/cs)
        # else:
        #     urbansimdata = "No"         #global attribute
        #    
        #     landuseraster = self.getRasterData("City", self.landuse)
        #     popdensityraster = self.getRasterData("City", self.popdensity)
        #     #landuseraster = self.landuseraster.getItem()
        #     #popdensityraster = self.popdensityraster.getItem()
        #     #social_parameter1 = self.social_parameter1.getItem()
        #     #social_parameter2 = self.social_parameter2.getItem()
        #
        #     #if self.landuseraster.getItem().getWidth() != self.soilraster.getItem().getWidth():
        #     if landuseraster.getWidth() != soilraster.getWidth():
        #         print "WARNING, input rasters are not equal in size!"
        #
        # ##### -------- END OF URBANSIM FORK #1 -------- #####'''
        #------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
        
        #Note that the simulation area needs to have a larger width and larger height than the data input area!
        whfactor = 1 - (1/(cs*2))               #factor replaces the rounding function and speeds up computation
        widthnew = int(width/cs+whfactor)       #width of the simulation area (divide total width by block size and round) [#Blocks]
        heightnew = int(height/cs+whfactor)      #height of the simulation area (multiply block size with this to get actual length) [#Blocks]
        numblocks = widthnew * heightnew        #number of blocks based on how many blocks wide x how many blocks tall [#Blocks]
        
        #Look up long and lat of CBD if need to be considered
        if self.considerCBD:
            #Grab CBD coordinates, convert to UTM if necessary
            cityeasting, citynorthing = self.getCBDcoordinates()        #EASTING = X, NORTHING = Y
            xoffset = 0 #get Input Raster File X-offset           #delinblocks works at Global (0,0)
            yoffset = 0 #get Input Raster File Y-offset           #then exports it and offsets the map
                                                                #to realign it with the original data
            map_attr.addAttribute("CBDLocationLong", cityeasting)
            map_attr.addAttribute("CBDLocationLat", citynorthing)
            
            #Wait for Christian to update DynaMind so I can get the input offset
            
            #See if marklocation can be added
            if self.marklocation:
                loc = city.addNode(cityeasting-xoffset, citynorthing-yoffset, 0)
                loc.addAttribute("BlockID", -1)     #-1 for CBD
                
            
        ### MAP ATTRIBUTES - The Global Attributes List - write present information across to this component
        map_attr = Component()
        map_attr.addAttribute("NumBlocks", numblocks)                   #Number of blocks in the grid
        map_attr.addAttribute("WidthBlocks", widthnew)                  #Width of simulation area in # of blocks
        map_attr.addAttribute("HeightBlocks", heightnew)                #Height of simulation area in # of blocks
        map_attr.addAttribute("BlockSize", cs)                          #Size of block [m]
        map_attr.addAttribute("InputReso", inputres)                    #Resolution of the input data [m]
        map_attr.addAttribute("Neigh_Type", neighbourhood_type) 
        map_attr.addAttribute("ConsiderCBD", self.considerCBD)
        #map_attr.addAttribute("UrbanSimData", urbansimdata)            #"Yes" or "no" as to whether input derived from UrbanSim
        
        city.addComponent(map_attr, self.mapattributes)                 #add the component list map_attr to the View self.mapattributes
        
        x_adj = 0               #these track the position of the 'draw cursor', these offset the cursor
        y_adj = 0               #can be used to offset the drawing completely from (0,0)
        
        ########################################################################
        ### DRAW BLOCKS AND ASSIGN INFO                                      ###
        ######################################################################## 
        blockIDcount = 1     #counts through Block ID, initialize this variable here
        for y in range(heightnew):              #outer loop scans through rows
            for x in range(widthnew):           #inner loop scans through columns
                print "CURRENT BLOCK ID: "+str(blockIDcount)
                block_attr = self.createBlockFace(city, x, y, cs, x_adj, y_adj, blockIDcount)
                
                xcentre = x*cs+0.5*cs       #Centre point               
                ycentre = y*cs+0.5*cs   
                       
                x_start = x*cellsinblock    #Bottom-left-hand corner (grid-numbering)
                y_start = y*cellsinblock
                
                xorigin = (x+x_adj)*cs
                yorigin = (y+y_adj)*cs
                
                block_attr.addAttribute("CentreX", xcentre)
                block_attr.addAttribute("CentreY", ycentre)
                block_attr.addAttribute("LocateX", x+1)
                block_attr.addAttribute("LocateY", y+1)
                block_attr.addAttribute("OriginX", xorigin)
                block_attr.addAttribute("OriginY", yorigin)
                offset = [(x+x_adj)*cs, (y+y_adj)*cs]
                
                ####################################################
                ### 1.1 DETERMINE BLOCK NEIGHBOURHOOD            ###
                ####################################################
                blockNHD = self.findNeighbourhood(blockIDcount, x, y, numblocks, widthnew, heightnew)
                block_attr.addAttribute("Nhd_N", blockNHD[0])             #North neighbour Block ID
                block_attr.addAttribute("Nhd_S", blockNHD[1])             #South neighbour Block ID
                block_attr.addAttribute("Nhd_W", blockNHD[2])             #West neighbour Block ID
                block_attr.addAttribute("Nhd_E", blockNHD[3])             #East neighbour Block ID
                block_attr.addAttribute("Nhd_NE", blockNHD[4])            #Northeast neighbour Block ID
                block_attr.addAttribute("Nhd_NW", blockNHD[5])            #Northwest neighbour Block ID
                block_attr.addAttribute("Nhd_SE", blockNHD[6])            #Southeast neighbour Block ID
                block_attr.addAttribute("Nhd_SW", blockNHD[7])            #Southwest neighbour Block ID
               
               
                ####################################################
                ### 1.2 CALCULATE DISTANCE FROM CBD IF NECESSARY ###
                ####################################################
                if self.considerCBD:
                    currenteasting = xcentre
                    currentnorthing = ycentre
                    
                    #Calculate distance and angle
                    dist = math.sqrt(math.pow((cityeasting-currenteasting),2)+math.pow((citynorthing-currentnorthing),2))
                    theta = math.degrees(math.atan((currentnorthing - citynorthing)/(currenteasting - cityeasting)))
                    
                    block_attr.addAttribute("CBDdistance", dist)
                    block_attr.addAttribute("CBDdirection", theta)
                
                
                ####################################################
                ### 1.3 RETRIEVE EXACT VALUES FROM INPUT DATA    ###
                ####################################################
                datasources = [landuseraster, population, elevationraster, soilraster, plan_map, employment, groundwater, socpar1, socpar2]
                datamatrices = self.retrieveData(datasources, [x_start, y_start], cellsinblock)
                
                lucdatamatrix = datamatrices[0]         #holds land use data from input 
                popdatamatrix = datamatrices[1]         #holds population data from input 
                elevdatamatrix = datamatrices[2]        #holds elevation data from input
                soildatamatrix = datamatrices[3]        #holds soil data from input
                
                planmapmatrix = datamatrices[4]
                employmentmatrix = datamatrices[5]
                groundwatermatrix = datamatrices[6]
                                
                socpar1matrix = datamatrices[7]
                socpar2matrix = datamatrices[8]
                
                #Determine frequency of land class occurrences
                landclassprop, activity = self.frequencyLUC(lucdatamatrix)
                if activity == 0:
                    blockstatus = 0
                else:
                    blockstatus = 1
                block_attr.addAttribute("Status", blockstatus)
                block_attr.addAttribute("Activity", activity)
                

                ####################################################
                ### 2.1 CALCULATE SPATIAL METRICS                ###
                ####################################################
                #Using land class frequencies
                if self.spatialmetrics:
                    richness = self.calcRichness(landclassprop)
                    shdiv, shdom, sheven = self.calcShannonMetrics(landclassprop, richness)
                else:
                    richness = None
                    shdiv = None
                    shdom = None
                    sheven = None
                block_attr.addAttribute("Richness", richness)
                block_attr.addAttribute("ShannonDiv", shdiv)
                block_attr.addAttribute("ShannonDom", shdom)
                block_attr.addAttribute("ShannonEven", sheven)
                  
              
                ####################################################
                ### 2.2 CONDUCT TALLYING UP OF DATA FOR BLOCK    ###
                ####################################################
                #Land use classes
                block_attr.addAttribute("pLU_RES", landclassprop[0])           #Land use proportions in block (multiply with block area to get Area
                block_attr.addAttribute("pLU_COM", landclassprop[1])           #RES = Residential      RD = Road
                block_attr.addAttribute("pLU_ORC", landclassprop[2])           #COM = Commercial       TR = Transport facility
                block_attr.addAttribute("pLU_LI", landclassprop[3])            #ORC = Offices & Res    PG = Parks & Gardens
                block_attr.addAttribute("pLU_HI", landclassprop[4])            #LI = Light Industry    REF = Reserves & Floodways
                block_attr.addAttribute("pLU_CIV", landclassprop[5])           #HI = Heavy Industry    UND = Undeveloped
                block_attr.addAttribute("pLU_SVU", landclassprop[6])           #CIV = Civic Facilities NA = Unclassified
                block_attr.addAttribute("pLU_RD", landclassprop[7])            #SVU = Services & Utility
                block_attr.addAttribute("pLU_TR", landclassprop[8])
                block_attr.addAttribute("pLU_PG", landclassprop[9])
                block_attr.addAttribute("pLU_REF", landclassprop[10])
                block_attr.addAttribute("pLU_UND", landclassprop[11])
                block_attr.addAttribute("pLU_NA", landclassprop[12])                
                
                #Averages & Counts for Soil, Elevation, Population and additional inputs
                raster_sum_soil, total_n_soil = 0, 0
                raster_sum_elev, total_n_elev = 0, 0
                pop_sum_total = 0
                soc_par1, total_n_soc_par1 = 0, 0       #to tally up an average in case
                soc_par2, total_n_soc_par2 = 0, 0       #to tally up an average in case    
                
                plan_map_sums = [0,0,0,0]       #4 categories of planner's map dependent on RES, COM, LI, HI
                plan_map_counts = [0,0,0,0]
                
                for a in range(cellsinblock):        #Loop across all cells in the block
                    for b in range(cellsinblock):
                        if soildatamatrix[a][b] != -9999:
                            raster_sum_soil += soildatamatrix[a][b]
                            total_n_soil += 1
                        if elevdatamatrix[a][b] != -9999:
                            total_n_elev += 1
                            if self.elevdatadatum == "S":
                                raster_sum_elev += elevdatamatrix[a][b]
                            elif self.elevdatadatum == "C":
                                raster_sum_elev += elevdatamatrix[a][b] + self.elevdatacustomref #bring it back to sea level
                            
                        if popdatamatrix[a][b] != -9999:
                            if self.popdatatype == "C":                         #If population data is a count
                                pop_sum_total += popdatamatrix[a][b]
                            else:                                               #Else population data is a density [pax/ha]
                                pop_sum_total += popdatamatrix[a][b] * (inputres*inputres)/10000
                        
                        #PLANNER'S MAP
                        if self.include_plan_map:
                            lucplanindex = [1, 2, 4, 5]     #numbers are LUC categories that planner's map deals with
                            if lucdatamatrix[a][b] in lucplanindex:
                                lucindex = lucplanindex.index(lucdatamatrix[a][b])
                                if len(planmapmatrix) != 0 and planmapmatrix[a][b] != -9999:
                                    plan_map_sums[lucindex] += planmapmatrix[a][b]
                                    plan_map_counts[lucindex] += 1
                                    
                        #EMPLOYMENT - Like Population
                        if self.include_employment:
                            pass
                        
                        #GROUNDWATER TABLE - Like Elevation, but scaled based on correct datum
                        if self.include_groundwater:
                            pass
                        
                        
                        #SOCIAL PARAMETERS - Like Population if proportion, if Binary, based on majority
                        if self.include_soc_par1:
                            if len(socpar1matrix) != 0 and socpar1matrix[a][b] != -9999:
                                soc_par1 += socpar1matrix[a][b]
                                total_n_soc_par1 += 1
                        if self.include_soc_par2:
                            if len(socpar2matrix) != 0 and socpar2matrix[a][b] != -9999:
                                soc_par2 += socpar2matrix[a][b]
                                total_n_soc_par2 += 1
                               
                #Adjust the total count in case it is zero to prevent division by zero. If count = 0, then sum = 0 because nothing was found
                total_n_soil = self.adjustCount(total_n_soil)
                total_n_elev = self.adjustCount(total_n_elev)
                total_n_soc_par1 = self.adjustCount(total_n_soc_par1)
                total_n_soc_par2 = self.adjustCount(total_n_soc_par2)
                for a in range(len(plan_map_counts)):
                    plan_map_counts[a] = self.adjustCount(plan_map_counts[a])
                
                block_attr.addAttribute("Soil_k", raster_sum_soil/total_n_soil)
                block_attr.addAttribute("AvgElev", raster_sum_elev/total_n_elev)
                block_attr.addAttribute("Population", pop_sum_total)
                
                if self.include_socpar1:
                    block_attr.addAttribute("SocPar1", soc_par1/total_n_soc_par1)
                    block_attr.addAttribute("SocPar2", soc_par2/total_n_soc_par2)
                if self.include_plan_map:
                    block_attr.addAttribute("PM_RES", plan_map_sums[0]/plan_map_counts[0])
                    block_attr.addAttribute("PM_COM", plan_map_sums[1]/plan_map_counts[1])
                    block_attr.addAttribute("PM_LI", plan_map_sums[2]/plan_map_counts[2])
                    block_attr.addAttribute("PM_HI", plan_map_sums[3]/plan_map_counts[3])
                if self.include_employment:
                    pass
                if self.include_groundwater:
                    pass
                    
                #Locality Map Data Locate for Block and Assign
                #coming soon...
                                
                
                ####################################################
                ### 2.3 DELINEATE PATCHES                        ###
                ####################################################
                #Call the function using the current Block's Patch information
                print "Start Patches"
                patchdict = ubpat.landscapePatchDelineation(lucdatamatrix, elevdatamatrix, soildatamatrix)
                #Draw the patches and save info to view
                for i in range(len(patchdict)):
                    panodes = patchdict["PatchID"+str(i+1)][4]
                    paarea = patchdict["PatchID"+str(i+1)][0]
                    paluc = patchdict["PatchID"+str(i+1)][1]
                    paelev = patchdict["PatchID"+str(i+1)][2]
                    pasoil = patchdict["PatchID"+str(i+1)][3]
                    self.drawPatchFace(city, panodes, inputres, offset, i+1, blockIDcount, paarea, paluc, paelev, pasoil)
                
                block_attr.addAttribute("TotPatches", len(patchdict))
                print "End Patches"
                blockIDcount += 1    #increase counter by one before next loop to represent next Block ID
        
        ########################################################################
        ### TERRAIN DELINEATION                                              ###
        ### v1.0, D8 or D-inf methods                                        ###
        ########################################################################
        #Smooth the DEM?
        #self.createParameter("demsmooth_choose", BOOL,"")
        #self.createParameter("demsmooth_passes", DOUBLE,"")
        
        
        sinkIDs = []
        
        #DynaMind's Block Views are saved using a special encoding - the UUID, we therefore have to reference
        #Block ID with the View's UUID.
        self.initBLOCKIDtoUUID(city)    #gets all UUIDs of each block and sets up a dictionary to refer to.
        
        for i in range(numblocks):
            currentID = i+1
            uuid = self.getBlockUUID(currentID, city)
            if uuid == "":
                print "Error, Block"+ str(currendID)+" not found."
                continue
        
        currentAttList = city.getFace(uuid)
        if currentAttList.getAttribute("Status").getDouble() == 0:
            print "BlockID"+str(currentID)+" not active in simulation"
            continue
        currentZ = currentAttList.getAttribute("AvgAltitude").getDouble()
        
        #Neighbours array: [N, S, W, E, NE, NW, SE, SW], the last four are 0 if only vonNeumann Nhd used.
        neighbours = self.getBlockNeighbourhood(currentAttList, neighbourhood_type)
        neighboursZ = self.getNeighbourhoodZ(neighbours, city)
        
        #Find Downstream Block
        if self.flow_method == "D8":
            flow_direction = self.findDownstreamD8(currentZ, neighbours)
        elif self.flow_method == "DI":
            flow_direction = self.findDownstreamDinf(currentZ, neighbours)
        
        if flow_direction == -9999:
            sinkIDs.append(currentID)
        else:
            downstreamID = neighbours(
        
    

#        flow_direction = max(current_neighbdZ)
#        if flow_direction < 0:              #identify sinks or outlets
#            downstreamID = -1
#            sinkIDs.append(currentID)
#        else:
#            downstreamID = current_neighb[current_neighbdZ.index(flow_direction)]        
        
#        #calculate avg slope between the two blocks
#        if current_neighbdZ.index(flow_direction) > 3:
#            dx = cs
#        else:
#            dx = cs
#        avg_slope = flow_direction/dx               #slope: downhill = +ve, uphill = -ve (when in sink)
#        if currentID == 25:
#            print 
#        currentAttList.addAttribute("downstrID", downstreamID)
#        currentAttList.addAttribute("max_Zdrop", max(flow_direction,0))                     
#        currentAttList.addAttribute("avg_slope", avg_slope)
        
#        #DRAW NETWORKS
        
        
        
#    total_sinks = len(sinkIDs)
#    print "A total of: "+str(total_sinks)+" sinks found in map!"
        
#    #Sink unblocking algorithm for immediate neighbourhood
#    for i in sinkIDs:
#        print i
#        currentID = i
#        currentAttList = city.getFace(self.getBlockUUID(currentID,city))           
#        currentZ = currentAttList.getAttribute("AvgAltitude").getDouble()    
        
#        #Scan the 8 neighbours, if all of them drain into the sink, then proceed further
#        ID_N = int(round(currentAttList.getAttribute("Neighb_N").getDouble()))
#        ID_S = int(round(currentAttList.getAttribute("Neighb_S").getDouble()))
#        ID_W = int(round(currentAttList.getAttribute("Neighb_W").getDouble()))
#        ID_E = int(round(currentAttList.getAttribute("Neighb_E").getDouble()))
#        if neighbourhood_type == 8:
#            ID_NE = int(round(currentAttList.getAttribute("Neighb_NE").getDouble()))
#            ID_NW = int(round(currentAttList.getAttribute("Neighb_NW").getDouble()))
#            ID_SE = int(round(currentAttList.getAttribute("Neighb_SE").getDouble()))
#            ID_SW = int(round(currentAttList.getAttribute("Neighb_SW").getDouble()))
#            current_neighb = [ID_N, ID_S, ID_W, ID_E, ID_NE, ID_NW, ID_SE, ID_SW]
#        else:
#            current_neighb = [ID_N, ID_S, ID_W, ID_E]
       
#        possible_IDdrains = []
#        possible_ID_dZ = []
#        possibility = 0
#        for j in current_neighb:
#            uuid = self.getBlockUUID(j,city)
#            if  len(uuid)!=0:
#                    print "block neigh" + str(j)
#                    f = city.getFace(uuid)
#                    if int(round(f.getAttribute("downstrID").getDouble())) != currentID:
#                        if int(round(f.getAttribute("Status").getDouble())) != 0:
#                            possible_IDdrains.append(j)
#                            possible_ID_dZ.append(f.getAttribute("AvgAltitude").getDouble()-currentZ)
#                            possibility += 1
#        if possibility > 0:         #if algorithm found a possible pathway for sink to unblock, then get the ID and connect network
#            print "possible"                
#            sink_path = min(possible_ID_dZ)
#            sink_drainID = possible_IDdrains[possible_ID_dZ.index(sink_path)]
#            currentAttList.addAttribute("drainto_ID", sink_drainID)            
#            currentAttList.addAttribute("h_pond", min(possible_ID_dZ))
#        else:               #need to broaden search space and start again
#            continue               #PROBLEM: cannot simply expand the neighbourhood, we risk running a loop through the network
#                                    # Solutions to this problem: will probably need the waterways data set and the outlet location!
#                                    # Search the space adding blocks to the current_neighb matrix that are linked with the existing IDs
#                                    # until we find one that isn't part of the basin.
        
#        ##Draw the network in
#        x_up = currentAttList.getAttribute("Centre_x").getDouble()
#        y_up = currentAttList.getAttribute("Centre_y").getDouble()
#        z_up = currentAttList.getAttribute("AvgAltitude").getDouble()
        
#        uppernode = city.addNode(x_up, y_up, z_up)
#        x_down = city.getFace(self.getBlockUUID(sink_drainID,city)).getAttribute("Centre_x").getDouble()
#        y_down = city.getFace(self.getBlockUUID(sink_drainID,city)).getAttribute("Centre_y").getDouble()
#        z_down = city.getFace(self.getBlockUUID(sink_drainID,city)).getAttribute("AvgAltitude").getDouble()

#        downnode = city.addNode(x_down, y_down, z_down)        

#        network_attr = city.addEdge(uppernode, downnode, self.network)
#        network_attr.addAttribute("NetworkID", currentID)
#        network_attr.addAttribute("BlockID", currentID)
#        network_attr.addAttribute("Z_up", z_up)
#        network_attr.addAttribute("Z_down", z_down)
#        network_attr.addAttribute("max_Zdrop", (min(possible_ID_dZ)*-1))
#        network_attr.addAttribute("Type", -1)                            #1 = basic downstream, -1 = unblocked sink

        
#        #-----------------------------------------------------------------------#
#    ###---------TERRAIN DELINEATION END ------------------------------------------------------------------###

        
    
    
    
    ########################################################################
    ### DELINBLOCKS SUB-FUNCTIONS                                        ###
    ########################################################################
    def getBlockUUID(self, blockid,city):
	try:
            key = self.BLOCKIDtoUUID[blockid]
	except KeyError:
            key = ""	
	return key

    def initBLOCKIDtoUUID(self, city):
	blockuuids = city.getUUIDsOfComponentsInView(self.block)
        for blockuuid in blockuuids:
            block = city.getFace(blockuuid)
            ID = int(round(block.getAttribute("BlockID").getDouble()))
	    self.BLOCKIDtoUUID[ID] = blockuuid

    def autosizeBlocks(self, width, height):
        #Calculates the recommended Block Size dependent on the size of the case study
        #determined by the input map dimensions. Takes width and height and returns block
        #size
        #
        #Rules:
        #   - Based on experience from simulations, aims to reduce simulation times
        #     while providing enough accuracy.
        #   - Aim to simulate under 500 Blocks
        blocklimit = 500
        totarea = width * height
        idealblockarea = totarea / 500
        idealblocksize = math.sqrt(idealblockarea)
        print "IdBS:", idealblocksize
        
        if idealblocksize <= 200:
            blocksize = 200
        elif idealblocksize <= 500:
            blocksize = 500
        elif idealblocksize <= 1000:
            blocksize = 1000
        elif idealblocksize <= 2000:
            blocksize = 2000
        elif idealblocksize/1000 < 10:
            blocksize = (int(idealblocksize/1000)+1)*1000
        else:
            blocksize = (int(idealblocksize/10000)+1)*10000
        
        if blocksize >= 10000:
            print "WARNING: Block Size is very large, it is recommended to use a smaller case study!"    
        
        return blocksize        
        
    def createBlockFace(self, city, x, y, cs, x_adj, y_adj, ID):
        n1 = city.addNode((x+x_adj)*cs,(y+y_adj)*cs,0)
        n2 = city.addNode((x+x_adj+1)*cs,(y+y_adj)*cs,0)
        n3 = city.addNode((x+x_adj+1)*cs,(y+y_adj+1)*cs,0)
        n4 = city.addNode((x+x_adj)*cs,(y+y_adj+1)*cs,0)
        
        plist = nodevector()
        plist.append(n1)
        plist.append(n2)
        plist.append(n3)
        plist.append(n4)
        plist.append(n1)
        
        #Add a face denoted by the point list plist to block view
        block_attr = city.addFace(plist, self.block)        
        block_attr.addAttribute("BlockID", ID)
        return block_attr
        
    def getCBDcoordinates(self):
        if self.locationOption == "S":
            #look up city and grab coordinates
            coordinates = self.CBDcoordinates[self.locationCity]
            return coordinates[0], coordinates[1]   #easting, northing
        elif self.locationOption == "C":
            longitude = self.locationLong
            latitude = self.locationLat
            coordinates = ubcc.convertGeographic2UTM(longitude, latitude)
            return coordinates[0], coordinates[1]   #easting, northing

        
    def retrieveData(self, datasources, startextents, cellsinblock):
        #Scans the original data range and retrieves all the data values contained
        #therein:
        #           - datasources: the Views containing the rasters
        #           - startextents: [xstart, ystart] coordinates
        #           - cellsinblock: how many cells are in one block (defines extents)
        
        #Base Inputs
        lucdatamatrix = []
        popdatamatrix = []
        elevdatamatrix = []
        soildatamatrix = []
        
        #Additional Inputs
        planmapmatrix = []
        employmentmatrix = []
        groundwatermatrix = []
        socpar1matrix = []
        socpar2matrix = []
        
        
        x_start = startextents[0]
        y_start = startextents[1]
        
        for i in range(cellsinblock):
            lucdatamatrix.append([])
            popdatamatrix.append([])
            elevdatamatrix.append([])
            soildatamatrix.append([])
            planmapmatrix.append([])
            employmentmatrix.append([])
            groundwatermatrix.append([])
            socpar1matrix.append([])
            socpar2matrix.append([])
            
            for j in range(cellsinblock):
                lucdatamatrix[i].append(datasources[0].getValue(x_start+i, y_start+j))
                
                
                popdatamatrix[i].append(datasources[1].getValue(x_start+i, y_start+j))
                
                
                elevdatamatrix[i].append(datasources[2].getValue(x_start+i, y_start+j))
                
                
                if self.soildatatype == "C":
                    if datasources[3].getValue(x_start+i, y_start+j) != -9999:
                        soildatamatrix[i].append(self.soildictionary[int(datasources[3].getValue(x_start+i, y_start+j))-1])        #look up mm/hr value
                    else:
                        soildatamatrix[i].append(-9999)
                elif self.soildataunits == "hrs":
                    soildatamatrix[i].append(datasources[3].getValue(x_start+i, y_start+j))     #keep as mm/hr
                elif self.soildataunits == "sec":
                    soildatamatrix[i].append((datasources[3].getValue(x_start+i, y_start+j))*1000*60*60)        #convert to mm/hr
                
                if datasources[4] != 0: planmapmatrix[i].append(datasources.getValue(x_start+i, y_start+j))
                if datasources[5] != 0: employmentmatrix[i].append(datasources.getValue(x_start+i, y_start+j))
                if datasources[6] != 0: groundwatermatrix[i].append(datasources.getValue(x_start+i, y_start+j))
                if datasources[7] != 0: socpar1matrix[i].append(datasources.getValue(x_start+i, y_start+j))
                if datasources[8] != 0: socpar2matrix[i].append(datasources.getValue(x_start+i, y_start+j))
                
        datamatrices = [lucdatamatrix, popdatamatrix, elevdatamatrix, soildatamatrix, planmapmatrix, employmentmatrix, groundwatermatrix, socpar1matrix, socpar2matrix]
        return datamatrices

    def frequencyLUC(self, lucdatamatrix):
        #Determine size of matrix
        matsize = len(lucdatamatrix)
        #'RES', 'COM', 'ORC', 'LI', 'HI', 'CIV', 'SVU', 'RD', 'TR', 'PG', 'REF', 'UND', 'NA'
        lucprop = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        for i in range(matsize):
            for j in range(matsize):
                landclass = lucdatamatrix[i][j]
                if landclass == -9999:
                    pass
                else:
                    lucprop[int(landclass-1)] += 1
        
        #Convert frequency to proportion
        total_n_luc = float(sum(lucprop))
        if total_n_luc == 0:
            return [0,0,0,0,0,0,0,0,0,0,0,0,0], 0
        for i in range(len(lucprop)):
            lucprop[i] = float(lucprop[i])/total_n_luc
        activity = float(total_n_luc) / float((matsize * matsize))
        return lucprop, activity
    
    def calcRichness(self, landclassprop):
        richness = 0
        for i in landclassprop:
            if i != 0:
                richness += 1
        return richness

    def calcShannonMetrics(self, landclassprop, richness):
        if richness == 0:
            return 0,0,0
        
        #Shannon Diversity Index (Shannon, 1948) - measures diversity in categorical data, the information entropy of
        #the distribution: H = -sum(pi ln(pi))
        shandiv = 0
        for sdiv in landclassprop:
            if sdiv != 0:
                shandiv += sdiv*math.log(sdiv)
        shandiv = -1 * shandiv
        
        #Shannon Dominance Index: The degree to which a single class dominates in the area, 0 = evenness
        shandom = math.log(richness) - shandiv
        
        #Shannon Evenness Index: Similar to dominance, the level of evenness among the land classes
        if richness == 1:
            shaneven = 1
        else:
            shaneven = shandiv/math.log(richness)
            
        return shandiv, shandom, shaneven
    
    def findNeighbourhood(self, ID, x, y, numblocks, widthnew, heightnew):
        ### NEIGHBOURHOODs - Search for all 8 neighbours. ###
        neighbour_assign = 0
        #check neighbour IDs
        #check for corner pieces
        if ID - 1 == 0:                            #bottom left
            neighbour_assign = 1
            N_neighbour = ID + widthnew 
            S_neighbour = 0
            W_neighbour = 0
            E_neighbour = ID + 1
            NE_neighbour = N_neighbour + 1
            NW_neighbour = 0
            SE_neighbour = 0
            SW_neighbour = 0
        if ID + 1 == numblocks+1:                  #top right
            neighbour_assign = 1
            N_neighbour = 0
            S_neighbour = ID - widthnew
            W_neighbour = ID - 1
            E_neighbour = 0
            NE_neighbour = 0
            NW_neighbour = 0
            SE_neighbour = 0
            SW_neighbour = S_neighbour - 1
        if ID - widthnew == 0:                     #bottom right
            neighbour_assign = 1
            N_neighbour = ID + widthnew
            S_neighbour = 0
            W_neighbour = ID - 1
            E_neighbour = 0
            NE_neighbour = 0
            NW_neighbour = N_neighbour - 1
            SE_neighbour = 0
            SW_neighbour = 0
        if ID + widthnew == numblocks+1:           #top left
            neighbour_assign = 1
            N_neighbour = 0
            S_neighbour = ID - widthnew
            W_neighbour = 0
            E_neighbour = ID + 1
            NE_neighbour = 0
            NW_neighbour = 0
            SE_neighbour = S_neighbour + 1
            SW_neighbour = 0
        
        #check for edge piece
        if neighbour_assign == 1:
            pass
        else:
            if float(ID)/widthnew == y+1:                  #East edge
                neighbour_assign = 1
                N_neighbour = ID + widthnew
                S_neighbour = ID - widthnew
                W_neighbour = ID - 1
                E_neighbour = 0
                NE_neighbour = 0
                NW_neighbour = N_neighbour - 1
                SE_neighbour = 0
                SW_neighbour = S_neighbour - 1
            if float(ID-1)/widthnew == y:                  #West edge
                neighbour_assign = 1
                N_neighbour = ID + widthnew
                S_neighbour = ID - widthnew
                W_neighbour = 0
                E_neighbour = ID + 1
                NE_neighbour = N_neighbour + 1
                NW_neighbour = 0
                SE_neighbour = S_neighbour + 1
                SW_neighbour = 0
            if ID - widthnew < 0:                          #South edge
                neighbour_assign = 1
                N_neighbour = ID + widthnew
                S_neighbour = 0
                W_neighbour = ID - 1
                E_neighbour = ID + 1
                NE_neighbour = N_neighbour + 1
                NW_neighbour = N_neighbour - 1
                SE_neighbour = 0
                SW_neighbour = 0
            if ID + widthnew > numblocks+1:                #North edge
                neighbour_assign = 1
                N_neighbour = 0
                S_neighbour = ID - widthnew
                W_neighbour = ID - 1
                E_neighbour = ID + 1
                NE_neighbour = 0
                NW_neighbour = 0
                SE_neighbour = S_neighbour + 1
                SW_neighbour = S_neighbour - 1
        
        #if there is still no neighbours assigned then assume standard cross
        if neighbour_assign == 1:
            pass
        else:
            neighbour_assign = 1
            N_neighbour = ID + widthnew
            S_neighbour = ID - widthnew
            W_neighbour = ID - 1
            E_neighbour = ID + 1
            NE_neighbour = N_neighbour + 1
            NW_neighbour = N_neighbour - 1
            SE_neighbour = S_neighbour + 1
            SW_neighbour = S_neighbour - 1
        
        blockNHD = [N_neighbour, S_neighbour, W_neighbour, E_neighbour, NE_neighbour, NW_neighbour, SE_neighbour, SW_neighbour]    
        return blockNHD                
        
    def adjustCount(self, total_count):
        if total_count == 0:
            total_count = 1
        else:
            pass
        return total_count

    def drawPatchFace(self, city, nodes, scalar, offset, PaID, ID, area, LUC, elev, soil):
        rs = scalar #rs = raster size
        plist = nodevector()
        
        for i in range(len(nodes)): #loop across the nodes
            n = city.addNode(nodes[i][0]*rs+offset[0], nodes[i][1]*rs+offset[1], 0)
            plist.append(n)
        
        endnode = city.addNode(nodes[0][0]*rs+offset[0], nodes[0][1]*rs+offset[1], 0)
        plist.append(endnode)
        
        patch_attr = city.addFace(plist, self.patch)
        patch_attr.addAttribute("PatchID", PaID)              #ID of Patch in Block ID
        patch_attr.addAttribute("LandUse", LUC)              #Land use of the patch
        patch_attr.addAttribute("Area", area*rs*rs)                 #Area of the patch
        patch_attr.addAttribute("AvgElev", elev)              #Average elevation of the patch
        patch_attr.addAttribute("SoilK", soil)
        patch_attr.addAttribute("BlockID", ID)              #Block ID that patch belongs to
        return True
    

    
    
    
    
    ########################################################
    #LINK WITH GUI                                         #
    ########################################################        
    def createInputDialog(self):
        form = activatedelinblocksGUI(self, QApplication.activeWindow())
        form.show()
        return True 
