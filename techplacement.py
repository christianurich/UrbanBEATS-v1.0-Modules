# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 1.0
@section LICENSE

This file is part of UrbanBEATS, Dynamind
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
import tech_templates as tt
import tech_design as td

from techplacementguic import *

import os, sqlite3, gc

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from pydynamind import *

class Techplacement(Module):
    """Log of Updates made at each version:
    
    v1.00 update (April 2013):
        - Complete revamp of existing 5 modules, merger into a single Module with multiple functions
        - Creation of separate scripts to steer tech planning, placement and evaluation
        - Rewrite of technology.py, now called tech_library.py, class functions are now more efficient
        - Inclusion of water recycling functionality
        - Inclusion of more planning options available to user
        - Integration of techretrofit features to deal with dynamics more efficiently
        
    v0.80 update (July 2012):
        - upgraded techplanning to include forks for dynamics, planning and implementation cycles
        - allowed planning with custom design curves input by the user or from UrbanBEATs' database
        - included retrofit functionality in techplacement
        - upgraded techstrategy eval with bug fixes and improved decision-making
    
    v0.80 update (March 2012):
        - Split module into five parts: initial data prep, 4x planning at different scales and one evaluation
        - Built Monte Carlo Brainstorming method for technologies (see 9UDM Conference Paper)
        - Added functionality for Infiltration systems, biofilters, swales, wetlands and ponds
        - Included new information about certain technologies, refined GUI to include location
        - Upgraded techstrat-eval with some bug fixes and improved decision-making
    
    v0.75 update (October 2011):
        - Added in initial design methods for several systems, upgraded GUI to include new features
    
    v0.5 update (August 2011):
        - Updated Techplacement to include multi-criteria evaluation options, methods
        - Concept brainstorming completed
        
    v0.5 first (July 2011):
        - Created first version, initial GUI concepts and ideas
        - Created initial list of techplacement ideas
	
	@ingroup UrbanBEATS
	@author Peter M Bach
	"""
        
    def __init__(self):
        Module.__init__(self)
        self.block_size = 0
        ##########################################################################
        #   DESIGN CRITERIA INPUTS                                               #
        ##########################################################################
        
        #DESIGN RATIONALE SETTINGS
        self.createParameter("ration_runoff", BOOL,"")
        self.createParameter("ration_pollute", BOOL,"")
        self.createParameter("ration_harvest",BOOL,"")
        self.createParameter("runoff_pri", DOUBLE,"")
        self.createParameter("pollute_pri", DOUBLE,"")
        self.createParameter("harvest_pri",DOUBLE,"")
        self.ration_runoff = True                #Design for flood mitigation?
        self.ration_pollute = True               #Design for pollution management?
        self.ration_harvest = False              #Design for harvesting & reuse? Adds storage-sizing to certain systems
        self.runoff_pri = 1                      #Priority of flood mitigation?
        self.pollute_pri = 1                     #Priority of pollution management?
        self.harvest_pri = 1                     #Priority for harvesting & reuse
	
        #WATER MANAGEMENT TARGETS
        self.createParameter("targets_runoff", DOUBLE,"")
        self.createParameter("targets_TSS", DOUBLE,"")
        self.createParameter("targets_TN", DOUBLE,"")
        self.createParameter("targets_TP", DOUBLE,"")
        self.createParameter("targets_harvest", DOUBLE,"")
        self.createParameter("targets_reliability", DOUBLE, "")
        self.targets_runoff = 80            #Runoff reduction target [%]
        self.targets_TSS = 70               #TSS Load reduction target [%]
        self.targets_TN = 30                #TN Load reduction target [%]
        self.targets_TP = 30                #TP Load reduction target [%]
        self.targets_harvest = 50           #required supply substitution % by recycling
        self.targets_reliability = 50       #required reliability of harvesting systems    
        
        #CALCULATE SOME GLOBAL VARIABLES RELATING TO TARGETS
        self.system_tarQ = self.ration_runoff * self.targets_runoff
        self.system_tarTSS = self.ration_pollute * self.targets_TSS
        self.system_tarTP = self.ration_pollute * self.targets_TP
        self.system_tarTN = self.ration_pollute * self.targets_TN
        self.system_tarHARVEST = self.ration_harvest * self.targets_harvest
        self.system_tarREL = self.ration_harvest * self.targets_reliability
        self.targetsvector = [self.system_tarQ, self.system_tarTSS, self.system_tarTN, 
                        self.system_tarHARVEST, self.system_tarREL]
        #---> TO BE USED TO ASSESS OPPORTUNITIES
        
        #WATER MANAGEMENT SERVICE LEVELS
        self.createParameter("service_swm", DOUBLE, "")
        self.createParameter("service_wr_private", DOUBLE, "")
        self.createParameter("service_wr_public", DOUBLE, "")
        self.createParameter("service_res", BOOL, "")
        self.createParameter("service_hdr", BOOL, "")
        self.createParameter("service_com", BOOL, "")
        self.createParameter("service_li", BOOL, "")
        self.createParameter("service_hi", BOOL, "")
        self.service_swm = 100                  #required service level for stormwater management
        self.service_wr_private = 50            #required service level for water recycling for private use
        self.service_wr_public = 50             #required service level for water recycling for public use
        self.service_res = True
        self.service_hdr = True
        self.service_com = True
        self.service_li = True
        self.service_hi = True
        
        #STRATEGY CUSTOMIZE
        self.createParameter("strategy_lot_check", BOOL, "")
        self.createParameter("strategy_street_check", BOOL, "")
        self.createParameter("strategy_neigh_check", BOOL, "")
        self.createParameter("strategy_subbas_check", BOOL, "")
        self.createParameter("lot_rigour", DOUBLE, "")
        self.createParameter("street_rigour", DOUBLE, "")
        self.createParameter("neigh_rigour", DOUBLE, "")
        self.createParameter("subbas_rigour", DOUBLE, "")
        self.strategy_lot_check = 1
        self.strategy_street_check = 1
        self.strategy_neigh_check = 1
        self.strategy_subbas_check = 1
        self.lot_rigour = 10
        self.street_rigour = 10
        self.neigh_rigour = 10
        self.subbas_rigour = 10
        
        #ADDITIONAL STRATEGIES
        self.createParameter("strategy_specific1", BOOL,"")
        self.createParameter("strategy_specific2", BOOL,"")
        self.createParameter("strategy_specific3", BOOL,"")
        self.createParameter("strategy_specific4", BOOL,"")
        self.createParameter("strategy_specific5", BOOL,"")
        self.strategy_specific1 = False
        self.strategy_specific2 = False
        self.strategy_specific3 = False
        self.strategy_specific4 = False
        self.strategy_specific5 = False
        
        ##########################################################################
        #   RECYCLING STRATEGY DESIGN INPUTS                                     #
        ##########################################################################
        #coming soon...
        
        #WATER HARVESTING LOCATIONS
        
        #REGIONAL RECYCLING-SUPPLY ZONES
        
        #ADDITIONAL INPUTS
        
        
        ##########################################################################
        #   RETROFIT CONDITIONS INPUTS                                           #
        ##########################################################################
        
        #SCENARIO DESCRIPTION
        self.createParameter("retrofit_scenario", STRING,"")
        self.createParameter("renewal_cycle_def", BOOL,"")
        self.createParameter("renewal_lot_years", DOUBLE,"")
        self.createParameter("renewal_street_years", DOUBLE,"")
        self.createParameter("renewal_neigh_years", DOUBLE,"")
        self.createParameter("renewal_lot_perc", DOUBLE,"")
        self.createParameter("force_street", BOOL,"")
        self.createParameter("force_neigh", BOOL,"")
        self.createParameter("force_prec", BOOL,"")
        self.retrofit_scenario = "N"    #N = Do Nothing, R = With Renewal, F = Forced
        self.renewal_cycle_def = 1      #Defined renewal cycle?
        self.renewal_lot_years = 10         #number of years to apply renewal rate
        self.renewal_street_years = 20      #cycle of years for street-scale renewal
        self.renewal_neigh_years = 40       #cycle of years for neighbourhood-precinct renewal
        self.renewal_lot_perc = 5           #renewal percentage
        self.force_street = 0              #forced renewal on lot?
        self.force_neigh = 0           #forced renewal on street?
        self.force_prec = 0            #forced renewal on neighbourhood and precinct?
        
        #LIFE CYCLE OF EXISTING SYSTEMS
        self.createParameter("lot_renew", BOOL,"")
        self.createParameter("lot_decom", BOOL,"")
        self.createParameter("street_renew", BOOL,"")
        self.createParameter("street_decom", BOOL,"")
        self.createParameter("neigh_renew", BOOL,"")
        self.createParameter("neigh_decom", BOOL,"")
        self.createParameter("prec_renew", BOOL,"")
        self.createParameter("prec_decom", BOOL,"")
        self.createParameter("decom_thresh", DOUBLE,"")
        self.createParameter("renewal_thresh", DOUBLE,"")
        self.createParameter("renewal_alternative", STRING,"")
        self.lot_renew = 0
        self.lot_decom = 0
        self.street_renew = 0
        self.street_decom = 0
        self.neigh_renew = 0
        self.neigh_decom = 0
        self.prec_renew = 0
        self.prec_decom = 0
	self.decom_thresh = 40
        self.renewal_thresh = 30
        self.renewal_alternative = "K"          #if renewal cannot be done, what to do then? K=Keep, D=Decommission
        
        ##########################################################################
        #   TECHNOLOGIES LIST AND CUSTOMIZATION                                  #
        ##########################################################################
        
        #---ADVANCED STORMWATER HARVESTING PLANT [ASHP]---###TBA###-------------
        self.createParameter("ASHPstatus", BOOL,"")
        self.ASHPstatus = 0
        self.ASHPlot = 0
        self.ASHPstreet = 0
        self.ASHPneigh = 0
        self.ASHPprec = 0
        
        #---AQUACULTURE/LIVING SYSTEMS [AQ]---###TBA###-------------------------
        self.createParameter("AQstatus", BOOL,"")
        self.AQstatus = 0
        
        #---AQUIFER STORAGE & RECOVERY SYSTEM [ASR]---###TBA###-----------------
        self.createParameter("ASRstatus", BOOL,"")
        self.ASRstatus = 0
        
        #---BIOFILTRATION SYSTEM/RAINGARDEN [BF]--------------------------------
        self.createParameter("BFstatus", BOOL,"")
        self.BFstatus = 1
        
        #Available Scales
        self.createParameter("BFlot", BOOL,"")
        self.createParameter("BFstreet", BOOL,"")
        self.createParameter("BFneigh", BOOL,"")
        self.createParameter("BFprec", BOOL,"")
        self.BFlot = True
        self.BFstreet = True
        self.BFneigh = True
        self.BFprec = True
        
        #Available Applications
        self.createParameter("BFflow", BOOL, "")
	self.createParameter("BFpollute", BOOL,"")
        self.BFflow = False
	self.BFpollute = True
	
        #Design Curves
        self.createParameter("BFdesignUB", BOOL,"")
        self.createParameter("BFdescur_path", STRING,"")
        self.BFdesignUB = True          #use DAnCE4Water's default curves to design system?
        self.BFdescur_path = "no file"  #path for design curve
        
        #Design Information
        self.createParameter("BFspec_EDD", DOUBLE,"")
        self.createParameter("BFspec_FD", DOUBLE,"")
        self.createParameter("BFmaxsize", DOUBLE,"")
        self.createParameter("BFavglife", DOUBLE,"")
        self.createParameter("BFlined", BOOL,"")
        self.BFspec_EDD = 0.3
        self.BFspec_FD = 0.6
        self.BFmaxsize = 999999         #maximum surface area of system in sqm
	self.BFavglife = 20             #average life span of a biofilter
        self.BFlined = True
        
        #---GREEN ROOF [GR]---###TBA###-----------------------------------------
        self.createParameter("GRstatus", BOOL,"")
        self.GRstatus = 0
        
        #---INFILTRATION SYSTEM [IS]--------------------------------------------
        self.createParameter("ISstatus", BOOL,"")
        self.ISstatus = 1
        
        #Available Scales
        self.createParameter("ISlot", BOOL,"")
        self.createParameter("ISstreet", BOOL,"")
        self.createParameter("ISneigh", BOOL,"")
        self.ISlot = True
        self.ISstreet = True
        self.ISneigh = True
        
        #Available Applications
        self.createParameter("ISflow", BOOL,"")
        self.createParameter("ISpollute", BOOL,"")
        self.ISflow = True
        self.ISpollute = True
        
        #Design Curves
        self.createParameter("ISdesignUB", BOOL,"")
        self.createParameter("ISdescur_path", STRING,"")
        self.ISdesignUB = True          #use DAnCE4Water's default curves to design system?
        self.ISdescur_path = "no file"  #path for design curve
        
        #Design Information        self.createParameter("ISspec_EDD", DOUBLE,"")
        self.createParameter("ISspec_FD", DOUBLE,"")
        self.createParameter("ISspec_EDD", DOUBLE,"")
        self.createParameter("ISmaxsize", DOUBLE,"")
        self.createParameter("ISavglife", DOUBLE,"")
        self.ISspec_EDD = 0.2
        self.ISspec_FD = 0.8
        self.ISmaxsize = 99999          #maximum surface area of system in sqm
	self.ISavglife = 20             #average life span of an infiltration system
        
        #---GROSS POLLUTANT TRAP [GPT]------------------------------------------
        self.createParameter("GPTstatus", BOOL,"")
        self.GPTstatus = 0
        
        #---GREYWATER TREATMENT & DIVERSION SYSTEM [GT]-------------------------
        self.createParameter("GTstatus", BOOL,"")
        self.GTstatus = 0
        
        #---PACKAGED PLANT [PPL]---###TBA###------------------------------------
        self.createParameter("PPLstatus", BOOL,"")
        self.PPLstatus = 0
        
        #---PONDS & SEDIMENTATION BASIN [PB]------------------------------------
        self.createParameter("PBstatus", BOOL,"")
        self.PBstatus = 1
        
        #Available Scales
        self.createParameter("PBneigh", BOOL,"")
        self.createParameter("PBprec", BOOL,"")
        self.PBneigh = True
        self.PBprec = True
        
        #Available Applications
        self.createParameter("PBflow", BOOL,"")
        self.createParameter("PBpollute", BOOL,"")
        self.PBflow = True
        self.PBpollute = True
        
        #Design Curves
        self.createParameter("PBdesignUB", BOOL,"")
        self.createParameter("PBdescur_path", STRING,"")
        self.PBdesignUB = True          #use DAnCE4Water's default curves to design system?
        self.PBdescur_path = "no file"  #path for design curve
        
        #Design Information
        self.createParameter("PBspec_MD", STRING,"")
        self.createParameter("PBmaxsize", DOUBLE,"")
        self.createParameter("PBavglife", DOUBLE,"")
        self.PBspec_MD = "1.25" 	#need a string for the combo box
        self.PBmaxsize = 9999999           #maximum surface area of system in sqm
	self.PBavglife = 20             #average life span of a pond/basin

        #---POROUS/PERVIOUS PAVEMENT [PP]---###TBA###---------------------------
        self.createParameter("PPstatus", BOOL,"")
        self.PPstatus = 0
        
        #---RAINWATER TANK [RT]-------------------------------------------------
        self.createParameter("RTstatus", BOOL,"")
        self.RTstatus = 0
        
        self.createParameter("RTscale_lot", BOOL,"")
        self.createParameter("RTscale_street", BOOL,"")
        self.createParameter("RTpurp_flood", BOOL,"")
        self.createParameter("RTpurp_recyc", BOOL,"")
        self.RTscale_lot = True
        self.RTscale_street = True
        self.RTpurp_flood = True
        self.RTpurp_recyc = False
        
        self.createParameter("RT_firstflush", DOUBLE,"")
        self.createParameter("RT_maxdepth", DOUBLE,"")
        self.createParameter("RT_mindead", DOUBLE,"")
        self.createParameter("RT_shape_circ", BOOL,"")
        self.createParameter("RT_shape_rect", BOOL,"")
        self.createParameter("RT_sbmodel", STRING,"")
        self.createParameter("RTdesignD4W", BOOL,"")
        self.createParameter("RTdescur_path", STRING,"")
        self.createParameter("RTavglife", DOUBLE,"")
        self.RT_firstflush = 2          #first flush volume [mm]
        self.RT_maxdepth = 2            #max tank depth [m]
        self.RT_mindead = 0.1           #minimum dead storage level [m]
        self.RT_shape_circ = True       #consider circular tanks
        self.RT_shape_rect = True       #consider rectangular tanks
        self.RT_sbmodel = "ybs"         #storage-behaviour model settings
        self.RTdesignD4W = True         #use DAnCE4Water's default curves to design system?
        self.RTdescur_path = "no file"  #path for design curve
        self.RTavglife = 20             #average life span of a raintank
        
        #---SAND/PEAT/GRAVEL FILTER [SF]----------------------------------------
        self.createParameter("SFstatus", BOOL,"")
        self.SFstatus = 0
        
        #---SUBSURFACE IRRIGATION SYSTEM [IRR]---###TBA###----------------------
        self.createParameter("IRRstatus", BOOL,"")
        self.IRRstatus = 0
        
        #---SUBSURFACE WETLAND/REED BED [WSUB]----------------------------------
        self.createParameter("WSUBstatus", BOOL,"")
        self.WSUBstatus = 0
        
        #---SURFACE WETLAND [WSUR]----------------------------------------------
        self.createParameter("WSURstatus", BOOL,"")
        self.WSURstatus = 1
        
        #Available Scales
        self.createParameter("WSURneigh", BOOL,"")
	self.createParameter("WSURprec", BOOL,"")
        self.WSURneigh = True
        self.WSURprec = True
        
        #Available Applications
        self.createParameter("WSURflow", BOOL,"")
        self.createParameter("WSURpollute", BOOL,"")
        self.WSURflow = True
        self.WSURpollute = True
        
        #Design Curves
        self.createParameter("WSURdesignUB", BOOL,"")
        self.createParameter("WSURdescur_path", STRING,"")
        self.WSURdesignUB = True          #use DAnCE4Water's default curves to design system?
        self.WSURdescur_path = "no file"  #path for design curve
        
        #Design Information
	self.createParameter("WSURspec_EDD", DOUBLE,"")
	self.createParameter("WSURmaxsize", DOUBLE,"")
	self.createParameter("WSURavglife", DOUBLE,"")
        self.WSURspec_EDD = 0.75
        self.WSURmaxsize = 9999999           #maximum surface area of system in sqm
	self.WSURavglife = 20             #average life span of a wetland

        #---SWALES & BUFFER STRIPS [SW]-----------------------------------------
        self.createParameter("SWstatus", BOOL,"")
        self.SWstatus = 1
        
        #Available Scales
        self.createParameter("SWstreet", BOOL,"")
        self.SWstreet = True
        
        #Available Applications
        self.createParameter("SWflow", BOOL,"")
        self.createParameter("SWpollute", BOOL,"")
        self.SWflow = True
        self.SWpollute = True
        
        #Design Curves
        self.createParameter("SWdesignUB", BOOL,"")
        self.createParameter("SWdescur_path", STRING,"")
        self.SWdesignUB = True          #use DAnCE4Water's default curves to design system?
        self.SWdescur_path = "no file"  #path for design curve
        
        #Design Information
        self.createParameter("SWspec", DOUBLE,"")
        self.createParameter("SWmaxsize", DOUBLE,"")
        self.createParameter("SWavglife", DOUBLE,"")
        self.SWspec = 0
        self.SWmaxsize = 9999           #maximum surface area of system in sqm
	self.SWavglife = 20             #average life span of a swale
        
        #---TREE PITS [TPS]---###TBA###-----------------------------------------
        self.createParameter("TPSstatus", BOOL,"")
        self.TPSstatus = 0
        
        #---URINE-SEPARATING TOILET [UT]---###TBA###----------------------------
        self.createParameter("UTstatus", BOOL,"")
        self.UTstatus = 0
        
        #---WASTEWATER RECOVERY & RECYCLING PLANT [WWRR]---###TBA###------------
        self.createParameter("WWRRstatus", BOOL,"")
        self.WWRRstatus = 0
        
        #---WATERLESS/COMPOSTING TOILETS [WT]---###TBA###-----------------------
        self.createParameter("WTstatus", BOOL,"")
        self.WTstatus = 0
        
        #---WATER EFFICIENT APPLIANCES [WEF]------------------------------------
        self.createParameter("WEFstatus", BOOL,"")
        self.WEFstatus = 0
        
        self.createParameter("WEF_implement_method", STRING,"")
        self.createParameter("LEG_force", BOOL,"")
        self.createParameter("LEG_minrate", DOUBLE,"")
        self.createParameter("PPP_force", BOOL,"")
        self.createParameter("PPP_likelihood", DOUBLE,"")
        self.createParameter("SEC_force", BOOL,"")
        self.createParameter("SEC_urbansim", BOOL,"")
        self.createParameter("D4W_UDMactive", BOOL,"")
        self.createParameter("D4W_STMactive", BOOL,"")
        self.createParameter("D4W_EVMactive", BOOL,"")
        self.WEF_implement_method = "LEG"
        self.LEG_force = False
        self.LEG_minrate = 5
        self.PPP_force = False
        self.PPP_likelihood = 50
        self.SEC_force = False
        self.SEC_urbansim = False
        self.D4W_UDMactive = False
        self.D4W_STMactive = False
        self.D4W_EVMactive = False
        
        self.createParameter("WEF_rating_system", STRING,"")
        self.createParameter("WEF_loc_famhouse", BOOL,"")
        self.createParameter("WEF_loc_apart", BOOL,"")
        self.createParameter("WEF_loc_nonres", BOOL,"")
        self.createParameter("WEF_flow_method", STRING,"")
        self.WEF_rating_system = "AS"
        self.WEF_loc_famhouse = True
        self.WEF_loc_apart = True
        self.WEF_loc_nonres = True
        self.WEF_flow_method = "M"
        
        #---REGIONAL INFORMATION -----------------------------------------------
        self.createParameter("regioncity", STRING,"")
        self.regioncity = "Melbourne"
        
        #---MULTI-CRITERIA INPUTS-----------------------------------------------
        #SELECT EVALUATION METRICS
        self.createParameter("scoringmatrix_path", STRING,"")
        self.createParameter("scoringmatrix_default", BOOL,"")
        self.scoringmatrix_path = "C:/UrbanBEATSv1Dev/ub_modules/resources/mcadefault.csv"
        self.scoringmatrix_default = False
        
        #CUSTOMIZE EVALUATION CRITERIA
        self.createParameter("bottomlines_tech", BOOL,"")
        self.createParameter("bottomlines_env", BOOL,"")
        self.createParameter("bottomlines_ecn",BOOL,"")
        self.createParameter("bottomlines_soc", BOOL,"")
        self.createParameter("bottomlines_tech_n", DOUBLE,"")
        self.createParameter("bottomlines_env_n", DOUBLE,"")
        self.createParameter("bottomlines_ecn_n", DOUBLE,"")
        self.createParameter("bottomlines_soc_n", DOUBLE,"")
        self.createParameter("bottomlines_tech_w", DOUBLE,"")
        self.createParameter("bottomlines_env_w", DOUBLE,"")
        self.createParameter("bottomlines_ecn_w", DOUBLE,"")
        self.createParameter("bottomlines_soc_w", DOUBLE,"")
        self.bottomlines_tech = True   #Include criteria? Yes/No
        self.bottomlines_env = True
        self.bottomlines_ecn = True
        self.bottomlines_soc = True
        self.bottomlines_tech_n = 4     #Metric numbers
        self.bottomlines_env_n = 5
        self.bottomlines_ecn_n = 2
        self.bottomlines_soc_n = 4
        self.bottomlines_tech_w = 1     #Criteria Weights
        self.bottomlines_env_w = 1
        self.bottomlines_ecn_w = 1
        self.bottomlines_soc_w = 1
        self.mca_techlist, self.mca_tech, self.mca_env, self.mca_ecn, self.mca_soc = [], [], [], [], [] #initialize as globals
        
        #SCORING OF STRATEGIES
        self.createParameter("scope_stoch", BOOL,"")
        self.createParameter("score_method", STRING,"")
        self.createParameter("ingroup_scoring", STRING,"")
        self.scope_stoch = False
        self.score_method = "AHP"       #MCA scoring method
        self.ingroup_scoring = "Avg"
        
        #RANKING OF STRATEGIES
        self.createParameter("ranktype", STRING,"")
        self.createParameter("topranklimit", DOUBLE,"")
        self.createParameter("conf_int", DOUBLE,"")
        self.ranktype = "RK"            #CI = Confidence Interval, RK = ranking
        self.topranklimit = 10
        self.conf_int = 95
        
        #ADVANCED PARAMETERS & VARIABLES
        self.createParameter("dcvdirectory", STRING, "")
        self.dcvdirectory = "C:/UrbanBEATSv1Dev/ub_modules/wsuddcurves/"
        self.technames = ["ASHP", "AQ", "ASR", "BF", "GR", "GT", 
                          "GPT", "IS", "PPL", "PB", "PP", "RT", 
                          "SF", "IRR", "WSUB", "WSUR", "SW", 
                          "TPS", "UT", "WWRR", "WT", "WEF"]
        self.scaleabbr = ["lot", "street", "neigh", "prec"]
        
        self.sqlDB = 0  #Global variable to hold the 
        self.dbcurs = 0 #cursor to execute sqlcommands
        
	#Views
	self.blocks = View("Block", FACE,WRITE)
	self.blocks.getAttribute("Status")
	self.blocks.addAttribute("HasLotS")
	self.blocks.addAttribute("HasNeighS")
	self.blocks.addAttribute("HasStreetS")
	self.blocks.addAttribute("HasPrecS")
	self.blocks.addAttribute("MaxLotDeg")
	self.blocks.addAttribute("IAServiced")
	self.blocks.addAttribute("IADeficit")
	self.blocks.addAttribute("UpstrImpTreat")

	self.mapattributes = View("GlobalMapAttributes", COMPONENT,READ)
	self.mapattributes.getAttribute("NumBlocks")
	
	self.sysGlobal = View("SystemGlobal", COMPONENT, WRITE)
        self.sysGlobal.getAttribute("TotalSystems")
        
        self.sysAttr = View("SystemAttribute", COMPONENT, WRITE)
        
        self.wsudAttr = View("WsudAttr", NODE, WRITE)
	self.wsudAttr.addAttribute("ScaleN")
	self.wsudAttr.addAttribute("Scale")
	self.wsudAttr.addAttribute("Location")
	self.wsudAttr.addAttribute("Type")
	self.wsudAttr.addAttribute("TypeN")
	self.wsudAttr.addAttribute("Qty")
	self.wsudAttr.addAttribute("GoalQty")
	self.wsudAttr.addAttribute("Degree")
	self.wsudAttr.addAttribute("SysArea")
	self.wsudAttr.addAttribute("Status")
	self.wsudAttr.addAttribute("Year")
	self.wsudAttr.addAttribute("EAFact")
	self.wsudAttr.addAttribute("ImpT")
	self.wsudAttr.addAttribute("CurImpT")
	self.wsudAttr.addAttribute("Upgrades")
	self.wsudAttr.addAttribute("WDepth")
	self.wsudAttr.addAttribute("FDepth")
	self.wsudAttr.addAttribute("StrategyNr")
        
	#Datastream
	datastream = []
	datastream.append(self.mapattributes)
	datastream.append(self.blocks)
        datastream.append(self.sysGlobal)
        datastream.append(self.sysAttr)
        
	self.addData("City", datastream)
	
	self.BLOCKIDtoUUID = {}
        self.SYSTEMIDtoUUID = {}

    def run(self):
        city = self.getData("City")
	self.initBLOCKIDtoUUID(city)
        strvec = city.getUUIDsOfComponentsInView(self.mapattributes)
        map_attr = city.getComponent(strvec[0])
        
        #SET DESIGN CURVES DIRECTORY        
