# -*- coding: utf-8 -*-
"""
@file
@author Peter M Bach <peterbach@gmail.com>
@version 1.0
@section LICENSE

This file is part of UrbanBEATS
Copyright (C) 2013 Peter M Bach

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

from techimplementguic import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pydynamind import *
import math
import numpy as np

class Techimplement(Module):
    """Loads the Blocks and Patches Shapefile and transfers all relevant information into
    a suitable data management structure for use in urbplanbb and other modules
    Inputs: Either project path or exact filename
    - Obtain file directly from a filename or from an ongoing simulation? - Boolean
    Filename: specify path
    Ongoing simulation: specify project path (it is likely the program will load a text file with information on how to grab the shapefile)
    Outputs: Vector Data containing block attributes (these are used in later modules as a comparison with the newly entered data)
    Log of Updates made at each version:
    
    v1.00 (June 2013):
        - full update of module features
        - compatbility with new v1.00 modules
    
    v0.80 (July 2012):
        - First created.

    @ingroup UrbanBEATS
    @author Peter M Bach
    """
    
    def __init__(self):
        Module.__init__(self)
        
        #IMPLEMENTATION RULES TAB
        self.createParameter("dynamic_rule", STRING,"")
        self.dynamic_rule = "B" #B = Block-based, P = Parcel-based
        
        #Block-based Rules
        self.createParameter("block_based_thresh", DOUBLE, "")
        self.createParameter("bb_lot_rule", STRING, "")
        self.createParameter("bb_street_zone", BOOL, "")
        self.createParameter("bb_neigh_zone", BOOL, "")
        self.block_based_thresh = 30    #Threshold for implementation, % exceeded
        self.bb_lot_rule = "AMAP"       #AMAP = as many as possible, STRICT = strictly abide by %
        self.bb_street_zone = 1         #implement even if area hasn't been zoned yet
        self.bb_neigh_zone = 1          #implement even if neigh area hasn't been zoned yet
        
        self.createParameter("pb_lot_rule", STRING,"")
        self.createParameter("pb_street_rule", STRING,"")
        self.createParameter("pb_neigh_rule", STRING,"")
        self.createParameter("pb_neigh_zone_ignore",BOOL,"")
        self.pb_lot_rule = "G" #G = gradual, I = immediate, D = delayed
        self.pb_street_rule = "G"
        self.pb_neigh_rule = "G"
        self.pb_neigh_zone_ignore = 0
        
        self.createParameter("prec_rule", STRING,"")
        self.createParameter("prec_zone_ignore", BOOL,"")
        self.createParameter("prec_dev_threshold", BOOL,"")
        self.createParameter("prec_dev_percent", DOUBLE,"")
        self.prec_rule = "G"
        self.prec_zone_ignore = 0
        self.prec_dev_threshold = 0
        self.prec_dev_percent = 50
        
        #DRIVERS TAB - NOT ACTIVE YET, BUT PARAMETER LIST IS DEFINED FOR NOW
        self.createParameter("driver_people", BOOL,"")
        self.createParameter("driver_legal", BOOL,"")
        self.createParameter("driver_establish", BOOL,"")
        self.driver_people = 0
        self.driver_legal = 0
        self.driver_establish = 0
    
        ### ADVANCED PARAMETERS ######
        self.createParameter("currentyear", DOUBLE, "")
        self.createParameter("startyear", DOUBLE, "")
        self.currentyear = 1960
        self.startyear = 1960
        
        self.scale_matrix = ["L", "S", "N", "P"]

        # ----------------------------- #
        
	#Views - From Urbplanbb
        self.mapattributes = View("GlobalMapAttributes", COMPONENT, WRITE)
	self.mapattributes.getAttribute("NumBlocks")
	self.mapattributes.getAttribute("BlockSize")
	self.mapattributes.getAttribute("WidthBlocks")
	self.mapattributes.getAttribute("HeightBlocks")
	self.mapattributes.getAttribute("InputReso")
	self.mapattributes.addAttribute("TotalBasins")
        
	self.blocks = View("Block",FACE,READ)
	self.blocks.getAttribute("BlockID")

        self.patch = View("Patch", FACE, READ)

        #Views - From GetPreviousBlocks
	self.prevBlocks = View("PreviousBlocks",COMPONENT,READ)
        
        self.prevPatch = View("PatchAttributes", COMPONENT, READ)

	self.mastermapattributes = View("MasterMapAttributes",COMPONENT,READ)
        self.mastermapattributes.getAttribute("Xmin")
        self.mastermapattributes.getAttribute("Ymin")
        self.mastermapattributes.getAttribute("Width")
        self.mastermapattributes.getAttribute("Height")
        self.mastermapattributes.getAttribute("BlockSize")
        self.mastermapattributes.getAttribute("BlocksWidth")
        self.mastermapattributes.getAttribute("BlocksHeight")
        self.mastermapattributes.getAttribute("TotalBlocks")
        
        #Views - GetSystems
	self.sysGlobal = View("SystemGlobal",COMPONENT, READ)
	self.sysGlobal.getAttribute("TotalSystems")
	
        self.sysAttr = View("SystemAttribute",COMPONENT, READ)
	self.sysAttr.getAttribute("StrategyID")
        self.sysAttr.getAttribute("posX")
        self.sysAttr.getAttribute("posY")
	self.sysAttr.getAttribute("BasinID")
	self.sysAttr.getAttribute("Location")
	self.sysAttr.getAttribute("Scale")
	self.sysAttr.getAttribute("Type")
        self.sysAttr.getAttribute("Qty")
	self.sysAttr.getAttribute("GoalQty")
	self.sysAttr.getAttribute("SysArea")
	self.sysAttr.getAttribute("Status")
	self.sysAttr.getAttribute("Year")
	self.sysAttr.getAttribute("EAFact")
	self.sysAttr.getAttribute("ImpT")
	self.sysAttr.getAttribute("CurImpT")
	self.sysAttr.getAttribute("Upgrades")
	self.sysAttr.getAttribute("WDepth")
	self.sysAttr.getAttribute("FDepth")
        
        #Views - Output
	self.techimplAttr = View("WsudAttr",COMPONENT ,WRITE)	
	self.techimplAttr.addAttribute("StrategyID")
        self.techimplAttr.addAttribute("posX")
        self.techimplAttr.addAttribute("posY")
        self.techimplAttr.addAttribute("BasinID")
        self.techimplAttr.addAttribute("Location")
        self.techimplAttr.addAttribute("Scale")
        self.techimplAttr.addAttribute("Type")
        self.techimplAttr.addAttribute("Qty")
        self.techimplAttr.addAttribute("GoalQty")
        self.techimplAttr.addAttribute("SysArea")
        self.techimplAttr.addAttribute("Status")
        self.techimplAttr.addAttribute("Year")
        self.techimplAttr.addAttribute("EAFact")
        self.techimplAttr.addAttribute("ImpT")
        self.techimplAttr.addAttribute("CurImpT")
        self.techimplAttr.addAttribute("Upgrades")
        self.techimplAttr.addAttribute("WDepth")
        self.techimplAttr.addAttribute("FDepth")

        #Datastream
	datastream = []
        datastream.append(self.mapattributes)
        datastream.append(self.blocks)
        datastream.append(self.patch)
	datastream.append(self.prevBlocks)
	datastream.append(self.prevPatch)
	datastream.append(self.mastermapattributes)
        datastream.append(self.sysGlobal)
	datastream.append(self.sysAttr)
	datastream.append(self.techimplAttr)
        
        self.addData("City", datastream)
	
	self.BLOCKIDtoUUID = {}
        self.prevBLOCKIDtoUUID = {}     #DYNAMIND
        
    def run(self):
	city = self.getData("City")
	self.initBLOCKIDtoUUID(city)
        self.initPrevBLOCKIDtoUUID(city)        #DYNAMIND - initialize the dictionary that tracks Previous Block IDs and UUID
        
        currentyear = self.currentyear  #Tracking years in the dynamic simulation
        startyear = self.startyear

        #Get global map attributes
	strvec = city.getUUIDsOfComponentsInView(self.mapattributes)
        map_attr = city.getComponent(strvec[0])
        
        #Find out how many systems are in the list of systems to be implemented
	strvec = city.getUUIDsOfComponentsInView(self.sysGlobal)
        totsystems = city.getComponent(strvec[0]).getAttribute("TotalSystems").getDouble()
        print "Total Systems in map: "+str(totsystems)
        
        #Get block number, etc.
        blocks_num = map_attr.getAttribute("NumBlocks").getDouble() #number of blocks to loop through   
	blocks_size = map_attr.getAttribute("BlockSize").getDouble() #size of block

        #Get all systems for current block, also do a double-check on system location
        blockXY = self.getBlockXYcentres(city, blocks_num)
        sysList = {}
        for i in range(int(blocks_num)):
            sysList[i+1] = []   #Initialize the vector
        sysuuids = city.getUUIDsOfComponentsInView(self.sysAttr)
        for uuid in sysuuids:
            location = int(city.getComponent(uuid).getAttribute("Location").getDouble())
            if location == 0:
                posX = city.getComponent(uuid).getAttribute("posX").getDouble()
                posY = city.getComponent(uuid).getAttribute("posY").getDouble()
                location = self.determineSystemBlockLocation(posX, posY, blockXY, blocks_size)
            if self.skipIfStatusZero(location, city):
                continue        #If system is not within simulation bounds i.e. active blocks, skip
            else:
                sysList[int(location)].append(city.getComponent(uuid))  #Append the UUID for the current matrix
                
        #print sysList
        
        #Begin looping across blocks
        for i in range(int(blocks_num)):
            currentID = i + 1
            currentAttList = self.getBlockUUID(currentID,city) #attribute list of current block structure
            masterplanAttList = self.getPrevBlockUUID(currentID, city)
            
            #-----------------------------------------------------------------#
            # DETERMINE WHETHER TO IMPLEMENT IN CURRENT BLOCK AT ALL #
            #-----------------------------------------------------------------#
            ### QUIT CONDITION #1 - BLOCK STATUS = 0 ###
            if self.skipIfStatusZero(currentID, city):
                continue
            
            ### QUIT CONDITION #2 - NO SYSTEMS PLANNED FOR BLOCK AT ALL ###
            syscount = len(sysList[currentID])
            if syscount == 0:
                continue
 
            ### QUIT CONDITION #3 - DYNAMIC-MODE = Block-based and DEVELOPMENT < Threshold ###
            if self.dynamic_rule == "B":
                block_skip = self.skipIfBelowBlockThreshold(currentID, float(self.block_based_thresh/100), city)
                #use block_skip to determine whether to skip the next few steps
 
            print "BlockID", currentID, " has systems to be implemented"
            
            #LOOP ACROSS SYSTEMS IN THE sysList and implement them if necessary
            for sys in sysList[currentID]:
                if sys.getAttribute("Scale").getString() in ["L_RES"]:
                    qty, curImpT, year = self.implementLotSystem(currentAttList, masterplanAttList, sys)
                    if qty != 0:
                        self.writeSystemAttributesToOutput(sys, year, qty, curImpT, currentAttList, blocks_size, city)
                    
                elif sys.getAttribute("Scale").getString() in ["L_COM", "L_HDR", "L_LI", "L_HI"]:
                    qty, curImpT, year = self.implementLotSystem(currentAttList, masterplanAttList, sys)
                    if qty != 0:
                        self.writeSystemAttributesToOutput(sys, year, qty, curImpT, currentAttList, blocks_size, city)
                    
                elif sys.getAttribute("Scale").getString() in ["S", "N"]:
                    curImpT, year = self.implementStreetNeighSystem(currentAttList, masterplanAttList, sys)
                    if curImpT != 0:
                        self.writeSystemAttributesToOutput(sys, year, 1, curImpT, currentAttList, blocks_size, city)
                    
                elif sys.getAttribute("Scale").getString() in ["B"]:
                    curImpT, year = self.implementBasinSystem(currentAttList, masterplanAttList, sys, city)
                    if curImpT != 0:
                        self.writeSystemAttributesToOutput(sys, year, 1, curImpT, currentAttList, blocks_size, city)
            
            #BLOCK FOR LOOP END (Repeat for next BlockID)
            
        print "End of Implementation Module"

    ########################################################
    #TECHIMPLEMENT FUNCTIONS                               #
    ########################################################
    def skipIfStatusZero(self, ID, city):
        """Determines if the current BlockID's status is 1 or 0, if 0 transfers all its data
        to the output vector and returns true. If main function receives true"""
        if self.getBlockUUID(ID,city).getAttribute("Status").getDouble() == 0:
            print "BlockID"+str(ID)+" is not active in simulation"
            return True
        else:
            return False
    
    def getBlockXYcentres(self, city, blocks_num):
        """Scans the array of Blocks and creates an XY vector of block coordinates"""
        blockXY = {}
        for i in range(int(blocks_num)):
            currentID = i+1
            currentAttList = self.getBlockUUID(currentID, city)
            cX = currentAttList.getAttribute("CentreX").getDouble()
            cY = currentAttList.getAttribute("CentreY").getDouble()
            blockXY[currentID] = [cX, cY]
        return blockXY

    def determineSystemBlockLocation(self, posX, posY, blockXY, block_size):
        """Returns the BlockID, where the system is located. If no BlockID was found,
        returns 0"""
        for i in blockXY.keys():    #Loop across blockIDs
            xmin = blockXY[i][0] - block_size/2     #Xmin is centre minus half the block size
            xmax = xmin + block_size        #max is min + block size
            ymin = blockXY[i][1] - block_size/2    
            ymax = ymin + block_size
            if posX > xmin and posX < xmax:
                if posY > ymin and posY < ymax:
                    return int(i)        #Found the BlockID
        return 0
    
    def skipIfBelowBlockThreshold(self, ID, threshold,city):
	undevland = self.getBlockUUID(ID, city).getAttribute("pLU_UND").getDouble()
        undevprev = self.getPrevBlockUUID(ID, city).getAttribute("pLU_UND").getDouble() #This is the final value
        devtot = 1 - undevprev  #Developed = Masterplan, i.e. once 1-%UND has been developed
        if ((1-undevland)/devtot) < threshold:
            #If the developmed land (according to masterplan) has reached a threshold for development, implement
            return True
        else:
            return False        #Otherwise skip
    
    def writeSystemAttributesToOutput(self, sys, year, qty, currentImpT, currentAttList, block_size, city):
        """Writes the attributes to module output of the systems implemented"""
        centreX = currentAttList.getAttribute("CentreX").getDouble()
        centreY = currentAttList.getAttribute("CentreY").getDouble() 
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        
        offsets_matrix = [[centreX+float(block_size)/16.0, centreY+float(block_size)/4.0],
                          [centreX+float(block_size)/12.0, centreY+float(block_size)/4.0],
                          [centreX+float(block_size)/8.0, centreY+float(block_size)/4.0],
                          [centreX+float(block_size)/4.0, centreY+float(block_size)/4.0],
                          [centreX+float(block_size)/3.0, centreY+float(block_size)/4.0],
                          [centreX+float(block_size)/4.0, centreY-float(block_size)/8.0],
                          [centreX-float(block_size)/8.0, centreY-float(block_size)/4.0],
                          [centreX-float(block_size)/4.0, centreY-float(block_size)/8.0]]
        blockscale_names = ["L_RES", "L_HDR", "L_LI", "L_HI", "L_COM", "S", "N", "B"]
        
        coordinates = offsets_matrix[blockscale_names.index(sys.getAttribute("Scale").getString())]
        
        #WRITE THE ATTRIBUTES
        sysAttr = Component()
        sysAttr.addAttribute("StrategyID", int(sys.getAttribute("StrategyID").getDouble()))
        sysAttr.addAttribute("posX", coordinates[0])
        sysAttr.addAttribute("posY", coordinates[1])
        sysAttr.addAttribute("BasinID", int(sys.getAttribute("BasinID").getDouble()))
        sysAttr.addAttribute("Location", currentID)
        sysAttr.addAttribute("Scale", sys.getAttribute("Scale").getString())
        sysAttr.addAttribute("Type", sys.getAttribute("Type").getString())
        sysAttr.addAttribute("Qty", qty)      #Currently none available
        sysAttr.addAttribute("GoalQty", sys.getAttribute("GoalQty").getDouble())  #lot scale mainly - number of lots to build
        sysAttr.addAttribute("SysArea", sys.getAttribute("SysArea").getDouble())
        sysAttr.addAttribute("Status", 1)   #0 = not built, 1 = built
        sysAttr.addAttribute("Year", int(year))
        sysAttr.addAttribute("EAFact", sys.getAttribute("EAFact").getDouble())
        sysAttr.addAttribute("ImpT", sys.getAttribute("ImpT").getDouble())
        sysAttr.addAttribute("CurImpT", currentImpT)
        sysAttr.addAttribute("Upgrades", sys.getAttribute("Upgrades").getDouble()) #Done in the retrofit/implementation part
        sysAttr.addAttribute("WDepth", sys.getAttribute("WDepth").getDouble()) #Done in the retrofit/implementation part
        sysAttr.addAttribute("FDepth", sys.getAttribute("FDepth").getDouble()) #Done in the retrofit/implementation part
        city.addComponent(sysAttr, self.techimplAttr)
        return True
    
    def implementLotSystem(self, currentAttList, masterAttList, sys):
        """Performs the checks to determine whether a residential lot system can be
        implemented in the current block using current Block data and masterplan
        data."""
        #GoalQty for different land uses:
            #-RES - allotments or houses
            #-HDR - always 1, it's a yes/no implementation
            #-LI - always implemented in all estates, but can only be done if they're built
            #-HI - same as LI
            #-COM - same as LI
        
        if sys.getAttribute("Scale").getString() == "L_RES":
            unitEIA = currentAttList.getAttribute("ResLotEIA").getDouble()
            if sys.getAttribute("Type").getString() in ["BF", "IS"]:    #Pick the correct units to use
                units = currentAttList.getAttribute("ResAllots").getDouble()        #Allotments
                masterUnits = masterAttList.getAttribute("ResAllots").getDouble()
            elif sys.getAttribute("Type").getString() in ["RT"]:
                units = currentAttList.getAttribute("ResHouses").getDouble()        #Houses
                masterUnits = masterAttList.getAttribute("ResHouses").getDouble()
        elif sys.getAttribute("Scale").getString() == "L_LI":
            unitEIA = currentAttList.getAttribute("LIAeEIA").getDouble()
            units = currentAttList.getAttribute("LIestates").getDouble()
            masterunits = currentAttList.getAttribute("LIestates").getDouble()
        elif sys.getAttribute("Scale").getString() == "L_HI":
            unitEIA = currentAttList.getAttribute("HIAeEIA").getDouble()
            units = currentAttList.getAttribute("HIestates").getDouble()
            masterunits = currentAttList.getAttribute("HIestates").getDouble()
        elif sys.getAttribute("Scale").getString() == "L_COM":
            unitEIA = currentAttList.getAttribute("COMAeEIA").getDouble()
            units = currentAttList.getAttribute("COMestates").getDouble()
            masterunits = currentAttList.getAttribute("COMestates").getDouble()
        elif sys.getAttribute("Scale").getString() == "L_HDR":
            unitEIA = currentAttList.getAttribute("HDR_EIA").getDouble()
            units = currentAttList.getAttribute("HasFlats").getDouble()             #Simple yes/no
            masterunits = currentAttList.getAttribute("HasFlats").getDouble()
                
        if units == 0:
            print "Current Block has no units for that particular land use to implement on"
            return 0,0,0
        
        goallots = sys.getAttribute("GoalQty").getDouble()      #Saved from Techplacement
        if goallots == 0:
            return 0,0,0    #No implementation specified, not even going to try
        
        if int(sys.getAttribute("Year").getDouble()) == 9999:       #System not even built yet
            if self.bb_lot_rule == "AMAP":
                #As many as possible, the smaller of what the goal is or how many allotments have been built
                lotqty = min(goallots, units)      #The smaller of the two
                year = int(self.currentyear)
            elif self.bb_lot_rule == "STRICT":
                #Maintain ratio as development is built
                lotqty = (goallots/masterUnits) * units   #Envisioned ratio x current number of units
                year = int(self.currentyear)
                
        elif int(sys.getAttribute("Year").getDouble()) != 9999:     #Code is duplicated in case of future algorithms
            remainingQty = max(goallots - sys.getAttribute("Qty").getDouble(),0)
            if remainingQty > 0 and self.bb_lot_rule == "AMAP":
                lotqty = min(goallots, units)
                year = int(self.currentyear)
                
            elif remainingQty > 0 and self.bb_lot_rule == "STRICT":
                lotqty = (goallots/masterUnits) * units   #New systems
                year = int(self.currentyear)
                
            elif remainingQty <= 0:
                lotqty = goallots
                year = int(sys.getAttribute("Year").getDouble())
        
        #SPACE FOR FUTURE DECISION VARIABLES
        
        currentImpT = lotqty * sys.getAttribute("ImpT").getDouble()
        return lotqty, currentImpT, year
    
    
    def implementStreetNeighSystem(self, currentAttList, masterAttList, sys):
        """Performs the checks to determine whether a street or neighbourhood-scale
        system can be implemented in the current block using current Block data and
        masterplan data."""
        
        if int(sys.getAttribute("Status").getDouble()) == 1:    #Only for S and N systems
            #Transfer attributes as is
            curImpT = sys.getAttribute("CurImpT").getDouble()
            year = int(sys.getAttribute("Year").getDouble())
            return curImpT, year
        #If status == 0, then buildyear is also 9999
        
        #CRITERIA 1 - Check available space
        if sys.getAttribute("Scale").getString() == "S":
            avl_space = currentAttList.getAttribute("avSt_RES").getDouble()
        elif sys.getAttribute("Scale").getString() == "N":
            if sys.getAttribute("Type").getString() in ["BF", "WSUR", "PB", "IS"]:
                avl_space = currentAttList.getAttribute("PG_av").getDouble() + \
                    currentAttList.getAttribute("REF_av").getDouble()
        
        sysarea = sys.getAttribute("SysArea").getDouble()
        if sys.getAttribute("Scale").getString() == "S":
            if self.bb_street_zone == 0 and avl_space < sysarea:
                return 0,0
        elif sys.getAttribute("Scale").getString() == "N":
            if self.bb_neigh_zone == 0 and avl_space < sysarea:
                return 0,0
        
        #CRITERIA X - Future Criteria for deciding on implementation
        
        #CRITERIA 2 - Check development Status
        if sys.getAttribute("Scale").getString() == "S":
            devarea = currentAttList.getAttribute("ResLotEIA").getDouble() * \
                currentAttList.getAttribute("ResAllots").getDouble()
            masterplan = currentAttList.getAttribute("ResLotEIA").getDouble() * \
                currentAttList.getAttribute("ResAllots").getDouble()
            if devarea/masterplan < float(self.block_based_thresh/100):
                return 0,0
            else:
                year = self.currentyear
                curImpT = sys.getAttribute("ImpT").getDouble()
                return curImpT, year
        elif sys.getAttribute("Scale").getString() == "N":
            #Develop. Have already checked the block threshold for the Neighbourhood
            year = self.currentyear
            curImpT = sys.getAttribute("ImpT").getDouble()
            return curImpT, year
        return 0,0
    
    def implementBasinSystem(self, currentAttList, masterAttList, sys, city):
        """Performs the checks to determine whether a sub-basin scale technology can be
        implemented in the current Block using current Block data and masterplan data"""
        if int(sys.getAttribute("Status").getDouble()) == 1:    #Only for S and N systems
            #Transfer attributes as is
            curImpT = sys.getAttribute("CurImpT").getDouble()
            year = int(sys.getAttribute("Year").getDouble())
            return curImpT, year
        #If status == 0, then buildyear is also 9999
        
        #CRITERIA 1 - Check available space
        if sys.getAttribute("Type").getString() in ["BF", "WSUR", "PB", "IS"]:
            avl_space = currentAttList.getAttribute("PG_av").getDouble() + \
                currentAttList.getAttribute("REF_av").getDouble()
        
        sysarea = sys.getAttribute("SysArea").getDouble()
        if self.prec_zone_ignore == 0 and avl_space < sysarea:
            return 0,0
        
        #CRITERIA X - Future space for further criteria
        
        #CRITERIA 2 - Check development status of upstream area
        curUD, mastUD = self.retrieveUndevelopedAreas(currentAttList, masterAttList, city, "upstream")
        if self.prec_dev_threshold == True: 
            if (1-curUD)/(1-mastUD) < float(self.prec_dev_percent/100):
                #print "Upstream area not developed enough, skipping..."
                return 0,0
        
        #If the models makes it to this point, then the system is implemented
        year = self.currentyear
        curImpT = sys.getAttribute("ImpT").getDouble()
        return curImpT, year

    def retrieveUndevelopedAreas(self, currentAttList, prevAttList, city, direction):
        """Retrieves the proportion of undeveloped area in all upstream blocks including
        the current block being implemented with WSUD. Returns current and masterplan
        proportions."""
        if direction == "upstream":
            attname = "UpstrIDs"
        elif direction == "downstream":
            attname = "DownstrIDs"
        
        streamstring = currentAttList.getAttribute(attname).getString()
        streamIDs = streamstring.split(',')
        streamIDs.remove('')
        
        for i in range(len(streamIDs)):
            streamIDs[i] = int(streamIDs[i])
        if len(streamIDs) == 0:
            return 0
        
        undevarea = currentAttList.getAttribute("pLU_UND").getDouble() * \
            currentAttList.getAttribute("Active").getDouble() 
        mastplanundev = prevAttList.getAttribute("pLU_UND").getDouble() * \
            prevAttList.getAttribute("pLU_UND").getDouble()
        activetrack = currentAttList.getAttribute("Active").getDouble()
        
        for i in range(len(streamIDs)):
            print streamIDs[i]
            blockattr = self.getBlockUUID(streamIDs[i], city)
            mastattr = self.getPrevBlockUUID(streamIDs[i], city)
            undevarea += blockattr.getAttribute("pLU_UND").getDouble() * \
                blockattr.getAttribute("Active").getDouble()
            mastplanundev += mastattr.getAttribute("pLU_UND").getDouble() * \
                mastattr.getAttribute("Active").getDouble()
            activetrack += blockattr.getAttribute("Active").getDouble()
        
        undevarea = undevarea/activetrack
        mastplanundev = mastplanundev/activetrack
        return undevarea, mastplanundev
        
    ########################################################
    #DYNAMIND FUNCTIONS                                    #
    ########################################################
    def initBLOCKIDtoUUID(self, city):
	blockuuids = city.getUUIDsOfComponentsInView(self.blocks)
        for blockuuid in blockuuids:
            block = city.getFace(blockuuid)
            ID = int(round(block.getAttribute("BlockID").getDouble()))
	    self.BLOCKIDtoUUID[ID] = blockuuid

    def initPrevBLOCKIDtoUUID(self, city):
        prevblockuuids = city.getUUIDsOfComponentsInView(self.prevBlocks)
        for uuid in prevblockuuids:
            block = city.getComponent(uuid)
            ID = int(round(block.getAttribute("BlockID").getDouble()))
            self.prevBLOCKIDtoUUID[ID] = uuid

    def getBlockUUID(self, blockid,city):
	try:
		key = self.BLOCKIDtoUUID[blockid]
	except KeyError:
		key = ""
	return city.getFace(key)

    def getPrevBlockUUID(self, blockid, city):
        try:
            key = self.prevBLOCKIDtoUUID[blockid]
        except KeyError:
            key = ""
        return city.getComponent(key)

    def createInputDialog(self):
        form = activatetechimplementGUI(self, QApplication.activeWindow())
        form.exec_()
        return True 
