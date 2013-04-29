# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 1.0
@section LICENSE

This file is part of UrbanBEATS (www.urbanbeatsmodel.com)
Copyright (C) 2011, 2012, 2013  Peter M Bach

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
#from md_delinblocksguic import *        #UBCORE
from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4
import math, time
import random as rand
import ubpatchdelin as ubpat
import ubconvertcoord as ubcc
import ubvectormapload as ubvmap
#import urbanbeatsdatatypes as ubdata    #UBCORE

from pydynamind import *               #DYNAMIND
from delinblocksguic import *          #DYNAMIND

class Delinblocks(Module):      #DYNAMIND
#class Delinblocks(object):      #UBCORE
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
        - Modularisation of entire module, patches, vector map loading and other features extracted as separated files
        - Implementation of all remaining features as indicated in the GUI (e.g. D-infinity, DEM smoothing, CBD info, loading of vector maps)
        - delinbasins.py code from previous versions has been integrated into this module, improved upon
            now runs 10 times faster
        - Most of the drawing algorithms are in their own separate functions, a lot of sub-procedures have been made their own functions
    
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
	
	@ingroup UrbanBEATS
        @author Peter M Bach
        """
    
    def __init__(self):            #DYNAMIND
        Module.__init__(self)       #DYNAMIND

#    def __init__(self, activesim, curstate, tabindex):      #UBCORE
#        self.cycletype = curstate       #UBCORE: contains either planning or implementation (so it knows what to do and whether to skip)
#        self.tabindex = tabindex        #UBCORE: the simulation period (knowing what iteration this module is being run at)
#        self.activesim = activesim      #UBCORE
        
        #PARAMETER LIST START
        #-----------------------------------------------------------------------
        
        #General Simulation Parameters
        self.createParameter("BlockSize", DOUBLE, "")       #DYNAMIND
        self.createParameter("blocksize_auto", BOOL, "")    #DYNAMIND    
        self.BlockSize = 400                    #size of the blocks (in m)
        self.blocksize_auto = False             #should the size be chosen automatically?
        
        #DYNAMIND ------->
        self.createParameter("popdatatype", STRING, "")         #DYNAMIND
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
        self.createParameter("spatialmetrics", BOOL, "")        #DYNAMIND
        #-------> DYNAMIND 

        self.popdatatype = "D"                  #population data type: D = density, C = count
        self.soildatatype = "I"                 #I = infiltration rates, C = classification
        self.soildataunits = "hrs"              #sec = m/s, hrs = mm/hr
        self.elevdatadatum = "S"                #S = sea level, C = custom
        self.elevdatacustomref = float(0.0)              #reference above sea level for custom elevation
        self.include_plan_map = False           #planner's map displaying typology distributions
        self.include_local_map = False          #locality map displaying location of centres
        self.include_employment = False         #include employment data for industrial land uses?
        self.jobdatatype = "D"                  #employment data type: D = density, C = count
        self.include_rivers = False             #include river systems
        self.include_lakes = False              #include lake systems
        self.include_groundwater = False        #include groundwater table
        self.groundwater_datum = "Sea"          #"Sea" = Sea level, "Surf" = Surface level
        
        #self.include_road_net = False           #road network map not working yet
        #self.include_supply_net = False       #include water supply mains
        #self.include_sewer_net = False        #include sewer mains
        
        self.include_soc_par1 = False            #include a social parameter in the simulation?
        self.include_soc_par2 = False            #include a social parameter in the simulation?
        self.social_par1_name = "unnamed1"      #name of social parameter1
        self.social_par2_name = "unnamed2"      #name of social parameter2
        self.socpar1_type = "B"                 #B = Binary, P = Proportionate
        self.socpar2_type = "B"
        
        self.patchdelin = True                  #perform patch delineation? All subsequent algorithms will need to consider this
        self.spatialmetrics = True              #perform calculation of spatial metrics? Just an additional feature
        
        #Local Extents and Map Connectivity                   
        #DYNAMIND ------>        
        self.createParameter("Neighbourhood", STRING,"")
        self.createParameter("vn4FlowPaths", BOOL,"")
        self.createParameter("vn4Patches", BOOL,"")                
        self.createParameter("flow_method", STRING,"")
        self.createParameter("demsmooth_choose", BOOL,"")
        self.createParameter("demsmooth_passes", DOUBLE,"")
        #------> DYNAMIND 
        
        self.Neighbourhood = "M"                #three options: M = Moore, N = von Neumann
        self.vn4FlowPaths = False
        self.vn4Patches = False               
        self.flow_method = "D8"                 #three options: DI = D-infinity (Tarboton), D8 = D8 (O'Callaghan & Mark) and MS = Divergent (Freeman)
        self.demsmooth_choose = False
        self.demsmooth_passes = 1
        
        #Regional Geography
        #DYNAMIND ------------>        
        self.createParameter("considerCBD", BOOL, "")
        self.createParameter("locationOption", STRING, "")
        self.createParameter("locationCity", STRING, "")
        self.createParameter("locationLong", DOUBLE, "")
        self.createParameter("locationLat", DOUBLE, "")
        self.createParameter("marklocation", BOOL, "")
        #------------> DYNAMIND 
        
        self.considerCBD = False
        self.locationOption = "S"       #method for setting location option: S = selection, C = coordinates
        self.locationCity = "Melbourne" #index of the combobox, it returns the city name in a different vector
        self.locationLong = float(0.0)           #longitude of the location
        self.locationLat = float(0.0)            #latitude of the location
        self.marklocation = False       #should this CBD location be marked on the map as a point? If yes, it will be saved to the Block Centre Points
        
        #Hidden Inputs
        #-------------> DYNAMIND
        self.createParameter("LocalityFilename", STRING, "")
        self.createParameter("RiversFilename", STRING, "")
        self.createParameter("LakesFilename", STRING, "")
        self.createParameter("obtain_flowbasins", STRING, "")           #changed internally depending on cycle to skip flowpath delineation
        self.LocalityFilename = "C:/UrbanBEATSv1CaseStudies/Yarra Estuary Catchment/GIS Maps/LocalityMap_UTM.shp"
        self.RiversFilename = "C:/UrbanBEATSv1CaseStudies/Yarra Estuary Catchment/GIS Maps/Rivers_UTM.shp"
        self.LakesFilename = "C:/UrbanBEATSv1CaseStudies/Yarra Estuary Catchment/GIS Maps/Lakes.shp"
        self.obtain_flowbasins = "D"                                    #F = file, D = delineate
        
        self.createParameter("xllcorner", DOUBLE, "")
        self.createParameter("yllcorner", DOUBLE, "")
        self.xllcorner = 313420.7405    #Yarra Estuary Limits
        self.yllcorner = 5807211.478    #spatial extents of the input map
        #-------------> DYNAMIND
        
        #LATER ON! FOR LATER CYCLES - CHANGING THIS VARIABLE WILL ALLOW SKIPPING OF FLOWPATHS AND BASIN DELINATION!
        self.obtain_flowbasins = "D"                                    #F = file, D = delineate
        
#        self.xllcorner = 0    #UBCORE Obtained from the loaded raster data (elevation) upon run-time
#        self.yllcorner = 0    #UBCORE spatial extents of the input map
        
        #-----------------------------------------------------------------------
        #END OF INPUT PARAMETER LIST
        
        #Input Data
        #DYNAMIND -------------->        
        self.elevation = View("Elevation", RASTERDATA, READ)
        self.soil = View("Soil", RASTERDATA, READ)
        self.landuse = View("LandUse", RASTERDATA, READ)
        self.population = View("Population", RASTERDATA, READ)
        self.plan_map = View("PlanMap", RASTERDATA, READ)               #<-- ADDITIONAL INPUTS
        self.employment = View("Employment", RASTERDATA, READ)          #rivers, lakes and localities are read externally
        self.groundwater = View("Groundwater", RASTERDATA, READ)        #see HIDDEN PARAMETERS
        self.socpar1 = View("SocialParam1", RASTERDATA, READ)
        self.socpar2 = View("SocialParam2", RASTERDATA, READ)
        #--------------> DYNAMIND 
        
#        #self.road_map = View("RoadMap", VECTORDATA, READ)
#        #self.supply_net = View("SupplyMains", VECTORDATA, READ)
#        #self.sewer_net = View("SewerMains", VECTORDATA, READ)
        
#        #UBCORE -------------->
#        self.elevation = 0            #<-- BASE INPUTS
#        self.soil = 0
#        self.landuse = 0
#        self.population = 0
#        self.plan_map = 0               #<-- ADDITIONAL INPUTS
#        self.employment = 0          #rivers, lakes and localities are read externally
#        self.groundwater = 0        #see HIDDEN PARAMETERS
#        self.socpar1 = 0
#        self.socpar2 = 0
#        #-------------- END OF UBCORE ---------

        #DYNAMIND VIEWS =================================================================================================
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
        self.mapattributes.addAttribute("TotalBasins")
        self.mapattributes.addAttribute("include_plan_map")
        self.mapattributes.addAttribute("include_local_map")
        self.mapattributes.addAttribute("include_employment")
        self.mapattributes.addAttribute("include_rivers")
        self.mapattributes.addAttribute("include_lakes")
        self.mapattributes.addAttribute("include_groundwater")
        self.mapattributes.addAttribute("include_soc_par1")
        self.mapattributes.addAttribute("include_soc_par2")
        self.mapattributes.addAttribute("patchdelin")
        self.mapattributes.addAttribute("spatialmetrics")
        self.mapattributes.addAttribute("considerCBD")
        #self.mapattributes.addAttribute("UrbanSimData")             #"Yes" or "no" as to whether input derived from UrbanSim
        
        #Block Data View
        self.block = View("Block", FACE, WRITE)
        self.block.addAttribute("BlockID")              #ID of the Block (different from UUID)
        self.block.addAttribute("BasinID")              #ID of the Basin that Block belongs to
        self.block.addAttribute("LocateX")             #x location of bottom-left corner of block (for drawing)
        self.block.addAttribute("LocateY")             #y location of bottom-right corner of block (for drawing)
        self.block.addAttribute("CentreX")             #centre x location of block
        self.block.addAttribute("CentreY")              #centre y location of block
        self.block.addAttribute("OriginX")
        self.block.addAttribute("OriginY")             
        self.block.addAttribute("Status")               #Status: 1 = part of simulation, 0 = not part of simulation
        self.block.addAttribute("Active")             #Degree to which block is active in simulation (how much data is available)
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
        
        self.block.addAttribute("Pop")           #Total people LIVING in block
        self.block.addAttribute("Employ")           #Total people EMPLOYED in block
        self.block.addAttribute("GWDepth")              #Depth to groundwater from surface
        self.block.addAttribute("SocPar1")
        self.block.addAttribute("SocPar2")
        self.block.addAttribute("PM_RES")
        self.block.addAttribute("PM_COM")
        self.block.addAttribute("PM_LI")
        self.block.addAttribute("PM_HI")
        self.block.addAttribute("HasRiv")
        self.block.addAttribute("HasLake")
        self.block.addAttribute("LakeAr")
        self.block.addAttribute("HasLoc")
        self.block.addAttribute("NFacil")
        
        self.block.addAttribute("Patches")           #Total Patches in Block
        self.block.addAttribute("Rich")             #Richness of Land use mix in Block
        self.block.addAttribute("ShDIV")           #Shannon Diversity Index
        self.block.addAttribute("ShDOM")           #Shannon Dominance Index
        self.block.addAttribute("ShEVEN")          #Shannon Evenness Index
        
        self.block.addAttribute("downID")            #ID block water flows to naturally
        self.block.addAttribute("maxdZ")            #maximum drop in elevation
        self.block.addAttribute("slope")            #average slope
        self.block.addAttribute("drainID")           #ID block drains to if a sink
        self.block.addAttribute("h_pond")               #height of ponding before sink can drain
        self.block.addAttribute("Outlet")       #If the Block is an outlet = 1, yes - 0, no
        self.block.addAttribute("CBDdist")          #Distance from CBD [km]
        self.block.addAttribute("CBDdir")         #Which direction to travel from CBD to get to Block? Specified as an angle in degrees
        
        self.block.addAttribute("UpstrIDs")
        
        #Patch Data View
        self.patch = View("Patch", FACE, WRITE)
        self.patch.addAttribute("LandUse")              #Land use of the patch
        self.patch.addAttribute("Area")                 #Area of the patch
        self.patch.addAttribute("AvgElev")              #Average elevation of the patch
        self.patch.addAttribute("SoilK")
        self.patch.addAttribute("BlockID")              #Block ID that patch belongs to
        
        #Network Data View
        self.network = View("Network", EDGE, WRITE)
        self.network.addAttribute("BlockID")
        self.network.addAttribute("DownID")
        self.network.addAttribute("Z_up")
        self.network.addAttribute("Z_down")
        self.network.addAttribute("max_Zdrop")
        self.network.addAttribute("Type")
        self.network.addAttribute("avg_slope")
        
        #Nodes Data View
        self.blocknodes = View("BlockNodes", NODE, WRITE)
        self.blocknodes.addAttribute("BlockID")         #Holds the Block ID or -1 for CBD location
        self.blocknodes.addAttribute("AvgElev")
        self.blocknodes.addAttribute("Type")
        
        #Locality Map Data View
        self.blocklocality = View("BlockLocality", NODE, WRITE)
        self.blocklocality.addAttribute("BlockID")
        self.blocklocality.addAttribute("Type")
        self.blocklocality.addAttribute("Area")
        self.blocklocality.addAttribute("TIF")
        self.blocklocality.addAttribute("ARoof")
        self.blocklocality.addAttribute("AvgWD")
        
        #Append all views to the data stream
        datastream = []
        datastream.append(self.elevation)
        datastream.append(self.soil)
        datastream.append(self.landuse)
        datastream.append(self.population)
        #datastream.append(self.urbansim)
        
        datastream.append(self.plan_map)
        datastream.append(self.employment)
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
        datastream.append(self.blocklocality)
        
        self.addData("City", datastream)

        #================================================================================================= DYNAMIND VIEWS END
  
        self.BlockIDtoUUID = {} #DYNAMIND : Define dictionary to hold Block ID - UUID relationship
        
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

#    def printc(self, message):      #UBCORE FUNCTION
#        self.activesim.console.appendPlainText(str(time.asctime())+" | "+str(message))
#        return True
    
#    def loadRaster(self, dataset, dtype):       #UBCORE FUNCTION
#        self.printc("Loading "+str(dtype))
#        rasterload = ubdata.importRasterData(dataset[str(dtype)])
#        self.printc("Load "+str(dtype)+" Complete")
#        return rasterload    
    
    def getBlockUUID(self, blockid,city):       #DYNAMIND FUNCTION
        try:
            key = self.BlockIDtoUUID[int(blockid)]
        except KeyError:
            key = ""	
        return key


    def initBLOCKIDtoUUID(self, city):          #DYNAMIND FUNCTION
        blockuuids = city.getUUIDsOfComponentsInView(self.block)
        for blockuuid in blockuuids:
            block = city.getFace(blockuuid)
            ID = int(block.getAttribute("BlockID").getDouble())
            self.BlockIDtoUUID[ID] = blockuuid
    
    def run(self):
#        self.printc("StartDelinBlocks!")        #UBCORE
        rand.seed()

        city = self.getData("City")     #DYNAMIND : Get the datastream containing all the info
        
        cs = self.BlockSize             #set blocksize to a local variable with a short name cs = cell size
                
        if self.Neighbourhood == "N":           #Set neighbourhood Type
            neighbourhood_type = 4              #von Neumann = 4 neighbours
        else: 
            neighbourhood_type = 8              #Moore = 8 neighbours
        
#        self.printc(self.BlockSize)        #UBCORE
        
#        ## Retrieve the raster data UBCORE VERSION ###############################################################################
#        ## 4 BASIC INPUTS ###
#        cycledataset = self.activesim.getCycleDataSet("pc", 0)          #UBCORE        
#        elevationraster = self.loadRaster(cycledataset, "Elevation")   #ELEVATION AND SOIL DATA ARE NOT URBANSIM DEPENDENT!
#        self.xllcorner = elevationraster.getExtents()[0] 
#        self.yllcorner = elevationraster.getExtents()[1]    #spatial extents of the input map
        
#        soilraster = self.loadRaster(cycledataset, "Soil")
#        landuseraster = self.loadRaster(cycledataset, "Land Use")
#        population = self.loadRaster(cycledataset, "Population")        
        
#        ### 7 ADDITIONAL INPUTS ###
#        #(1) - Planner's Map
#        if self.include_plan_map: plan_map = self.loadRaster(cycledataset, "Planning")        
#        else: plan_map = 0
       
#        #(2) - Locality Map
#        if self.include_local_map: localitymap = ubvmap.runLocalityImport(cycledataset["Locality"])
#        else: localitymap = 0
        
#        #(3) - Employment Map
#        if self.include_employment: employment = self.loadRaster(cycledataset, "Employment")
#        else: employment = 0
        
#        #(4) - Rivers Map
#        if self.include_rivers: riverpoints = ubvmap.runRiverImport(float(cs/4), cycledataset["Rivers"])
#        else: riverpoints = 0
        
#        #(5) - Lakes Map
#        if self.include_lakes: lakepoints = ubvmap.runLakesImport(cycledataset["Lakes"])
#        else: lakepoints = 0
        
#        #(6) - Groundwater Map
#        if self.include_groundwater: groundwater = self.loadRaster(cycledataset, "Groundwater")
#        else: groundwater = 0
        
#        #(7) - Social Parameters
#        if self.include_soc_par1: socpar1 = self.loadRaster(cycledataset, "Social Parameters")
#        else: socpar1 = 0
#        #print "Socpar1", socpar1
#        if self.include_soc_par2: socpar2 = self.loadRaster(cycledataset, "Social Parameters")
#        else: socpar2 = 0
#        #print "Socpar2", socpar2
        
#        #road_net, supply_net and sewer_net = coming in future versions

#        ################################### END OF DATA RETRIEVAL UBCORE VERSION ##############################################        
        
        ## Retrieve the raster data DYNAMIND VERSION ##########################################################################        
        ### 4 BASIC INPUTS ###
        elevationraster = self.getRasterData("City", self.elevation)                   #ELEVATION AND SOIL DATA ARE NOT URBANSIM DEPENDENT!
        soilraster = self.getRasterData("City", self.soil)
        landuseraster = self.getRasterData("City", self.landuse)
        population = self.getRasterData("City", self.population)
        
        ### 7 ADDITIONAL INPUTS ###
        #(1) - Planner's Map
        if self.include_plan_map: plan_map = self.getRasterData("City", self.plan_map)
        else: plan_map = 0
        
        #(2) - Locality Map
        if self.include_local_map: localitymap = ubvmap.runLocalityImport(self.LocalityFilename)
        else: localitymap = 0
        
        #(3) - Employment Map
        if self.include_employment: employment = self.getRasterData("City", self.employment)
        else: employment = 0
        
        #(4) - Rivers Map
        if self.include_rivers: riverpoints = ubvmap.runRiverImport(float(cs/4), self.RiversFilename)
        else: riverpoints = 0
        
        #(5) - Lakes Map
        if self.include_lakes: lakepoints = ubvmap.runLakesImport(self.LakesFilename)
        else: lakepoints = 0
        
        #(6) - Groundwater Map
        if self.include_groundwater: groundwater = self.getRasterData("City", self.groundwater)
        else: groundwater = 0
        
        #(7) - Social Parameters
        if self.include_soc_par1: socpar1 = self.getRasterData("City", self.socpar1)
        else: socpar1 = 0
        print "Socpar1", socpar1
        if self.include_soc_par2: socpar2 = self.getRasterData("City", self.socpar2)
        else: socpar2 = 0
        print "Socpar2", socpar2
        
        #road_net, supply_net and sewer_net = coming in future versions
        
        ################################## END OF DATA RETRIEVAL DYNAMIND VERSION ##############################################
        
        inputres = landuseraster.getCellSize()                                #input data resolution [m]
#        width =  elevationraster.getDimensions()[0] * elevationraster.getCellSize()     #UBCORE
#        height =  elevationraster.getDimensions()[1] * elevationraster.getCellSize()   #UBCORE 
        width = elevationraster.getWidth() * elevationraster.getCellSize()              #DYNAMIND "getWidth" syntax returns no. of cells
        height = elevationraster.getHeight() * elevationraster.getCellSize()            #DYNAMIND to get actual width, need to multiply by cell size [m]         

#        xllcorner, yllcorner = landuseraster.getExtents()       #UBCORE
        xllcorner = self.xllcorner              #DYNAMIND
        yllcorner = self.yllcorner              #DYNAMIND
#        self.printc(elevationraster.getDimensions()[0])         #UBCORE
#        self.printc(str(width)+","+str(height))                 #UBCORE

        #####################################################################################                
        
        ### AUTO SIZE BLOCKS ###
        if self.blocksize_auto == True:
            cs = self.autosizeBlocks(width, height)
        else:
            cs = self.BlockSize                                                 #BlockSize stored locally [m]
        cellsinblock = int(cs/inputres)                                         #tells us how many smaller cells are in one length of block  
        
#        #UBCORE ---------------->
#        self.printc("Width "+str(width))
#        self.printc("Height "+str(height))                  
#        self.printc("Block Size: "+str(cs))
#        self.printc("Cells in Block: "+str(cellsinblock))
#        #------------------> UBCORE 
        
        #DYNAMIND --------------->
        print "Width", width
        print "Height", height
        print "Block Size: ", cs
        print "Cells in Block: ", cellsinblock
        #---------------> DYNAMIND
        
        #Note that the simulation area needs to have a larger width and larger height than the data input area!
        whfactor = 1 - (1/(cs*2))               #factor replaces the rounding function and speeds up computation
        widthnew = int(width/cs+whfactor)       #width of the simulation area (divide total width by block size and round) [#Blocks]
        heightnew = int(height/cs+whfactor)      #height of the simulation area (multiply block size with this to get actual length) [#Blocks]
        numblocks = widthnew * heightnew        #number of blocks based on how many blocks wide x how many blocks tall [#Blocks]
        
        ### MAP ATTRIBUTES - The Global Attributes List - write present information across to this component
#        map_attr = ubdata.UBComponent()         #UBCORE
        map_attr = Component()                  #DYNAMIND
        map_attr.addAttribute("NumBlocks", numblocks)                   #Number of blocks in the grid
        map_attr.addAttribute("WidthBlocks", widthnew)                  #Width of simulation area in # of blocks
        map_attr.addAttribute("HeightBlocks", heightnew)                #Height of simulation area in # of blocks
        map_attr.addAttribute("BlockSize", cs)                          #Size of block [m]
        map_attr.addAttribute("InputReso", inputres)                    #Resolution of the input data [m]
        map_attr.addAttribute("xllcorner", xllcorner)
        map_attr.addAttribute("yllcorner", yllcorner)
        map_attr.addAttribute("Neigh_Type", neighbourhood_type) 
        map_attr.addAttribute("ConsiderCBD", self.considerCBD)
        map_attr.addAttribute("include_plan_map", self.include_plan_map)
        map_attr.addAttribute("include_local_map", self.include_local_map)
        map_attr.addAttribute("include_employment", self.include_employment)
        map_attr.addAttribute("include_rivers", self.include_rivers)
        map_attr.addAttribute("include_lakes", self.include_lakes)
        map_attr.addAttribute("include_groundwater", self.include_groundwater)
        map_attr.addAttribute("include_soc_par1", self.include_soc_par1)
        map_attr.addAttribute("include_soc_par2", self.include_soc_par2)
        map_attr.addAttribute("patchdelin", self.patchdelin)
        map_attr.addAttribute("spatialmetrics", self.spatialmetrics)
        map_attr.addAttribute("considerCBD", self.considerCBD)
        
        city.addComponent(map_attr, self.mapattributes)                 #DYNAMIND: add the component list map_attr to the View self.mapattributes        
        
        #Look up long and lat of CBD if need to be considered
        if self.considerCBD:
            #Grab CBD coordinates, convert to UTM if necessary
            cityeasting, citynorthing = self.getCBDcoordinates()        #EASTING = X, NORTHING = Y
            #delinblocks works at Global (0,0) then exports it and offsets the map. Hidden parameters xll and yllcorner deal with real extents
                                                                #to realign it with the original data
            map_attr.addAttribute("CBDLocationLong", cityeasting)
            map_attr.addAttribute("CBDLocationLat", citynorthing)
            
            #Use HIDDEN PARAMETERS FOR NOW
            
            #See if marklocation can be added
#            #UBCORE ------------------>            
#            if self.marklocation:
#                city_pts = ubdata.UBVector([(cityeasting-self.xllcorner, citynorthing-self.yllcorner,0)])
#                city_pts.addAttribute("BlockID", -1)     #-1 for CBD
#                city_pts.addAttribute("AvgElev", -1)     #-1 for CBD
#                city_pts.addAttribute("Type", "CBD")     #-1 for CBD
#                self.activesim.addAsset("CPCityCentre", city_pts)
#            #------------------> UBCORE 

            #DYNAMIND --------------->
            if self.marklocation:
                loc = city.addNode(cityeasting-self.xllcorner, citynorthing-self.yllcorner, 0, self.blocknodes)
                loc.addAttribute("BlockID", -1)     #-1 for CBD
                loc.addAttribute("AvgElev", -1)     #-1 for CBD
                loc.addAttribute("Type", "CBD")     #-1 for CBD
            #---------------> DYNAMIND         
        
#        self.activesim.addAsset("MapAttributes", map_attr)                 #UBCORE: save Mapattribuets as an asset of the current simulation
        
        x_adj = 0               #these track the position of the 'draw cursor', these offset the cursor
        y_adj = 0               #can be used to offset the drawing completely from (0,0)
        
        ########################################################################
        ### DRAW BLOCKS AND ASSIGN INFO                                      ###
        ######################################################################## 
        blockIDcount = 1     #counts through Block ID, initialize this variable here
        for y in range(heightnew):              #outer loop scans through rows
            for x in range(widthnew):           #inner loop scans through columns

                print "CURRENT BLOCK ID: "+str(blockIDcount)           #DYNAMIND                
#                self.printc("CURRENT BLOCK ID: "+str(blockIDcount))     #UBCORE

                block_attr = self.createBlockFace(city, x, y, cs, x_adj, y_adj, blockIDcount)   #DYNAMIND                
#                block_attr = self.createBlockFace(x, y, cs, x_adj, y_adj, blockIDcount)         #UBCORE
                
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
                    currenteasting = xcentre + self.xllcorner
                    currentnorthing = ycentre + self.yllcorner
                    
                    #Calculate distance and angle
                    dist = math.sqrt(math.pow((cityeasting-currenteasting),2)+math.pow((citynorthing-currentnorthing),2))
                    theta = math.degrees(math.atan((currentnorthing - citynorthing)/(currenteasting - cityeasting)))
                    
                    block_attr.addAttribute("CBDdist", dist)
                    block_attr.addAttribute("CBDdir", theta)
                
                
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
                block_attr.addAttribute("Active", activity)
                
                
                ####################################################
                ### 2.1 CALCULATE SPATIAL METRICS                ###
                ####################################################
                #Using land class frequencies
                if self.spatialmetrics:
                    richness = self.calcRichness(landclassprop)
                    shdiv, shdom, sheven = self.calcShannonMetrics(landclassprop, richness)
                    block_attr.addAttribute("Rich", richness)
                    block_attr.addAttribute("ShDiv", shdiv)
                    block_attr.addAttribute("ShDom", shdom)
                    block_attr.addAttribute("ShEven", sheven)                    
                
              
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
                job_sum_total = 0
                
                plan_map_sums = [0,0,0,0]       #4 categories of planner's map dependent on RES, COM, LI, HI
                plan_map_counts = [0,0,0,0]
                
                elevlist = []
                
                for a in range(cellsinblock):        #Loop across all cells in the block
                    for b in range(cellsinblock):
                        if soildatamatrix[a][b] != -9999:
                            raster_sum_soil += soildatamatrix[a][b]
                            total_n_soil += 1
                        if elevdatamatrix[a][b] != -9999:
                            total_n_elev += 1
                            elevlist.append(elevdatamatrix[a][b])
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
                            if employmentmatrix[a][b] != -9999:
                                if self.jobdatatype == "C":
                                    job_sum_total += employmentmatrix[a][b]
                                else:
                                    job_sum_total += employmentmatrix[a][b] * (inputres*inputres)/10000
                            
                        #GROUNDWATER TABLE - Like Elevation, but scaled based on correct datum
                        if self.include_groundwater:
                            gwdepthcumu = 0
                            gwcount = 0
                            if groundwatermatrix[a][b] != -9999:
                                gwdepthcumu += groundwatermatrix[a][b]
                                gwcount += 1
                        
                        #SOCIAL PARAMETERS - Like Population if proportion, if Binary, based on majority
                        if self.include_soc_par1:
                            if len(socpar1matrix) != 0:
                                if socpar1matrix[a][b] != -9999:
                                    soc_par1 += socpar1matrix[a][b]
                                    total_n_soc_par1 += 1
                        if self.include_soc_par2:
                            if len(socpar2matrix) != 0 :
                                if socpar2matrix[a][b] != -9999:
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
                block_attr.addAttribute("Pop", pop_sum_total)
                
                if blockstatus == 1:
#                    curblock_node = ubdata.UBVector([(xcentre,ycentre,0)])              #UBCORE
                    curblock_node = city.addNode(xcentre,ycentre,0, self.blocknodes)    #DYNAMIND
                    curblock_node.addAttribute("BlockID", blockIDcount)
                    curblock_node.addAttribute("AvgElev", raster_sum_elev/total_n_elev)
                    curblock_node.addAttribute("Type", "Block")
#                    self.activesim.addAsset("CPBlockID"+str(blockIDcount), curblock_node)   #UBCORE
                
                if self.include_soc_par1:
                    block_attr.addAttribute("SocPar1", soc_par1/total_n_soc_par1)
                if self.include_soc_par2:
                    block_attr.addAttribute("SocPar2", soc_par2/total_n_soc_par2)
                if self.include_plan_map:
                    block_attr.addAttribute("PM_RES", plan_map_sums[0]/plan_map_counts[0])
                    block_attr.addAttribute("PM_COM", plan_map_sums[1]/plan_map_counts[1])
                    block_attr.addAttribute("PM_LI", plan_map_sums[2]/plan_map_counts[2])
                    block_attr.addAttribute("PM_HI", plan_map_sums[3]/plan_map_counts[3])
                if self.include_employment:
                    block_attr.addAttribute("Employ", job_sum_total)           #Total people EMPLOYED in block
                if self.include_groundwater:
                    if self.groundwater_datum == "Sea":
                        if total_n_elev == 0 or gwcount == 0:
                            gwdepth = -9999
                        else:
                            gwdepth = float(raster_sum_elev/total_n_elev) - float(gwdepthcumu/gwcount)
                    elif self.groundwater_datum == "Surf":
                        if gwcount == 0:
                            gwdepth = -9999
                        else:
                            gwdepth = float(gwdepthcumu/gwcount)
                    block_attr.addAttribute("GWDepth", gwdepth)
                    
                #Rivers, Lakes & Locality Map Data Locate for Block and Assign
                blockxmin = xorigin + self.xllcorner            #Grab the corners of the current block
                blockxmax = xorigin + self.xllcorner + cs
                blockymin = yorigin + self.yllcorner
                blockymax = yorigin + self.yllcorner + cs
                
                #RIVERS - At least one point within Block
                hasriver = 0
                if self.include_rivers:
                    pointcount = 0
                    while pointcount != len(riverpoints):
                        pointset = riverpoints[pointcount]
                        pointcount += 1
                        if pointset[0] >= blockxmin and pointset[0] < blockxmax:
                            if pointset[1] >= blockymin and pointset[1] < blockymax:
                                hasriver = 1
                                pointcount = len(riverpoints)
                    block_attr.addAttribute("HasRiv", hasriver)
                
                #LAKES - Centroid within Block
                haslake = 0
                lakearea = 0
                if self.include_lakes:
                    pointcount = 0
                    while pointcount != len(lakepoints):
                        pointset = lakepoints[pointcount]
                        pointcount += 1
                        if pointset[0] >= blockxmin and pointset[0] < blockxmax:
                            if pointset[1] >= blockymin and pointset[1] < blockymax:
                                haslake = 1
                                lakearea = pointset[2]
                                pointcount = len(lakepoints)
                    block_attr.addAttribute("HasLake", haslake)
                    block_attr.addAttribute("LakeAr", lakearea)
                    
                #LOCALITY MAP - Must scan each point and place in Block!
                haslocal = 0
                facilcount = 0
                if self.include_local_map:
                    for locfeature in localitymap:
                        if locfeature[1] >= blockxmin and locfeature[1] < blockxmax:
                            if locfeature[2] >= blockymin and locfeature[2] < blockymax:
                                haslocal = 1
                                facilcount += 1
                                fac_attr = city.addNode(locfeature[1]-self.xllcorner, locfeature[2]-self.yllcorner, 0, self.blocklocality)  #DYNAMIND                                
#                                fac_attr = ubdata.UBVector([(locfeature[1]-self.xllcorner, locfeature[2]-self.yllcorner, 0, self.blocklocality)])   #UBCORE
                                fac_attr.addAttribute("BlockID", blockIDcount)
                                fac_attr.addAttribute("Type", locfeature[0])
                                fac_attr.addAttribute("Area", locfeature[3])
                                fac_attr.addAttribute("TIF", locfeature[4])
                                fac_attr.addAttribute("ARoof", locfeature[5])
                                fac_attr.addAttribute("AvgWD", locfeature[6])
#                                self.activesim.addAsset("FacilityID"+str(facilcount))       #UBCORE
                                localitymap.remove(locfeature)  #Remove this entry from the matrix to make it shorter for next time
                                
                    block_attr.addAttribute("HasLoc", haslocal)
                    block_attr.addAttribute("NFacil", facilcount)
                
                
                ####################################################
                ### 2.3 DELINEATE PATCHES                        ###
                ####################################################
                #Call the function using the current Block's Patch information
                if self.patchdelin:
                    patchdict = ubpat.landscapePatchDelineation(lucdatamatrix, elevdatamatrix, soildatamatrix)
                    #Draw the patches and save info to view
                    for i in range(len(patchdict)):
                        panodes = patchdict["PatchID"+str(i+1)][4]
                        paarea = patchdict["PatchID"+str(i+1)][0]
                        paluc = patchdict["PatchID"+str(i+1)][1]
                        paelev = patchdict["PatchID"+str(i+1)][2]
                        pasoil = patchdict["PatchID"+str(i+1)][3]
#                        self.drawPatchFace(panodes, inputres, offset, i+1, blockIDcount, paarea, paluc, paelev, pasoil)         #UBCORE
                        self.drawPatchFace(city, panodes, inputres, offset, i+1, blockIDcount, paarea, paluc, paelev, pasoil)   #DYNAMIND
                        
                    block_attr.addAttribute("Patches", len(patchdict))
                    #print "End Patches"
                
                ### FINISH UP THE LOOP ###
                block_attr.addAttribute("BasinID", 0)               #Assign Default value of zero, this is altered below
                
                ### INCREMENT BLOCK ID COUNT BY 1 ###
#                self.activesim.addAsset("BlockID"+str(blockIDcount), block_attr)        #UBCORE: Add block asset to simulation storage
                blockIDcount += 1    #increase counter by one before next loop to represent next Block ID
                #END OF BLOCK LOOP
        
        ########################################################################
        ### 3.) TERRAIN & BASIN DELINEATION                                  ###
        ########################################################################
        #DynaMind's Block Views are saved using a special encoding - the UUID, we therefore have to reference
        #Block ID with the View's UUID.
        self.initBLOCKIDtoUUID(city)    #DYNAMIND: gets all UUIDs of each block and sets up a dictionary to refer to.
                
        if self.demsmooth_choose:
            for currentpass in range(int(self.demsmooth_passes)):
                self.smoothDEM(numblocks, neighbourhood_type) 
        
        #Determine whether terrain delineation already exists or whether it needs to be done
        if self.obtain_flowbasins == "F":               #F = file
            self.retrieveFlowBasinsFromFile(filename, city, numblocks)          #DYNAMIND
#            self.retrieveFlowBasinsFromFile(filename, numblocks)                #UBCORE
        elif self.obtain_flowbasins == "D":             #D = delineate
#            #-----> UBCORE
#            self.delineateFlowPaths(numblocks, cs, neighbourhood_type)         
#            hash_table = self.createBlockHashTable(numblocks)                   
#            totalbasins = self.delineateBasins(numblocks, hash_table)
#            map_attr.addAttribute("TotalBasins", totalbasins)
#            #-------> UBCORE

            #DYNAMIND -------------->            
            self.delineateFlowPaths(city, numblocks, cs, neighbourhood_type)
            hash_table = self.createBlockHashTable(city, numblocks)
            totalbasins = self.delineateBasins(city, numblocks, hash_table)
            map_attr.addAttribute("TotalBasins", totalbasins)
            #------------> DYNAMIND
            
            self.saveFlowBasinsToFile(numblocks, hash_table)
            
    ########################################    
#        #UBCORE ----------------------------------------->       
#        #RESET ALL RASTER AND VECTOR DATA VARIABLES        
#        elevationraster.resetData()
#        soilraster.resetData()
#        landuseraster.resetData()
#        population.resetData()
#        if plan_map != 0: plan_map.resetData()
#        if localitymap != 0: localitymap = 0
#        if employment != 0: employment.resetData()
#        if riverpoints != 0: riverpoints = 0
#        if lakepoints != 0: lakepoints = 0
#        if groundwater != 0: groundwater.resetData()
#        if socpar1 != 0: socpar1.resetData()
#        if socpar2 != 0: socpar2.resetData()
#        self.printc("End of DelinBlocks")
#        #-----------------------------------------> UBCORE 

    ########################################################################
    ### DELINBLOCKS SUB-FUNCTIONS                                        ###
    ########################################################################

    def autosizeBlocks(self, width, height):
        """Calculates the recommended Block Size dependent on the size of the case study
        determined by the input map dimensions. Takes width and height and returns block
        size
        
        Rules:
           - Based on experience from simulations, aims to reduce simulation times
             while providing enough accuracy.
           - Aim to simulate under 500 Blocks"""
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
    
    def createBlockFace(self, city, x, y, cs, x_adj, y_adj, ID):                #DYNAMIND VERSION
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
        block_attr.addAttribute("BlockID", int(ID))
        return block_attr       # ------------------------------------------END OF DYNAMIND VERSION
    
#    def createBlockFace(self, x, y, cs, x_adj, y_adj, ID):                      #UBCORE VERSION
#        n1 = ((x+x_adj)*cs,(y+y_adj)*cs,0)
#        n2 = ((x+x_adj+1)*cs,(y+y_adj)*cs,0)
#        n3 = ((x+x_adj+1)*cs,(y+y_adj+1)*cs,0)
#        n4 = ((x+x_adj)*cs,(y+y_adj+1)*cs,0)
        
#        #Definte the UrbanBEATS Asset        
#        block_attr = ubdata.UBVector([n1, n2, n3, n4, n1])        
#        block_attr.addAttribute("BlockID", int(ID))
        
#        return block_attr   # --------------------------------------------- END OF UBCORE VERSION
    
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
        """Scans the original data range and retrieves all the data values contained
        therein:
                   - datasources: the Views containing the rasters
                   - startextents: [xstart, ystart] coordinates
                   - cellsinblock: how many cells are in one block (defines extents)
        """
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
                
                if datasources[4] != 0: planmapmatrix[i].append(datasources[4].getValue(x_start+i, y_start+j))
                if datasources[5] != 0: employmentmatrix[i].append(datasources[5].getValue(x_start+i, y_start+j))
                if datasources[6] != 0: groundwatermatrix[i].append(datasources[6].getValue(x_start+i, y_start+j))
                if datasources[7] != 0: socpar1matrix[i].append(datasources[7].getValue(x_start+i, y_start+j))
                if datasources[8] != 0: socpar2matrix[i].append(datasources[8].getValue(x_start+i, y_start+j))
                
        datamatrices = [lucdatamatrix, popdatamatrix, elevdatamatrix, soildatamatrix, planmapmatrix, employmentmatrix, groundwatermatrix, socpar1matrix, socpar2matrix]
        return datamatrices


    def frequencyLUC(self, lucdatamatrix):
        #Determine size of matrix
        matsize = len(lucdatamatrix)
        #'RES', 'COM', 'ORC', 'LI', 'HI', 'CIV', 'SVU', 'RD', 'TR', 'PG', 'REF', 'UND', 'NA'
        lucprop = [0,0,0,0,0,0,0,0,0,0,0,0,0]
        total_n_luc = 0
        for i in range(matsize):
            for j in range(matsize):
                landclass = lucdatamatrix[i][j]
                if landclass == -9999:
                    pass
                else:
                    lucprop[int(landclass-1)] += 1
                    total_n_luc += 1
        
        #Convert frequency to proportion
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
        """NEIGHBOURHOODs - Search for all 8 neighbours. """
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


#    def drawPatchFace(self, nodes, scalar, offset, PaID, ID, area, LUC, elev, soil):        #UBCORE VERSION ----------------->
#        rs = scalar #rs = raster size
#        plist = []
        
#        for i in range(len(nodes)): #loop across the nodes
#            n = (nodes[i][0]*rs+offset[0], nodes[i][1]*rs+offset[1], 0)
#            plist.append(n)
        
#        plist.append(plist[0])
        
#        patch_attr = ubdata.UBVector(plist)
#        patch_attr.addAttribute("PatchID", PaID)              #ID of Patch in Block ID
#        patch_attr.addAttribute("LandUse", LUC)              #Land use of the patch
#        patch_attr.addAttribute("Area", area*rs*rs)                 #Area of the patch
#        patch_attr.addAttribute("AvgElev", elev)              #Average elevation of the patch
#        patch_attr.addAttribute("SoilK", soil)
#        patch_attr.addAttribute("BlockID", ID)              #Block ID that patch belongs to
        
#        self.activesim.addAsset("B"+str(ID)+"PatchID"+str(PaID), patch_attr)
#        return True     # END OF UBCORE VERSION ------------------------------------------------------------------------------
    
    def drawPatchFace(self, city, nodes, scalar, offset, PaID, ID, area, LUC, elev, soil):  #DYNAMIND VERSION --------------------->
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
        return True # END OF DYNAMIND VERSION ------------------------------------------------------------------------------   
    
#    def smoothDEM(self, numblocks, nhd_type):       #UBCORE VERSION -----------------------------------------------------------
#        new_elevs = []
#        for i in range(int(numblocks)):
#            nhd_count = 1
#            currentID = i+1
#            currentAttList = self.activesim.getAssetWithName("BlockID"+str(currentID))
#            if currentAttList.getAttribute("Status") == 0:
#                new_elevs.append(0)
#                continue
            
#            new_elev = currentAttList.getAttribute("AvgElev")
            
#            neighbourhood = self.getBlockNeighbourhood(currentAttList)
#            neighbourhoodZ = self.getNeighbourhoodZ(neighbourhood)
            
#            if nhd_type == 4:
#                #only vonNeumann cells
#                for k in range(len(neighbourhoodZ)-4):
#                    if k == 99999:
#                        continue
#                    new_elev += k
#                    nhd_count += 1
#            else:
#                for k in neighbourhoodZ:                #Scan all neighbour cells
#                    if k == 99999:                      #if the value is 99999, it means the cell isn't active
#                        continue
#                    new_elev += k
#                    nhd_count += 1
                    
#                new_elevs.append(new_elev/nhd_count)    #calculate average, add to the new matrix
        
#        for i in range(int(numblocks)):     #write all new elevations to replace the existing value
#            currentID = i+1
#            currentAttList = self.activesim.getAssetWithName(currentID)
#            currentAttList.setAttribute("AvgElev", new_elevs[i])
#        return True #END OF UBCORE VERSION ----------------------------------------------------------------------------------------


    def smoothDEM(self, city, numblocks, nhd_type): #DYNAMIND VERSION ------------------------------------------------------------
        new_elevs = []
        for i in range(int(numblocks)):
            nhd_count = 1
            currentID = i+1
            currentAttList = city.getFace(uuid = self.getBlockUUID(currentID, city))
            if currentAttList.getAttribute("Status").getDouble() == 0:
                new_elevs.append(0)
                continue
            
            new_elev = currentAttList.getAttribute("AvgElev").getDouble()
            
            neighbourhood = self.getBlockNeighbourhood(currentAttList)
            neighbourhoodZ = self.getNeighbourhoodZ(neighbourhood, city)
            
            if nhd_type == 4:
                #only vonNeumann cells
                for k in range(len(neighbourhoodZ)-4):
                    if k == 99999:
                        continue
                    new_elev += k
                    nhd_count += 1
            else:
                for k in neighbourhoodZ:                #Scan all neighbour cells
                    if k == 99999:                      #if the value is 99999, it means the cell isn't active
                        continue
                    new_elev += k
                    nhd_count += 1
                    
                new_elevs.append(new_elev/nhd_count)    #calculate average, add to the new matrix
        
        for i in range(int(numblocks)):     #write all new elevations to replace the existing value
            currentID = i+1
            currentAttList = city.getFace(self.getBlockUUID(currentID, city))
            currentAttList.modifyAttribute("AvgElev", new_elevs[i])
        return True #END OF DYNAMIND VERSION -------------------------------------------------------------------------------------------



#    def getBlockNeighbourhood(self, currentAttList):        #UBCORE VERSION --------------------------------------------------
#        """Returns the Moore neighbouhoord for the Block (8 neighbours in all cardinal
#        directions, the order is North, South, West, Est, followed by NE, NW, SE, SW"""
#        ID_N = int(round(currentAttList.getAttribute("Nhd_N")))
#        ID_S = int(round(currentAttList.getAttribute("Nhd_S")))
#        ID_W = int(round(currentAttList.getAttribute("Nhd_W")))
#        ID_E = int(round(currentAttList.getAttribute("Nhd_E")))
#        ID_NE = int(round(currentAttList.getAttribute("Nhd_NE")))
#        ID_NW = int(round(currentAttList.getAttribute("Nhd_NW")))
#        ID_SE = int(round(currentAttList.getAttribute("Nhd_SE")))
#        ID_SW = int(round(currentAttList.getAttribute("Nhd_SW")))
#        current_neighb = [ID_N, ID_S, ID_W, ID_E, ID_NE, ID_NW, ID_SE, ID_SW]
#        return current_neighb   #END OF UBCORE VERSION -----------------------------------------------------------------------

    def getBlockNeighbourhood(self, currentAttList):        #DYNAMIND VERSION -----------------------------------------------
        """Returns the Moore neighbouhoord for the Block (8 neighbours in all cardinal
        directions, the order is North, South, West, Est, followed by NE, NW, SE, SW"""
        ID_N = int(round(currentAttList.getAttribute("Nhd_N").getDouble()))
        ID_S = int(round(currentAttList.getAttribute("Nhd_S").getDouble()))
        ID_W = int(round(currentAttList.getAttribute("Nhd_W").getDouble()))
        ID_E = int(round(currentAttList.getAttribute("Nhd_E").getDouble()))
        ID_NE = int(round(currentAttList.getAttribute("Nhd_NE").getDouble()))
        ID_NW = int(round(currentAttList.getAttribute("Nhd_NW").getDouble()))
        ID_SE = int(round(currentAttList.getAttribute("Nhd_SE").getDouble()))
        ID_SW = int(round(currentAttList.getAttribute("Nhd_SW").getDouble()))
        current_neighb = [ID_N, ID_S, ID_W, ID_E, ID_NE, ID_NW, ID_SE, ID_SW]
        return current_neighb   #END OF DYNAMIND VERSION -------------------------------------------------------------------

    
#    def getNeighbourhoodZ(self, nhdIDs):    #UBCORE VERSION ------------------------------------------------------------------
#        current_neighbdZ = []
#        for i in nhdIDs:       #scan all 8 neighbours
#            if i == 0:  #if the Neighbourhood ID == 0
#                current_neighbdZ.append(99999)
#                continue
#            curface = self.activesim.getAssetWithName("BlockID"+str(i))
#            if int(round(curface.getAttribute("Status"))) == 0:
#                current_neighbdZ.append(99999) #works based on Sea Level, so nothing can really be higher than Everest :)
#            else:
#                current_neighbdZ.append(curface.getAttribute("AvgElev"))
#        return current_neighbdZ #END OF UBCORE VERSION -----------------------------------------------------------------------

    def getNeighbourhoodZ(self, nhdIDs, city):      #DYNAMIND VERSION -------------------------------------------------------
        current_neighbdZ = []
        for i in nhdIDs:       #scan all 8 neighbours
            uuid = self.getBlockUUID(i, city)
            if uuid == "":   #if not found because of some error, then return a very high number
                current_neighbdZ.append(99999)
                continue
            curface = city.getFace(uuid)
            if int(round(curface.getAttribute("Status").getDouble())) == 0:
                current_neighbdZ.append(99999) #works based on Sea Level, so nothing can really be higher than Everest :)
            else:
                current_neighbdZ.append(curface.getAttribute("AvgElev").getDouble())
        return current_neighbdZ #END OF DYNAMIND VERSION --------------------------------------------------------------------


    def findDownstreamD8(self, currentZ, neighboursZ, neighbourhood_type):
        if neighbourhood_type == 4:
            neighboursZ[4] = 999999
            neighboursZ[5] = 999999
            neighboursZ[6] = 999999
            neighboursZ[7] = 999999
        for i in range(len(neighboursZ)):            #D8 is simply the largest drop
            neighboursZ[i] = currentZ - neighboursZ[i]
        max_Zdrop = max(neighboursZ)
        if max_Zdrop <= 0:
            direction = -9999  #-9999 means that the current block is a sink
        else:
            direction = neighboursZ.index(max_Zdrop)
        return direction, max_Zdrop


    def findDownstreamDinf(self, currentZ, blocksize, neighboursZ, neighbourhood_type):
        """D-infinity method adapted to only direct water in one direction based on the steepest
        slope of the 8 triangular facets surrounding a Block's neighbourhood and a probabilistic
        choice weighted by the proportioning of flow. This is the stochastic option of flowpath
        delineation for UrbanBEATS and ONLY works with Moore neighbourhood"""

        facetdict = {}      #Stores all the information about the 8 facets
        facetdict["e1"] = ["E","N","N","W","W","S","S","E"]
        facetdict["e2"] = ["NE","NE","NW","NW","SW","SW","SE","SE"]
        facetdict["ac"] = [0,1,1,2,2,3,3,4]
        facetdict["af"] = [1,-1,1,-1,1,-1,1,-1]
        cardin = { "E":0, "NE":1, "N":2, "NW":3, "W":4, "SW":5, "S":6, "SE":7 }
        
        e0 = currentZ               #CONSTANT PARAMETERS (because of constant block grid and centre point)
        d1 = blocksize
        d2 = d1
        facetangles = [0, math.pi/4, math.pi/2, 3*math.pi/4, math.pi, 5*math.pi/4, 3*math.pi/2, 7*math.pi/4]
        
        #Re-sort the neighbours matrix based on polar angle
        sortedneighb = [neighboursZ[3],neighboursZ[4],neighboursZ[0],neighboursZ[5],neighboursZ[2],neighboursZ[7],neighboursZ[1],neighboursZ[6]]
        rmatrix = []
        smatrix = []

        for i in range(len(sortedneighb)):  #Calculate slopes of all 8 facets
            currentfacet = i
            
            e1 = sortedneighb[cardin[facetdict["e1"][currentfacet]]]        #e1 elevation:  (1) get cardinal direction from dictionary, 
                                                                            #               (2) get the index from cardin and 
            e2 = sortedneighb[cardin[facetdict["e2"][currentfacet]]]        #               (3) get the value from neighbz
            
            ac = facetdict["ac"][currentfacet]
            af = facetdict["af"][currentfacet]
            
            s1 = (e0 - e1)/d1
            s2 = (e1 - e2)/d2
            r = math.atan(s2/s1)
            s = math.sqrt(math.pow(s1,2) + math.pow(s2, 2))
            
            if r < 0:
                r = 0
                s = s1
            elif r > math.atan(d2/d1):
                r = math.atan(d2/d1)
                s = (e0 - e2)/math.sqrt(math.pow(d1, 2) + math.pow(d2, 2))
            
            rmatrix.append(r)
            smatrix.append(s)
        
        #Find the maximum slope and get the angle
        rmax = max(rmatrix)
        rg = af*rmax + ac*math.pi/2.0
        
        #Find the facet
        for i in range(len(facetangles)):
            if rg > facetangles[i]:
                continue
            else:
                facet = i-1
                theta1 = facetangles[i-1]
                theta2 = facetangles[i]
        #Adjust angles based on rg to get proportions
        alpha1 = rg - theta1
        alpha2 = theta2 - rg
        p1 = alpha1/(alpha1 + alpha2)
        p2 = alpha2/(alpha2 + alpha1)
        
        print "Proportioned Flows:", p1, p2
        
        if rand.random() < p1:
            choice = p1
            directionfacet = int(theta1/(math.pi/4))
        else:
            choice = p2
            directionfacet = int(theta2/(math.pi/4))
            
        print "Choice:", choice
        
        direction = neighboursZ.index(sortedneighb[directionfacet-1])
        return direction, max_Zdrop
    
    
#    def drawFlowPaths(self, currentID, downstreamID, currentAttList, max_Zdrop, avg_slope, typenum):    #UBCORE VERSION ------------
#        f = self.activesim.getAssetWithName("BlockID"+str(int(downstreamID)))
            
#        x_up = currentAttList.getAttribute("CentreX")
#        y_up = currentAttList.getAttribute("CentreY")
#        z_up = currentAttList.getAttribute("AvgElev")
#        upNode = (x_up,y_up,z_up)
        
#        x_down = f.getAttribute("CentreX")
#        y_down = f.getAttribute("CentreY")
#        z_down = f.getAttribute("AvgElev")
#        downNode = (x_down,y_down,z_down)
        
#        network_attr = ubdata.UBVector([upNode, downNode])         
#        network_attr.addAttribute("BlockID", currentID)
#        network_attr.addAttribute("DownID", downstreamID)
#        network_attr.addAttribute("Z_up", z_up)
#        network_attr.addAttribute("Z_down", z_down)
#        network_attr.addAttribute("max_Zdrop", max_Zdrop)
#        network_attr.addAttribute("Type", typenum)       #1 = basic downstream, -1 = unblocked sink, #0 = sink
#        network_attr.addAttribute("avg_slope", avg_slope)
#        self.activesim.addAsset("NetworkID"+str(currentID), network_attr)
#        return True #END OF UBCORE VERSION ------------------------------------------------------------------------------
    
    def drawFlowPaths(self, city, currentID, downstreamID, currentAttList, max_Zdrop, avg_slope, typenum):  #DYNAMIND VERSION ------
        print "BlockID", currentID
        uuid = self.getBlockUUID(downstreamID,city)
        if  uuid == "":
            print "Error block not found: " + str(downstreamID)
            return True
        
        f = city.getFace(uuid)
        x_up = currentAttList.getAttribute("CentreX").getDouble()
        y_up = currentAttList.getAttribute("CentreY").getDouble()
        z_up = currentAttList.getAttribute("AvgElev") .getDouble()
        upNode = city.addNode(x_up,y_up,z_up)
        
        x_down = f.getAttribute("CentreX").getDouble()
        y_down = f.getAttribute("CentreY").getDouble()
        z_down = f.getAttribute("AvgElev").getDouble()
        downNode = city.addNode(x_down,y_down,z_down)
        
        network_attr = city.addEdge(upNode,downNode,self.network)         
        network_attr.addAttribute("BlockID", currentID)
        network_attr.addAttribute("DownID", downstreamID)
        network_attr.addAttribute("Z_up", z_up)
        network_attr.addAttribute("Z_down", z_down)
        network_attr.addAttribute("max_Zdrop", max_Zdrop)
        network_attr.addAttribute("Type", typenum)       #1 = basic downstream, -1 = unblocked sink, #0 = sink
        network_attr.addAttribute("avg_slope", avg_slope)
        return True #END OF DYNAMIND VERSION ------------------------------------------------------------------------------
        
    
#    def delineateFlowPaths(self, numblocks, cs, neighbourhood_type): #UBCORE VERSION ------------------------------------
#        sinkIDs = []
#        riverIDs = []
#        lakeIDs = []

#        for i in range(numblocks):
#            currentID = i+1
            
#            #CONDITION 1 - Block is Active in Simulation
#            currentAttList = self.activesim.getAssetWithName("BlockID"+str(currentID))
            
#            if currentAttList.getAttribute("Status") == 0:
#                #print "BlockID"+str(currentID)+" not active in simulation"
#                continue
            
#            #CONDITION 2 - Block already contains a sink e.g. river/etc.
#            if currentAttList.getAttribute("HasRiv") == 1:
#                hasRiver = 1
#                riverIDs.append(currentID)
#                continue
            
#            currentZ = currentAttList.getAttribute("AvgElev")
            
#            #Neighbours array: [N, S, W, E, NE, NW, SE, SW], the last four are 0 if only vonNeumann Nhd used.
#            neighbours = self.getBlockNeighbourhood(currentAttList)
#            neighboursZ = self.getNeighbourhoodZ(neighbours)
            
#            #Find Downstream Block - The Functions return the Index of the Cardinal Direction
#            if self.flow_method == "D8":
#                flow_direction, max_Zdrop = self.findDownstreamD8(currentZ, neighboursZ, neighbourhood_type)
#            elif self.flow_method == "DI":
#                flow_direction, max_Zdrop = self.findDownstreamDinf(currentZ, cs, neighboursZ, neighbourhood_type)
            
#            if flow_direction == -9999:
#                sinkIDs.append(currentID)
#                downstreamID = -1
#            else:
#                downstreamID = neighbours[flow_direction]
            
#            #Grab Distance/Slope between two Block IDs
#            if flow_direction == -9999:
#                dx = 0
#            elif flow_direction <= 3:
#                dx = cs
#            elif flow_direction > 3:
#                dx = math.sqrt(2*cs*cs)                        #diagonal
                
#            if dx == 0: avg_slope = 0
#            else: avg_slope = max_Zdrop/dx
            
#            currentAttList.addAttribute("downID", downstreamID)
#            currentAttList.addAttribute("maxdZ", max_Zdrop)
#            currentAttList.addAttribute("slope", avg_slope)
            
#            #DRAW NETWORKS OF PATHS THAT ARE NOT SINKS
#            if downstreamID != -1 and downstreamID != 0:
#                print "To Draw"                
#                print currentID
#                print downstreamID
#                self.drawFlowPaths(currentID, downstreamID, currentAttList, max_Zdrop, avg_slope, 1)
            
#        self.unblockSinks(sinkIDs, numblocks)
#        self.connectRiverBlocks(riverIDs, numblocks)
#        return True #END OF UBCORE VERSION ----------------------------------------------------------------------------------
    
    def delineateFlowPaths(self, city, numblocks, cs, neighbourhood_type): #DYNAMIND VERSION ------------------------------------
        sinkIDs = []
        riverIDs = []
        lakeIDs = []

        for i in range(numblocks):
            currentID = i+1
            uuid = self.getBlockUUID(int(currentID), city)
            if uuid == "":
                print "Error, Block"+ str(currentID)+" not found."
                continue
            
            #CONDITION 1 - Block is Active in Simulation
            currentAttList = city.getFace(uuid)
            if currentAttList.getAttribute("Status").getDouble() == 0:
                #print "BlockID"+str(currentID)+" not active in simulation"
                continue
            
            #CONDITION 2 - Block already contains a sink e.g. river/etc.
            if currentAttList.getAttribute("HasRiv").getDouble() == 1:
                hasRiver = 1
                riverIDs.append(currentID)
                continue
            
            
            currentZ = currentAttList.getAttribute("AvgElev").getDouble()
            
            #Neighbours array: [N, S, W, E, NE, NW, SE, SW], the last four are 0 if only vonNeumann Nhd used.
            neighbours = self.getBlockNeighbourhood(currentAttList)
            neighboursZ = self.getNeighbourhoodZ(neighbours, city)
            
            #Find Downstream Block - The Functions return the Index of the Cardinal Direction
            if self.flow_method == "D8":
                flow_direction, max_Zdrop = self.findDownstreamD8(currentZ, neighboursZ, neighbourhood_type)
            elif self.flow_method == "DI":
                flow_direction, max_Zdrop = self.findDownstreamDinf(currentZ, cs, neighboursZ, neighbourhood_type)
            
            if flow_direction == -9999:
                sinkIDs.append(currentID)
                downstreamID = -1
            else:
                downstreamID = neighbours[flow_direction]
            
            #Grab Distance/Slope between two Block IDs
            if flow_direction == -9999:
                dx = 0
            elif flow_direction <= 3:
                dx = cs
            elif flow_direction > 3:
                dx = math.sqrt(2*cs*cs)                        #diagonal
                
            if dx == 0: avg_slope = 0
            else: avg_slope = max_Zdrop/dx
            
            currentAttList.addAttribute("downID", downstreamID)
            currentAttList.addAttribute("maxdZ", max_Zdrop)
            currentAttList.addAttribute("slope", avg_slope)
            
            #DRAW NETWORKS OF PATHS THAT ARE NOT SINKS
            if downstreamID != -1 or downstreamID != 0:
                self.drawFlowPaths(city, currentID, downstreamID, currentAttList, max_Zdrop, avg_slope, 1)
            
        
        self.unblockSinks(sinkIDs, city, numblocks)
        #self.connectRiverBlocks(riverIDs, city, numblocks)
        return True    #END OF DYNAMIND VERSION ----------------------------------------------------------------------------------
    
    
#    def unblockSinks(self, sinkIDs, numblocks): #UBCORE VERSION ---------------------------------------------------------------------
#        total_sinks = len(sinkIDs)
#        print "A total of: "+str(total_sinks)+" sinks found in map!"
        
#        #Sink unblocking algorithm for immediate neighbourhood
#        for i in sinkIDs:
#            currentID = i
#            currentAttList = self.activesim.getAssetWithName("BlockID"+str(int(currentID)))           
#            currentZ = currentAttList.getAttribute("AvgElev")    
            
#            current_neighb = self.getBlockNeighbourhood(currentAttList)
            
#            possible_IDdrains = []
#            possible_IDdZ = []
#            possibility = 0
            
#            for j in current_neighb:
#                f = self.activesim.getAssetWithName("BlockID"+str(int(j)))                
#                testdownID = int(round(f.getAttribute("downID")))
#                if  testdownID not in [currentID, -1] and testdownID not in current_neighb and int(round(f.getAttribute("Status"))) != 0:
#                    possible_IDdrains.append(j)
#                    possible_IDdZ.append(f.getAttribute("AvgElev")-currentZ)
#                    possibility += 1
        
#            if possibility > 0:         #if algorithm found a possible pathway for sink to unblock, then get the ID and connect network
#                sink_path = min(possible_IDdZ)
#                sink_drainID = possible_IDdrains[possible_IDdZ.index(sink_path)]
#                currentAttList.addAttribute("drainID", sink_drainID)            
#                currentAttList.addAttribute("h_pond", sink_path)
#                self.drawFlowPaths(currentID, sink_drainID, currentAttList, sink_path, 0, -1) 
#                continue
#            else:
#                #IF the model reaches this point, the identified cell is either most definitely an outlet or a very troublesome sink
#                currentAttList.addAttribute("drainID", -1)      #-1 in drainID = outlet or sub-outlet        
#        return True #END OF UBCORE VERSION ---------------------------------------------------------------------------------------------------    
    
    def unblockSinks(self, sinkIDs, city, numblocks):   #DYNAMIND VERSION ---------------------------------------------------------------------
        total_sinks = len(sinkIDs)
        print "A total of: "+str(total_sinks)+" sinks found in map!"
        
        #Sink unblocking algorithm for immediate neighbourhood
        for i in sinkIDs:
            currentID = i
            currentAttList = city.getFace(self.getBlockUUID(currentID,city))           
            currentZ = currentAttList.getAttribute("AvgElev").getDouble()    
            
            current_neighb = self.getBlockNeighbourhood(currentAttList)
            
            possible_IDdrains = []
            possible_IDdZ = []
            possibility = 0
            
            for j in current_neighb:
                uuid = self.getBlockUUID(j,city)
                if len(uuid)!= 0:
                    f = city.getFace(uuid)
                    testdownID = int(round(f.getAttribute("downID").getDouble()))
                    if  testdownID not in [currentID, -1] and testdownID not in current_neighb and int(round(f.getAttribute("Status").getDouble())) != 0:
                        possible_IDdrains.append(j)
                        possible_IDdZ.append(f.getAttribute("AvgElev").getDouble()-currentZ)
                        possibility += 1
            
            if possibility > 0:         #if algorithm found a possible pathway for sink to unblock, then get the ID and connect network
                sink_path = min(possible_IDdZ)
                sink_drainID = possible_IDdrains[possible_IDdZ.index(sink_path)]
                currentAttList.addAttribute("drainID", sink_drainID)            
                currentAttList.addAttribute("h_pond", sink_path)
                self.drawFlowPaths(city, currentID, sink_drainID, currentAttList, sink_path, 0, -1) 
                continue
            
            else:
                #IF the model reaches this point, the identified cell is either most definitely an outlet or a very troublesome sink
                currentAttList.addAttribute("drainID", -1)      #-1 in drainID = outlet or sub-outlet        
        return True #END OF DYNAMIND VERSION ---------------------------------------------------------------------------------------------------    
    
    
    def connectRiverBlocks(self, riverIDs, numblocks):
        print "A total of: "+str(len(riverIDs))+" Blocks contain a river body!"
        riverbodycount = 0        
        return True
    
    
#    def createBlockHashTable(self, numblocks): #UBCORE VERSION ----------------------------------------------
#        """Indexes through the list of blocks and finds the downstream blocks that each
#        block flows into (0 = outlet). This hash table is required for finding basins
#        within the case study area.
#        """
#        hash_table = [[],[]]    #COLUMN1: BLOCK ID (UP), COLUMN2: DOWNSTREAM ID (DOWN)
#        for i in range(int(numblocks)):
#            currentID = i+1
#            currentAttList = self.activesim.getAssetWithName("BlockID"+str(currentID))
#            if currentAttList.getAttribute("Status") == 0:
#                #print "BlockID"+str(currentID)+" not active in simulation"
#                continue
            
#            hash_table[0].append(int(currentID))
            
#            if currentAttList.getAttribute("downID") not in [0, -1]:
#                hash_table[1].append(int(currentAttList.getAttribute("downID")))
#            elif currentAttList.getAttribute("drainID") not in [0, -1]:
#                hash_table[1].append(int(currentAttList.getAttribute("drainID")))
#            else:
#                hash_table[1].append(int(0))
#        print hash_table
#        return hash_table #END OF UBCORE VERSION --------------------------------------------------------------------

    def createBlockHashTable(self, city, numblocks):    #DYNAMIND VERSION ----------------------------------------------
        """Indexes through the list of blocks and finds the downstream blocks that each
        block flows into (0 = outlet). This hash table is required for finding basins
        within the case study area.
        """
        hash_table = [[],[]]    #COLUMN1: BLOCK ID (UP), COLUMN2: DOWNSTREAM ID (DOWN)
        for i in range(int(numblocks)):
            currentID = i+1
            uuid = self.getBlockUUID(currentID, city)
            if uuid == "":
                print "Error, Block"+ str(currentID)+" not found"
                continue
            
            currentAttList = city.getFace(uuid)
            if currentAttList.getAttribute("Status").getDouble() == 0:
                #print "BlockID"+str(currentID)+" not active in simulation"
                continue
            
            hash_table[0].append(int(currentID))
            
            if currentAttList.getAttribute("downID").getDouble() not in [0, -1]:
                hash_table[1].append(int(currentAttList.getAttribute("downID").getDouble()))
            elif currentAttList.getAttribute("drainID").getDouble() not in [0, -1]:
                hash_table[1].append(int(currentAttList.getAttribute("drainID").getDouble()))
            else:
                hash_table[1].append(int(0))
        
        print hash_table
        return hash_table   #END OF DYNAMIND VERSION --------------------------------------------------------------------
    
    
#    def delineateBasins(self, numblocks, hash_table): #UBCORE VERSION ------------------------------------------------------
#        basinID = 0
#        for i in range(numblocks):
#            currentID = i+1
#            currentAttList = self.activesim.getAssetWithName("BlockID"+str(int(currentID)))
#            if currentAttList.getAttribute("Status") == 0:
#                #print "BlockID"+str(currentID)+" not active in simulation"
#                continue
            
#            if currentID not in hash_table[1]:
#                currentAttList.addAttribute("UpstrIDs", "")
#                if currentID in hash_table[0]:
#                    if hash_table[1][hash_table[0].index(currentID)] == 0:
#                        print "Found a single block basin at Block: ", currentID
#                        basinID += 1   #transfer currentID to all blocks
#                        currentAttList.addAttribute("BasinID", basinID)
#                        currentAttList.addAttribute("Outlet", 1)
#                continue
            
#            upstreamIDs = [currentID]
#            for id in upstreamIDs:
#                for j in range(len(hash_table[1])):
#                    if id == hash_table[1][j]:
#                        if hash_table[0][j] not in upstreamIDs:
#                            upstreamIDs.append(hash_table[0][j])
            
#            upstreamIDs.remove(currentID)
#            print "BlockID", currentID, "Upstream: ", upstreamIDs
            
#            outputstring = ""
#            for j in upstreamIDs:
#                outputstring += str(j)+","
#            currentAttList.addAttribute("UpstrIDs", outputstring)
            
#            #Set Basin IDs
#            if hash_table[1][hash_table[0].index(currentID)] == 0:
#                print "Found a basin outlet at Block: ", currentID
#                basinID += 1   #transfer currentID to all blocks
#                currentAttList.addAttribute("Outlet", 1)
#                currentAttList.addAttribute("BasinID", basinID)
#                for j in upstreamIDs:
#                    upblock = self.activesim.getAssetWithName("BlockID"+str(int(j)))
#                    upblock.addAttribute("BasinID", basinID)
#                    upblock.addAttribute("Outlet", 0)
        
#        print "Total Basins in Case Study: ", basinID
        
#        return basinID #UBCORE VERSION ------------------------------------------------------------------------------------
    
    def delineateBasins(self, city, numblocks, hash_table): #DYNAMIND VERSION ------------------------------------------------------
        basinID = 0
        for i in range(numblocks):
            currentID = i+1
            uuid = self.getBlockUUID(currentID, city)
            if uuid == "":
                print "Error, Block"+ str(currentID)+" not found"
                continue
                
            currentAttList = city.getFace(uuid)
            if currentAttList.getAttribute("Status").getDouble() == 0:
                #print "BlockID"+str(currentID)+" not active in simulation"
                continue
            
            if currentID not in hash_table[1]:
                currentAttList.addAttribute("UpstrIDs", "")
                if currentID in hash_table[0]:
                    if hash_table[1][hash_table[0].index(currentID)] == 0:
                        print "Found a single block basin at Block: ", currentID
                        basinID += 1   #transfer currentID to all blocks
                        currentAttList.addAttribute("BasinID", basinID)
                        currentAttList.addAttribute("Outlet", 1)
                continue
            
            upstreamIDs = [currentID]
            for id in upstreamIDs:
                for j in range(len(hash_table[1])):
                    if id == hash_table[1][j]:
                        if hash_table[0][j] not in upstreamIDs:
                            upstreamIDs.append(hash_table[0][j])
            
            upstreamIDs.remove(currentID)
            print "BlockID", currentID, "Upstream: ", upstreamIDs
            
            outputstring = ""
            for j in upstreamIDs:
                outputstring += str(j)+","
            currentAttList.addAttribute("UpstrIDs", outputstring)
            
            #Set Basin IDs
            if hash_table[1][hash_table[0].index(currentID)] == 0:
                print "Found a basin outlet at Block: ", currentID
                basinID += 1   #transfer currentID to all blocks
                currentAttList.addAttribute("Outlet", 1)
                currentAttList.addAttribute("BasinID", basinID)
                for j in upstreamIDs:
                    upblock = city.getFace(self.getBlockUUID(j, city))
                    upblock.addAttribute("BasinID", basinID)
                    upblock.addAttribute("Outlet", 0)
        
        print "Total Basins in Case Study: ", basinID
        
        return basinID  #DYNAMIND VERSION ------------------------------------------------------------------------------------
    
    def saveFlowBasinsToFile(self, numblocks, hash_table):
        #f = open("simulationflowbasins.txt", 'w')
        pass
#        f.close()
        return True
    
    def retrieveFlowBasinsFromFile(filename, numblocks):
        f = open(filename, 'r')
        
        f.close()        
        return True
    
    ########################################################
    #LINK WITH GUI                                         #
    ########################################################        
#    def getParameter(self, name):   #UBCORE FUNCTION
#        return self.__dict__.get(name)
    
#    def setParameter(self, name, value):    #UBCORE FUNCTION
#        self.__dict__.__setitem__(name, value)
#        return True
    
    def createInputDialog(self):    #DYNAMIND FUNCTION --------------------------
        form = activatedelinblocksGUI(self, QApplication.activeWindow())
        form.show()
        return True #-----------------END OF DYNAMIND FUNCTIOn ------------------