#	homeDir = os.environ['HOME']
#	dcvdirectory = homeDir + '/Documents/UrbanBEATS/UrbanBeatsModules/wsuddcurves/'
#	print dcvdirectory
	#dcvdirectory = "C:\\Users\\Peter M Bach\\Documents\\UrbanBEATS Development\\__urbanBEATS\\wsuddcurves\\"
	dcvdirectory = "./UrbanBEATS/UrbanBeatsModules/wsuddcurves/"
	#dcvdirectory = "C:\\Heiko\\WSC\\data\\wsuddcurves\\"
	
        #GET NECESSARY GLOBAL DATA TO DO ANALYSIS
        blocks_num = map_attr.getAttribute("NumBlocks").getDouble()     #number of blocks to loop through
        self.block_size = map_attr.getAttribute("BlockSize").getDouble()    #size of block
        map_w = map_attr.getAttribute("WidthBlocks").getDouble()        #num of blocks wide
        map_h = map_attr.getAttribute("HeightBlocks").getDouble()       #num of blocks tall
        input_res = map_attr.getAttribute("InputReso").getDouble()      #resolution of input data
        basins = map_attr.getAttribute("TotalBasins").getDouble()
        
        #Create Technologies Shortlist - THIS IS THE USER'S CUSTOMISED SHORTLIST
        userTechList = self.compileUserTechList()               #holds the active technologies selected by user for simulation
        
        print userTechList
        
        #Create technology list for scales
        techListLot = self.fillScaleTechList("lot", userTechList)
        techListStreet = self.fillScaleTechList("street", userTechList)
        techListNeigh = self.fillScaleTechList("neigh", userTechList)
        techListSubbas = self.fillScaleTechList("subbas", userTechList)
        
        #PROCESS MCA Parameters and Scoring Details
        self.mca_techlist, self.mca_tech, self.mca_env, self.mca_ecn, self.mca_soc = self.retrieveMCAscoringmatrix()
        
        ###-------------------------------------------------------------------###
        #  FIRST LOOP - RETROFIT ALGORITHM                                      #
        ###-------------------------------------------------------------------###
        self.initSYSTEMIDtoUUID(city)   #initialize indexing of systems vector
        #Do the retrofitting
        
        
        ###-------------------------------------------------------------------###
        #  SECOND LOOP - OPPORTUNITIES ASSESSMENT ACROSS SCALES & IN-BLOCK TOP  #
        #                RANKED OPTIONS (ACROSS BLOCKS)                         #
        ###-------------------------------------------------------------------###
        #Initialize the database
        if os.path.isfile(r"D:\ubeatsdb1.db"):
            os.remove(r"D:\ubeatsdb1.db")
        self.sqlDB = sqlite3.connect(r"D:\ubeatsdb1.db")
        self.dbcurs = self.sqlDB.cursor()
        
        #Create Table for Individual Systems
        self.dbcurs.execute('''CREATE TABLE watertechs(BlockID, Type, Size, Scale, Service, Areafactor, Landuse, Designdegree)''')
        self.dbcurs.execute('''CREATE TABLE blockstrats(BlockID, Bin, RESType, RESQty, RESservice, HDRType, HDRQty, HDRService,
                            LIType, LIQty, LIService, HIType, HIQty, HIService, COMType, COMQty, COMService, StreetType, StreetQty, 
                            StreetService, NeighType, NeighQty, NeighService, TotService, MCATech, MCAEnv, MCAEcn, MCASoc, MCATotal)''')
        inblock_options = {}
        for i in range(int(blocks_num)):
            currentID = i+1
            print "Current on Block ",currentID
            currentAttList = self.getBlockUUID(currentID, city)
            if currentAttList.getAttribute("Status").getDouble() == 0:
                print "Block not active in simulation"
                continue
            
            #INITIALIZE VECTORS
            lot_techRES = []
            lot_techHDR = []
            lot_techLI = []
            lot_techHI = []
            lot_techCOM = []
            street_tech = []
            neigh_tech = []
            subbas_tech = []
            
            #Assess Lot Opportunities
            if len(techListLot) != 0:
                lot_techRES, lot_techHDR, lot_techLI, lot_techHI, lot_techCOM = self.assessLotOpportunities(techListLot, currentAttList)
            else:
                lot_techRES.append(0)      #append the "Do Nothing Option regardless"
                lot_techHDR.append(0)
                lot_techLI.append(0)
                lot_techHI.append(0)
                lot_techCOM.append(0)
                
            #Assess Street Opportunities
            if len(techListStreet) != 0:
                street_tech = self.assessStreetOpportunities(techListStreet, currentAttList)
            else:
                street_tech.append(0)
                
            #Assess Neigh Opportunities
            if len(techListNeigh) != 0:
                neigh_tech = self.assessNeighbourhoodOpportunities(techListNeigh, currentAttList)
            else:
                neigh_tech.append(0)
                
            #Assess Precinct Opportunities
            if len(techListSubbas) != 0:
                subbas_tech = self.assessSubbasinOpportunities(techListSubbas, currentAttList, city)
            else:
                subbas_tech.append(0)
            
            
                
            inblock_options["BlockID"+str(currentID)] = self.constructInBlockOptions(currentAttList, lot_techRES, lot_techHDR, lot_techLI, lot_techHI, lot_techCOM, street_tech, neigh_tech)
        self.sqlDB.commit()
        ###-------------------------------------------------------------------###
        #  THIRD LOOP - MONTE CARLO (ACROSS BASINS)                              #
        ###-------------------------------------------------------------------###
        gc.collect()
        
        
        ###-------------------------------------------------------------------###
        #  PICK FINAL OPTIONS                                                   #
        ###-------------------------------------------------------------------###
        self.sqlDB.close()
        
        
        
    ########################################################
    #TECHPLACEMENT SUBFUNCTIONS                            #
    ########################################################
    def compileUserTechList(self):
        """Compiles a dictionary of the technologies the user should use and at
        what scales these different technologies should be used. Results are 
        presented as a dictionary:
            userTechList = { "TechAbbreviation" : [boolean, boolean, boolean, boolean], }
                            each boolean corresponds to one of the four scales in the order
                            lot, street, neighbourhood, sub-basin
        """
        userTechList = {}
        for j in self.technames:
            if eval("self."+j+"status == 1"):
                userTechList[j] = [0,0,0,0]
                for k in range(len(self.scaleabbr)):
                    k_scale = self.scaleabbr[k]
                    try:
                        if eval("self."+str(j)+str(k_scale)+"==1"):
                            userTechList[j][k] = 1
                    except NameError:
                        pass
        return userTechList
    
    
    def fillScaleTechList(self, scale, userTechList):
        """Returns a vector of tech abbreviations for a given scale of application
        by scanning the userTechList dictionary. Used to fill out the relevant variables
        that will be called when assessing opportunities
            - Inputs: scale (the desired scale to work with, note that subbas and prec are interchangable)
                    userTechList (the created dictionary output from self.compileUserTechList()
        """
        techlist = []
        if eval("self.strategy_"+scale+"_check == 1"):
            if scale == "subbas":
                scalelookup = "prec"
            else:
                scalelookup = scale
            scaleindex = self.scaleabbr.index(scalelookup)
            for key in userTechList.keys():
                if userTechList[key][scaleindex] == 1:
                    techlist.append(key)
                else:
                    pass
            return techlist
        else:
            return techlist


    def getDCVPath(self, techType):
        """Retrieves the string for the path to the design curve file, whether it is a custom loaded
        design curve or the UB default curves.
        """
        if eval("self."+techType+"designUB"):
            if techType in ["BF", "IS"]:
                return self.dcvdirectory+techType+"-EDD"+str(eval("self."+techType+"spec_EDD"))+"m-FD"+str(eval("self."+techType+"spec_FD"))+"m-DC.dcv"
            elif techType in ["PB"]:
                return self.dcvdirectory+techType+"-MD"+str(eval("self."+techType+"spec_MD"))+"m-DC.dcv"
            elif techType in ["WSUR"]:
                return self.dcvdirectory+techType+"-EDD"+str(eval("self."+techType+"spec_EDD"))+"m-DC.dcv"
            
            else:
                return "No DC Located"
        else:
            return eval("self."+techType+"descur_path")
    
    
    def getTechnologyApplications(self, j):
        """Simply creates a boolean list of whether a particular technology was chosen for flow management
        water quality control and/or water recycling, this list will inform the sizing of the system.
        """
        try:
            purposeQ = eval("self."+j+"flow")
        except NameError:
            purposeQ = 0
        try:
            purposeWQ = eval("self."+j+"pollute")
        except NameError:
            purposeWQ = 0
        try:
            purposeREC = eval("self."+j+"harvest")
        except NameError:
            purposeREC = 0
        purposes = [purposeQ, purposeWQ, purposeREC]
        return purposes
    
    def retrieveMCAscoringmatrix(self):
        """Retrieves the Multi-Criteria Assessment Scoring Matrix from either the file
        or the default UrbanBEATS values. Returns the vector data containing all scores.
        """
        mca_scoringmatrix, mca_tech, mca_env, mca_ecn, mca_soc = [], [], [] ,[] ,[]
        if self.scoringmatrix_default:
            mca_fname = "C:/UrbanBEATSv1Dev/ub_modules/resources/mcadefault.csv"  #uses UBEATS default matrix
            #Do something to retrieve UrbanBEATS default matrix, specify default path            
        else:
            mca_fname = self.scoringmatrix_path #loads file
        
        f = open(str(mca_fname), 'r')
        for lines in f:
            readingline = lines.split(',')
            readingline[len(readingline)-1] = readingline[len(readingline)-1].rstrip()
            #print readingline
            mca_scoringmatrix.append(readingline)
        f.close()
        total_metrics = len(mca_scoringmatrix[0])-1    #total number of metrics
        total_tech = len(mca_scoringmatrix)-1          #for total number of technologies
        
        #Grab index of technologies to relate to scores
        mca_techlist = []
        for i in range(len(mca_scoringmatrix)):
            if i == 0:
                continue        #Skip the header line
            mca_techlist.append(mca_scoringmatrix[i][0])
            
        metrics = [self.bottomlines_tech_n, self.bottomlines_env_n, self.bottomlines_ecn_n, self.bottomlines_soc_n]
        if total_metrics != sum(metrics):
            print "Warning, user-defined number of metrics does not match that of loaded file! Attempting to identify metrics!"
            metrics, positions = self.identifyMCAmetriccount(mca_scoringmatrix[0])
        else:
            print "User-defined number of metrics matches that of loaded file!"
            metrics = [self.bottomlines_tech_n, self.bottomlines_env_n, self.bottomlines_ecn_n, self.bottomlines_soc_n, 0]
            techpos, envpos, ecnpos, socpos = [], [], [], []
            poscounter = 1
            for i in range(int(self.bottomlines_tech_n)):
                techpos.append(int(poscounter))
                poscounter += 1
            for i in range(int(self.bottomlines_env_n)):
                envpos.append(int(poscounter))
                poscounter += 1
            for i in range(int(self.bottomlines_ecn_n)):
                ecnpos.append(int(poscounter))
                poscounter += 1
            for i in range(int(self.bottomlines_soc_n)):
                socpos.append(int(poscounter))
                poscounter += 1
            positions = [techpos, envpos, ecnpos, socpos, []]
                
        for lines in range(len(mca_scoringmatrix)):
            if lines == 0:
                continue
            mca_tech.append(self.filloutMCAscorearray(mca_scoringmatrix[lines], metrics[0], positions[0]))
            mca_env.append(self.filloutMCAscorearray(mca_scoringmatrix[lines], metrics[1], positions[1]))
            mca_ecn.append(self.filloutMCAscorearray(mca_scoringmatrix[lines], metrics[2], positions[2]))
            mca_soc.append(self.filloutMCAscorearray(mca_scoringmatrix[lines], metrics[3], positions[3]))
        
        for i in ["tech", "env", "ecn", "soc"]:                     #Runs the check if the criteria was selected
            if eval("self.bottomlines_"+str(i)) == False:           #if not, creates a zero-length empty array
                eval("mca_"+str(i)+" = []")
        
        mca_tech = self.rescaleMCAscorelists(mca_tech)
        mca_env = self.rescaleMCAscorelists(mca_env)
        mca_ecn = self.rescaleMCAscorelists(mca_ecn)
        mca_soc = self.rescaleMCAscorelists(mca_soc)
        
