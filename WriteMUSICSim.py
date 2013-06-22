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
        
    Inputs: 
    
    Log of Updates made at each version:
    
    v1.0 (June 2013):
        - Version 1 release
    
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
        self.currentyear = 1960
	self.masterplanmodel = True
        #self.include_secondary_links = 0

	self.mapattributes = View("Mapattributes", COMPONENT,READ)
	self.mapattributes.getAttribute("NumBlocks")
	self.mapattributes.getAttribute("WidthBlocks")
	self.mapattributes.getAttribute("HeightBlocks")
	self.mapattributes.getAttribute("InputReso")
	self.mapattributes.getAttribute("TotalBasins")
        self.mapattributes.getAttribute("OutputStrats")
	
	self.blocks = View("Block",FACE,WRITE)
	self.blocks.getAttribute("Status")
	self.blocks.getAttribute("Centre_x")
	self.blocks.getAttribute("Centre_y")
	self.blocks.getAttribute("ResTIArea")
	self.blocks.getAttribute("ResAllots")
	self.blocks.getAttribute("ResLotImpA")
	self.blocks.getAttribute("Soil_k")
	self.blocks.getAttribute("downstrID")
	self.blocks.getAttribute("drainto_ID")


	self.wsudAttr = View("WsudAttr",COMPONENT,READ)
	self.wsudAttr.getAttribute("ScaleN")
	self.wsudAttr.getAttribute("Scale")
	self.wsudAttr.getAttribute("Location")
	self.wsudAttr.getAttribute("Type")
	self.wsudAttr.getAttribute("TypeN")
	self.wsudAttr.getAttribute("Qty")
	self.wsudAttr.getAttribute("GoalQty")
	self.wsudAttr.getAttribute("Degree")
	self.wsudAttr.getAttribute("SysArea")
	self.wsudAttr.getAttribute("Status")
	self.wsudAttr.getAttribute("Year")
	self.wsudAttr.getAttribute("EAFact")
	self.wsudAttr.getAttribute("ImpT")
	self.wsudAttr.getAttribute("CurImpT")
	self.wsudAttr.getAttribute("Upgrades")
	self.wsudAttr.getAttribute("WDepth")
	self.wsudAttr.getAttribute("FDepth")

	self.basin = View("Basin", COMPONENT, READ)
	self.basin.getAttribute("BasinID")
	self.basin.getAttribute("Blocks")
	self.basin.getAttribute("DownBlockID")
	self.basin.getAttribute("UpStr")

	datastream = []
        datastream.append(self.mapattributes)
	datastream.append(self.basin)
	datastream.append(self.wsudAttr)
	datastream.append(self.blocks)
        self.addData("City", datastream)
	
	self.BLOCKIDtoUUID = {}
	self.BASINIDtoUUID = {}
	self.WSUDS = {}
	
    def run(self):
	city = self.getData("City")
	self.initBASINIDtoUUID(city)
        self.initBLOCKIDtoUUID(city)
	self.initWsudUUIDs(city)

        
        strvec = city.getUUIDsOfComponentsInView(self.simulation)
	simulationData = city.getComponent(strvec[0])
	runs = int(simulationData.getAttribute("Runs").getDouble())
	#strvec = city.getUUIDsOfComponentsInView(self.desAttr)
        #des_attr = city.getComponent(strvec[0])
	strvec = city.getUUIDsOfComponentsInView(self.mapattributes)
        map_attr = city.getComponent(strvec[0])
        


        #get data needed to being for loop analysis
        blocks_num = map_attr.getAttribute("NumBlocks").getDouble()     #number of blocks to loop through
        blocks_size = map_attr.getAttribute("BlockSize").getDouble()    #size of block
        map_w = map_attr.getAttribute("WidthBlocks").getDouble()        #num of blocks wide
        map_h = map_attr.getAttribute("HeightBlocks").getDouble()       #num of blocks tall
        input_res = map_attr.getAttribute("InputReso").getDouble()      #resolution of input data
        totalbasins = map_attr.getAttribute("TotalBasins").getDouble()       #total number of basins in map
        print totalbasins
        receivingblocks = []
        for i in range(int(totalbasins)):
            print "Basin ID: "+str(self.getBasinUUID(i+1,city).getAttribute("BasinID").getDouble())
            print self.getBasinUUID(1+i,city).getAttribute("DownBlockID").getDouble()
            
            receivingblocks.append(self.getBasinUUID(i+1,city).getAttribute("DownBlockID").getDouble())
        
        print "Receiving Blocks: "
        print receivingblocks
        for k in range(runs): 
		k = k+1   
		system_list = []
		for i in range(int(blocks_num)):
		    lot_count = 0
		    street_count = 0
		    neigh_count = 0
		    prec_count = 0
		    print self.WSUDS
		    print str(i+1)+"L"+str(k)
		    print self.getWsud(i+1,"L",k)
		    if self.getWsud(i+1,"L",k) != None:
		    	if self.getWsud(i+1,"L",k).getAttribute("Location").getDouble() != 0: #if systems HAS a location, then
		            lot_count = 1 #system exists!
		    if self.getWsud(i+1,"S",k) != None:
			if self.getWsud(i+1,"S",k).getAttribute("Location").getDouble() != 0:
			    street_count = 1
		    if self.getWsud(i+1,"N",k) != None:
		        if self.getWsud(i+1,"N",k).getAttribute("Location").getDouble() != 0:
		            neigh_count = 1
		    if self.getWsud(i+1,"P",k) != None:
			if self.getWsud(i+1,"P",k).getAttribute("Location").getDouble() != 0:
			    prec_count = 1
		    total_systems = lot_count + street_count + neigh_count + prec_count
		    system_list.append([lot_count, street_count, neigh_count, prec_count])
		print system_list
		
		if self.masterplanmodel == 1:
		    filesuffix = "PC"
		else:
		    filesuffix = "IC"

		ufile = umusic.createMUSICmsf(self.pathname,self.filename+"-"+str(self.currentyear)+filesuffix+str(k))
		umusic.writeMUSICheader(ufile, "melbourne")      #write the header line
		scalar = 10
		ncount = 1

		musicnodedb = [[],[]]       #contains the database of nodes [[ID], [details]]
		for i in range(int(blocks_num)):
		    currentID = i+1
		    currentAttList = self.getBlockUUID(currentID,city)        #attribute list of current block structure
		    current_soilK = currentAttList.getAttribute("Soil_k").getDouble()

		    if currentAttList.getAttribute("Status").getDouble() == 0:
		        #skips the for loop iteration to the next block, not more needs to be done
		        continue
		    
		    musicnodedb[0].append(currentID)        #add the nodeID list for current block to a central matrix
		    
		    blockX = currentAttList.getAttribute("Centre_x").getDouble()
		    blockY = currentAttList.getAttribute("Centre_y").getDouble()

		    #lot scale node = x - size/2, y + size/2
		    #lot scale untreated = x - size/2, y
		    #street scale = x - size/2, y - size/2
		    #lot system = x, y + size/2
		    #street system = x, y
		    #neigh system = x, y-size/2
		    #prec system = x + size/2, y    
		    
		    #write catchment nodes - maximum possibility of two nodes
		    catchment_paramter_list = [1,120,30,20,200,1,10,25,5,0]
		    total_catch_imparea = currentAttList.getAttribute("ResTIArea").getDouble()/10000
		    total_lot_impA = (currentAttList.getAttribute("ResAllots").getDouble()*currentAttList.getAttribute("ResLotImpA").getDouble())/10000
		    street_imp_area = total_catch_imparea - total_lot_impA
		    ncount_list = []


		    if system_list[i][0] == 0:
		        #No strategies - GET AREAS AND PARAMETERS FOR A SINGLE CATCHMENT NODE
		        ncount_list.append(0)
		        umusic.writeMUSICcatchmentnode(ufile, currentID, "", ncount, (blockX-blocks_size/4)*scalar, (blockY)*scalar, total_catch_imparea,1, catchment_paramter_list)
		        ncount_list.append(ncount)
		        ncount += 1
		        
		    elif system_list[i][0] != 0:
		        #There are lot systems so get the lot sub-catchment node and merge the other untreated lots into the other node
		        #get lot areas
		        ncount_list.append(ncount)
		        umusic.writeMUSICcatchmentnode(ufile, currentID, "LT", ncount, (blockX-blocks_size/4)*scalar, (blockY+blocks_size/4)*scalar, total_lot_impA ,1, catchment_paramter_list)
		        ncount += 1
		        #get other areas
		        ncount_list.append(ncount)
		        umusic.writeMUSICcatchmentnode(ufile, currentID, "R", ncount, (blockX-blocks_size/4)*scalar, (blockY)*scalar, street_imp_area,1, catchment_paramter_list)
		        ncount += 1
		        
		    #write treatment nodes
		    
		    #Find lot-scale system, write the node
		    if system_list[i][0] != 0:
			wsud_attr = self.getWsud(i+1,"L",k)
		        lottype = wsud_attr.getAttribute("Type").getString()

		        parameter_list = [1,1]
		        ncount_list.append(ncount)
		        if lottype == "BF":
		            #setup parameter list:
		            #parameter_list = [EDD, surface area, filter area, unlined perimeter, satk, filterdepth, exfiltration]
		            
		            #sysedd = float(des_attr.getStringAttribute("BFspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()
		            


		            #sysfd = float(des_attr.getStringAttribute("BFspec_FD"))
		            sysfd = wsud_attr.getAttribute("FDepth").getDouble()
		           

		            parameter_list = [sysedd, sysarea, sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), 180, sysfd, current_soilK] #EDD, Asystem, FilterArea, UnlinedPerimeter, ksat, depth, exfil rate]
			    umusic.writeMUSICnodeBF(ufile, currentID, "L", ncount, blockX*scalar, (blockY+blocks_size/4)*scalar, parameter_list)
		        elif lottype == "IS":
		            #setup parameter list
		            #parameter_list = [surface area, EDD, filter area, unlined perimeter, filterdepth, exfiltration]
		            
		            #sysedd = float(des_attr.getStringAttribute("ISspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            #sysfd = float(des_attr.getStringAttribute("ISspec_FD"))
		            sysfd = wsud_attr.getAttribute("FDepth").getDouble()
		            

		            parameter_list = [sysarea, sysedd, sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), sysfd, current_soilK] #EDD, Asystem, FilterArea, UnlinedPerimeter, ksat, depth, exfil rate]

		            umusic.writeMUSICnodeIS(ufile, currentID, "L", ncount, blockX*scalar, (blockY+blocks_size/4)*scalar, parameter_list)
		        #writedetail = eval('umusic.writeMUSICnode'+str(lottype)+'('+str(ufile)+','+str(currentID)+',L,'+str(ncount)+','+str(blockX*scalar)+","+str((blockY+blocks_size/4)*scalar)+','+str(parameter_list)+')')
		        ncount += 1
		    else:
		        ncount_list.append(0)
		        
		        #Find the street-scale system, write the node
		    if system_list[i][1] != 0:
			wsud_attr = self.getWsud(i+1,"S",k)
		        streettype = wsud_attr.getAttribute("Type").getString()
		        parameter_list = [1,1]

		        ncount_list.append(ncount)
		        if streettype == "BF":
		            #setup parameter list:
		            #parameter_list = [EDD, surface area, filter area, unlined perimeter, satk, filterdepth, exfiltration]
		            
		            #sysedd = float(des_attr.getStringAttribute("BFspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            
		            #sysfd = float(des_attr.getStringAttribute("BFspec_FD"))
		            sysfd = wsud_attr.getAttribute("FDepth").getDouble()


		            parameter_list = [sysedd, sysarea, sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), 180, sysfd, current_soilK]
		            umusic.writeMUSICnodeBF(ufile, currentID, "S", ncount, blockX*scalar, blockY*scalar, parameter_list)
		            pass
		        elif streettype == "IS":
		            #setup parameter list:
		            #parameter_list = [surface area, EDD, filter area, unlined perimeter, filterdepth, exfiltration]
		            
		            #sysedd = float(des_attr.getStringAttribute("ISspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            
		            #sysfd = float(des_attr.getStringAttribute("ISspec_FD"))
		            sysfd = wsud_attr.getAttribute("FDepth").getDouble()


		            parameter_list = [sysarea, sysedd, sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), sysfd, current_soilK]
		            umusic.writeMUSICnodeIS(ufile, currentID, "S", ncount, blockX*scalar, blockY*scalar, parameter_list)

		            pass
		        elif streettype == "SW":
		            #setup parameter list
		            #parameter_list = [length, bedslope, Wbase, Wtop, depth, veg.height, exfilrate]
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            parameter_list = [sysarea/4, 5, 2, 6, float(1.0/3.0),0.05, current_soilK] #[length, bedslope, Wbase, Wtop, depth, veg.height, exfilrate]
		            umusic.writeMUSICnodeSW(ufile, currentID, "S", ncount, blockX*scalar, blockY*scalar, parameter_list)



		            pass
		        #writedetail = eval('umusic.writeMUSICnode'+str(streettype)+'('+str(ufile)+','+str(currentID)+',S,'+str(ncount)+','+str(blockX*scalar)+","+str(blockY*scalar)+','+str(parameter_list)+')')
		        ncount += 1
		    else:
		        ncount_list.append(0)
		        
		    #Find the neigh-scale system, write the node
		    if system_list[i][2] != 0:
			wsud_attr = self.getWsud(i+1,"N",k)
		        neightype = wsud_attr.getAttribute("Type").getString()

		        parameter_list = [1,1]
		        ncount_list.append(ncount)
		        if neightype == "BF":
		            #setup parameter list:
		            #parameter_list = [EDD, surface area, filter area, unlined perimeter, satk, filterdepth, exfiltration]
		            
		            #sysedd = float(des_attr.getStringAttribute("BFspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            #sysfd = float(des_attr.getStringAttribute("BFspec_FD"))
		            sysfd = wsud_attr.getAttribute("FDepth").getDouble()

		            parameter_list = [sysedd, sysarea, sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), 180, sysfd, current_soilK]
		            umusic.writeMUSICnodeBF(ufile, currentID, "N", ncount, blockX*scalar, (blockY-blocks_size/4)*scalar, parameter_list)
		            pass
		        elif neightype == "IS":
		            #setup parameter list:
		            #parameter_list = [surface area, EDD, filter area, unlined perimeter, filterdepth, exfiltration]
		            
		            #sysedd = float(des_attr.getStringAttribute("ISspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            
		            #sysfd = float(des_attr.getStringAttribute("ISspec_FD"))
		            sysfd = wsud_attr.getAttribute("FDepth").getDouble()
		            

		            parameter_list = [sysarea, sysedd, sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), sysfd, current_soilK]

		            parameter_list = [10, 0.2, 10, 14, 1, 100] #[pond_area, EDD, filter area, unlined filter perimeter, depth, exfil rate]
		            umusic.writeMUSICnodeIS(ufile, currentID, "N", ncount, blockX*scalar, (blockY-blocks_size/4)*scalar, parameter_list)
		            pass
		        elif neightype == "WSUR":
		            #setup parameter list:
		            #parameter_list = [surface area, EDD, permanent pool, exfil, eq pipe diam, det time]
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            
		            #sysedd = float(des_attr.getStringAttribute("WSURspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()
		            
		            parameter_list = [sysarea, sysedd, sysarea*0.2, current_soilK, 1000*numpy.sqrt(((0.895*sysarea*sysedd)/(72*3600*0.6*0.25*numpy.pi*numpy.sqrt(2*9.81*sysedd)))), 72.0]
		            umusic.writeMUSICnodeWSUR(ufile, currentID, "N", ncount, blockX*scalar, (blockY-blocks_size/4)*scalar, parameter_list)

		            pass
		        elif neightype == "PB":
		            #setup parameter list:
		            #parameter_list = [surface area, mean depth, permanent pool, exfil, eq pipe diam, det time]
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            
		            #sysedd = float(des_attr.getStringAttribute("PBspec_MD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()




		            parameter_list = [sysarea, sysedd, sysarea*0.2, current_soilK, 1000*numpy.sqrt(((0.895*sysarea*sysedd)/(72*3600*0.6*0.25*numpy.pi*numpy.sqrt(2*9.81*sysedd)))), 72.0]
		            
		            umusic.writeMUSICnodePB(ufile, currentID, "N", ncount, blockX*scalar, (blockY-blocks_size/4)*scalar, parameter_list)

		            pass
		        #writedetail = eval('umusic.writeMUSICnode'+str(neightype)+'('+str(ufile)+','+str(currentID)+',N,'+str(ncount)+','+str(blockX*scalar)+","+str((blockY-blocks_size/4)*scalar)+','+str(parameter_list)+')')
		        ncount += 1
		    else:
		        ncount_list.append(0)
		        
		    #write the Block's Junction
		    ncount_list.append(ncount)
		    umusic.writeMUSICjunction(ufile, currentID, ncount, (blockX+blocks_size/4)*scalar, (blockY)*scalar)
		    ncount += 1
		    
		    #write links
		    #Link 1: Lot catch to Lot System
		    if ncount_list[0] == 0:
		        pass
		    else:
		        umusic.writeMUSIClink(ufile, ncount_list[0], ncount_list[2])
		    
		    #Link 2: Other Catch to smallest scale treat system
		    blocksystemIDs = ncount_list[3:]
		    while 0 in blocksystemIDs:
		        blocksystemIDs.remove(0)
		    umusic.writeMUSIClink(ufile, ncount_list[1],min(blocksystemIDs))
		    
		    #Link 3: Lot scale system
		    if ncount_list[2] == 0:
		        pass
		    else:
		        umusic.writeMUSIClink(ufile,ncount_list[2], min(blocksystemIDs))
		    
		    #Link 4: Street system
		    if ncount_list[3] == 0:
		        pass
		    else:
		        blocksystemIDs = ncount_list[4:]
		        while 0 in blocksystemIDs:
		            blocksystemIDs.remove(0)
		        umusic.writeMUSIClink(ufile, ncount_list[3], min(blocksystemIDs))
		    
		    #Link 5: Neigh system
		    if ncount_list[4] == 0:
		        pass
		    else:
		        umusic.writeMUSIClink(ufile, ncount_list[4], ncount_list[5])
		    
		    #write the Precinct-scale system
		    if system_list[i][3] == 0:
		        ncount_list.append(0)
		    else:
			wsud_attr = self.getWsud(i+1,"P",k)
		        prectype = wsud_attr.getAttribute("Type").getString()
		        parameter_list = [1,1]
		        ncount_list.append(ncount)
		        if prectype == "BF":
		            #setup parameter list:
		            #parameter_list = [EDD, surface area, filter area, unlined perimeter, satk, filterdepth, exfiltration]
		            
		            #sysedd = float(des_attr.getStringAttribute("BFspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()
		            
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            
		            #sysfd = float(des_attr.getStringAttribute("BFspec_FD"))
		            sysfd = wsud_attr.getAttribute("FDepth").getDouble()
		            
		            parameter_list = [sysedd, sysarea, sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), 180, sysfd, current_soilK]
		            umusic.writeMUSICnodeBF(ufile, currentID, "P", ncount, (blockX+blocks_size/4)*scalar, (blockY-blocks_size/4)*scalar, parameter_list)

		            pass
		        elif prectype == "IS":
		            #setup parameter list:
		            #parameter_list = [surface area, EDD, filter area, unlined perimeter, filterdepth, exfiltration]
		            
		            #sysedd = float(des_attr.getStringAttribute("ISspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()
		            
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            
		            #sysfd = float(des_attr.getStringAttribute("ISspec_FD"))
		            sysfd = wsud_attr.getAttribute("FDepth").getDouble()
		            
		            parameter_list = [sysarea, sysedd, sysarea, (2*numpy.sqrt(sysarea/0.4)+2*sysarea/(numpy.sqrt(sysarea/0.4))), sysfd, current_soilK]
		            umusic.writeMUSICnodeIS(ufile, currentID, "P", ncount, (blockX+blocks_size/4)*scalar, (blockY-blocks_size/4)*scalar, parameter_list)

		            pass
		        elif prectype == "WSUR":
		            #setup parameter list
		            #parameter_list = [surface area, EDD, permanent pool, exfil, eq pipe diam, det time]
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            
		            #sysedd = float(des_attr.getStringAttribute("WSURspec_EDD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()

		            parameter_list = [sysarea, sysedd, sysarea*0.2, current_soilK, 1000*numpy.sqrt(((0.895*sysarea*sysedd)/(72*3600*0.6*0.25*numpy.pi*numpy.sqrt(2*9.81*sysedd)))), 72.0]
		            umusic.writeMUSICnodeWSUR(ufile, currentID, "P", ncount, (blockX+blocks_size/4)*scalar, (blockY-blocks_size/4)*scalar, parameter_list)
		            pass
		        elif prectype == "PB":
		            #setup parameter list:
		            #parameter_list = [surface area, mean depth, permanent pool, exfil, eq pipe diam, det time]
		            sysarea = wsud_attr.getAttribute("SysArea").getDouble()/wsud_attr.getAttribute("EAFact").getDouble()

		            
		            #sysedd = float(des_attr.getStringAttribute("PBspec_MD"))
		            sysedd = wsud_attr.getAttribute("WDepth").getDouble()

		            parameter_list = [sysarea, sysedd, sysarea*0.2, current_soilK, 1000*numpy.sqrt(((0.895*sysarea*sysedd)/(72*3600*0.6*0.25*numpy.pi*numpy.sqrt(2*9.81*sysedd)))), 72.0]

		            umusic.writeMUSICnodePB(ufile, currentID, "P", ncount, (blockX+blocks_size/4)*scalar, (blockY-blocks_size/4)*scalar, parameter_list)
		            pass
		        #writedetail = eval('umusic.writeMUSICnode'+str(neightype)+'('+str(ufile)+','+str(currentID)+',N,'+str(ncount)+','+str(blockX*scalar)+","+str((blockY-blocks_size/4)*scalar)+','+str(parameter_list)+')')
		        ncount += 1
		    #Link 6: Junction to prec tech
		    if system_list[i][3] != 0:
		        umusic.writeMUSIClink(ufile, ncount_list[5], ncount_list[6])
		        
		    #write receiving node for the basin
		    #Check if that Block is the downstream-most in the basin
		    if currentID in receivingblocks:
		        print currentID
		        ncount_list.append(ncount)
		        umusic.writeMUSICreceiving(ufile, currentID, ncount, (blockX)*scalar, (blockY-blocks_size/2)*scalar)
			receivingNode = ncount                
			ncount += 1
		        #Link 7: Junction/Prec-Tech to receiving Node
		        if system_list[i][3] != 0: #if there is a precinct technology...
		            umusic.writeMUSIClink(ufile, ncount_list[6], ncount_list[7])
		        else:
		            umusic.writeMUSIClink(ufile, ncount_list[5], ncount_list[7])
		        
		    musicnodedb[1].append(ncount_list)
		        
		    print "NCOUNT-LIST"
		    print ncount_list
		        
		    print musicnodedb
		    
		#CONNECT ALL BLOCK JUNCTIONS/TOGETHER TO STRING THE CATCHMENT TOGETHER
		for i in range(int(blocks_num)):
		    currentID = i+1
		    currentAttList = self.getBlockUUID(currentID,city)        #attribute list of current block structure
		    
		    block_status = currentAttList.getAttribute("Status").getDouble()
		    if block_status == 0:
		        #skips the for loop iteration to the next block, not more needs to be done
		        continue
		    

		    upindex = musicnodedb[0].index(currentID)
		    ncount_list_up = musicnodedb[1][upindex]

		    downID = int(round(currentAttList.getAttribute("downstrID").getDouble()))
		    print downID
		    if downID == -1:
		        downID = int(round(currentAttList.getAttribute("drainto_ID").getDouble()))
		    else:
		        downID == 0

		    if downID == 0:
		        pass
		    else:
		        downindex = musicnodedb[0].index(downID)
		        ncount_list_down = musicnodedb[1][downindex]
		        umusic.writeMUSIClink(ufile, max(ncount_list_up[5:]), ncount_list_down[5])


    def getBlockUUID(self, blockid,city):
	try:
		key = self.BLOCKIDtoUUID[blockid]
	except KeyError:
		key = ""
	return city.getFace(key)

    def getBasinUUID(self, basinid,city):
	try:
		key = self.BASINIDtoUUID[basinid]
	except KeyError:
		key = ""
	return city.getComponent(key)

    def getWsud(self,ID,scale,stratnr):
	try:
	   return self.WSUDS.get(str(int(ID))+scale+str(int(stratnr)))
	   '''if scale == 'L':
		return self.LotUUIDs[ID]
	   elif scale == 'S':
		return self.StreetUUIDs[ID]
	   elif scale == 'N':
		return self.NeighUUIDs[ID]
	   elif scale == 'P':
		return self.PrecUUIDs[ID]
	   else:
		print "Error in initWsudUUIDs Function, scale does not match :" + str(scale)''' 	
	except KeyError:
		key = ""
	return key

    def initWsudUUIDs(self, city):				#fills the 4 vectors for each scale and places them on their id slot in the vector (in location is the blockID)
	uuids = city.getUUIDsOfComponentsInView(self.wsudAttr)	#in scale is either "L" for Lot, "S" for Street, "N" for Neigh or "P" for Precinct 
        for uuid in uuids:
            wsud = city.getComponent(uuid)
            scale = wsud.getAttribute("Scale").getString()
	    ID = wsud.getAttribute("Location").getDouble()
	    stratNr = wsud.getAttribute("StrategyNr").getDouble()
	    self.WSUDS.update({str(int(ID))+scale+str(int(stratNr)):wsud})
	    '''if scale == 'L':
		ID = wsud.getAttribute("Location").getDouble()
		self.LotUUIDs[ID] = wsud
	    elif scale == 'S':
		ID = wsud.getAttribute("Location").getDouble()
		self.StreetUUIDs[ID] = wsud
	    elif scale == 'N':
		ID = wsud.getAttribute("Location").getDouble()
		self.NeighUUIDs[ID] = wsud
	    elif scale == 'P':
		ID = wsud.getAttribute("Location").getDouble()
		self.PrecUUIDs[ID] = wsud
	    else:
		print "Error in initWsudUUIDs Function, scales does not match :" + str(scale)'''

    def initBLOCKIDtoUUID(self, city):
	blockuuids = city.getUUIDsOfComponentsInView(self.blocks)
        for blockuuid in blockuuids:
            block = city.getFace(blockuuid)
            ID = int(round(block.getAttribute("BlockID").getDouble()))
	    self.BLOCKIDtoUUID[ID] = blockuuid

    def initBASINIDtoUUID(self, city):
	basinuuids = city.getUUIDsOfComponentsInView(self.basin)
        for basinuuid in basinuuids:
            basin = city.getComponent(basinuuid)
            ID = int(round(basin.getAttribute("BasinID").getDouble()))
	    self.BASINIDtoUUID[ID] = basinuuid






