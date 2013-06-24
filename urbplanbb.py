# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 1.0
@section LICENSE

This file is part of UrbanBEATS (www.urbanbeatsmodel.com), DynaMind
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
from urbplanbbguic import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pydynamind import *
import random, math
import numpy as np

class Urbplanbb(Module):
    """Determines urban form of grid of blocks for model city by processing the
    individual land zoning classes along with the planning map, locality map and
    population input with local planning regulations/rules/geometries.
	
    The updated grid is output along with all parameters in two separate
    vector files: 
	- <description of inputs/outputs>
    
    Log of Updates made at each version:
    
    v1.0 update (November, 2012):
        - Restructured entire module, the five modules are now one single module and several
            separate functions and external scripts
        - Urbplanbb can now do all land uses as illustrated in the GUI
        - Uses patch information in its planning as well
        - Introduced Building Block Dynamics by working with the previously planned blocks
            and thresholds to determine if block properties can be transferred across or 
            whether the block needs to be redeveloped.
    
    v0.8 update (March, 2012):
        - Split the planning into four separate modules with prefix ubp_
        - This has cut several hundred lines of code in urbplanbb.py
        - urbplansummary.py now active, will take the existing map from this module
            and add the additional planning data to it
        - urbplanbb's sole purpose at the moment is to process information from the GUI
    
    v0.5 update (August 2011):
        - Can do residential houses districts
        - Updated the GUI with new features, other land uses, etc.
        
    v0.5 first (July 2011):
        - Created urbplanbb, basic GUI layout, basic features, initial processing of information
	
	@ingroup UrbanBEATS
        @author Peter M Bach
        """

    def __init__(self):
        Module.__init__(self)
        #inputs from previous modules and output vector data to next module
        
        ############################
        #GENERAL RULES PARAMETERS 
        ############################
        #--> General City Structure
        self.createParameter("cityarchetype", STRING, "")       #DYNAMIND
        self.createParameter("citysprawl", DOUBLE, "")          #DYNAMIND
        self.createParameter("locality_mun_trans", BOOL, "")    #DYNAMIND
        self.cityarchetype = "MC"       #MC = monocentric, PC = polycentric
        self.citysprawl = 50.0          #km - approximate urban sprawl radius from main CBD
        self.locality_mun_trans = False #Locality Map available for use? Yes/No
        
        #--> Decision Variables for Block Dynamics
        self.createParameter("lucredev", BOOL, "")              #DYNAMIND
        self.createParameter("popredev", BOOL, "")              #DYNAMIND
        self.createParameter("lucredev_thresh", DOUBLE, "")     #DYNAMIND
        self.createParameter("popredev_thresh", DOUBLE, "")     #DYNAMIND
        self.createParameter("noredev", BOOL, "")               #DYNAMIND
        self.lucredev = False
        self.popredev = False
        self.lucredev_thresh = 50       #% threshold required for redevelopment to take place
        self.popredev_thresh = 50       #% threshold required for redevelopment to take place
        self.noredev = True             #DO NOT REDEVELOP - if checked = True, then all the above parameters no longer used
        
        ############################
        #RESIDENTIAL PARAMETERS
        ############################
        #(includes all residential land uses of varying density)
        #--> Planning Parameters
        self.createParameter("occup_avg", DOUBLE, "")
        self.createParameter("occup_max", DOUBLE, "")
        self.createParameter("person_space", DOUBLE, "")
        self.createParameter("extra_comm_area", DOUBLE, "")
        self.createParameter("setback_f_min", DOUBLE, "")
        self.createParameter("setback_f_max", DOUBLE, "")
        self.createParameter("setback_s_min", DOUBLE, "")
        self.createParameter("setback_s_max", DOUBLE, "")
        self.createParameter("setback_f_med", BOOL, "")
        self.createParameter("setback_s_med", BOOL, "")
        self.createParameter("carports_max", DOUBLE, "")
        self.createParameter("garage_incl", BOOL, "")
        self.createParameter("w_driveway_min", DOUBLE, "")
        self.createParameter("patio_area_max", DOUBLE, "")
        self.createParameter("patio_covered", BOOL, "")
        self.createParameter("floor_num_max", DOUBLE, "")
        self.createParameter("occup_flat_avg", DOUBLE, "")
        self.createParameter("commspace_indoor", DOUBLE, "")
        self.createParameter("commspace_outdoor", DOUBLE, "")
        self.createParameter("flat_area_max", DOUBLE, "")
        self.createParameter("floor_num_HDRmax", DOUBLE, "")
        self.createParameter("setback_HDR_avg", DOUBLE, "")
        self.createParameter("parking_HDR", STRING, "")
        self.createParameter("park_OSR", BOOL, "")
        self.createParameter("roof_connected", STRING, "")
        self.createParameter("imperv_prop_dced", DOUBLE, "")
        self.occup_avg = 2.67                   #average occupancy (house)
        self.occup_max = 5                      #maximum occupancy (house)
        self.person_space = 84                  #space per person [sqm]
        self.extra_comm_area = 10               #extra space for communal area
        self.setback_f_min = 2                  #minimum front setback
        self.setback_f_max = 9                  #maximum front setback
        self.setback_s_min = 1                  #minimum side setback (applies to rear as well)
        self.setback_s_max = 2                  #maximum side setback (applies to rear as well)
        self.setback_f_med = 0                  #Use median for min/max front setback?
        self.setback_s_med = 0                  #Use median for min/max side setback?
        self.carports_max = 2                   #max number of carports
        self.garage_incl = False                #include garage? YES/NO
        self.w_driveway_min = 2.6               #minimum driveway width [m]
        self.patio_area_max = 2                 #maximum patio area [sqm]
        self.patio_covered = False              #is patio covered by roof?
        self.floor_num_max = 2                  #maximum number of floors
        self.occup_flat_avg = 1.5               #average occupancy of apartment
        self.commspace_indoor = 10              #communal space % indoor
        self.commspace_outdoor = 5              #communal space % outdoor
        self.flat_area_max = 90                 #maximum apartment size [sqm]
        self.floor_num_HDRmax = 10              #maximum number of floors of high-rise apartments
        self.setback_HDR_avg = 1                #average setback for HDR site
        self.parking_HDR = "On"                 #On = On-site, Off = Off-site, Var = Vary, NA = None
        self.park_OSR = 0                       #Leverage parks to fulfill outdoor open space requirements?
        self.roof_connected = "Direct"          #how is the roof connected to drainage? Direct/Disconnected/Varied?
        self.imperv_prop_dced = 10              #proportion of impervious area disconnected
        
        #--> Advanced Parameters
        self.min_allot_width = 10       #minimum width of an allotment = 10m if exceeded, then will build double allotments
        self.houseLUIthresh = [3.0, 5.4]   #house min and max threshold for LUI
        self.aptLUIthresh = [3.7, 6.5]     #walk-up apartment min and max threshold for LUI
        self.highLUIthresh = [5.9, 8.0]    #high-rise apartments min and max threshold for LUI
        
        self.resLUIdict = {}               #ratio tables for residential distict planning (from Time-Saver Standards)
        self.resLUIdict["LUI"] = [3.0,3.1,3.2,3.3,3.4,3.5,3.6,3.7,3.8,3.9,4.0,4.1,4.2,4.3,4.4,4.5,4.6,4.7,4.8,4.9,
                        5.0,5.1,5.2,5.3,5.4,5.5,5.6,5.7,5.8,5.9,6.0,6.1,6.2,6.3,6.4,6.5,6.6,6.7,6.8,6.9,7.0,7.1,
                        7.2,7.3,7.4,7.5,7.6,7.7,7.8,7.9,8.0]
        self.resLUIdict["FAR"] = [0.100,0.107,0.115,0.123,0.132,0.141,0.152,0.162,0.174,0.187,0.200,0.214,0.230,0.246,
                        0.264,0.283,0.303,0.325,0.348,0.373,0.400,0.429,0.459,0.492,0.528,0.566,0.606,0.650,0.696,
                        0.746,0.800,0.857,0.919,0.985,1.060,1.130,1.210,1.300,1.390,1.490,1.600,1.720,1.840,
                        1.970,2.110,2.260,2.420,2.600,2.790,2.990,3.200]
        self.resLUIdict["OSR"] = [0.80,0.80,0.79,0.79,0.78,0.78,0.78,0.77,0.77,0.77,0.76,0.76,0.75,0.75,0.74,0.74,0.73,
                        0.73,0.73,0.72,0.72,0.72,0.72,0.71,0.71,0.71,0.70,0.70,0.69,0.69,0.68,0.68,0.68,0.68,0.68,
                        0.67,0.67,0.67,0.68,0.68,0.68,0.68,0.69,0.70,0.71,0.72,0.75,0.76,0.81,0.83,0.86]
        self.resLUIdict["LSR"] = [0.65,0.62,0.60,0.58,0.55,0.54,0.53,0.53,0.52,0.52,0.52,0.51,0.51,0.49,0.48,0.48,0.46,
                        0.46,0.45,0.45,0.44,0.43,0.42,0.41,0.41,0.40,0.40,0.40,0.40,0.40,0.40,0.40,0.40,0.40,0.40,0.41,
                        0.41,0.42,0.42,0.43,0.43,0.45,0.46,0.47,0.49,0.50,0.51,0.52,0.56,0.57,0.61]
        self.resLUIdict["RSR"] = [0.025,0.026,0.026,0.028,0.029,0.030,0.030,0.032,0.033,0.036,0.036,0.039,0.039,0.039,
                        0.042,0.042,0.046,0.046,0.049,0.052,0.052,0.055,0.056,0.059,0.062,0.062,0.065,0.065,0.070,0.075,
                        0.080,0.080,0.083,0.085,0.085,0.090,0.097,0.104,0.104,0.104,0.112,0.115,0.115,0.118,0.127,0.136,
                        0.145,0.145,0.145,0.150,0.160]
        self.resLUIdict["OCR"] = [2.00,1.90,1.90,1.80,1.70,1.70,1.60,1.60,1.50,1.50,1.40,1.40,1.40,1.30,1.30,1.20,1.20,1.20,
                        1.10,1.10,1.10,1.00,1.00,0.99,0.96,0.93,0.90,0.87,0.84,0.82,0.79,0.77,0.74,0.72,0.70,0.68,0.66,0.64,
                        0.62,0.60,0.58,0.57,0.56,0.54,0.52,0.50,0.49,0.47,0.46,0.45,0.44]
        self.resLUIdict["TCR"] = [2.20,2.10,2.10,2.00,1.90,1.90,1.80,1.80,1.70,1.70,1.60,1.60,1.50,1.50,1.50,1.40,1.40,1.30,
                        1.30,1.30,1.20,1.20,1.20,1.10,1.10,1.10,1.00,1.00,0.99,0.96,0.83,0.90,0.85,0.85,0.83,0.81,0.79,0.77,
                        0.75,0.73,0.71,0.69,0.67,0.65,0.63,0.61,0.60,0.58,0.56,0.55,0.54]
        
        #############################
        #Non-Residential Parameters 
        #############################
        #(includes Trade, Office/Rescom, Light Industry, Heavy Industry, Education, Health & Comm, Serv & Util)
        #--> Commercial & Industrial Zones :: Employment Details
        self.createParameter("employment_mode", STRING, "")
        self.createParameter("ind_edist", DOUBLE, "")
        self.createParameter("com_edist", DOUBLE, "")
        self.createParameter("orc_edist", DOUBLE, "")
        self.createParameter("employment_total", DOUBLE, "")
        self.createParameter("ind_subd_min", DOUBLE, "")
        self.createParameter("ind_subd_max", DOUBLE, "")
        self.createParameter("com_subd_min", DOUBLE, "")
        self.createParameter("com_subd_max", DOUBLE, "")
        self.createParameter("nres_minfsetback", DOUBLE, "")
        self.createParameter("nres_maxfloors", DOUBLE, "")
        self.createParameter("nres_setback_auto", BOOL, "")
        self.createParameter("nres_nolimit_floors", BOOL, "")
        self.createParameter("maxplotratio_ind", DOUBLE, "")
        self.createParameter("maxplotratio_com", DOUBLE, "")
        self.createParameter("carpark_Wmin", DOUBLE, "")
        self.createParameter("carpark_Dmin", DOUBLE, "")
        self.createParameter("carpark_imp", DOUBLE, "")
        self.createParameter("carpark_ind", DOUBLE, "")
        self.createParameter("carpark_com", DOUBLE, "")
        self.createParameter("loadingbay_A", DOUBLE, "")
        self.createParameter("lscape_hsbalance", DOUBLE, "")
        self.createParameter("lscape_impdced", DOUBLE, "")
        self.employment_mode = "D"      #I = input, D = distribution, S = single
        self.ind_edist = 100                    #Employment Mode D: suggests the industrial employment distribution in employees/ha
        self.com_edist = 100                    #Employment Mode D: suggests the commercial employment distribution in employees/ha
        self.orc_edist = 400                    #Employment Mode D: suggests the office employment distribution
        self.employment_total = 200             #Employment Mode S: 
        self.ind_subd_min = 4
        self.ind_subd_max = 6
        self.com_subd_min = 2
        self.com_subd_max = 4
        self.nres_minfsetback = 2
        self.nres_maxfloors = 4
        self.nres_setback_auto = 0
        self.nres_nolimit_floors = 0
        self.maxplotratio_ind = 60
        self.maxplotratio_com = 50
        self.carpark_Wmin = 2.6
        self.carpark_Dmin = 4.6
        self.carpark_imp = 100
        self.carpark_ind = 1
        self.carpark_com = 2
        self.loadingbay_A = 27
        self.lscape_hsbalance = 1
        self.lscape_impdced = 10
        
        self.nonres_far = {}
        self.nonres_far["LI"] = 70
        self.nonres_far["HI"] = 150
        self.nonres_far["COM"] = 220 
        self.nonres_far["ORC"] = 110 
        
        #--> Civic Facilities
        self.createParameter("mun_explicit", BOOL, "")
        self.createParameter("edu_school", BOOL, "")
        self.createParameter("edu_uni", BOOL, "")
        self.createParameter("edu_lib", BOOL, "")
        self.createParameter("civ_hospital", BOOL, "")
        self.createParameter("civ_clinic", BOOL, "")
        self.createParameter("civ_police", BOOL, "")
        self.createParameter("civ_fire", BOOL, "")
        self.createParameter("civ_jail", BOOL, "")
        self.createParameter("civ_worship", BOOL, "")
        self.createParameter("civ_leisure", BOOL, "")
        self.createParameter("civ_museum", BOOL, "")
        self.createParameter("civ_zoo", BOOL, "")
        self.createParameter("civ_stadium", BOOL, "")
        self.createParameter("civ_racing", BOOL, "")
        self.createParameter("civ_cemetery", BOOL, "")
        self.mun_explicit = False
        self.edu_school = False
        self.edu_uni = False
        self.edu_lib = False
        self.civ_hospital = False
        self.civ_clinic = False
        self.civ_police = False
        self.civ_fire = False
        self.civ_jail = False
        self.civ_worship = False
        self.civ_leisure = False
        self.civ_museum = False
        self.civ_zoo = False
        self.civ_stadium = False
        self.civ_racing = False
        self.civ_cemetery = False

        ############################
        #Transport Parameters
        ############################
        #(includes Roads, Transport)
        #--> Residential Pedestrian
        self.createParameter("res_fpwmin", DOUBLE, "")
        self.createParameter("res_nswmin", DOUBLE, "")
        self.createParameter("res_fpwmax", DOUBLE, "")
        self.createParameter("res_nswmax", DOUBLE, "")
        self.createParameter("nres_fpwmin", DOUBLE, "")
        self.createParameter("nres_nswmin", DOUBLE, "")
        self.createParameter("nres_fpwmax", DOUBLE, "")
        self.createParameter("nres_nswmax", DOUBLE, "")
        self.createParameter("res_fpmed", BOOL, "")
        self.createParameter("res_nsmed", BOOL, "")
        self.createParameter("nres_fpmed", BOOL, "")
        self.createParameter("nres_nsmed", BOOL, "")
        self.createParameter("lane_wmin", DOUBLE, "")
        self.createParameter("lane_wmax", DOUBLE, "")
        self.createParameter("lane_crossfall", DOUBLE, "")
        self.createParameter("lane_wmed", BOOL, "")
        self.res_fpwmin = 1
        self.res_nswmin = 1
        self.res_fpwmax = 3
        self.res_nswmax = 3
        self.nres_fpwmin = 1
        self.nres_nswmin = 1
        self.nres_fpwmax = 3
        self.nres_nswmax = 3
        self.res_fpmed = False
        self.res_nsmed = False
        self.nres_fpmed = False
        self.nres_nsmed = False
        self.lane_wmin = 3
        self.lane_wmax = 5
        self.lane_crossfall = 3
        self.lane_wmed = False
        
        self.createParameter("hwy_wlanemin", DOUBLE, "")
        self.createParameter("hwy_wlanemax", DOUBLE, "")
        self.createParameter("hwy_wmedianmin", DOUBLE, "")
        self.createParameter("hwy_wmedianmax", DOUBLE, "")
        self.createParameter("hwy_wbufmin", DOUBLE, "")
        self.createParameter("hwy_wbufmax", DOUBLE, "")
        self.createParameter("hwy_crossfall", DOUBLE, "")
        self.createParameter("hwy_lanemed", BOOL, "")
        self.createParameter("hwy_medmed", BOOL, "")
        self.createParameter("hwy_bufmed", BOOL, "")
        self.createParameter("hwy_restrict", BOOL, "")
        self.createParameter("hwy_buffer", BOOL, "")
        self.hwy_wlanemin = 5
        self.hwy_wlanemax = 10
        self.hwy_wmedianmin = 4
        self.hwy_wmedianmax = 6
        self.hwy_wbufmin = 2
        self.hwy_wbufmax = 5
        self.hwy_crossfall = 3
        self.hwy_lanemed = 0
        self.hwy_medmed = 0
        self.hwy_bufmed = 0
        self.hwy_restrict = 0
        self.hwy_buffer = 1
        
        self.createParameter("considerTRFacilities", BOOL, "")
        self.createParameter("trans_airport", BOOL, "")
        self.createParameter("trans_seaport", BOOL, "")
        self.createParameter("trans_busdepot", BOOL, "")
        self.createParameter("trans_railterminal", BOOL, "")
        self.considerTRFacilities = 0
        self.trans_airport = 0
        self.trans_seaport = 0
        self.trans_busdepot = 0
        self.trans_railterminal = 0
        
        ############################
        #Open Space Parameters
        ############################
        #(includes Parks & Garden, Reserves & Floodways)
        #--> Parks, Squares & Gardens :: General
        self.createParameter("pg_greengrey_ratio", DOUBLE, "")
        self.createParameter("pgsq_distribution", STRING, "")
        self.createParameter("pg_unused_space", DOUBLE, "")
        self.createParameter("pg_restrict", BOOL, "")
        self.pg_greengrey_ratio = 0
        self.pgsq_distribution = "S"    #S = separate, C = combined
        self.pg_unused_space = 40       #% of space in park not used for anything else
        self.pg_restrict = 0        #Prohibit the use of park space 
        
        self.createParameter("ref_usable", BOOL, "")
        self.createParameter("ref_usable_percent", DOUBLE, "")
        self.createParameter("ref_limit_stormwater", BOOL, "")
        self.createParameter("svu_water", DOUBLE, "")
        self.createParameter("svu4supply", BOOL, "")
        self.createParameter("svu4waste", BOOL, "")
        self.createParameter("svu4storm", BOOL, "")
        self.createParameter("svu4supply_prop", DOUBLE, "")
        self.createParameter("svu4waste_prop", DOUBLE, "")
        self.createParameter("svu4storm_prop", DOUBLE, "")
        self.ref_usable = 1
        self.ref_usable_percent = 100
        self.ref_limit_stormwater = 0
        self.svu_water = 50
        self.svu4supply = 1
        self.svu4waste = 1
        self.svu4storm = 1
        self.svu4supply_prop = 30
        self.svu4waste_prop = 30
        self.svu4storm_prop = 40
        
        ############################
        #Others Parameters
        ############################
        #(includes Unclassified and Undeveloped)
        #--> Unclassified Land
        self.createParameter("unc_merge", BOOL, "")                     #DYNAMIND
        self.createParameter("unc_pgmerge", BOOL, "")                   #DYNAMIND
        self.createParameter("unc_pgmerge_w", DOUBLE, "")               #DYNAMIND
        self.createParameter("unc_refmerge", BOOL, "")                  #DYNAMIND
        self.createParameter("unc_refmerge_w", DOUBLE, "")              #DYNAMIND
        self.createParameter("unc_rdmerge", BOOL, "")                   #DYNAMIND
        self.createParameter("unc_rdmerge_w", DOUBLE, "")               #DYNAMIND
        self.createParameter("unc_custom", BOOL, "")                    #DYNAMIND
        self.createParameter("unc_customthresh", DOUBLE, "")            #DYNAMIND
        self.createParameter("unc_customimp", DOUBLE, "")               #DYNAMIND
        self.createParameter("unc_landirrigate", BOOL, "")              #DYNAMIND
        self.unc_merge = False  #Merge unclassified land?
        self.unc_pgmerge = False
        self.unc_pgmerge_w = 0
        self.unc_refmerge = False
        self.unc_refmerge_w = 0
        self.unc_rdmerge = False
        self.unc_rdmerge_w = 0
        self.unc_custom = False
        self.unc_customthresh = 50
        self.unc_customimp = 50
        self.unc_landirrigate = False
        
        #--> Undeveloped Land
        self.createParameter("und_state", STRING, "")                   #DYNAMIND
        self.createParameter("und_type_manual", STRING, "")             #DYNAMIND
        self.createParameter("und_allowdev", BOOL, "")                  #DYNAMIND
        self.und_state = "M"    #M = manual, A = Auto
        self.und_type_manual = "GF"     #GF = Greenfield, BF = Brownfield, AG = Agriculture
        self.und_allowdev = False       #Allow developent for large water infrastructure?
        
        #-->Advanced Parameters
        self.und_BFtoGF = 50     #Threshold distance % between Brownfield and Greenfield
        self.und_BFtoAG = 90    #Threshold distance % between Brownfield and Agriculture
        self.undtypeDefault = "BF"
        self.considerGF = True     #Even consider Greenfield?
        self.considerAG = True     #Even consider Agriculture areas in model?
        self.CBD_MAD_dist = 10.0        #km - approximate distance between main CBD and major activity districts
        
        #------------------------------------------
        #END OF INPUT PARAMETER LIST

        #VIEWS-------------------------------------
	self.mapattributes = View("GlobalMapAttributes", COMPONENT,READ)
	self.mapattributes.getAttribute("NumBlocks")
	self.mapattributes.getAttribute("BlockSize")
	self.mapattributes.getAttribute("WidthBlocks")
	self.mapattributes.getAttribute("HeightBlocks")
	self.mapattributes.getAttribute("InputReso")
	self.mapattributes.addAttribute("ParkProhibit")
        self.mapattributes.addAttribute("RefLimit")
        self.mapattributes.addAttribute("UndevAllow")
        self.mapattributes.addAttribute("HwyMedLimit")
	
        self.blocks = View("Block", FACE, WRITE)
        self.blocks.getAttribute("BlockID")
        self.blocks.modifyAttribute("Employ")
        self.blocks.addAttribute("MiscAtot")
        self.blocks.addAttribute("MiscAimp")
        self.blocks.addAttribute("UndType")
        self.blocks.addAttribute("UND_av")
        self.blocks.addAttribute("OpenSpace")
        self.blocks.addAttribute("AGardens")
        self.blocks.addAttribute("ASquare")
        self.blocks.addAttribute("PG_av")
        self.blocks.addAttribute("REF_av")
        self.blocks.addAttribute("ANonW_Utils")
        self.blocks.addAttribute("SVU_avWS")
        self.blocks.addAttribute("SVU_avWW")
        self.blocks.addAttribute("SVU_avSW")
        self.blocks.addAttribute("SVU_avOTH")
        self.blocks.addAttribute("RoadTIA")
        self.blocks.addAttribute("ParkBuffer")
        self.blocks.addAttribute("RD_av")
        self.blocks.addAttribute("RDMedW")
        self.blocks.addAttribute("DemPublicI")
        
        #BlockDYNAMICS Views
        self.prevBlocks = View("PreviousBlocks", COMPONENT, READ)
        self.prevMapAttr = View("MasterMapAttributes", COMPONENT, READ)
        
        #DEFINE DATA STREAM:
        datastream = []
        datastream.append(self.blocks)
        datastream.append(self.mapattributes)
        datastream.append(self.prevBlocks)
        datastream.append(self.prevMapAttr)
        self.addData("City", datastream)
        self.BLOCKIDtoUUID = {}         #DYNAMIND
        self.prevBLOCKIDtoUUID = {}     #DYNAMIND
        
    def run(self):
	#random.seed()   #Random seed has already been placed in delinblocks
	city = self.getData("City")             #DYNAMIND - obtain the City's datastream
        self.initBLOCKIDtoUUID(city)            #DYNAMIND - initialize the dictionary that tracks Block ID and UUID
        
        strvec = city.getUUIDsOfComponentsInView(self.mapattributes)    #DYNAMIND - get map attributes
        map_attr = city.getComponent(strvec[0]) #Get Map Attributes     #DYNAMIND - save attributes to a variable
        strvec = city.getUUIDsOfComponentsInView(self.prevMapAttr)
        prev_map_attr = city.getComponent(strvec[0])
        
        #DYNAMIND ------------------------------------>
        #Get all the relevant information
        blocks_num = map_attr.getAttribute("NumBlocks").getDouble()     #number of blocks to loop through
        block_size = map_attr.getAttribute("BlockSize").getDouble()     #size of blocks
        Atblock = block_size * block_size                               #Total area of one block
        map_w = map_attr.getAttribute("WidthBlocks").getDouble()        #num of blocks Wide
        map_h = map_attr.getAttribute("HeightBlocks").getDouble()       #num of blocks Tall
        input_res = map_attr.getAttribute("InputReso").getDouble()      #Resolution of input area
        #----------------- DYNAMIND ------------------
        
        print "Begin Urban Planning!"
        
        #Make Adjustments to sampling ranges for specific parameters
        #If parameter range median boxes were checked, adjust these parameters to reflect that
        hwy_wlane = self.adjustSampleRange(self.hwy_wlanemin, self.hwy_wlanemax, self.hwy_lanemed)
        hwy_med = self.adjustSampleRange(self.hwy_wmedianmin, self.hwy_wmedianmax, self.hwy_medmed)
        hwy_buf = self.adjustSampleRange(self.hwy_wbufmin, self.hwy_wbufmax, self.hwy_bufmed)
        nres_fpw = self.adjustSampleRange(self.nres_fpwmin, self.nres_fpwmax, self.nres_fpmed)
        nres_nsw = self.adjustSampleRange(self.nres_nswmin, self.nres_nswmax, self.nres_nsmed)
        lane_w = self.adjustSampleRange(self.lane_wmin, self.lane_wmax, self.lane_wmed)
        
        if int(prev_map_attr.getAttribute("Impl_cycle").getDouble()) == 0:    #Is this implementation cycle?
            self.initPrevBLOCKIDtoUUID(city)        #DYNAMIND - initialize the dictionary that tracks Previous Block IDs and UUID
        
        #LOOP ACROSS BLOCKS
        for i in range(int(blocks_num)):
            #Reset tally variables
            blk_tia = 0         #Total Block Impervious Area
            blk_roof = 0        #Total Block Roof Area
            blk_eia = 0         #Total Block effective impervious area
            blk_avspace = 0     #Total available space for decentralised water infrastructure
            
            currentID = i+1             #GRAB BLOCK INFORMATION
            currentAttList = self.getBlockUUID(currentID, city)         #DYNAMIND - assign block information to variable currentAttList
            
            print "Now Developing BlockID", currentID
            
            #Skip Condition 1: Block is not active
            if currentAttList.getAttribute("Status").getDouble() == 0:
                #print "BlockID"+str(currentID)+" is not active, moving to next ID"
                currentAttList.addAttribute("Blk_TIA", -9999)
                currentAttList.addAttribute("Blk_EIF", -9999)
                currentAttList.addAttribute("Blk_TIF", -9999)
                currentAttList.addAttribute("Blk_RoofsA", -9999)
                continue
            
            #Determine whether to Update Block at all using Dynamics Parameters
            if int(prev_map_attr.getAttribute("Impl_cycle").getDouble()) == 0:    #Is this implementation cycle?
                prevAttList = self.getPrevBlockUUID(currentID, city)
                if self.keepBlockDataCheck(currentAttList, prevAttList):        #NO = check block for update
                    print "Changes in Block are below threshold levels, transferring data"
                    self.transferBlockAttributes(currentAttList, prevAttList)
                    continue        #If Block does not need to be developed, skip it
                
            #Get Active Area
            activity = currentAttList.getAttribute("Active").getDouble()
            Aactive = activity*Atblock
            #print "Active Area for Block: ", Aactive
            
            cumu_irrigatearea = 0       #initialize public land irrigation value
            
            #------------UNCLASSIFIED AREA--------------------------------------
            #Allocate unclassified area to the rest of the block's LUC distribution
            A_unc = currentAttList.getAttribute("pLU_NA").getDouble() * Aactive
            A_park = currentAttList.getAttribute("pLU_PG").getDouble() * Aactive
            A_ref = currentAttList.getAttribute("pLU_REF").getDouble() * Aactive
            A_rd = currentAttList.getAttribute("pLU_RD").getDouble() * Aactive
            
            #print "Unclassifiable Area: ", A_unc
            #print "Park, Ref and Rd Areas: ", A_park, A_ref, A_rd
            if A_unc != 0:      #If the area is not zero
                unc_area_subdivide = self.planUnclassified(A_unc, A_park, A_ref, A_rd, Atblock)
                undevextra, pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra = unc_area_subdivide
            else:
                undevextra, pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra = 0,0,0,0,0,0,0
            
            #print "End of Unclassified Area, writing attributes"
            #print "Undevextra", undevextra
            #print "Merged Area", pgextra, refextra, rdextra
            #print "Cutom Area", otherarea, otherimp
            
            otherperv = otherarea - otherimp            #Pervious Unclassified Area
            
            currentAttList.addAttribute("MiscAtot", otherarea)
            currentAttList.addAttribute("MiscAimp", otherimp)
            
            #Add to cumulative area variables
            blk_tia += otherimp
            blk_eia += otherimp
            blk_roof += 0
            blk_avspace += 0
            
            #-----------UNDEVELOPED AREA----------------------------------------
            #Determine the Undeveloped area's state
            considerCBD = map_attr.getAttribute("considerCBD").getDouble()
            A_und = currentAttList.getAttribute("pLU_UND").getDouble() * Aactive + undevextra
            #print "Undeveloped Area: ", A_und
            if A_und != 0:
                type = self.determineUndevType(currentAttList, considerCBD)
            else:
                type = str("NA")
            
            #print "Undev Area Type: ",type
            currentAttList.addAttribute("UndType", type)
            currentAttList.addAttribute("UND_av", float(A_und*self.und_allowdev))
            
            #Add to cumulative area variables
            blk_tia += 0
            blk_eia += 0
            blk_roof += 0
            blk_avspace += float(A_und*self.und_allowdev)
            
            #-----------OPEN SPACES---------------------------------------------
            A_park += pgextra 
            A_ref += refextra
            A_svu = currentAttList.getAttribute("pLU_SVU").getDouble() * Aactive
            #print "Total Open Space Area: ", A_park + A_ref
            #print "Total area for Services & Utilities: ", A_svu
            
            #---Parks & Gardens
            parkratio = float((self.pg_greengrey_ratio + 10)/20)  #Ratio of green/grey spaces
            sqratio = 1-parkratio
            sqarea = A_park * sqratio   #CUMULATIVE IMPERVIOUSNESS
            parkarea = A_park * parkratio
            avail_space = parkarea * self.pg_unused_space/100
            
            currentAttList.addAttribute("OpenSpace", A_park + A_ref)
            currentAttList.addAttribute("AGardens", parkarea)
            currentAttList.addAttribute("ASquare", sqarea)
            currentAttList.addAttribute("PG_av", avail_space)
            
            #Add to cumulative area variables
            blk_tia += sqarea
            blk_eia += sqarea
            blk_roof += 0
            blk_avspace += avail_space
            
            #---Reserves & Floodways
            avail_ref = A_ref * self.ref_usable_percent/100
            currentAttList.addAttribute("REF_av", avail_ref)
            
            #Add to cumulative area variables
            blk_tia += 0
            blk_eia += 0
            blk_roof += 0
            blk_avspace += avail_ref
            
            #---Services & Utilities
            Asvu_water = float(A_svu * self.svu_water/100)
            Asvu_others = A_svu - Asvu_water
            
                #Adjust percentages
            svu_props = [self.svu4supply_prop*self.svu4supply, 
                         self.svu4waste_prop*self.svu4waste, 
                         self.svu4storm_prop*self.svu4storm]    #take into account check boxes
            
            if sum(svu_props) > 100:            #we want to allow for less than 100% so that
                sumfactor = sum(svu_props)      #SVU has leftover area that can be used for anything
            else:
                sumfactor = 100
                         
            for i in range(len(svu_props)):                     #"Normalize" proportions
                svu_props[i] = svu_props[i]/sumfactor
                
            Asvu_WS = float(Asvu_water*self.svu4supply*svu_props[0])
            Asvu_WW = float(Asvu_water*self.svu4waste*svu_props[1])
            Asvu_SW = float(Asvu_water*self.svu4storm*svu_props[2])
            Asvu_OTH = Asvu_water - Asvu_WS - Asvu_WW - Asvu_SW         #non-accounted for water area, use for anything
            
            currentAttList.addAttribute("ANonW_Utils", Asvu_others)
            currentAttList.addAttribute("SVU_avWS", Asvu_WS)
            currentAttList.addAttribute("SVU_avWW", Asvu_WW)
            currentAttList.addAttribute("SVU_avSW", Asvu_SW)
            currentAttList.addAttribute("SVU_avOTH", Asvu_OTH)
            
            #Add to cumulative area variables
            blk_tia += 0
            blk_eia += 0
            blk_roof += 0
            blk_avspace += (Asvu_WS + Asvu_WW + Asvu_SW + Asvu_OTH)
            
            #-----------ROADS---------------------------------------------------
            A_rd =+ rdextra                              #This part only plans out the Major Arterials & Hwys
            #print "Total Road Area: ", A_rd
            
            #Draw stochastic values:
            laneW = random.randint(hwy_wlane[0], hwy_wlane[1])
            medW = random.randint(hwy_med[0], hwy_med[1])
            buffW = random.randint(hwy_buf[0], hwy_buf[1])
            
            if (A_park+A_ref) >= 0.5*A_rd:               #if total open space is greater than half the road area, use it as buffer
                rd_imp = float((2*laneW)/(2*laneW + medW))
                park_buffer = 1
                av_spRD = float(medW/(2*laneW+medW)) * A_rd
            else:                                       #consider road's own buffer
                rd_imp = float((2*laneW)/(2*laneW + medW + 2*buffW))
                park_buffer = 0
                av_spRD = float(medW/(2*laneW+medW+buffW*2)) * A_rd
            
            Aimp_rd = A_rd*rd_imp
            
            currentAttList.addAttribute("RoadTIA", Aimp_rd)
            currentAttList.addAttribute("ParkBuffer", park_buffer)
            currentAttList.addAttribute("RD_av", av_spRD)
            currentAttList.addAttribute("RDMedW", medW)
            
            #Add to cumulative area variables
            blk_tia += Aimp_rd
            blk_eia += Aimp_rd * 0.9
            blk_roof += 0
            blk_avspace += av_spRD
             
            #------------RESIDENTIAL AREA---------------------------------------
            ResPop = currentAttList.getAttribute("Pop").getDouble()
            A_res = currentAttList.getAttribute("pLU_RES").getDouble() * Aactive
            minHouse = self.person_space * self.occup_avg * 4
            #print "Residential Area: ",A_res
            if A_res >= minHouse and ResPop > self.occup_flat_avg:
                resdict = self.buildResidential(currentAttList, map_attr, A_res)
                
                #Transfer res_dict attributes to output vector
                currentAttList.addAttribute("HasRes", 1)
                
                if resdict["TypeHouse"] == 1:
                    currentAttList.addAttribute("HasHouses", 1)
                    currentAttList.addAttribute("HouseOccup", resdict["HouseOccup"])
                    currentAttList.addAttribute("ResParcels", resdict["ResParcels"])
                    currentAttList.addAttribute("ResFrontT", resdict["TotalFrontage"])
                    currentAttList.addAttribute("avSt_RES", resdict["avSt_RES"])
                    currentAttList.addAttribute("WResNstrip", resdict["WResNstrip"])
                    currentAttList.addAttribute("ResAllots", resdict["ResAllots"])
                    currentAttList.addAttribute("ResDWpLot", resdict["ResDWpLot"])
                    currentAttList.addAttribute("ResHouses", resdict["ResHouses"])
                    currentAttList.addAttribute("ResLotArea", resdict["ResLotArea"])
                    currentAttList.addAttribute("ResRoof", resdict["ResRoof"])
                    currentAttList.addAttribute("avLt_RES", resdict["avLt_RES"])
                    currentAttList.addAttribute("ResHFloors", resdict["ResHFloors"])
                    currentAttList.addAttribute("ResLotTIA", resdict["ResLotTIA"])
                    currentAttList.addAttribute("ResLotEIA", resdict["ResLotEIA"])
                    currentAttList.addAttribute("ResGarden", resdict["ResGarden"])
                    currentAttList.addAttribute("ResRoofCon", resdict["ResRoofCon"])
                    
                    frontageTIF = 1 - (resdict["avSt_RES"] / resdict["TotalFrontage"])
                    
                    #Add to cumulative area variables
                    blk_tia += (resdict["ResLotTIA"] * resdict["ResAllots"]) + frontageTIF * resdict["TotalFrontage"]
                    blk_eia += (resdict["ResLotEIA"] * resdict["ResAllots"]) + 0.9 * frontageTIF * resdict["TotalFrontage"]
                    blk_roof += (resdict["ResRoof"] * resdict["ResAllots"])
                    blk_avspace += (resdict["avLt_RES"] * resdict["ResAllots"]) + resdict["avSt_RES"]
                    
                if resdict["TypeApt"] == 1:
                    currentAttList.addAttribute("HasFlats", 1)
                    currentAttList.addAttribute("avSt_RES", 0)
                    currentAttList.addAttribute("HDRFlats", resdict["HDRFlats"])
                    currentAttList.addAttribute("HDRRoofA", resdict["HDRRoofA"])
                    currentAttList.addAttribute("HDROccup", resdict["HDROccup"])
                    currentAttList.addAttribute("HDR_TIA", resdict["HDR_TIA"])
                    currentAttList.addAttribute("HDR_EIA", resdict["HDR_EIA"])
                    currentAttList.addAttribute("HDRFloors", resdict["HDRFloors"])
                    currentAttList.addAttribute("av_HDRes", resdict["av_HDRes"])
                    currentAttList.addAttribute("HDRGarden", resdict["HDRGarden"])
                    currentAttList.addAttribute("HDRCarPark", resdict["HDRCarPark"])
                    #...
                    #Add to cumulative area variables
                    blk_tia += resdict["HDR_TIA"]
                    blk_eia += resdict["HDR_EIA"]
                    blk_roof += resdict["HDRRoofA"]
                    blk_avspace += resdict["av_HDRes"]
            else:
                currentAttList.addAttribute("HasRes", 0)
                currentAttList.addAttribute("avSt_RES", A_res)  #becomes street-scape area available
                
                #Add to cumulative area variables
                blk_tia += 0
                blk_eia += 0
                blk_roof += 0
                blk_avspace += A_res
                
            #-----------NON-RESIDENTIAL (HOTSPOTS) -----------------------------
            A_civ = currentAttList.getAttribute("pLU_CIV").getDouble() * Aactive
            A_tr = currentAttList.getAttribute("pLU_TR").getDouble() * Aactive
            extraCom = 0        #Additional commercial land area (if facilities are not to be considered)
            extraInd = 0        #Additional inustrial land area (and if specific facilities are not selected)
            
            #MERGE INTO OTHER AREAS IF NOT CONSIDERED EXPLICITLY
            
            #print "Total Civic Area: ", A_civ
            #print "Total Transport Area: ", A_tr
            
            #Decide what to do with the information!
            if A_civ != 0:
                if self.mun_explicit == 0:
                    extraCom += A_civ               #Civic Area becomes extra commercial area
                else:
                    hotspotsCIV, remainA = self.identifyHotspots(A_civ, currentAttList, map_attr) #get info
                    extraCom += remainA
                    #Write attributes from hotspotsCIV
                    
                    #Add to cumulative area variables - MODIFY WHEN IMPLEMENTING MUNICIPAL FACILITIES!!!
                    blk_tia += 0
                    blk_eia += 0
                    blk_roof += 0
                    blk_avspace += 0
                    
            if A_tr != 0:
                if self.considerTRFacilities == 0:
                    extraInd += A_tr                #Transport Facilities become extra Industrial area
                else:
                    hotspotsTR, remainA = self.identifyHotspots(A_tr, currentAttList, map_attr)  #get info
                    extraInd += remainA
                    #Write attributes from hotspotsTR

                    #Add to cumulative area variables - MODIFY WHEN IMPLEMENTING MUNICIPAL FACILITIES!!!
                    blk_tia += 0
                    blk_eia += 0
                    blk_roof += 0
                    blk_avspace += 0
            
            #-----------NON-RESIDENTIAL (PLANNING RULES) -----------------------
            A_li = currentAttList.getAttribute("pLU_LI").getDouble() * Aactive + extraInd + A_svu
            A_hi = currentAttList.getAttribute("pLU_HI").getDouble() * Aactive
            A_com = currentAttList.getAttribute("pLU_COM").getDouble() * Aactive + extraCom
            A_orc = currentAttList.getAttribute("pLU_ORC").getDouble() * Aactive 
            
            #Sample frontage information and create vector to store this
            Wfp = random.randint(nres_fpw[0], nres_fpw[1])
            Wns = random.randint(nres_nsw[0], nres_nsw[1])
            Wrd = random.randint(lane_w[0], lane_w[1])
            frontage = [Wfp, Wns, Wrd]
            
            #print "Total Non-res Area to be constructed with Planning Rules: ", A_li + A_hi + A_com + A_orc
            totalblockemployed = 0
            
            if A_li != 0:
                indLI_dict = self.buildNonResArea(currentAttList, map_attr, A_li, "LI", frontage)
                if indLI_dict["Has_LI"] == 1:
                    currentAttList.addAttribute("Has_LI", 1)
                    #Transfer attributes from indLI dictionary
                    currentAttList.addAttribute("LIjobs", indLI_dict["TotalBlockEmployed"])
                    currentAttList.addAttribute("LIestates", indLI_dict["Estates"])
                    currentAttList.addAttribute("avSt_LI", indLI_dict["av_St"])
                    currentAttList.addAttribute("LIAfront", indLI_dict["Afrontage"])
                    currentAttList.addAttribute("LIAfrEIA", indLI_dict["FrontageEIA"])
                    currentAttList.addAttribute("LIAestate", indLI_dict["Aestate"])
                    currentAttList.addAttribute("LIAeBldg", indLI_dict["EstateBuildingArea"])
                    currentAttList.addAttribute("LIFloors", indLI_dict["Floors"])
                    currentAttList.addAttribute("LIAeLoad", indLI_dict["Aloadingbay"])
                    currentAttList.addAttribute("LIAeCPark", indLI_dict["Outdoorcarpark"])     #TOTAL OUTDOOR VISIBLE CARPARK
                    currentAttList.addAttribute("avLt_LI", indLI_dict["EstateGreenArea"])
                    currentAttList.addAttribute("LIAeLgrey", indLI_dict["Alandscape"]-indLI_dict["EstateGreenArea"])
                    currentAttList.addAttribute("LIAeEIA", indLI_dict["EstateEffectiveImpervious"])
                    currentAttList.addAttribute("LIAeTIA", indLI_dict["EstateImperviousArea"])
                    
                    #Add to cumulative area variables
                    totalblockemployed += indLI_dict["TotalBlockEmployed"]
                    blk_tia += indLI_dict["Estates"] *(indLI_dict["EstateImperviousArea"] + indLI_dict["FrontageEIA"])
                    blk_eia += indLI_dict["Estates"] *(indLI_dict["EstateEffectiveImpervious"] + 0.9*indLI_dict["FrontageEIA"])
                    blk_roof += indLI_dict["Estates"] * indLI_dict["EstateBuildingArea"]
                    blk_avspace += indLI_dict["Estates"] * (indLI_dict["EstateGreenArea"] + indLI_dict["av_St"])
                    
            if A_hi != 0:
                indHI_dict = self.buildNonResArea(currentAttList, map_attr, A_hi, "HI", frontage)
                if indHI_dict["Has_HI"] == 1:
                    currentAttList.addAttribute("Has_HI", 1)
                    #Transfer attributes from indHI dictionary
                    currentAttList.addAttribute("HIjobs", indHI_dict["TotalBlockEmployed"])
                    currentAttList.addAttribute("HIestates", indHI_dict["Estates"])
                    currentAttList.addAttribute("avSt_HI", indLI_dict["av_St"])
                    currentAttList.addAttribute("HIAfront", indLI_dict["Afrontage"])
                    currentAttList.addAttribute("HIAfrEIA", indLI_dict["FrontageEIA"])
                    currentAttList.addAttribute("HIAestate", indHI_dict["Aestate"])
                    currentAttList.addAttribute("HIAeBldg", indHI_dict["EstateBuildingArea"])
                    currentAttList.addAttribute("HIFloors", indHI_dict["Floors"])
                    currentAttList.addAttribute("HIAeLoad", indHI_dict["Aloadingbay"])
                    currentAttList.addAttribute("HIAeCPark", indHI_dict["Outdoorcarpark"])     #TOTAL OUTDOOR VISIBLE CARPARK
                    currentAttList.addAttribute("avLt_HI", indHI_dict["EstateGreenArea"])
                    currentAttList.addAttribute("HIAeLgrey", indHI_dict["Alandscape"]-indHI_dict["EstateGreenArea"])
                    currentAttList.addAttribute("HIAeEIA", indHI_dict["EstateEffectiveImpervious"])
                    currentAttList.addAttribute("HIAeTIA", indHI_dict["EstateImperviousArea"])
            
                    #Add to cumulative area variables
                    totalblockemployed += indHI_dict["TotalBlockEmployed"]
                    blk_tia += indHI_dict["Estates"] *(indHI_dict["EstateImperviousArea"] + indHI_dict["FrontageEIA"])
                    blk_eia += indHI_dict["Estates"] *(indHI_dict["EstateEffectiveImpervious"] + 0.9*indHI_dict["FrontageEIA"])
                    blk_roof += indHI_dict["Estates"] * indHI_dict["EstateBuildingArea"]
                    blk_avspace += indHI_dict["Estates"] * (indHI_dict["EstateGreenArea"] + indHI_dict["av_St"])
            
            if A_com != 0:
                com_dict = self.buildNonResArea(currentAttList, map_attr, A_com, "COM", frontage)
                if com_dict["Has_COM"] == 1:
                    currentAttList.addAttribute("Has_Com", 1)
                    #Transfer attributes from COM dictionary
                    currentAttList.addAttribute("COMjobs", com_dict["TotalBlockEmployed"])
                    currentAttList.addAttribute("COMestates", com_dict["Estates"])
                    currentAttList.addAttribute("avSt_COM", com_dict["av_St"])
                    currentAttList.addAttribute("COMAfront", com_dict["Afrontage"])
                    currentAttList.addAttribute("COMAfrEIA", com_dict["FrontageEIA"])
                    currentAttList.addAttribute("COMAestate", com_dict["Aestate"])
                    currentAttList.addAttribute("COMAeBldg", com_dict["EstateBuildingArea"])
                    currentAttList.addAttribute("COMFloors", com_dict["Floors"])
                    currentAttList.addAttribute("COMAeLoad", com_dict["Aloadingbay"])
                    currentAttList.addAttribute("COMAeCPark", com_dict["Outdoorcarpark"])     #TOTAL OUTDOOR VISIBLE CARPARK
                    currentAttList.addAttribute("avLt_COM", com_dict["EstateGreenArea"])
                    currentAttList.addAttribute("COMAeLgrey", com_dict["Alandscape"]-com_dict["EstateGreenArea"])
                    currentAttList.addAttribute("COMAeEIA", com_dict["EstateEffectiveImpervious"])
                    currentAttList.addAttribute("COMAeTIA", com_dict["EstateImperviousArea"])
                    
                    #Add to cumulative area variables
                    totalblockemployed += com_dict["TotalBlockEmployed"]
                    blk_tia += com_dict["Estates"] *(com_dict["EstateImperviousArea"] + com_dict["FrontageEIA"])
                    blk_eia += com_dict["Estates"] *(com_dict["EstateEffectiveImpervious"] + 0.9*com_dict["FrontageEIA"])
                    blk_roof += com_dict["Estates"] * com_dict["EstateBuildingArea"]
                    blk_avspace += com_dict["Estates"] * (com_dict["EstateGreenArea"] + com_dict["av_St"])
                    
            if A_orc != 0:
                orc_dict = self.buildNonResArea(currentAttList, map_attr, A_orc, "ORC", frontage)
                if orc_dict["Has_ORC"] == 1:
                    currentAttList.addAttribute("Has_ORC", 1)
                    #Transfer attributes from Offices dictionary
                    currentAttList.addAttribute("ORCjobs", orc_dict["TotalBlockEmployed"])
                    currentAttList.addAttribute("ORCestates", orc_dict["Estates"])
                    currentAttList.addAttribute("avSt_ORC", orc_dict["av_St"])
                    currentAttList.addAttribute("ORCAfront", orc_dict["Afrontage"])
                    currentAttList.addAttribute("ORCAfrEIA", orc_dict["FrontageEIA"])
                    currentAttList.addAttribute("ORCAestate", orc_dict["Aestate"])
                    currentAttList.addAttribute("ORCAeBldg", orc_dict["EstateBuildingArea"])
                    currentAttList.addAttribute("ORCFloors", orc_dict["Floors"])
                    currentAttList.addAttribute("ORCAeLoad", orc_dict["Aloadingbay"])
                    currentAttList.addAttribute("ORCAeCPark", orc_dict["Outdoorcarpark"])     #TOTAL OUTDOOR VISIBLE CARPARK
                    currentAttList.addAttribute("avLt_ORC", orc_dict["EstateGreenArea"])
                    currentAttList.addAttribute("ORCAeLgrey", orc_dict["Alandscape"]-orc_dict["EstateGreenArea"])
                    currentAttList.addAttribute("ORCAeEIA", orc_dict["EstateEffectiveImpervious"])
                    currentAttList.addAttribute("ORCAeTIA", orc_dict["EstateImperviousArea"])
                    
                    #Add to cumulative area variables
                    totalblockemployed += orc_dict["TotalBlockEmployed"]
                    blk_tia += orc_dict["Estates"] *(orc_dict["EstateImperviousArea"] + orc_dict["FrontageEIA"])
                    blk_eia += orc_dict["Estates"] *(orc_dict["EstateEffectiveImpervious"] + 0.9*orc_dict["FrontageEIA"])
                    blk_roof += orc_dict["Estates"] * orc_dict["EstateBuildingArea"]
                    blk_avspace += orc_dict["Estates"] * (orc_dict["EstateGreenArea"] + orc_dict["av_St"])
                    
            #TALLY UP TOTAL BLOCK DETAILS
            currentAttList.changeAttribute("Employ", totalblockemployed)
            currentAttList.addAttribute("Blk_TIA", blk_tia)
            currentAttList.addAttribute("Blk_EIA", blk_eia)
            
            blk_eif = blk_eia / Aactive
            currentAttList.addAttribute("Blk_EIF", blk_eif)
            
            blk_tif = blk_tia / Aactive
            currentAttList.addAttribute("Blk_TIF", blk_tif)
            
            currentAttList.addAttribute("Blk_RoofsA", blk_roof)

            #END OF BLOCK LOOP
        
        #Add new attributes to Map Attributes for use later
        map_attr.addAttribute("ParkProhibit", self.pg_restrict)                 #Prohibit use of park space for systems
        map_attr.addAttribute("RefLimit", self.ref_limit_stormwater)            #Limit Reserves and Floodways to SW Management
        map_attr.addAttribute("UndevAllow", self.und_allowdev)                  #Allow developing water infrastructure in undev areas
        map_attr.addAttribute("HwyMedLimit", self.hwy_restrict)                 #Restrict tech placement along Highway medians
        
        print "End of Module"
    
    ########################################################################
    ### URBPLANBB SUB-FUNCTIONS                                          ###
    ########################################################################
    def keepBlockDataCheck(self, currentAttList, prevAttList):
        """Performs the dynamic checks on the current Block to see if its previous
        planning data can be transferred."""
        if self.noredev == 1:
            return True
        
        decisionmatrix = [] #Multiple decisions, in order to redevelop, only one needs to be True
        
        if self.lucredev == 1:
            lucsum = 0
            for i in ["pLU_CIV", "pLU_COM", "pLU_HI", "pLU_LI", "pLU_NA", "pLU_ORC",
                      "pLU_PG", "pLU_RD", "pLU_REF", "pLU_RES", "pLU_SVU", "pLU_TR",
                      "pLU_UND"]:
                lucsum += abs(currentAttList.getAttribute(i).getDouble() - \
                              prevAttList.getAttribute(i).getDouble())
            if lucsum > self.lucredev_thresh/100:
                decisionmatrix.append(1)
            else:
                decisionmatrix.append(0)
            
        if self.popredev == 1:
            popnow = currentAttList.getAttribute("Pop").getDouble()
            popprev = prevAttList.getAttribute("Pop").getDouble()
            popdiff = abs(popnow - popprev)/(popprev)
            if popdiff > self.popredev_thresh/100:
                decisionmatrix.append(1)
            else:
                decisionmatrix.append(0)
        
        if sum(decisionmatrix) > 0:
            return False #If even one factor says 'redev'! return False
        else:
            return True #otherwise return True = you can keep the existing data
        
        return False    #Otherwise just redevelop block by default if no option is ticked
    
    def adjustSampleRange(self, min, max, usemedian):
        """Returns a min/max sample range for the input variables. Returns the same
        numbers if the user has specified to use the median.
            Inputs:
                - Min and Max values specifying range
                - Boolean of whether to use the median instead
        """
        if usemedian == True:
            med = (min + max)/2     #if using median, 
            return [med, med]
        else:
            return [min, max]
    
    def planUnclassified(self, A_unc, A_park, A_ref, A_rd, Atblock):
        """Planning Algorithm for Unclassified Areas within the Block
        which performs three possible options:
            1) Merges unclassified land with existing other LUCs: Parks, Reserves, Roads
            2) Treats Unclassified land as a special area with custom surface cover properties
            3) Merges unclassified land with undeveloped land (default action if none of above options ticked)
        """
        
        #Check if exceedence of threshold
        if self.unc_custom and A_unc >= (Atblock*self.unc_customthresh/100):  #Case 1: Treat land as its own
            unc_Aimp = A_unc * self.unc_customimp/100   #Surface cover
            unc_Aperv = A_unc - unc_Aimp
            if self.unc_landirrigate:   #determine if land needs to be irrigated
                irrigateextra = unc_Aperv  #Add area to public irrigation
            
            otherarea = A_unc
            otherimp = unc_Aimp
            undevextra, pgextra, refextra, rdextra = 0,0,0,0
        elif self.unc_merge and (A_park + A_ref + A_rd) > 0:            #Case 2: Merge area with other LUCs
            weights = [self.unc_pgmerge * self.unc_pgmerge_w * bool(A_park > 0),
                       self.unc_refmerge * self.unc_refmerge_w * bool(A_ref > 0),
                       self.unc_rdmerge * self.unc_rdmerge_w * bool(A_rd > 0)]
            finaldiv = []
            for i in weights:
                #Tally up division of areas
                finaldiv.append(A_unc * i/sum(weights))
            pgextra = finaldiv[0]
            refextra = finaldiv[1]
            rdextra = finaldiv[2]                       
            undevextra, otherarea, otherimp, irrigateextra = 0, 0, 0, 0
        else:                                                           #Case 3: Neither option was checked
            undevextra = A_unc
            pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra = 0,0,0,0,0,0
            
        return [undevextra, pgextra, refextra, rdextra, otherarea, otherimp, irrigateextra]
    
    
    def determineUndevType(self, currentAttList, considerCBD):
        """Determines the type of undeveloped land in the current block passed to
        the function. This is dependent on the city archetype and the block's location
        within the city"""
        
        if self.und_state == "M":
            return self.und_type_manual
        elif considerCBD == 0:
            return self.undtypeDefault
        else:
            distCBD = currentAttList.getAttribute("CBDdist").getDouble()/1000   #convert to km
            #print "distance from CBD: ", distCBD
            if self.cityarchetype == "MC":       #Monocentric City Case
                BFdist = float(self.und_BFtoGF)/100 * float(self.citysprawl)  #from 0 to BFdist --> BF
                GFdist = float(self.und_BFtoAG)/100 * float(self.citysprawl)  #from BFdist to GFdist --> GF
                                                                #>GFdist --> AG
            else:       #Polycentric City Case
                MAD_sprawl = self.citysprawl - self.CBD_MAD_dist
                BFdist = self.CBD_MAD_dist + MAD_sprawl*self.und_BFtoGF/100
                GFdist = self.CBD_MAD_dist + MAD_sprawl*self.und_BFtoAG/100
            #print "BFdist, GFdist", BFdist, GFdist
            if distCBD <= BFdist:       #Brownfield
                undtype = "BF"
            elif distCBD <= GFdist and self.considerGF: #Greenfield
                undtype = "GF"
            elif distCBD > GFdist and self.considerAG:  #Agriculture
                undtype = "AG"
            elif distCBD > GFdist and self.considerGF:  #Greenfield because AG not considered
                undtype = "GF"
            else:
                undtype = "BF"  #Brownfield because GF and AG not considered
        return undtype
    
    def buildResidential(self, currentAttList, map_attr, A_res):
        """Builds residential urban form - either houses or apartments depending on the
        density of the population on the land available"""
        #Step 1 - Determine Typology
        popBlock = currentAttList.getAttribute("Pop").getDouble()
        Afloor = self.person_space * popBlock
        farblock = Afloor / A_res   #Calculate FAR
        #print "FARBlock", farblock
        
        blockratios = self.retrieveRatios(farblock)
        restype = self.retrieveResType(blockratios[0])
        if restype[0] == "HighRise":
            hdr_person_space = float(self.flat_area_max)/float(self.occup_flat_avg)
            Afloor = hdr_person_space * popBlock
            farblock = Afloor / A_res
            blockratios = self.retrieveRatios(farblock)
            restype = self.retrieveResType(blockratios[0])
        
        if "House" in restype:      #Design houses by default
            resdict = self.designResidentialHouses(currentAttList, map_attr, A_res, popBlock, blockratios, Afloor)
            resdict["TypeApt"] = 0
        elif "Apartment" in restype or "HighRise" in restype: #Design apartments
            resdict = self.designResidentialApartments(currentAttList, map_attr, A_res, popBlock, blockratios, Afloor)
            resdict["TypeHouse"] = 0
        return resdict
        
    def designResidentialHouses(self, currentAttList, map_attr, A_res, pop, ratios, Afloor):
        """All necessary urban planning calculations for residential dwellings urban form """
        resdict = {}
        resdict["TypeHouse"] = 1
        
        #Sample parameters from specified ranges
        occupmin = self.occup_flat_avg  #Absolute min
        occupmax = self.occup_max       #Absolute max
        
        occup = 0       #initialize to enter the loop
        while occup < occupmin or occup > occupmax or occup == 0:
            occup = random.normalvariate(self.occup_avg, self.occup_avg/10)
        #print "Block occupancy: ", occup
        
        resdict["HouseOccup"] = occup
        
        res_fpw = self.adjustSampleRange(self.res_fpwmin, self.res_fpwmax, self.res_fpmed)
        res_nsw = self.adjustSampleRange(self.res_nswmin, self.res_nswmax, self.res_nsmed)
        lane_w = self.adjustSampleRange(self.lane_wmin, self.lane_wmax, self.lane_wmed)
        Wfp = random.randint(res_fpw[0], res_fpw[1])
        Wns = random.randint(res_nsw[0], res_nsw[1])
        Wrd = random.randint(lane_w[0], lane_w[1])
        Wfrontage = Wfp + Wns + Wrd
        
        #Step 2: Subdivide Area
        Ndwunits = float(int((((pop/occup)/2)+1)))*2        #make it an even number, divide by 1, add 1, truncate, multiply by 2
        district_L = A_res/100                              #default typology depth = 100m
        parcels = max(float(int(district_L / 200)), 1.0)   #default typology width = 200m
        Wparcel = district_L / parcels
        Aparcel = Wparcel * 100                             #Area of one parcel
        Afrontage = (district_L * Wfrontage * 2) + ((parcels*2)*Wfrontage*(100 - 2*Wfrontage))
        Dlot = (100 - 2*Wfrontage)/2                        #Depth of one allotment
        Aca = A_res - Afrontage
        
        #print "Ndwunits", Ndwunits
        #print "district_L", district_L
        #print "parcels", parcels
        
        #print "Dlot", Dlot
        #print "Aca", Aca
        
        AfrontagePerv = float(Afrontage * (Wns / Wfrontage))
        
        resdict["ResParcels"] = parcels
        resdict["TotalFrontage"] = Afrontage
        resdict["avSt_RES"] = AfrontagePerv
        resdict["WResNstrip"] = Wns
        
        #Step 2b: Determine how many houses on one allotment based on advanced parameter "min Allotment Width"
        Wlot = 0
        DWperLot = 0
        while Wlot < self.min_allot_width:
            DWperLot += 1
            Nallotments = Ndwunits/DWperLot
            Alot = Aca / Nallotments
            Wlot = Alot / Dlot
            #print DWperLot, Nallotments, Alot, Wlot
        
        #print "For this block, we need ", DWperLot, " dwellings on each allotment"
        
        resdict["ResAllots"] = Nallotments
        resdict["ResDWpLot"] = DWperLot
        resdict["ResHouses"] = Ndwunits
        
        if self.setback_f_med == 0:
            fsetback = round(random.uniform(self.setback_f_min, self.setback_f_max),1)
        else:
            fsetback = (self.setback_f_min + self.setback_f_max)/2
        
        if self.setback_s_med == 0:
            ssetback = round(random.uniform(self.setback_s_min, self.setback_s_max),1)
        else:
            ssetback = (self.setback_s_min + self.setback_s_max)/2
        
        #Step 3: Subdivide ONE Lot
        res_parking_area = self.carports_max * 2.6*4.9              #ADDITIONAL COVERAGE ON SITE
        if self.garage_incl:
            Agarage = res_parking_area
            Aparking = res_parking_area* 0.5
        else:
            Agarage = 0
            Aparking = res_parking_area
        
        if self.patio_covered:
            Acover = self.patio_area_max
            Apatio = 0
        else:
            Acover = 0
            Apatio = self.patio_area_max

        Alotfloor = DWperLot*(occup*self.person_space*(1+self.extra_comm_area/100) + Agarage + Acover)
        farlot = Alotfloor / Alot
        lotratios = self.retrieveRatios(farlot)
        Als = lotratios[3]*Alot
        Ars = lotratios[4]*Alot
        Apave = fsetback * self.w_driveway_min + Apatio + Aparking  #DRIVEWAY + PATIO + PARKING
        
        #Determine if need more floors
        floors = 1
        Aba = Alotfloor
        while (Aba + Apave + Als) > Alot:
            #print "Need more than ", floors, " floor(s)!"
            floors += 1
            Aba = Alotfloor/floors
        
        #Retry #1 - Als set to Ars
        if floors > self.floor_num_max:
            Als = Ars       #set the remaining garden space to recreational space
            floors = 1
            Aba = Alotfloor
            while (Aba + Apave + Als) > Alot:
                #print "Even with less garden, need more than ", floors, "floor(s)!"
                floors += 1
                Aba = Alotfloor/floors
        #Retry #2 - Remove Carpark Paving
        if floors > self.floor_num_max:
            if Agarage == 0:
                Apave =- Aparking/2                         #DRIVEWAY + PATIO + half of PARKING since no garage!
            else: 
                Apave =- Aparking                           #DRIVEWAY + PATIO
            floors = 1
            Aba = Alotfloor
            while(Aba + Apave + Als) > Alot:
                #print "Even with less garden and less carpark paving, need more than ", floors, "floor(s)!"
                floors += 1
                Aba = Alotfloor/floors
        
        #Retry #3 - fsetback becomes ssetback (i.e. reduces paved driveway area even further)
        if floors > self.floor_num_max:
            Apave =- (fsetback - ssetback)*self.w_driveway_min      #REDUCED DRIVEWAY + PATIO + either half of PARKING or NONE
            floors = 1
            Aba = Alotfloor
            while(Aba + Apave + Als) > Alot:
                #print "Even with less garden, carpark paving and driveway, need more than ", floors, "floor(s)!"
                floors += 1
                Aba = Alotfloor/floors
        
        #Last Resort - exceed floor limit
        if floors > self.floor_num_max:
            pass
            #print "Floor Limit Exceeded! Cannot plan within bounds, continuing!"
        
        Aba = Alotfloor/floors
        Dbuilding = Aba / (Wlot - 2*ssetback)
        Apa = ssetback * Dbuilding * 2
        av_LOT = Alot - Ars - Aba - Apave - Apa   #WSUD SPACE = Lot area - Building - Recreation - Paving - Planning Req.
        
        #Calcualte Imperviousness, etc. write to residential dictionary
        
        resdict["ResLotArea"] = Alot
        resdict["ResRoof"] = Aba
        resdict["avLt_RES"] = av_LOT
        resdict["ResHFloors"] = floors
        
        #Determine Roof Connectivity
        roofconnect = self.roof_connected
        connectivity = ["Direct", "Disconnect"]
        if roofconnect == "Vary":
            choice = random.randint(0, 1)
            roofconnect = connectivity[choice]
        if roofconnect == "Direct":
            AroofEff = Aba
        elif roofconnect == "Disconnect":
            AroofEff = 0
        
        resdict["ResRoofCon"] = roofconnect
        
        AimpLot = Aba + Apave
        AConnectedImp = (AroofEff + Apave) * (1.0 - float(self.imperv_prop_dced/100))
        Agarden = av_LOT + Ars + Apa
        
        resdict["ResLotTIA"] = AimpLot
        resdict["ResLotEIA"] = AConnectedImp
        resdict["ResGarden"] = Agarden
        
        return resdict

    def designResidentialApartments(self, currentAttList, map_attr, A_res, pop, ratios, Afloor):
        """Lays out the specified residential area with high density apartments for a given population
        and ratios for the block. Algorithm works within floor constraints, but ignores these if the site
        cannot be laid out properly.
        """
        resdict = {}
        resdict["TypeApt"] = 1
        
        #Step 2: Subdivide Area
        Apa = math.sqrt(A_res)*2*self.setback_HDR_avg + (math.sqrt(A_res)-self.setback_HDR_avg)*2*self.setback_HDR_avg
        A_res_adj = A_res - Apa     #minus Planning Area Apa
        Aos = ratios[2]*A_res_adj   #min required open space area (outdoor + 1/2 indoor) (within A_res_adj)
        Als = ratios[3]*A_res_adj   #min required liveability space area (within Aos)
        Ars = ratios[4]*A_res_adj   #min required recreation space area (within Als)
        
        #Step3: Work out N units and car parking + indoor/outdoor spaces
        Naptunits = float(int(pop/self.occup_flat_avg+1))    #round up (using integer conversion/truncation)
        Ncparksmin = ratios[5]*Naptunits    #min required carparks, based on OCR (within Ncparksmax)
        Ncparksmax = ratios[6]*Naptunits    #max required carparks, based on TCR
        cpMin = Ncparksmin*2.6*4.9
        cpMax = Ncparksmax*2.6*4.9

        AextraIndoor = float(self.commspace_indoor)/100 * Afloor
        AextraOutdoor = float(self.commspace_outdoor)/100 * Afloor
        
        resdict["HDRFlats"] = Naptunits
        
        if AextraOutdoor < Aos:
            #print "User-defined Outdoor space requirements are less than minimum suggested, scaling down..."
            Aos = AextraOutdoor
            Als = AextraOutdoor * (Als/Aos)
            Ars = AextraOutdoor * (Ars/Aos)
        
        pPG = currentAttList.getAttribute("pLU_PG").getDouble()
        pactive = currentAttList.getAttribute("Active").getDouble()
        Ablock = map_attr.getAttribute("BlockSize").getDouble()*map_attr.getAttribute("BlockSize").getDouble()
        Apg = pPG * pactive * Ablock * float(int(self.park_OSR))
        
        #Step 4a: Work out Building Footprint using OSR
        Aoutdoor = max(Aos - 0.5*AextraIndoor - Apg, 0)     #if indoor space is much greater, Aoutdoor becomes negative
        if Aoutdoor == 0:   #if there is no outdoor space, then ls and rs spaces on-site are zero
            Als_site = 0
            Ars_site = 0
        else:
            Als_site = Als
            Ars_site = Ars
            
        Aca = A_res_adj - Aoutdoor
        Nfloors = float(int(((Afloor + AextraIndoor)/Aca)+1))
        if Nfloors < self.floor_num_HDRmax:
            #print "Try #1 - HDR residential design OK, floors not exceeded"
            #Step 5: Layout Urban Form
            Aba = (Afloor + AextraIndoor)/Nfloors
            Aouts = A_res - Apa - Aba
            Aon_rs = max(Ars_site - Apg, 0)
            av_RESHDR = max(Als_site - Aon_rs, 0)   #Available WSUD Space for residential district
            
            Aparking = self.calculateParkingArea(Aouts, Als_site, cpMin, cpMax)
            Aimp = Aba + Aparking 
            Aeff = Aimp * float(1- self.imperv_prop_dced/100)
            Agarden = A_res - Aba - Aparking
            
            #Calculate Imperviousness, etc., write to residential dictionary
            resdict["HDRRoofA"] = Aba
            resdict["HDROccup"] = self.occup_flat_avg
            resdict["HDR_TIA"] = Aimp
            resdict["HDR_EIA"] = Aeff
            resdict["HDRFloors"] = Nfloors
            resdict["av_HDRes"] = av_RESHDR
            resdict["HDRGarden"] = Agarden
            resdict["HDRCarPark"] = Aparking
            return resdict
        else:
            pass
            #print "Exceeded floors, executing 2nd method"
        
        #Step 4b: Work out Building Footprint using LSR
        Aoutdoor = max(Als - Apg, 0)
        if Aoutdoor == 0:
            Als_site = 0 #on-site
            Ars_site = 0 #on-site
        else:
            Als_site = Als
            Ars_site = Ars
                
        Aca = A_res_adj - Aoutdoor
        Nfloors = float(int(((Afloor + AextraIndoor)/Aca)+1))
        if Nfloors < self.floor_num_HDRmax:
            #print "Try #2 - HDR residential design OK, floors not exceeded"
            #Step 5: Layout Urban Form
            Aba = (Afloor + AextraIndoor)/Nfloors
            Aouts = A_res - Apa - Aba
            Aon_rs = max(Ars_site - Apg, 0)
            av_RESHDR = max(Als_site - Aon_rs, 0)  #Available WSUD Space for residential district
                    
            Aparking = self.calculateParkingArea(Aouts, Als_site, cpMin, cpMax)
            Aimp = Aba + Aparking 
            Aeff = Aimp * float(1- self.imperv_prop_dced/100)
            Agarden = A_res - Aba - Aparking
            
            #Calculate Imperviousness, etc., write to residential dictionary
            resdict["HDRRoofA"] = Aba
            resdict["HDROccup"] = self.occup_flat_avg
            resdict["HDR_TIA"] = Aimp
            resdict["HDR_EIA"] = Aeff
            resdict["HDRFloors"] = Nfloors
            resdict["av_HDRes"] = av_RESHDR
            resdict["HDRGarden"] = Agarden
            resdict["HDRCarPark"] = Aparking
            return resdict
        else:
            pass
            #print "Exceeded floors, executing 3rd method, ignoring floor limit"
        
        #Step 4c: Work out Building Footprint using OSR, ignoring floor limit
        Aoutdoor = max(Aos - 0.5*AextraIndoor - Apg, 0)
        if Aoutdoor == 0:
            Als_site = 0
            Ars_site = 0
        else:
            Als_site = Als
            Ars_site = Ars
        
        Aca = A_res_adj - Aoutdoor
        Nfloors = float(int(((Afloor + AextraIndoor)/Aca)+1))
        #print "Try #3 - HDR average floors determined as: ", Nfloors
        #Step 5: Layout Urban Form
        Aba = (Afloor + AextraIndoor)/Nfloors
        Aouts = A_res - Apa - Aba
        Aon_rs = max(Ars_site - Apg,0)
        av_RESHDR = max(Als_site - Aon_rs, 0)
            
        Aparking = self.calculateParkingArea(Aouts, Als_site, cpMin, cpMax)
        Aimp = Aba + Aparking 
        Aeff = Aimp * float(1- self.imperv_prop_dced/100)
        Agarden = A_res - Aba - Aparking
        
        #Calculate Imperviousness, etc., write to residential dictionary
        resdict["HDRRoofA"] = Aba
        resdict["HDROccup"] = self.occup_flat_avg
        resdict["HDR_TIA"] = Aimp
        resdict["HDR_EIA"] = Aeff
        resdict["HDRFloors"] = Nfloors
        resdict["av_HDRes"] = av_RESHDR
        resdict["HDRGarden"] = Agarden
        resdict["HDRCarPark"] = Aparking
        
        return resdict

    def calculateParkingArea(self, Aout, Alive, cpMin, cpMax):
        """Determines the total outdoor parking space on the HDR site based on OSR's remaining
        available space, using information about parking requirements, liveability space and
        inputs.
        
        Inputs:
            - Aout - Outdoor space = Land Area - PlanningArea - Building Area
            - Alive - Liveability space on-site = LSR x LA or zero if all area is leveraged by park
            - cpMin - minimum area required for car parks
            - cpMax - maximum area required for car parks
        Outputs:
            - Aparking - area of parking outside
        """
        if self.parking_HDR == "Vary":
            park_options = ["On", "Off", "Var"]
            choice = random.randint(0, 2)
            parking_HDR = park_options[choice]
        
        if self.parking_HDR == "On":
            avail_Parking = max(Aout - Alive,0)
            if avail_Parking < cpMin:
                Aparking = avail_Parking
            elif avail_Parking <cpMax:
                Aparking = avail_Parking
            elif avail_Parking > cpMax:
                Aparking = avail_Parking - cpMax
        elif parking_HDR == "Off" or parking_HDR == "Var":
            Aparking = 0
        return Aparking

    def retrieveResType(self, lui):
        """Retrieves the residence type for the specified lui, if the type
        is between two options, both are returned
        Input:
            - LUI: land use intensity
        Output:
            - [Type1, Type2], if only one type, then Type2=0
        """
        #print "LUI", lui
        if lui == -9999:
            return ["HighRise", 0]
        if lui < self.aptLUIthresh[0]:
            return ["House", 0]
        elif lui > self.aptLUIthresh[0] and lui < self.houseLUIthresh[1]:
            return ["House", "Apartment"]
        elif lui < self.aptLUIthresh[1] and lui > self.houseLUIthresh[1]:
            return ["Apartment", 0]
        elif lui > self.highLUIthresh[0] and lui < self.aptLUIthresh[1]:
            return ["Apartment", "HighRise"]
        elif lui < self.highLUIthresh[0] and lui > self.aptLUIthresh[1]:
            return ["HighRise", 0]
        else:
            return ["HighRise", 0]

    def retrieveRatios(self, far):
        """Retrieves the LUI and other values from the lookup dictionary
        Input:
            - FAR - floor-area-ratio of the site
        Output:
            - [LUI, FAR, OSR, LSR, RSR, OCR, TCR] matrix
        """
        #print "Searching Table for FAR = ", far
        mindex = 0  #counter for while loop
        found = 0
        while mindex < len(self.resLUIdict["FAR"]):
            if far < self.resLUIdict["FAR"][mindex]:     #will want to take the higher FAR
                far = self.resLUIdict["FAR"][mindex]
                mindex = len(self.resLUIdict["FAR"])
                found = 1
            else:
                mindex += 1
        
        if found == 0:      #means that FAR > FAR[LUI8.0)
            return [-9999,far,0,0,0,0,0]    #returns the -9999 not found case for LUI
            
        if found == 1:
            #get LUI and others
            dictindex = self.resLUIdict["FAR"].index(far)
            return [self.resLUIdict["LUI"][dictindex], 
                    far,
                    self.resLUIdict["OSR"][dictindex],
                    self.resLUIdict["LSR"][dictindex],
                    self.resLUIdict["RSR"][dictindex],
                    self.resLUIdict["OCR"][dictindex],
                    self.resLUIdict["TCR"][dictindex]]
     
    def identifyHotspots(self, A_fac, currentAttList, map_attr):
        """Retrieves all the information for each specific Municipal Facility located using the
        Input Locality Map, aggregates this information and writes it to the output
        
        Input:
            - A_fac - total area of facilities
            - currentAttList - currentAttributes List that model can access for the current Block
            - map_attr - global attributes list
        Output:
            - hotspotsdict - a dictionary of all hotspots in the area
        """
        hotspots_dict = {}
        
        #Grab the list of hotspots currently contained in the block based on the locality map
        
        #Check which ones from the selected list of explicit facilities to consider apply
        
        #Redistribute the area based on relative proportions of facility size
        
        #Sample from the distribution of data available
        
        #Write the information
        
        return hotspotsdict, remainA
    
    def buildNonResArea(self, currentAttList, map_attr, Aluc, type, frontage):
        """Function to build non-residential urban form (LI, HI, COM, ORC) based on the
        typology of estates and plot ratios and the provision of sufficient space for 
        building, carparks, service/loading bay and landscaping."""
        
        nresdict = {}
        #Note: Auto-setback
        #The formula to calculate auto-setback = H/2 + 1.5m based on Monash Council's Documents
        #This, however, relates more predominantly to facilities in close proximity to residential
        #neighbourhoods. As a means to an end, however, this formula can be used within reason here.
        #H will be taken as 3m and the formula is used only to building up to floors = 5 --> 9m setback
        #which corresponds to roughly the average setback value of commercial areas in the technology
        #precinct. The problem with using this is that the site is treated as a square. As a result,
        #the setback will only be applied on two faces of the site (since the site is expected to adjoin
        #other neighbouring sites. This is up for future revision.
        
        #Determine frontage info
        laneW = float(frontage[0])
        nstrip = float(frontage[1])
        fpath = float(frontage[2])
        Wfrontage = laneW + nstrip + fpath
        
        #STEP 1: Determine employment in the area
        employed = self.determineEmployment(self.employment_mode, currentAttList, map_attr, Aluc, type)
        nresdict["TotalBlockEmployed"] = employed
        
        #print "Empployed + Dens" ,employed
        
        employmentDens = employed /(Aluc/10000)      #Employment density [jobs/ha]
        
        #print employmentDens
        
        #STEP 2: Subdivide the area and allocate employment
        if type == "LI" or type == "HI":
            blockthresh = round(random.uniform(self.ind_subd_min, self.ind_subd_max), 1)
        elif type == "ORC" or type == "COM":
            blockthresh = round(random.uniform(self.com_subd_min, self.com_subd_max), 1)
        
        estates = float(max(int(Aluc/(blockthresh*10000)),1))
        Aestate = Aluc/float(estates)
        Westate = math.sqrt(Aestate)
        Afrontage = Westate*Wfrontage + Wfrontage*(Westate-2*Wfrontage)
        Aca = max(Aestate - Afrontage, 0)
        
        employed = employmentDens * (Aestate/10000)
        
        nresdict["Afrontage"] = Afrontage
        nresdict["av_St"] = (nstrip/(laneW+nstrip+fpath)) * Afrontage
        nresdict["FrontageEIA"] = nresdict["Afrontage"] - nresdict["av_St"]
        nresdict["SiteArea"] = Aluc
        nresdict["Estates"] = estates
        nresdict["Aestate"] = Aestate
        nresdict["DevelopableArea"] = Aca
        nresdict["EstateEmployed"] = employed
        
        if Aca == 0:        #If the area is not substantial enough to build on, return an empty dictionary
            #print "Block's ", type, " area is not substantial enough to build on, not doing anything else"
            nresdict["Has_"+str(type)] = 0
            return nresdict
        nresdict["Has_"+str(type)] = 1
        
        #STEP 3: Determine building area, height, plot ratio balance for ONE estate
        Afloor = self.nonres_far[type] * employed        #Step 3a: Calculate total floor area

        if type == "LI" or type == "HI":            #Step 3b: Determine maximum building footprint
            Afootprintmax = self.maxplotratio_ind/100 * Aca
        elif type == "COM":
            Afootprintmax = self.maxplotratio_com/100 * Aca
        else:       #type = "ORC", plot ratio rules do not apply, but instead setback rules, taken on 2 faces
            Afootprintmax = Aca - 2.0*math.sqrt(Aca)* max(self.nres_minfsetback*float(not(self.nres_setback_auto)), 2.0)
            #Site area - (setback area, which is either minimum specified or 2meters if auto is enabled)
            #NOTE - need to go measure the setbacks for high-rise areas in the city just to make sure 2m is ok
        
        #print "Calculating Floors: ", Afloor, Afootprintmax, Afloor/Afootprintmax + 1
        
        num_floors = float(int(Afloor/Afootprintmax + 1))  #Step 3c: Calculate number of floors, either 1 or more
        
        #print "Num _Floors ", num_floors
        
        if num_floors <= self.nres_maxfloors or self.nres_nolimit_floors:   #If floors do not exceed max or aren't of concern
            pass
            #print "Number of floors not exceeded, proceeding to lay out site"
            #We have Afloor calculated from start and the number of floors in num_floors rounded up
        elif type == "ORC": #else if floors are exceeded, but the type is ORC then that's fine too
            pass
            #print "Number of floors exceeded but this is for High-rise offices in a major district"
            #We have Afloor calculated from start and the number of floors in num_floors rounded up
        else:
            #print "Number of floors exceeded, increasing building footprint"    #setback taken on two faces
            Afootprintmaxadj = max(Aca - 2.0*math.sqrt(Aca)*max(self.nres_minfsetback*float(not(self.nres_setback_auto)), 2.0),0)
            if Afootprintmaxadj != 0:
                num_floors = float(int(Afloor/Afootprintmaxadj + 1))
            else:
                num_floors = 0  #becomes zero if there is no building, treat the site as a yard
            if num_floors <= self.nres_maxfloors:
                pass
                #print "Newly adjusted building footprint is ok"
                #We have Afloor and the adjusted num_floors
            else:
                #print "Even ignoring plot ratio, floors exceeded, readjusting employment density"
                #Recalculate building footprint based on plot ratio and recalculate employees
                #Use maximum floors and maximum building size within limits of plot ratio
                num_floors = self.nres_maxfloors
                Afloor = Afootprintmax * num_floors        #total floor area is now building footprint * max number of floors
                employednew = float(int(Afloor/self.nonres_far[type] + 1))  #employed now calculated from new floor area
                employeddiscrepancy = employed - employednew
                #print "Site was adjusted for total employment: ", employeddiscrepancy, " jobs were removed."
                employed = employednew      #set new employed as the default employment
                
            #Tally up information
        #print "After num_floors: ", num_floors
        
        #STEP 4: Lay out site and determine parking and loading bay requirements
        if num_floors == 0:
            Afootprintfinal = 0
        else:
            Afootprintfinal = Afloor/float(num_floors)
        
        nresdict["EstateBuildingArea"] = Afootprintfinal
        nresdict["Floors"] = float(num_floors)
        nresdict["TotalEstateFloorArea"] = Afloor
        
            #Progress: We have site area, building placed on site. Now we need to determine remaining area
        
        #Step 4a: Loading bay requirements
        Aloadingbay = Afloor/100.0 * self.loadingbay_A
        
        #Step 4b: Car Parking requirements
        if type == "LI" or type == "HI":
            Acarpark = self.carpark_ind * employed * self.carpark_Wmin * self.carpark_Dmin
        elif type == "COM" or type == "ORC":
            Acarpark = self.carpark_com * Afloor/100 * self.carpark_Wmin * self.carpark_Dmin
        
        #print "Carparking: ", Acarpark
        
        nresdict["Aloadingbay"] = Aloadingbay
        nresdict["TotalAcarpark"] = Acarpark
        
        #Step 4c: Try to fit carpark and loading bay on-site, otherwise stack
        minsetback = max(not(self.nres_setback_auto)*self.nres_minfsetback, (num_floors/2+1.5)*self.nres_setback_auto*float(bool(num_floors <=5)),2.0)
        #setback determined as follows: if not automatic, uses the minimum specified, if automatic and below 5 floors, uses the formula
        #       if automatic but above 5 floors, uses 2m by default
        
        setbackArea = math.sqrt(Aestate)*minsetback*2 - minsetback*minsetback       #take setback area on two faces
        Asite_remain = Aca - Afootprintfinal - setbackArea
        
        if (Asite_remain - Acarpark - Aloadingbay) > 0:
            #Case 1: It all fits, hooray! --> Alandscape = setback area + remaining area
            Alandscape = (Asite_remain - Acarpark - Aloadingbay) + setbackArea
            nresdict["Alandscape"] = Alandscape
            nresdict["Outdoorcarpark"] = Acarpark
        elif (Asite_remain - Aloadingbay) > 0:
            #Case 2: Loading bay fits, but carpark does not entirely --> that's ok, Alandscape = setback area
            Alandscape = setbackArea
            nresdict["Alandscape"] = Alandscape
            nresdict["Outdoorcarpark"] = Asite_remain - Aloadingbay
        elif Asite_remain > 0:
            #Case 3: Loading bay does not fit --> use setback area to fit, Alandscape = remaining setback
            Alandscape = max(setbackArea - Aloadingbay, 0)
            nresdict["Alandscape"] = Alandscape
            nresdict["Outdoorcarpark"] = 0
        else:
            #Case 4: Loading bay does not fit even in setback area --> assume it is covered, no landscaping, but check setback
            #print "WARNING, SETBACK AREA NOT PROVIDED"
            revisedSetback = Aca - Afootprintfinal
            #print "Revised Setback: ", revisedSetback
            Alandscape = max(revisedSetback, 0)
            nresdict["Alandscape"] = Alandscape
            nresdict["Outdoorcarpark"] = 0
            
        #STEP 5: Landscaping
        if self.lscape_hsbalance == -1:
            prop_Soft = 0
            prop_Hard = 1
        elif self.lscape_hsbalance == 1:
            prop_Soft = 1
            prop_Hard = 0
        else:
            prop_Soft = 0.5
            prop_Hard = 0.5
         
        Aimpaddition = prop_Hard * Alandscape
        Agreen = prop_Soft * Alandscape
        
        #Tally up all land surface cover information
        Aimp_total = Aca - Alandscape + Aimpaddition
        Aimp_connected = (1- self.lscape_impdced/100) * Aimp_total
        
        nresdict["EstateGreenArea"] = Agreen
        nresdict["EstateImperviousArea"] = Aimp_total
        nresdict["EstateEffectiveImpervious"] = Aimp_connected
        
        return nresdict
        
    def determineEmployment(self, method, currentAttList, map_attr, Aluc, type):
        """Determines the employment of the block based on the selected method. Calls
        some alternative functions for scaling or other aspects"""
        if method == "I" and map_attr.getAttribute("include_employment").getDouble() == 1:
            #Condition required to do this: there has to be data on employment input
            employed = currentAttList.getAttribute("Employ").getDouble() #total employment for Block
            #Scale this value based on the hypothetical area and employee distribution
            
        elif method == "S":
            employed = 0   #Global employment/Total Non-res Built-up Area = block employed 
            #Do something to tally up total employment and density for the map
            
        elif method == "D":
            if type == "LI" or type == "HI":
                employed = self.ind_edist*Aluc/10000
            elif type == "COM":
                employed = self.com_edist*Aluc/10000
            elif type == "ORC":
                employed = self.orc_edist*Aluc/10000
            else:
                print "Something's wrong here..."
        return employed

    def scaleEmployment(self, currentAttList, employed, Aluc):
        pass
        #Scales the employed value down based on Aluc, used for "S" and "D" methods
        return employed
    
    def transferBlockAttributes(self, currentAttList, prevAttList):
        """Manually transfers all urbplanbb attributes from the previous block list into
        the new block list."""
        currentAttList.addAttribute("MiscAtot", prevAttList.getAttribute("MiscAtot").getDouble())
        currentAttList.addAttribute("MiscAimp", prevAttList.getAttribute("MiscAimp").getDouble())
        currentAttList.addAttribute("UndType", prevAttList.getAttribute("UndType").getString())
        currentAttList.addAttribute("UND_av", prevAttList.getAttribute("UND_av").getDouble())
        currentAttList.addAttribute("OpenSpace", prevAttList.getAttribute("OpenSpace").getDouble())
        currentAttList.addAttribute("AGardens", prevAttList.getAttribute("AGardens").getDouble())
        currentAttList.addAttribute("ASquare", prevAttList.getAttribute("ASquare").getDouble())
        currentAttList.addAttribute("PG_av", prevAttList.getAttribute("PG_av").getDouble())
        currentAttList.addAttribute("REF_av", prevAttList.getAttribute("REF_av").getDouble())
        currentAttList.addAttribute("ANonW_Utils", prevAttList.getAttribute("ANonW_Utils").getDouble())
        currentAttList.addAttribute("SVU_avWS", prevAttList.getAttribute("SVU_avWS").getDouble())
        currentAttList.addAttribute("SVU_avWW", prevAttList.getAttribute("SVU_avWW").getDouble())
        currentAttList.addAttribute("SVU_avSW", prevAttList.getAttribute("SVU_avSW").getDouble())
        currentAttList.addAttribute("SVU_avOTH", prevAttList.getAttribute("SVU_avOTH").getDouble())
        currentAttList.addAttribute("RoadTIA", prevAttList.getAttribute("RoadTIA").getDouble())
        currentAttList.addAttribute("ParkBuffer", prevAttList.getAttribute("ParkBuffer").getDouble())
        currentAttList.addAttribute("RD_av", prevAttList.getAttribute("RD_av").getDouble())
        currentAttList.addAttribute("RDMedW", prevAttList.getAttribute("RDMedW").getDouble())
        
        if currentAttList.getAttribute("pLU_RES").getDouble() != 0:
            currentAttList.addAttribute("HasRes", 1)
        else:
            currentAttList.addAttribute("HasRes", 0)
        if prevAttList.getAttribute("ResAllots").getDouble() != 0:
            currentAttList.addAttribute("HasHouses", 1)
        else:
            currentAttList.addAttribute("HasHouses", 0)
            
        currentAttList.addAttribute("HouseOccup", prevAttList.getAttribute("HouseOccup").getDouble())
        currentAttList.addAttribute("ResParcels", prevAttList.getAttribute("ResParcels").getDouble())
        currentAttList.addAttribute("ResFrontT", prevAttList.getAttribute("ResFrontT").getDouble())
        currentAttList.addAttribute("avSt_RES", prevAttList.getAttribute("avSt_RES").getDouble())
        currentAttList.addAttribute("WResNstrip", prevAttList.getAttribute("WResNstrip").getDouble())
        currentAttList.addAttribute("ResAllots", prevAttList.getAttribute("ResAllots").getDouble())
        currentAttList.addAttribute("ResDWpLot", prevAttList.getAttribute("ResDWpLot").getDouble())
        currentAttList.addAttribute("ResHouses", prevAttList.getAttribute("ResHouses").getDouble())
        currentAttList.addAttribute("ResLotArea", prevAttList.getAttribute("ResLotArea").getDouble())
        currentAttList.addAttribute("ResRoof", prevAttList.getAttribute("ResRoof").getDouble())
        currentAttList.addAttribute("avLt_RES", prevAttList.getAttribute("avLt_RES").getDouble())
        currentAttList.addAttribute("ResHFloors", prevAttList.getAttribute("ResHFloors").getDouble())
        currentAttList.addAttribute("ResLotTIA", prevAttList.getAttribute("ResLotTIA").getDouble())
        currentAttList.addAttribute("ResLotEIA", prevAttList.getAttribute("ResLotEIA").getDouble())
        currentAttList.addAttribute("ResGarden", prevAttList.getAttribute("ResGarden").getDouble())
        currentAttList.addAttribute("ResRoofCon", prevAttList.getAttribute("ResRoofCon").getDouble())
        
        if prevAttList.getAttribute("HDRFlats").getDouble() != 0:
            currentAttList.addAttribute("HasFlats", 1)
        else:
            currentAttList.addAttribute("HasFlats", 0)
            
        currentAttList.addAttribute("avSt_RES", prevAttList.getAttribute("avSt_RES").getDouble())
        currentAttList.addAttribute("HDRFlats", prevAttList.getAttribute("HDRFlats").getDouble())
        currentAttList.addAttribute("HDRRoofA", prevAttList.getAttribute("HDRRoofA").getDouble())
        currentAttList.addAttribute("HDROccup", prevAttList.getAttribute("HDROccup").getDouble())
        currentAttList.addAttribute("HDR_TIA", prevAttList.getAttribute("HDR_TIA").getDouble())
        currentAttList.addAttribute("HDR_EIA", prevAttList.getAttribute("HDR_EIA").getDouble())
        currentAttList.addAttribute("HDRFloors", prevAttList.getAttribute("HDRFloors").getDouble())
        currentAttList.addAttribute("av_HDRes", prevAttList.getAttribute("av_HDRes").getDouble())
        currentAttList.addAttribute("HDRGarden", prevAttList.getAttribute("HDRGarden").getDouble())
        currentAttList.addAttribute("HDRCarPark", prevAttList.getAttribute("HDRCarPark").getDouble())
        
        if prevAttList.getAttribute("LIestates").getDouble() != 0:
            currentAttList.addAttribute("Has_LI", 1)
        else:
            currentAttList.addAttribute("Has_LI", 0)
            
        currentAttList.addAttribute("LIjobs", prevAttList.getAttribute("LIjobs").getDouble())
        currentAttList.addAttribute("LIestates", prevAttList.getAttribute("LIestates").getDouble())
        currentAttList.addAttribute("avSt_LI", prevAttList.getAttribute("avSt_LI").getDouble())
        currentAttList.addAttribute("LIAfront", prevAttList.getAttribute("LIAfront").getDouble())
        currentAttList.addAttribute("LIAfrEIA", prevAttList.getAttribute("LIAfrEIA").getDouble())
        currentAttList.addAttribute("LIAestate", prevAttList.getAttribute("LIAestate").getDouble())
        currentAttList.addAttribute("LIAeBldg", prevAttList.getAttribute("LIAeBldg").getDouble())
        currentAttList.addAttribute("LIFloors", prevAttList.getAttribute("LIFloors").getDouble())
        currentAttList.addAttribute("LIAeLoad", prevAttList.getAttribute("LIAeLoad").getDouble())
        currentAttList.addAttribute("LIAeCPark", prevAttList.getAttribute("LIAeCPark").getDouble())
        currentAttList.addAttribute("avLt_LI", prevAttList.getAttribute("avLt_LI").getDouble())
        currentAttList.addAttribute("LIAeLgrey", prevAttList.getAttribute("LIAeLgrey").getDouble())
        currentAttList.addAttribute("LIAeEIA", prevAttList.getAttribute("LIAeEIA").getDouble())
        currentAttList.addAttribute("LIAeTIA", prevAttList.getAttribute("LIAeTIA").getDouble())
        
        if prevAttList.getAttribute("HIestates").getDouble() != 0:
            currentAttList.addAttribute("Has_HI", 1)
        else:
            currentAttList.addAttribute("Has_HI", 0)
            
        currentAttList.addAttribute("HIjobs", prevAttList.getAttribute("HIjobs").getDouble())
        currentAttList.addAttribute("HIestates", prevAttList.getAttribute("HIestates").getDouble())
        currentAttList.addAttribute("avSt_HI", prevAttList.getAttribute("avSt_HI").getDouble())
        currentAttList.addAttribute("HIAfront", prevAttList.getAttribute("HIAfront").getDouble())
        currentAttList.addAttribute("HIAfrEIA", prevAttList.getAttribute("HIAfrEIA").getDouble())
        currentAttList.addAttribute("HIAestate", prevAttList.getAttribute("HIAestate").getDouble())
        currentAttList.addAttribute("HIAeBldg", prevAttList.getAttribute("HIAeBldg").getDouble())
        currentAttList.addAttribute("HIFloors", prevAttList.getAttribute("HIFloors").getDouble())
        currentAttList.addAttribute("HIAeLoad", prevAttList.getAttribute("HIAeLoad").getDouble())
        currentAttList.addAttribute("HIAeCPark", prevAttList.getAttribute("HIAeCPark").getDouble())
        currentAttList.addAttribute("avLt_HI", prevAttList.getAttribute("avLt_HI").getDouble())
        currentAttList.addAttribute("HIAeLgrey", prevAttList.getAttribute("HIAeLgrey").getDouble())
        currentAttList.addAttribute("HIAeEIA", prevAttList.getAttribute("HIAeEIA").getDouble())
        currentAttList.addAttribute("HIAeTIA", prevAttList.getAttribute("HIAeTIA").getDouble())
        
        if prevAttList.getAttribute("COMestates").getDouble() != 0:
            currentAttList.addAttribute("Has_Com", 1)
        else:
            currentAttList.addAttribute("Has_Com", 0)
            
        currentAttList.addAttribute("COMjobs", prevAttList.getAttribute("COMjobs").getDouble())
        currentAttList.addAttribute("COMestates", prevAttList.getAttribute("COMestates").getDouble())
        currentAttList.addAttribute("avSt_COM", prevAttList.getAttribute("avSt_COM").getDouble())
        currentAttList.addAttribute("COMAfront", prevAttList.getAttribute("COMAfront").getDouble())
        currentAttList.addAttribute("COMAfrEIA", prevAttList.getAttribute("COMAfrEIA").getDouble())
        currentAttList.addAttribute("COMAestate", prevAttList.getAttribute("COMAestate").getDouble())
        currentAttList.addAttribute("COMAeBldg", prevAttList.getAttribute("COMAeBldg").getDouble())
        currentAttList.addAttribute("COMFloors", prevAttList.getAttribute("COMFloors").getDouble())
        currentAttList.addAttribute("COMAeLoad", prevAttList.getAttribute("COMAeLoad").getDouble())
        currentAttList.addAttribute("COMAeCPark", prevAttList.getAttribute("COMAeCPark").getDouble())
        currentAttList.addAttribute("avLt_COM", prevAttList.getAttribute("avLt_COM").getDouble())
        currentAttList.addAttribute("COMAeLgrey", prevAttList.getAttribute("COMAeLgrey").getDouble())
        currentAttList.addAttribute("COMAeEIA", prevAttList.getAttribute("COMAeEIA").getDouble())
        currentAttList.addAttribute("COMAeTIA", prevAttList.getAttribute("COMAeTIA").getDouble())
        
        if prevAttList.getAttribute("ORCestates").getDouble() != 0:
            currentAttList.addAttribute("Has_ORC", 1)
        else:
            currentAttList.addAttribute("Has_ORC", 0)
            
        currentAttList.addAttribute("ORCjobs", prevAttList.getAttribute("ORCjobs").getDouble())
        currentAttList.addAttribute("ORCestates", prevAttList.getAttribute("ORCestates").getDouble())
        currentAttList.addAttribute("avSt_ORC", prevAttList.getAttribute("avSt_ORC").getDouble())
        currentAttList.addAttribute("ORCAfront", prevAttList.getAttribute("ORCAfront").getDouble())
        currentAttList.addAttribute("ORCAfrEIA", prevAttList.getAttribute("ORCAfrEIA").getDouble())
        currentAttList.addAttribute("ORCAestate", prevAttList.getAttribute("ORCAestate").getDouble())
        currentAttList.addAttribute("ORCAeBldg", prevAttList.getAttribute("ORCAeBldg").getDouble())
        currentAttList.addAttribute("ORCFloors", prevAttList.getAttribute("ORCFloors").getDouble())
        currentAttList.addAttribute("ORCAeLoad", prevAttList.getAttribute("ORCAeLoad").getDouble())
        currentAttList.addAttribute("ORCAeCPark", prevAttList.getAttribute("ORCAeCPark").getDouble())
        currentAttList.addAttribute("avLt_ORC", prevAttList.getAttribute("avLt_ORC").getDouble())
        currentAttList.addAttribute("ORCAeLgrey", prevAttList.getAttribute("ORCAeLgrey").getDouble())
        currentAttList.addAttribute("ORCAeEIA", prevAttList.getAttribute("ORCAeEIA").getDouble())
        currentAttList.addAttribute("ORCAeTIA", prevAttList.getAttribute("ORCAeTIA").getDouble())
        currentAttList.addAttribute("Blk_TIA", prevAttList.getAttribute("Blk_TIA").getDouble())
        currentAttList.addAttribute("Blk_EIA", prevAttList.getAttribute("Blk_EIA").getDouble())
        currentAttList.addAttribute("Blk_EIF", prevAttList.getAttribute("Blk_EIF").getDouble())
        currentAttList.addAttribute("Blk_TIF", prevAttList.getAttribute("Blk_TIF").getDouble())
        currentAttList.addAttribute("Blk_RoofsA", prevAttList.getAttribute("Blk_RoofsA").getDouble())
        return True
    
    ########################################################
    #DYNAMIND-SPECIFIC FUNCTIONS                           #
    ########################################################   
    
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
    
    def createInputDialog(self):
        form = activateurbplanbbGUI(self, QApplication.activeWindow())
        form.show()
        return True  

        