#        print mca_techlist
#        print mca_tech[4]
#        print mca_env[4]
#        print mca_ecn[4]
#        print mca_soc[4]
        return mca_techlist, mca_tech, mca_env, mca_ecn, mca_soc

    def rescaleMCAscorelists(self, list):
        """Rescales the MCA scores based on the number of metrics in each criteria. This gives
        each criteria an equal weighting to start with and can then influence the evaluation
        later on with user-defined final criteria weights.
        """
        for i in range(len(list)):
            for j in range(len(list[i])):
                list[i][j] = list[i][j]/len(list[i])
        return list

    def filloutMCAscorearray(self, line, techcount, techpos):
        """Extracts scores for a particular criteria from a line in the loaded scoring matrix
        and transfers them to the respective array, also converts the value to a float"""
        line_index = []
        print line
        for i in range(int(techcount)):
            line_index.append(float(line[techpos[i]]))
        return line_index


    def identifyMCAmetriccount(self, metriclist):
        """A function to read the MCA file and identify how many technical, environmental
        economics and social metrics have been entered into the list. Returns a vector of
        the suggested correct metric count based on the four different criteria. Note that
        identification of metrics can only be done if the user-defined file has entered
        the criteria titles correctly, i.e. acceptable strings include
            Technical Criteria: "Te#", "Tec#", "Tech#", "Technical#", "Technology#"
                                    or "Technological#"
            Environmental Criteria: "En#", "Env#", "Enviro#", Environ#", Environment#" or
                                    "Environmental#"
            Economics Criteria: "Ec#", "Ecn#", "Econ#", "Economic#", "Economics#" or
                                    "Economical#"
            Social Criteria: "So#", "Soc#", "Social#", "Society#", "Socio#", "Societal#" or
                                    "People#" or "Person#"
        These acceptable strings can either be 'first-letter capitalized', 'all uppsercase'
        or 'all lowercase' format.
        """
        tec, env, ecn, soc, unid = 0,0,0,0,0
        tecpos, envpos, ecnpos, socpos, unidpos = [], [], [], [], []
        
        #List of acceptable strings
        tecstrings = ["Te", "TE", "te", "Tec", "TEC", "tec", "Tech", "TECH", "tech",
                      "Technical", "TECHNICAL", "technical", "Technology", "TECHNOLOGY",
                      "technology", "Technological", "TECHNOLOGICAL", "technological"]
        envstrings = ["En", "EN", "en", "Env", "ENV", "env", "Enviro", "ENVIRO", "enviro",
                      "Environ", "ENVIRON", "environ", "Environment", "ENVIRONMENT",
                      "environment", "Environmental", "ENVIRONMENTAL", "environmental"]
        ecnstrings = ["Ec", "EC", "ec", "Ecn", "ECN", "ecn", "Econ", "ECON", "econ",
                      "Economic", "ECONOMIC", "economic", "Economics", "ECONOMICS", 
                      "economics", "Economical", "ECONOMICAL", "economical"]
        socstrings = ["So", "SO", "so", "Soc", "SOC", "soc", "Social", "SOCIAL", "social",
                      "Society", "SOCIETY", "society", "Socio", "SOCIO", "socio", "Societal",
                      "SOCIETAL", "societal", "People", "PEOPLE", "people", "Person",
                      "PERSON", "person"]
        
        for i in range(len(metriclist)):
            print metriclist[i]
            if i == 0:
                continue
            if str(metriclist[i][0:len(metriclist[i])-1]) in tecstrings:
                tec += 1
                tecpos.append(i)
            elif str(metriclist[i][0:len(metriclist[i])-1]) in envstrings:
                env += 1
                envpos.append(i)
            elif str(metriclist[i][0:len(metriclist[i])-1]) in ecnstrings:
                ecn += 1
                ecnpos.append(i)
            elif str(metriclist[i][0:len(metriclist[i])-1]) in socstrings:
                soc += 1
                socpos.append(i)
            else:
                unid += 1
                unidpos.append(i)
        
        criteriametrics = [tec, env, ecn, soc, unid]
        criteriapos = [tecpos, envpos, ecnpos, socpos, unidpos]
        return criteriametrics, criteriapos
    
    def setupIncrementVector(self, increment):
        """A global function for creating an increment list from the user input 'rigour levels'.
        For example:
            - If Rigour = 4
            - Then Increment List will be:  [0, 0.25, 0.5, 0.75, 1.0]
        Returns the increment list
        """
        incr_matrix = [0]
        for i in range(int(increment)):
            incr_matrix.append(float(1/increment)*(i+1))
        return incr_matrix
    
    def retrieveUpstreamBlockIDs(self, currentAttList):
        """Returns a vector containing all upstream block IDs, allows quick collation of 
        details.
        """
        upstreamstring = currentAttList.getAttribute("UpstrIDs").getString()
        upstreamIDs = upstreamstring.split(',')
        upstreamIDs.remove('')
        
        for i in range(len(upstreamIDs)):
            upstreamIDs[i] = int(upstreamIDs[i])
        if len(upstreamIDs) == 0:
            return []
        else:
            return upstreamIDs

    def retrieveAttributeFromUpstreamIDs(self, city, upstreamID, attribute, calc):
        """Retrieves all values from the list of upstreamIDs with the attribute name
        <attribute> and calculates whatever <calc> specifies
            Input:
                - city: the city datastream with the block Views
                - upstreamID: the vector list of upstream IDs e.g. [3, 5, 7, 8, 10, 15, 22]
                - attribute: an exact string that matches the attribute as saved by other
                            modules
                - calc: the means of calculation, options include
                            'sum' - calculates total sum
                            'average' - calculates average
                            'max' - retrieves the maximum
                            'min' - retrieves the minimum
                            'minNotzero' - retrieves the minimum among non-zero numbers
                            'list' - returns the list itself
                                                            """
        output = 0
        datavector = []
        
        for i in upstreamID:
            blockFace = self.getBlockUUID(i, city)
            if blockFace.getAttribute("Status").getDouble() == 0:
                continue
            datavector.append(blockFace.getAttribute(attribute).getDouble())
        
        if calc == 'sum':
            output = sum(datavector)
        elif calc == 'average':
            pass
        elif calc == 'max':
            pass
        elif calc == 'min':
            pass
        elif calc == 'minNotzero':
            pass
        elif calc == 'list':
            output = datavector
        else:
            print "Error, calc not specified, returning sum"
            output = sum(datavector)
        return output


    def assessLotOpportunities(self, techList, currentAttList):
        """Assesses if the shortlist of lot-scale technologies can be put into the lot scale
        Does this for one block at a time, depending on the currentAttributesList and the techlist
        """
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        tdRES = [0]     #initialize with one option = no technology = 0
        tdHDR = [0]
        tdLI = [0]
        tdHI = [0]
        tdCOM = [0]
        
        #Check first if there is residential lot
        hasHouses = int(currentAttList.getAttribute("HasHouses").getDouble()) * int(self.service_res)
        hasApts = int(currentAttList.getAttribute("HasFlats").getDouble()) * int(self.service_hdr)
        hasLI = int(currentAttList.getAttribute("Has_LI").getDouble()) * int(self.service_li)
        hasHI = int(currentAttList.getAttribute("Has_HI").getDouble()) * int(self.service_hi)
        hasCOM = int(currentAttList.getAttribute("Has_Com").getDouble()) * int(self.service_com)
        if hasHouses + hasApts + hasLI + hasHI + hasCOM == 0:
            return tdRES, tdHDR, tdLI, tdHI, tdCOM
        
        lot_avail_sp = currentAttList.getAttribute("avLt_RES").getDouble() * int(self.service_res)
        hdr_avail_sp = currentAttList.getAttribute("av_HDRes").getDouble() * int(self.service_hdr)
        LI_avail_sp = currentAttList.getAttribute("avLt_LI").getDouble() * int(self.service_li)
        HI_avail_sp = currentAttList.getAttribute("avLt_HI").getDouble() * int(self.service_hi)
        com_avail_sp = currentAttList.getAttribute("avLt_COM").getDouble() * int(self.service_com)
        if lot_avail_sp + hdr_avail_sp + LI_avail_sp + HI_avail_sp + com_avail_sp < 0.0001:    #if there is absolutely no space, then continue
            return tdRES, tdHDR, tdLI, tdHI, tdCOM
        
        #GET INFORMATION FROM VECTOR DATA
        soilK = currentAttList.getAttribute("Soil_k").getDouble()                       #soil infiltration rate on area
        #print "Soil infiltration rate (mm/hr): "+str(soilK)
        Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble() #effective impervious area of one residential allotment
        Aimphdr = currentAttList.getAttribute("HDR_EIA").getDouble()
        AimpLI = currentAttList.getAttribute("LIAeEIA").getDouble()
        AimpHI = currentAttList.getAttribute("HIAeEIA").getDouble()
        AimpCOM = currentAttList.getAttribute("COMAeEIA").getDouble()
        #print "Impervious Area on Lot: ", Aimplot
        #print "Impervious Area on HDR: ", Aimphdr
        #print "Impervious Area on LI: ", AimpLI
        #print "Impervious Area on HI: ", AimpHI
        #print "Impervious Area on COM: ", AimpCOM
        lot_incr = self.setupIncrementVector(self.lot_rigour)
        #print lot_incr
        
        for j in techList:
            tech_applications = self.getTechnologyApplications(j)
            maxsize = eval("self."+j+"maxsize")          #gets the specific system's maximum size
            #Design curve path
            dcvpath = self.getDCVPath(j)            #design curve file as a string
            if hasHouses != 0 and Aimplot > 0.0001 and j not in ["banned","list","of","tech"]:    #Do lot-scale house system
                sys_object = self.designLotTechnology(1.0, Aimplot, j, dcvpath, tech_applications, soilK, maxsize, lot_avail_sp, "RES", currentID)
                if sys_object == 0:
                    pass
                else:
                    pass
                    tdRES.append(sys_object)
                
            if hasApts != 0 and Aimphdr > 0.0001 and j not in ["banned","list","of","tech"]:    #Do apartment lot-scale system
                for i in lot_incr:
                    if i == 0:
                        continue
                    sys_object = self.designLotTechnology(i, Aimphdr, j, dcvpath, tech_applications, soilK, maxsize, hdr_avail_sp, "HDR", currentID)
                    if sys_object == 0:
                        pass
                    else:
                        pass
                        tdHDR.append(sys_object)
                    
           
            if hasLI != 0 and AimpLI > 0.0001 and j not in ["banned","list","of","tech"]:
                for i in lot_incr:
                    if i == 0:
                        continue
                    sys_object = self.designLotTechnology(i, AimpLI, j, dcvpath, tech_applications, soilK, maxsize, LI_avail_sp, "LI", currentID)
                    if sys_object == 0:
                        pass
                    else:
                        pass
                        tdLI.append(sys_object)
                                           
            if hasHI != 0 and AimpHI > 0.0001 and j not in ["banned","list","of","tech"]:
                for i in lot_incr:
                    if i == 0:
                        continue
                    sys_object = self.designLotTechnology(i, AimpHI, j, dcvpath, tech_applications, soilK, maxsize, HI_avail_sp, "HI", currentID)
                    if sys_object == 0:
                        pass
                    else:
                        pass
                        tdLI.append(sys_object)
            
            if hasCOM != 0 and AimpCOM > 0.0001 and j not in ["banned","list","of","tech"]:
                for i in lot_incr:
                    if i == 0:
                        continue
                    sys_object = self.designLotTechnology(i, AimpCOM, j, dcvpath, tech_applications, soilK, maxsize, com_avail_sp, "COM", currentID)
                    if sys_object == 0:
                        pass
                    else:
                        pass
                        tdLI.append(sys_object)
            
            #Can insert more land uses here in future e.g. municipal
        return tdRES, tdHDR, tdLI, tdHI, tdCOM
    
    def designLotTechnology(self, incr, Aimp, techabbr, dcvpath, tech_applications, soilK, maxsize, avail_sp, landuse, currentID):
        """Carries out the lot-scale design for a given system type on a given land use. This function is
        used for the different land uses that can accommodate lot-scale technologies in the model.
        """            
        Adesign_imp = Aimp * incr
        Asystem = eval('td.design_'+str(techabbr)+'('+str(Adesign_imp)+',"'+str(dcvpath)+'",'+str(self.targetsvector)+','+str(tech_applications)+','+str(soilK)+','+str(maxsize)+')')
        #print Asystem
        if Asystem[0] < avail_sp:
            #print "Fits"
            self.dbcurs.execute("INSERT INTO watertechs VALUES ("+str(currentID)+",'"+str(techabbr)+"',"+str(Asystem[0])+",'L',"+str(Adesign_imp)+","+str(Asystem[1])+",'"+str(landuse)+"',"+str(incr)+")")
            sys_object = tt.WaterTech(techabbr, Asystem[0], 'L', Adesign_imp, Asystem[1], landuse, currentID)
            sys_object.setDesignIncrement(incr)
            return sys_object
        else:
            #print "Does not fit"
            return 0
    
    def assessStreetOpportunities(self, techList, currentAttList):
        """Assesses if the shortlist of street-scale technologies can be put into the streetscape
        Does this for one block at a time, depending on the currentAttributesList and the techlist
        """
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        technologydesigns = []
        #Check first if there is residential lot to manage
        hasHouses = int(currentAttList.getAttribute("HasHouses").getDouble())
        if hasHouses == 0:
            return technologydesigns
        
        street_avail_Res = currentAttList.getAttribute("avSt_RES").getDouble()
        if street_avail_Res < 0.0001:
            return technologydesigns
        
        #GET INFORMATION FROM VECTOR DATA
        allotments = currentAttList.getAttribute("ResAllots").getDouble()
        soilK = currentAttList.getAttribute("Soil_k").getDouble()
        
        Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
        AimpRes = Aimplot * allotments
        AimpstRes = currentAttList.getAttribute("ResFrontT").getDouble() - currentAttList.getAttribute("av_St_RES").getDouble
        
        Aimphdr = currentAttList.getAttribute("HDR_EIA").getDouble()
        
        lot_incr = self.setupIncrementVector(self.lot_rigour)
        street_incr = self.setupIncrementVector(self.street_rigour)
        
        for j in techList:
            tech_applications = self.getTechnologyApplications(j)
            maxsize = eval("self."+j+"maxsize")          #gets the specific system's maximum size
            #Design curve path
            dcvpath = self.getDCVPath(j)
            
            for lot_deg in lot_incr:
                AimpremainRes = AimpstRes + (AimpRes - Aimplot * allotments * lot_deg) #street + remaining lot
                AimpremainHdr = Aimphdr*(1.0-lot_deg)
                
                for street_deg in street_incr:
                    if street_deg == 0:
                        continue
                    AimptotreatRes = AimpremainRes * street_deg
                    AimptotreatHdr = AimpremainHdr * street_deg
                        
                    if hasHouses != 0 and AimptotreatRes > 0.0001:
                        Asystem = eval('td.design_'+str(j)+'('+str(AimptotreatRes)+',"'+str(dcvpath)+'",'+str(self.targetsvector)+','+str(tech_applications)+','+str(soilK)+','+str(maxsize)+')')
                        #print Asystem
                        if Asystem[0] < street_avail_Res:
                            #print "Fits"
                            self.dbcurs.execute("INSERT INTO watertechs VALUES ("+str(currentID)+",'"+str(j)+"',"+str(Asystem[0])+",'S',"+str(AimptotreatRes)+","+str(Asystem[1])+",'Street',"+str(street_deg)+")")
                            sys_object = tt.WaterTech(j, Asystem[0], 'S', AimptotreatRes, Asystem[1], "Street", currentID)
                            sys_object.setDesignIncrement([lot_deg, street_deg])
                            technologydesigns.append(sys_object)
                        else:
                            pass
                            #print "Does not fit"
        return technologydesigns


    def assessNeighbourhoodOpportunities(self, techList, currentAttList):
        """Assesses if the shortlist of neighbourhood-scale technologies can be put in local parks 
        & other areas. Does this for one block at a time, depending on the currentAttributesList 
        and the techlist
        """
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        technologydesigns = []
        
        #Grab total impervious area and available space
        AblockEIA = currentAttList.getAttribute("Blk_EIA").getDouble()
        if AblockEIA <= 0.0001:
            return technologydesigns
        
        av_PG = currentAttList.getAttribute("PG_av").getDouble()
        av_REF = currentAttList.getAttribute("REF_av").getDouble()
        totalavailable = av_PG + av_REF
        if totalavailable < 0.0001:
            return technologydesigns
        
        #GET INFORMATION FROM VECTOR DATA
        allotments = currentAttList.getAttribute("ResAllots").getDouble()
        soilK = currentAttList.getAttribute("Soil_k").getDouble()
        
        Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
        Aimphdr = currentAttList.getAttribute("HDR_EIA").getDouble()
        
        lot_incr = self.setupIncrementVector(self.lot_rigour)
        neigh_incr = self.setupIncrementVector(self.neigh_rigour)
        
        for j in techList:
            tech_applications = self.getTechnologyApplications(j)
            maxsize = eval("self."+j+"maxsize")         #Gets the specific system's maximum size
            #Design curve path
            dcvpath = self.getDCVPath(j)
            for lot_deg in lot_incr:
                Aimpremain = AblockEIA - lot_deg*allotments*Aimplot - lot_deg*Aimphdr
                for neigh_deg in neigh_incr:
                    if neigh_deg == 0:
                        continue
                    Aimptotreat=  neigh_deg * Aimpremain
                    if Aimptotreat > 0.0001:
                        Asystem = eval('td.design_'+str(j)+'('+str(Aimptotreat)+',"'+str(dcvpath)+'",'+str(self.targetsvector)+','+str(tech_applications)+','+str(soilK)+','+str(maxsize)+')')
                        #print Asystem
                        if Asystem[0] < totalavailable:
                            #print "Fits"
                            self.dbcurs.execute("INSERT INTO watertechs VALUES ("+str(currentID)+",'"+str(j)+"',"+str(Asystem[0])+",'N',"+str(Aimptotreat)+","+str(Asystem[1])+",'Neigh',"+str(neigh_deg)+")")
                            sys_object = tt.WaterTech(j, Asystem[0], 'N', Aimptotreat, Asystem[1], "Neigh", currentID)
                            sys_object.setDesignIncrement(neigh_deg)
                            technologydesigns.append(sys_object)
                        else:
                            pass
                            #print "System Does not fit"
        return technologydesigns

    def assessSubbasinOpportunities(self, techList, currentAttList, city):
        """Assesses if the shortlist of sub-basin-scale technologies can be put in local parks 
        & other areas. Does this for one block at a time, depending on the currentAttributesList 
        and the techlist
        """
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        technologydesigns = []  #Three Conditions: 1) there must be upstream blocks
                                                 # 2) there must be space available, 
                                                 # 3) there must be impervious to treat
        soilK = currentAttList.getAttribute("Soil_k").getDouble()
        #CONDITION 1: Grab Block's Upstream Area
        upstreamIDs = self.retrieveUpstreamBlockIDs(currentAttList)
        if len(upstreamIDs) == 0:
            print "Current Block has no upstream areas, skipping"
            return technologydesigns
        
        #CONDITION 2: Grab Total available space, if there is none, no point continuing
        av_PG = currentAttList.getAttribute("PG_av").getDouble()
        av_REF = currentAttList.getAttribute("REF_av").getDouble()
        totalavailable = av_PG + av_REF
        #print "Total Available Space in BLock to do STUFF: ", totalavailable
        if totalavailable < 0.0001:
            return technologydesigns
        
        #CONDITION 3: Get Block's upstream Impervious area
        upstreamImp = self.retrieveAttributeFromUpstreamIDs(city, upstreamIDs, "Blk_EIA", "sum")
        #print "Total Upstream Impervious Area: ", upstreamImp
        if upstreamImp < 0.0001:
            return technologydesigns
        
        subbas_incr = self.setupIncrementVector(self.subbas_rigour)
        #print "Now designing tech ", subbas_incr

        for j in techList:
            #print j
            tech_applications = self.getTechnologyApplications(j)
            maxsize = eval("self."+j+"maxsize")     #Gets the specific system's maximum allowable size
            #Design curve path
            dcvpath = self.getDCVPath(j)
            for bas_deg in subbas_incr:
                #print bas_deg
                if bas_deg == 0:
                    continue
                Aimptotreat = upstreamImp * bas_deg
                #print "Aimp to treat: ", Aimptotreat
                if Aimptotreat > 0.0001:
                    Asystem = eval('td.design_'+str(j)+'('+str(Aimptotreat)+',"'+str(dcvpath)+'",'+str(self.targetsvector)+','+str(tech_applications)+','+str(soilK)+','+str(maxsize)+')')
                    #print Asystem
                    if Asystem[0] < totalavailable:
                        #print "Fits"
                        self.dbcurs.execute("INSERT INTO watertechs VALUES ("+str(currentID)+",'"+str(j)+"',"+str(Asystem[0])+",'B',"+str(Aimptotreat)+","+str(Asystem[1])+",'Subbas',"+str(bas_deg)+")")
                        sys_object = tt.WaterTech(j, Asystem[0], 'N', Aimptotreat, Asystem[1], "Subbas", currentID)
                        sys_object.setDesignIncrement(bas_deg)
                        technologydesigns.append(sys_object)
                    else:
                        pass
                        #print "Does not fit"
        return technologydesigns

    def constructInBlockOptions(self, currentAttList, lot_techRES, lot_techHDR, lot_techLI, lot_techHI, lot_techCOM, street_tech, neigh_tech):
        """Tries every combination of technology and narrows down the list of in-block
        options based on MCA scoring and the Top Ranking Configuration selected by the
        user. Returns an array of the top In-Block Options for piecing together with
        sub-basin scale systems
        """
        allInBlockOptions = {}
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        blockarea = pow(self.block_size,2)*currentAttList.getAttribute("Active").getDouble()
        lot_incr = self.setupIncrementVector(self.lot_rigour)
        street_incr = self.setupIncrementVector(self.street_rigour)
        neigh_incr = self.setupIncrementVector(self.neigh_rigour)
        subbas_incr = self.setupIncrementVector(self.subbas_rigour)
        for i in range(len(subbas_incr)):         #[0, 0.25, 0.5, 0.75, 1.0]
            allInBlockOptions[subbas_incr[i]] = []       #Bins are: 0 to 25%, >25% to 50%, >50% to 75%, >75% to 100% of block treatment
        bracketwidth = 1.0/float(self.subbas_rigour)
        
        #Obtain all variables needed to do area balance for Impervious Area Service
        allotments = currentAttList.getAttribute("ResAllots").getDouble()
        estatesLI = currentAttList.getAttribute("LIestates").getDouble()
        estatesHI = currentAttList.getAttribute("HIestates").getDouble()
        estatesCOM = currentAttList.getAttribute("COMestates").getDouble()
        Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
        AimpRes = allotments * Aimplot
        AimpstRes = currentAttList.getAttribute("ResFrontT").getDouble() - currentAttList.getAttribute("av_St_RES").getDouble()
        Aimphdr = currentAttList.getAttribute("HDR_EIA").getDouble()    
        AimpAeLI = currentAttList.getAttribute("LIAeEIA").getDouble()
        AimpLI = AimpAeLI * estatesLI
        AimpAeHI = currentAttList.getAttribute("HIAeEIA").getDouble()
        AimpHI = AimpAeHI * estatesHI
        AimpAeCOM = currentAttList.getAttribute("COMAeEIA").getDouble()
        AimpCOM = AimpAeCOM * estatesCOM
        
        AblockEIA = currentAttList.getAttribute("Blk_EIA").getDouble()
        
        #Obtain all variables needed to do area balance for Public Area Service
        #(for irrigation of open space water recycling)
        #Obtain all variables needed to do demographic balance for Population Service
        #(for potable water substitution)
        
        #---- PROGRAMMER'S NOTES FOR COMBINING LOT, STREET, NEIGHBOURHOOD STRATEGIES -----------------------------------------------------------------------------
        #
        #fill out street tech array based on lot_deg and street_deg
        #(e.g. lot_deg = 0, 0.25, 0.5, 0.75, 1.0 and neigh_deg = 0.25, 0.5, 0.75, 1.0 the Total Combos = 20)
        #3D Array: tech_array_neigh[lot_degree][neigh_degree][combination] written as
        #     Lot Deg   0                         0.25                      0.5                      0.75                     1.00
        #   Neigh Deg   0.25, 0.50, 0.75, 1.00    0.25, 0.50, 0.75, 1.00    0.25, 0.50, 0.75, 1.00   0.25, 0.50, 0.75, 1.00   0.25, 0.50, 0.75, 1.0
        #               [...] [...] [...] [...]     becomes [[[option1, option2, etc.]],[[option1, option2, etc.]],[[option1, option2, etc.]]]
        #
        #Loop through all degrees of implementation and search out the correct one for each, creating a list each time
        #Total options of strategies available is calculated across each scale e.g.
        #           2 Lot scale, 2 street scale, 3 neighbourhood scale at one degree of implementation
        #           = 2+1 x 2+1 x 3+1 = 36 strategies (1 = not to use option at all) 
        #           1L 1S 1N, 1L 1S 2N, 1L 1S 3N    2L 1S, 1N       etc.
        #           1L 2S 1N, 1L 2S 2N, 1L 2S 3N    2L 2S, 1N       etc.
        #Need to check the current combination if it is realistic before coming up with strategies, e.g.
        #           if lot_deg = 0.25, street_deg = 0.25, neigh_deg = 0.25 --> check OK!
        #           if lot_deg = 0.25, street)deg = 0.25, neigh_deg = 1.00 --> check NOT OK! SKIP (neigh_deg + street_deg <= 1)
        #
        #NOTE: NEED TO CHECK HOW IF NO COMBINATIONS ARE IN NEIGHBOURHOOD SCALE TO DEAL WITH THE MAKING OF STRATEGIES
        #
        # --------------------------------------------------------------------------------------------------------------------------------------------------------
        #COMBINE ALL LOT SYSTEMS INTO ONE MASSIVE ARRAY TO LOOP THROUGH
        lot_tech = []
        for a in range(len(lot_incr)):
            lot_deg = lot_incr[a]   #currently working on all lot-scale systems of increment lot_deg
            if lot_deg == 0:
                lot_tech.append([lot_deg,0,0,0,0,0])      #([deg, res, hdr, li, hi, com])
                continue
            for b in lot_techRES:
                for c in lot_techHDR:
                    if c != 0 and c.getDesignIncrement() != lot_deg:
                        continue
                    for d in lot_techLI:
                        if d != 0 and d.getDesignIncrement() != lot_deg:
                            continue
                        for e in lot_techHI:
                            if e != 0 and e.getDesignIncrement() != lot_deg:
                                continue
                            for f in lot_techCOM:
                                if f != 0 and f.getDesignIncrement() != lot_deg:
                                    continue
                                lot_tech.append([lot_deg, b, c, d, e, f])
        if len(street_tech) == 0:
            street_tech.append(0)
        if len(neigh_tech) == 0:
            neigh_tech.append(0)
        #Combine all three scales together
        for a in lot_tech:
            for b in street_tech:
                for c in neigh_tech:
                    lot_deg = a[0]
                    combo = [a[1], a[2], a[3], a[4], a[5], b, c]
                    
                    #print "Combo: ", combo
                    lotcounts = [int(lot_deg * allotments), int(1), int(estatesLI), int(estatesHI), int(estatesCOM),int(1),int(1)]
                    
                    if allotments != 0 and int(lot_deg*allotments) == 0:
                        continue        #the case of minimal allotments on-site where multiplying by lot-deg and truncation returns zero
                                        #this results in totalimpserved = 0, therefore model crashes on ZeroDivisionError
                                        
                    #Check if street + lot systems exceed the requirements
                    if a[1] != 0 and b != 0 and (a[1].getService()*allotments + b.getService()) > (AimpRes+AimpstRes):
                        continue    #Overtreatment occurring in residential district at the lot scale
                    if combo.count(0) == 7:
                        continue
                    
                    totalimpserved = self.getTotalComboService(combo, lotcounts)
                    if totalimpserved > AblockEIA:
                        #print "Overtreatment"
                        continue
                    else:
                        #print "Strategy is fine"
                        #Create Block Strategy and put it into one of the subbas bins of allInBlockOptions
                        servicebin = self.identifyBin(totalimpserved, AblockEIA, subbas_incr)
                        blockstrat = tt.BlockStrategy(combo, totalimpserved, lotcounts, currentID, servicebin)
                        
                        tt.CalculateMCATechScores(blockstrat,AblockEIA, bracketwidth, self.mca_techlist, self.mca_tech, \
                                                  self.mca_env, self.mca_ecn, self.mca_soc)
                        
                        tt.CalculateMCAStratScore(blockstrat, [self.bottomlines_tech_w, self.bottomlines_env_w, \
                                                               self.bottomlines_ecn_w, self.bottomlines_soc_w])
                        
                    if len(allInBlockOptions[servicebin]) < 10:         #If there are less than ten options in each bin...
                        allInBlockOptions[servicebin].append(blockstrat)        #append the current strategy to the list of that bin
                    else:               #Otherwise get bin's lowest score, compare and replace if necessary
                        lowestscore, lowestscoreindex = self.getServiceBinLowestScore(allInBlockOptions[servicebin])
                        if blockstrat.getTotalMCAscore() > lowestscore:
                            allInBlockOptions[servicebin].pop(lowestscoreindex)      #Pop the lowest score and replace
                            allInBlockOptions[servicebin].append(blockstrat)
                            dbs = tt.createDataBaseString(blockstrat)
                                
                        else:
                            blockstrat = 0      #set null reference
        
        #Transfer all to database table
        for key in allInBlockOptions.keys():
            for i in range(len(allInBlockOptions[key])):
                dbs = tt.createDataBaseString(allInBlockOptions[key][i])
                self.dbcurs.execute("INSERT INTO blockstrats VALUES ("+str(dbs)+")")
        
        return allInBlockOptions
    
    def getServiceBinLowestScore(self, binlist):
        """Scans none list of BlockStrategies for the lowest MCA total score and returns
        its value as well as the position in the list.
        """
        scorelist = []
        for i in range(len(binlist)):
            scorelist.append(binlist[i].getTotalMCAscore())
        lowscore = min(scorelist)
        lowscoreindex = scorelist.index(lowscore)
        return lowscore, lowscoreindex
        
    
    def getTotalComboService(self, techarray, lotcounts):
        """Retrieves all the impervious area served by an array of systems and returns
        the value"""
        totalimpserved = 0
        for tech in techarray:
            if tech == 0:
                continue
            if tech.getScale() == "L" and tech.getLandUse() == "RES":
                totalimpserved += tech.getService() * lotcounts[0]
            elif tech.getScale() == "L" and tech.getLandUse() == "LI":
                totalimpserved += tech.getService() * lotcounts[2]
            elif tech.getScale() == "L" and tech.getLandUse() == "HI":
                totalimpserved += tech.getService() * lotcounts[3]
            elif tech.getScale() == "L" and tech.getLandUse() == "COM":
                totalimpserved += tech.getService() * lotcounts[4]
            else:
                totalimpserved += tech.getService()
        return totalimpserved

    def identifyBin(self, totalimpserved, AblockEIA, subbas_incr):
        """Determines what bin to sort a particular service into, used when determining
        which bin a BlockStrategy should go into"""
        servicelevel = totalimpserved/AblockEIA
        bracketwidth = 1.0/float(self.subbas_rigour)
        for i in subbas_incr:
            if i == 0:
                if servicelevel > i and servicelevel < i+(bracketwidth/2):
                    return i
                else:
                    continue
            if servicelevel > (i-(bracketwidth/2)) and servicelevel < (i+(bracketwidth/2)):
                return i
            if i == 1:
                if servicelevel > (i-(bracketwidth/2)) and servicelevel < i:
                    return i
                else:
                    continue
        return max(subbas_incr)
        
    ########################################################
    #DYNAMIND FUNCTIONS                                    #
    ########################################################
    def createInputDialog(self):
        form = activatetechplacementGUI(self, QApplication.activeWindow())
        form.show()
        return True  

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

    def getSystemUUID(self, systemid, city):
        try:
            key = self.SYSTEMIDtoUUID[systemid]
        except KeyError:
            key = ""
        return city.getComponent(key)
    
    def initSYSTEMIDtoUUID(self, city):
        systemuuids = city.getUUIDsOfComponentsInView(self.sysAttr)
        for systemuuid in systemuuids:
            sys = city.getComponent(systemuuid)
            ID = int(round(sys.getAttribute("SystemID").getDouble()))
            self.SYSTEMIDtoUUID[ID] = systemuuid



