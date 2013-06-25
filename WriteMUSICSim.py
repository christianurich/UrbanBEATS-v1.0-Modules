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

import ubmusicwrite as ubmusic
from pydynamind import * 
import sys, random, numpy, math

class WriteResults2MUSIC(Module):
    """Creates a fully functional MUSIC model file *.msf for the input map of blocks and systems
    Log of Updates made at each version:
    
    v1.0 (June 2013):
        - Version 1 release MUSIC interface now updated to work with other modules and v1.0 attribute
            names
        - Writes multiple MUSIC file outputs based on the number of strategies to retain
        - Incorporates new nodes for lot scale land uses
    
    v0.80 (August 2012):
        - First created
        - Future work: To make sure the projection is adjusted if the file was not created by UrbanBEATS
        
	@ingroup UrbanBEATS
	@author Peter M Bach
	"""

    def __init__(self):
        Module.__init__(self)
        self.createParameter("pathname", STRING, "")
        self.createParameter("filename", STRING, "")
        self.createParameter("currentyear", DOUBLE, "")
        self.createParameter("masterplanmodel", BOOL, "")
        self.pathname = "D:\\"
        self.filename = "ubeatsMUSIC"
        self.currentyear = 9999
	self.masterplanmodel = True
        #self.include_secondary_links = 0

        ########################################################################
	#Views

	self.mapattributes = View("GlobalMapAttributes", COMPONENT, READ)
	self.blocks = View("Block", FACE, READ)
	self.wsudAttr = View("WsudAttr", COMPONENT, READ)

	datastream = []
        datastream.append(self.mapattributes)
	datastream.append(self.wsudAttr)
	datastream.append(self.blocks)
        self.addData("City", datastream)
	
	self.BLOCKIDtoUUID = {}
	
    def run(self):
	city = self.getData("City")
	self.initBLOCKIDtoUUID(city)
	
	strvec = city.getUUIDsOfComponentsInView(self.mapattributes)
        map_attr = city.getComponent(strvec[0])
        
        #get data needed to being for loop analysis
        blocks_num = map_attr.getAttribute("NumBlocks").getDouble()     #number of blocks to loop through
        blocks_size = map_attr.getAttribute("BlockSize").getDouble()    #size of block
        map_w = map_attr.getAttribute("WidthBlocks").getDouble()        #num of blocks wide
        map_h = map_attr.getAttribute("HeightBlocks").getDouble()       #num of blocks tall
        input_res = map_attr.getAttribute("InputReso").getDouble()      #resolution of input data
        totalbasins = map_attr.getAttribute("TotalBasins").getDouble()  #total number of basins in map
        strats = map_attr.getAttribute("OutputStrats").getDouble()      #Number of MUSIC files to write
        
        print totalbasins
        print "Total Strategies :", strats
        
        if self.masterplanmodel == 1:   #differentiate between planning and implementation models
            filesuffix = "PC"
        else:
            filesuffix = "IC"
        
        #Begin writing music files
        for s in range(int(strats)):
            currentStratID = s+1
            systemlist = self.getWSUDSystemsForStratID(currentStratID, city) #Returns components of particular stratID
            
            ufile = ubmusic.createMUSICmsf(self.pathname, self.filename+"-ID"+str(currentStratID)+"-"+str(self.currentyear)+filesuffix)
            ubmusic.writeMUSICheader(ufile, "melbourne")
            scalar = 10
            ncount = 1
            musicnodedb = {}       #contains the database of nodes for each Block
            
            for i in range(int(blocks_num)):
                currentID = i+1
                currentAttList = self.getBlockUUID(currentID, city)
                if currentAttList.getAttribute("Status").getDouble() == 0:
                    continue    #Skip block since it has no info
                musicnodedb["BlockID"+str(currentID)] = {}
                current_soilK = currentAttList.getAttribute("Soil_k").getDouble()
                blocksystems = self.getBlockSystems(currentID, systemlist, city)      #Get all systems for the current block
                #print blocksystems
                
                blockX = currentAttList.getAttribute("CentreX").getDouble()
                blockY = currentAttList.getAttribute("CentreY").getDouble()
                
                #(1) WRITE CATCHMENT NODES - maximum possibility of 7 Nodes (Lot x 6, non-lot x 1)
                #       Lot: RES, HDR, COM, LI, HI, ORC
                #       Street/Neigh: x 1
                catchment_parameter_list = [1,120,30,80,200,1,10,25,5,0]
                total_catch_imparea = currentAttList.getAttribute("Blk_EIA").getDouble()/10000      #[ha]
                catchnodecount = self.determineBlockCatchmentNodeCount(blocksystems) 
                lotcount = catchnodecount - 1   #one less
                lotareas = self.determineCatchmentLotAreas(currentAttList, blocksystems)
                nonlotarea = total_catch_imparea - sum(lotareas.values())
                if nonlotarea == 0:
                    print "ISSUE: NONLOT AREA ZERO ON BLOCK: ", currentID
                ncount_list = []
                
                lotoffset = 0
                if catchnodecount > 1:
                    for j in lotareas.keys():       #Loop over lot catchments
                        if lotareas[j] == 0:
                            continue
                        ncount_list.append(ncount)
                        ubmusic.writeMUSICcatchmentnode(ufile, currentID, j, ncount, (blockX-blocks_size/4+(lotoffset*blocks_size/12))*scalar, (blockY+blocks_size/4+(lotoffset*blocks_size/12))*scalar, lotareas[j], 1, catchment_parameter_list)
                        lotoffset += 1
                        musicnodedb["BlockID"+str(currentID)]["C_"+j] = ncount
                        ncount += 1
                        
                    #Write Street/Neigh Catchment Node
                    ncount_list.append(ncount)
                    ubmusic.writeMUSICcatchmentnode(ufile, currentID, "", ncount, (blockX-blocks_size/4)*scalar, (blockY)*scalar, nonlotarea,1, catchment_parameter_list)
                    musicnodedb["BlockID"+str(currentID)]["C_R"] = ncount
                    ncount += 1
                else:
                    ncount_list.append(0)
                    ncount_list.append(ncount)
                    ubmusic.writeMUSICcatchmentnode(ufile, currentID, "", ncount, (blockX-blocks_size/4)*scalar, (blockY)*scalar, total_catch_imparea,1, catchment_parameter_list)
                    musicnodedb["BlockID"+str(currentID)]["C_R"] = ncount
                    ncount += 1
        
                #(2) WRITE TREATMENT NODES
                lotoffset = -1
                for sys in blocksystems.keys():
                    if len(blocksystems[sys]) == 0:
                        continue
                    curSys = blocksystems[sys][0]
                    
                    systype = curSys.getAttribute("Type").getString()
                    ncount_list.append(ncount)
                    scale = curSys.getAttribute("Scale").getString()
                    if "L" in scale:
                        lotoffset += 1
                        addOffset = lotoffset
                    else:
                        addOffset = 0
                    offsets = self.getSystemOffsetXY(curSys, blocks_size)
                    parameter_list = eval("self.prepareParameters"+str(curSys.getAttribute("Type").getString())+"(curSys, current_soilK)")
                    eval("ubmusic.writeMUSICnode"+str(systype)+"(ufile, currentID, scale, ncount, (blockX+offsets[0]+(addOffset*blocks_size/12))*scalar, (blockY+offsets[1]+(addOffset*blocks_size/12))*scalar, parameter_list)")
                    musicnodedb["BlockID"+str(currentID)]["S_"+scale] = ncount
                    ncount += 1
                
                #(3) WRITE BLOCK JUNCTION
                ncount_list.append(ncount)
                offsets = self.getSystemOffsetXY("J", blocks_size)
                if int(currentAttList.getAttribute("Outlet").getDouble()) == 1:
                    #print "GOT AN OUTLET at BlockID", currentID
                    basinID = int(currentAttList.getAttribute("BasinID").getDouble())
                    jname = "OUT_Bas"+str(basinID)+"-BlkID"+str(currentID)
                    #print jname
                else:
                    jname = "Block"+str(currentID)+"J"
                ubmusic.writeMUSICjunction(ufile, jname, ncount, (blockX+offsets[0])*scalar, (blockY+offsets[1])*scalar)
                musicnodedb["BlockID"+str(currentID)]["J"] = ncount
                ncount += 1
            
                #(4) WRITE ALL LINKS WITHIN BLOCK
                nodelinks = self.getInBlockNodeLinks(musicnodedb["BlockID"+str(currentID)])
                
                for link in range(len(nodelinks)):
                    ubmusic.writeMUSIClink(ufile, nodelinks[link][0], nodelinks[link][1])
            
            #(5) WRITE ALL LINKS BETWEEN BLOCKS
            for i in range(int(blocks_num)):
                currentID = i+1
                currentAttList = self.getBlockUUID(currentID, city)
                if currentAttList.getAttribute("Status").getDouble() == 0:
                    continue    #Skip block since it has no info
                downID = int(currentAttList.getAttribute("downID").getDouble())
                if downID == -1 or downID == 0:
                    downID = int(currentAttList.getAttribute("drainID").getDouble())
                if downID == -1 or downID == 0:
                    continue
                if int(currentAttList.getAttribute("Outlet").getDouble()) == 1:
                    continue
                else:
                    nodelink = self.getDownstreamNodeLink(musicnodedb["BlockID"+str(currentID)], musicnodedb["BlockID"+str(downID)])
                    ubmusic.writeMUSIClink(ufile, nodelink[0], nodelink[1])

            ubmusic.writeMUSICfooter(ufile)
    
    ########################################################
    #WriteMUSICSim SUBFUNCTIONS                            #
    ########################################################
    def getWSUDSystemsForStratID(self, stratID, city):
        """Scans the WSUD View and Returns an array of all components within the specified
        strategy ID"""
        wsudIDs = city.getUUIDsOfComponentsInView(self.wsudAttr)        #Holds all strategies
        systemlist = []
        for uuid in wsudIDs:
            systemattr = city.getComponent(uuid)
            if int(systemattr.getAttribute("StrategyID").getDouble()) != int(stratID):
                continue
            systemlist.append(uuid) #RETURNS THE UUIDs NOT THE ATTRIBUTE LISTS
            
        return systemlist

    def getBlockSystems(self, currentID, systemlist, city):
        """Scans the systemlist passed to the function and returns all WSUD components
        present in the currentID block in dictionary form based on scale
            - currentID: current Block ID that we want the systems for
            - systemlist: the system list created by scanning the self.wsudAttr View
            - city: city datastream
        """
        sysDict = {"L_RES":[], "L_LI":[], "L_COM":[], "L_HI":[], "L_HDR":[], "L_ORC":[], "S":[], "N":[], "B":[]}
        for uuid in systemlist:
            sysAttr = city.getComponent(uuid)
            if int(sysAttr.getAttribute("Location").getDouble()) != int(currentID):
                continue
            else:
                sysDict[sysAttr.getAttribute("Scale").getString()].append(sysAttr)
        return sysDict
    
    def determineBlockCatchmentNodeCount(self, blocksystems):
        """Determines the number of catchment nodes to construct in the current block
        based on the system count."""
        catchcount = 1      #Regardless for street/neighbourhood
        for i in blocksystems.keys():
            #One catchment for each lot scale, one combined catchment for street/neigh
            if i in ["S", "N", "B"]:
                continue
            if len(blocksystems[i]) == 0:       #Additional only apply to lot systems
                continue
            catchcount += 1
        return catchcount

    def determineCatchmentLotAreas(self, currentAttList, blocksystems):
        """Determines the areas for each of the lots, which have a system present."""
        lotareas = {"L_RES":0, "L_HDR":0, "L_LI":0, "L_HI":0, "L_COM":0, "L_ORC":0}
        
        #Residential Areas
        if len(blocksystems["L_RES"]) != 0:
            lotareas["L_RES"] = currentAttList.getAttribute("ResAllots").getDouble() * \
                currentAttList.getAttribute("ResLotEIA").getDouble() / 10000        #[ha]
                
        #High-Density Residential Areas
        if len(blocksystems["L_HDR"]) != 0:
            lotareas["L_HDR"] = currentAttList.getAttribute("HDR_EIA").getDouble() / 10000

        #Light Industrial Areas
        if len(blocksystems["L_LI"]) != 0:
            lotareas["L_LI"] = currentAttList.getAttribute("LIAeEIA").getDouble() * \
                currentAttList.getAttribute("LIestates").getDouble() / 10000
                
        #Heavy Industrial Areas
        if len(blocksystems["L_HI"]) != 0:
            lotareas["L_HI"] = currentAttList.getAttribute("HIAeEIA").getDouble() * \
                currentAttList.getAttribute("HIestates").getDouble() / 10000
            
        #Commercial Areas
        if len(blocksystems["L_COM"]) != 0:
            lotareas["L_COM"] = currentAttList.getAttribute("COMAeEIA").getDouble() * \
                currentAttList.getAttribute("COMestates").getDouble() / 10000
            
        #Office/ResCom Mixed Areas
        if len(blocksystems["L_ORC"]) != 0:
            lotareas["L_ORC"] = currentAttList.getAttribute("ORCAeEIA").getDouble() * \
                currentAttList.getAttribute("ORCestates").getDouble() / 10000
        return lotareas

    def getInBlockNodeLinks(self, nodedb):
        """Returns an array of nodeIDs that are connected by a link for all within-block aspects for
        following rules:        - lot catchment to lot system           - lot RES system to street/neigh system
                                - remain catch to stree/neigh system    - lot nonRES sys to neigh system
                                - street sys to neigh sys               - neigh sys to junction
                                - junction to basin sys                 - remain catchment to junction if no sys"""
        nodelinks = []
        linkmap = {"C_L_RES": ["S_L_RES"], "C_L_HDR":["S_L_HDR"], "C_L_LI": ["S_L_LI"], 
                   "C_L_HI": ["S_L_HI"], "C_L_COM": ["S_L_COM"], "C_L_ORC": ["S_L_ORC"],
                   "C_R": ["S_S", "S_N", "J"], "J": ["S_B", 0],
                   "S_L_RES": ["S_S", "S_N", "J"], "S_L_HDR": ["S_N", "J"], "S_L_LI": ["S_N", "J"],
                   "S_L_HI": ["S_N", "J"], "S_L_COM": ["S_N", "J"], "S_L_ORC": ["S_N", "J"],
                   "S_S": ["S_N", "J"], "S_N": ["J"], "S_B" : [0]}      #gives the order in which links can be arranged
        for key in nodedb.keys():
            map = linkmap[key]
            #print map
            for pos in range(len(map)):
                if map[pos] in nodedb.keys():
                    nodelinks.append([nodedb[key], nodedb[map[pos]]])   #[ID1, ID2] in an array
                    break
        #print nodelinks
        return nodelinks
    
    def getDownstreamNodeLink(self, upNodes, downNodes):
        """Returns the nodeIDs to connect with a link between two blocks"""
        nodelink = []
        #Case 1: Junction to Junction
        if "S_B" not in upNodes.keys():
            nodelink = [upNodes["J"], downNodes["J"]]
        #Case 2: Basin to Junction
        else:
            nodelink = [upNodes["S_B"], downNodes["J"]]
        return nodelink
    
    def getSystemOffsetXY(self, curSys, blocks_size):
        """Returns the coordinate offsets for the MUSIC node depending on the system scale.
        Offsets are defined in the offsetdictionary and are based on the pre-defined positioning
        for various treatment nodes and various scales. Node that the Lot nodes have an additional
        offset defined when they are placed"""
        offsetdictionary = {"L":[0, 0.25*blocks_size], "S":[0,0], 
                            "N":[0, 0.25*blocks_size*(-1)], 
                            "B":[0.25*blocks_size,0.25*blocks_size*(-1)] , 
                            "J":[0.25*blocks_size, 0]}  #Used to position treatment nodes depending on their scale
        if curSys == "J":
            return offsetdictionary["J"]
        scale = curSys.getAttribute("Scale").getString()
        if scale in ["L_RES", "L_COM", "L_LI", "L_HDR", "L_HI", "L_ORC"]:
            return offsetdictionary["L"]
        else:
            return offsetdictionary[scale]
        
    def prepareParametersBF(self, curSys, current_soilK):
        """Function to setup the parameter list vector for biofilters """
        #parameter_list = [EDD, surface area, filter area, unlined perimeter, satk, filterdepth, exfiltration]
        sysedd = curSys.getAttribute("WDepth").getDouble()
        sysarea = self.getEffectiveSystemArea(curSys)
        sysfd = curSys.getAttribute("FDepth").getDouble()
        parameter_list = [sysedd,sysarea,sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), 180, sysfd, current_soilK]
        return parameter_list
    
    def prepareParametersIS(self, curSys, current_soilK):
        """Function to setup the parameter list vector for infiltration systems"""
        #parameter_list = [surface area, EDD, filter area, unlined perimeter, filterdepth, exfiltration]
        sysedd = curSys.getAttribute("WDepth").getDouble()
        sysarea = self.getEffectiveSystemArea(curSys)
        sysfd = curSys.getAttribute("FDepth").getDouble()
        parameter_list = [sysarea,sysedd,sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), sysfd, current_soilK]
        return parameter_list
    
    def prepareParametersWSUR(self, curSys, current_soilK):
        """Function to setup the parameter list vector for Surface Wetlands """
        #parameter_list = [surface area, EDD, permanent pool, exfil, eq pipe diam, det time]
        sysarea = self.getEffectiveSystemArea(curSys)
        sysedd = curSys.getAttribute("WDepth").getDouble()
        parameter_list = [sysarea, sysedd, sysarea*0.2, current_soilK, 1000*numpy.sqrt(((0.895*sysarea*sysedd)/(72*3600*0.6*0.25*numpy.pi*numpy.sqrt(2*9.81*sysedd)))), 72.0]
        return parameter_list
    
    def prepareParametersPB(self, curSys, current_soilK):
        """Function to setup the parameter list vector for Ponds & Basins"""
        #parameter_list = [surface area, mean depth, permanent pool, exfil, eq pipe diam, det time]
        sysarea = self.getEffectiveSystemArea(curSys)
        sysedd = curSys.getAttribute("WDepth").getDouble()      #The mean depth
        parameter_list = [sysarea, sysedd, sysarea*0.2, current_soilK, 1000*numpy.sqrt(((0.895*sysarea*sysedd)/(72*3600*0.6*0.25*numpy.pi*numpy.sqrt(2*9.81*sysedd)))), 72.0]
        return parameter_list
        
    def prepareParametersSW(self, curSys, current_soilK):
        """Function to setup the parameter list vector for swales"""
        #parameter_list = [length, bedslope, Wbase, Wtop, depth, veg.height, exfilrate]
        sysarea = self.getEffectiveSystemArea(curSys)
        parameter_list = [sysarea/4, 5, 2, 6, float(1.0/3.0),0.05, current_soilK]   
        return parameter_list
        
    def prepareParametersRT(self, curSys, current_soilK):
        """Function to setup the parameter list vectr for raintanks"""
        #>>>FUTURE
        parameter_list = []
        return parameter_list
        
    def getEffectiveSystemArea(self, curSys):
        """Returns the effective system area of a given curSys input WSUD system
        equal to the total area divided by the effective area factor, both saved as attributes
        in the Attribue Object"""
        sysarea = curSys.getAttribute("SysArea").getDouble()/curSys.getAttribute("EAFact").getDouble()
        return sysarea
        

    ########################################################
    #DYNAMIND FUNCTIONS                                    #
    ########################################################
    def getBlockUUID(self, blockid,city):
	try:
		key = self.BLOCKIDtoUUID[blockid]
	except KeyError:
		key = ""
	return city.getFace(key)

    def initBLOCKIDtoUUID(self, city):
	blockuuids = city.getUUIDsOfComponentsInView(self.blocks)
        for blockuuid in blockuuids:
            block = city.getFace(blockuuid)
            ID = int(round(block.getAttribute("BlockID").getDouble()))
	    self.BLOCKIDtoUUID[ID] = blockuuid





