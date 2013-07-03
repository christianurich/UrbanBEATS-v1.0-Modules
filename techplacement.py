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
import tech_designbydcv as dcv          #sub-functions that design based on design curves
import tech_designbyeq as deq           #sub-functions that design based on design equations
import tech_designbysim as dsim         #sub-functions that design based on miniature simulations
import ubseriesread as ubseries         #sub-functions responsible for processing climate data

from techplacementguic import *

import os, sqlite3, gc, random
import numpy as np

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
        self.runoff_pri = 0                      #Priority of flood mitigation?
        self.pollute_pri = 0                     #Priority of pollution management?
        self.harvest_pri = 1                     #Priority for harvesting & reuse
	
	self.priorities = []            #ADVANCED PARAMETER, holds the final weights for MCA
	
        #WATER MANAGEMENT TARGETS
        self.createParameter("targets_runoff", DOUBLE,"")
        self.createParameter("targets_TSS", DOUBLE,"")
        self.createParameter("targets_TP", DOUBLE,"")
        self.createParameter("targets_TN", DOUBLE,"")
        self.createParameter("targets_reliability", DOUBLE, "")
        self.targets_runoff = 80            #Runoff reduction target [%]
        self.targets_TSS = 70               #TSS Load reduction target [%]
        self.targets_TP = 30                #TP Load reduction target [%]
        self.targets_TN = 30                #TN Load reduction target [%]
        self.targets_reliability = 80       #required reliability of harvesting systems    
        
        self.system_tarQ = 0            #INITIALIZE THESE VARIABLES
        self.system_tarTSS = 0
        self.system_tarTP = 0
        self.system_tarTN = 0
        self.system_tarREL = 0
        self.targetsvector = []         #---CALCULATED IN THE FIRST LINE OF RUN()
        
        #WATER MANAGEMENT SERVICE LEVELS
        self.createParameter("service_swmQty", DOUBLE, "")
        self.createParameter("service_swmWQ", DOUBLE, "")
        self.createParameter("service_rec", DOUBLE, "")
        self.createParameter("service_res", BOOL, "")
        self.createParameter("service_hdr", BOOL, "")
        self.createParameter("service_com", BOOL, "")
        self.createParameter("service_li", BOOL, "")
        self.createParameter("service_hi", BOOL, "")
        self.createParameter("service_redundancy", DOUBLE, "")
        self.service_swmQty = 50                #required service level for stormwater management
        self.service_swmWQ = 90                 #required service level for stormwater management
        self.service_rec = 50                   #required service level for substituting potable water demand through recycling
        self.service_res = True
        self.service_hdr = True
        self.service_com = True
        self.service_li = True
        self.service_hi = True
        self.service_redundancy = 25
        self.servicevector = []
        
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
        self.lot_rigour = 4
        self.street_rigour = 4
        self.neigh_rigour = 4
        self.subbas_rigour = 4
        
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
        #   WATER USE EFFICIENCY AND RECYCLING STRATEGY DESIGN INPUTS            #
        ##########################################################################
        
        #WATER DEMAND PATTERNS
        #--> Water Demands
        self.createParameter("freq_kitchen", DOUBLE, "")
        self.createParameter("freq_shower", DOUBLE, "")
        self.createParameter("freq_toilet", DOUBLE, "")
        self.createParameter("freq_laundry", DOUBLE, "")
        self.createParameter("dur_kitchen", DOUBLE, "")
        self.createParameter("dur_shower", DOUBLE, "")
        self.createParameter("demandvary_kitchen", DOUBLE, "")
        self.createParameter("demandvary_shower", DOUBLE, "")
        self.createParameter("demandvary_toilet", DOUBLE, "")
        self.createParameter("demandvary_laundry", DOUBLE, "")
        self.createParameter("ffp_kitchen", STRING, "")
        self.createParameter("ffp_shower", STRING, "")
        self.createParameter("ffp_toilet", STRING, "")
        self.createParameter("ffp_laundry", STRING, "")
        self.createParameter("priv_irr_vol", DOUBLE, "")
        self.createParameter("ffp_garden", STRING, "")
        self.freq_kitchen = 2                   #Household Demands START
        self.freq_shower = 2
        self.freq_toilet = 2
        self.freq_laundry = 2
        self.dur_kitchen = 10
        self.dur_shower = 5
        self.demandvary_kitchen = 0.00
        self.demandvary_shower = 0.00
        self.demandvary_toilet = 0.00
        self.demandvary_laundry = 0.00
        self.ffp_kitchen = "SW"
        self.ffp_shower = "SW"
        self.ffp_toilet = "SW"
        self.ffp_laundry = "SW"
        self.priv_irr_vol = 1                   #Private irrigation volume [ML/ha/yr]
        self.ffp_garden = "SW"
        
        self.createParameter("com_demand", DOUBLE, "")
        self.createParameter("com_demandvary", DOUBLE, "")
        self.createParameter("com_demandunits", STRING, "")
        self.createParameter("li_demand", DOUBLE, "")
        self.createParameter("li_demandvary", DOUBLE, "")
        self.createParameter("li_demandunits", STRING, "")
        self.createParameter("hi_demand", DOUBLE, "")
        self.createParameter("hi_demandvary", DOUBLE, "")
        self.createParameter("hi_demandunits", STRING, "")
        self.createParameter("ffp_nonres", STRING, "")
        self.com_demand = 40
        self.com_demandvary = 10
        self.com_demandunits = 'cap'    #sqm = per square metres floor area, cap = per capita
        self.li_demand = 40
        self.li_demandvary = 10
        self.li_demandunits = 'cap'
        self.hi_demand = 40
        self.hi_demandvary = 10
        self.hi_demandunits = 'cap'
        self.ffp_nonres = "SW"

        self.createParameter("public_irr_vol", DOUBLE, "")
        self.createParameter("irrigate_nonres", DOUBLE, "")
        self.createParameter("irrigate_parks", BOOL, "")
        self.createParameter("irrigate_refs", BOOL, "")
        self.createParameter("public_irr_wq", STRING, "")
        self.public_irr_vol = 1
        self.irrigate_nonres = 1
        self.irrigate_parks = 1
        self.irrigate_refs = 0
        self.public_irr_wq = "SW"       #PO = potable, NP = non-potable, RW = rainwater, SW = stormwater, GW = greywater
        
        #WATER EFFICIENCY
        self.createParameter("WEFstatus", BOOL,"")
        self.WEFstatus = 0
        
        self.createParameter("WEF_rating_system", STRING,"")
        self.createParameter("WEF_loc_house", BOOL,"")
        self.createParameter("WEF_loc_apart", BOOL,"")
        self.createParameter("WEF_loc_nonres", BOOL,"")
        self.WEF_rating_system = "AS"
        self.WEF_loc_house = True
        self.WEF_loc_apart = True
        self.WEF_loc_nonres = True
        
        self.createParameter("WEF_method", STRING, "")
        self.createParameter("WEF_c_rating", DOUBLE, "")
        self.createParameter("WEF_d_rating", DOUBLE, "")
        self.createParameter("WEF_distribution", STRING, "")
        self.createParameter("WEF_includezero", BOOL, "")
        self.WEF_method = 'C'   #C = constant, D = distribution
        self.WEF_c_rating = 2   #Number of stars
        self.WEF_d_rating = 5  #Maximum number of stars
        self.WEF_distribution = "UF"     #UF = Uniform, LH = log-normal (high-end), LL = log-normal (low-end), NM = normal
        self.WEF_includezero = True
        
        #REGIONAL RECYCLING-SUPPLY ZONES
        self.createParameter("rec_demrange_min", DOUBLE, "")
        self.createParameter("rec_demrange_max", DOUBLE, "")
        self.createParameter("ww_kitchen", BOOL, "")
        self.createParameter("ww_shower", BOOL, "")
        self.createParameter("ww_toilet", BOOL, "")
        self.createParameter("ww_laundry", BOOL, "")
        self.createParameter("hs_strategy", STRING, "")
        self.rec_demrange_min = 10
        self.rec_demrange_max = 100
        self.ww_kitchen = False         #Kitchen WQ default = GW
        self.ww_shower = False          #Shower WQ default = GW
        self.ww_toilet = False          #Toilet WQ default = BW --> MUST BE RECYCLED
        self.ww_laundry = False         #Laundry WQ default = GW
        self.hs_strategy = "ud"         #ud = upstream-downstream, uu = upstream-upstream, ua = upstream-around
        
        #ADDITIONAL INPUTS
        self.createParameter("sb_method", STRING, "")
        self.createParameter("rain_length", DOUBLE, "")
        self.sb_method = "Sim"  #Sim = simulation, Eqn = equation
        self.rain_length = 2   #number of years.
        
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
        self.lot_renew = 0      #NOT USED UNLESS LOT RENEWAL ALGORITHM EXISTS
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
        self.BFflow = True
	self.BFpollute = True
	
        #Design Curves
        self.createParameter("BFdesignUB", BOOL,"")
        self.createParameter("BFdescur_path", STRING,"")
        self.BFdesignUB = True          #use DAnCE4Water's default curves to design system?
        self.BFdescur_path = "no file"  #path for design curve
        
        #Design Information
        self.createParameter("BFspec_EDD", DOUBLE,"")
        self.createParameter("BFspec_FD", DOUBLE,"")
        self.createParameter("BFminsize", DOUBLE, "")
        self.createParameter("BFmaxsize", DOUBLE,"")
        self.createParameter("BFavglife", DOUBLE,"")
        self.createParameter("BFlined", BOOL,"")
        self.BFspec_EDD = 0.3
        self.BFspec_FD = 0.6
        self.BFminsize = 5              #minimum surface area of the system in sqm
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
        self.createParameter("ISminsize", DOUBLE, "")
        self.createParameter("ISmaxsize", DOUBLE,"")
        self.createParameter("ISavglife", DOUBLE,"")
        self.ISspec_EDD = 0.2
        self.ISspec_FD = 0.8
        self.ISminsize = 5
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
        self.createParameter("PBrecycle", BOOL, "")
        self.PBflow = True
        self.PBpollute = True
        self.PBrecycle = False
        
        #Design Curves
        self.createParameter("PBdesignUB", BOOL,"")
        self.createParameter("PBdescur_path", STRING,"")
        self.PBdesignUB = True          #use DAnCE4Water's default curves to design system?
        self.PBdescur_path = "no file"  #path for design curve
        
        #Design Information
        self.createParameter("PBspec_MD", STRING,"")
        self.createParameter("PBminsize", DOUBLE, "")
        self.createParameter("PBmaxsize", DOUBLE,"")
        self.createParameter("PBavglife", DOUBLE,"")
        self.PBspec_MD = "1.25" 	#need a string for the combo box
        self.PBminsize = 100
        self.PBmaxsize = 9999999           #maximum surface area of system in sqm
	self.PBavglife = 20             #average life span of a pond/basin

        #---POROUS/PERVIOUS PAVEMENT [PP]---###TBA###---------------------------
        self.createParameter("PPstatus", BOOL,"")
        self.PPstatus = 0
        
        #---RAINWATER TANK [RT]-------------------------------------------------
        self.createParameter("RTstatus", BOOL,"")
        self.RTstatus = 0
        
        self.createParameter("RTlot", BOOL,"")
        self.createParameter("RTneigh", BOOL,"")
        self.createParameter("RTflow", BOOL,"")
        self.createParameter("RTrecycle", BOOL,"")
        self.RTlot = True
        self.RTneigh = False
        self.RTflow = False
        self.RTrecycle = True
        
        self.createParameter("RT_maxdepth", DOUBLE,"")
        self.createParameter("RT_mindead", DOUBLE,"")
        self.createParameter("RTdesignUB", BOOL,"")
        self.createParameter("RTdescur_path", STRING,"")
        self.createParameter("RTavglife", DOUBLE,"")
        self.RT_maxdepth = 2            #max tank depth [m]
        self.RT_mindead = 0.1           #minimum dead storage level [m]
        self.RTdesignUB = True         #use DAnCE4Water's default curves to design system?
        self.RTdescur_path = "no file"  #path for design curve
        self.RTavglife = 20             #average life span of a raintank
        
        self.RT_minsize = 0             #placeholders, do not actually matter
        self.RT_maxsize = 9999  
        
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
        self.createParameter("WSURrecycle", BOOL, "")
        self.WSURflow = True
        self.WSURpollute = True
        self.WSURrecycle = False
        
        #Design Curves
        self.createParameter("WSURdesignUB", BOOL,"")
        self.createParameter("WSURdescur_path", STRING,"")
        self.WSURdesignUB = True          #use DAnCE4Water's default curves to design system?
        self.WSURdescur_path = "no file"  #path for design curve
        
        #Design Information
	self.createParameter("WSURspec_EDD", DOUBLE,"")
        self.createParameter("WSURminsize", DOUBLE, "")
	self.createParameter("WSURmaxsize", DOUBLE,"")
	self.createParameter("WSURavglife", DOUBLE,"")
        self.WSURspec_EDD = 0.75
        self.WSURminsize = 200
        self.WSURmaxsize = 9999999           #maximum surface area of system in sqm
	self.WSURavglife = 20             #average life span of a wetland

        #---SWALES & BUFFER STRIPS [SW]-----------------------------------------
        self.createParameter("SWstatus", BOOL,"")
        self.SWstatus = 0
        
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
        self.createParameter("SWminsize", DOUBLE, "")
        self.createParameter("SWmaxsize", DOUBLE,"")
        self.createParameter("SWavglife", DOUBLE,"")
        self.SWspec = 0
        self.SWminsize = 20
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
        self.score_method = "WSM"       #MCA scoring method
        self.ingroup_scoring = "Avg"
        
        #RANKING OF STRATEGIES
        self.createParameter("ranktype", STRING,"")
        self.createParameter("topranklimit", DOUBLE,"")
        self.createParameter("conf_int", DOUBLE,"")
        self.ranktype = "RK"            #CI = Confidence Interval, RK = ranking
        self.topranklimit = 10
        self.conf_int = 95
        
        ########################################################################
        #ADVANCED PARAMETERS & VARIABLES                                       #
        ########################################################################
        self.createParameter("dcvdirectory", STRING, "")
        self.dcvdirectory = "C:/UrbanBEATSv1Dev/ub_modules/wsuddcurves/"
        self.technames = ["ASHP", "AQ", "ASR", "BF", "GR", "GT", 
                          "GPT", "IS", "PPL", "PB", "PP", "RT", 
                          "SF", "IRR", "WSUB", "WSUR", "SW", 
                          "TPS", "UT", "WWRR", "WT"]
        self.scaleabbr = ["lot", "street", "neigh", "prec"]
        self.ffplevels = {"PO":1, "NP":2, "RW":3, "SW":4, "GW":5}  #Used to determine when a system is cleaner than the other
        self.sqlDB = 0  #Global variable to hold the sqlite database
        self.dbcurs = 0 #cursor to execute sqlcommands for the sqlite database
        self.lot_incr = []
        self.street_incr = []
        self.neigh_incr = []
        self.subbas_incr = []
        
        self.createParameter("num_output_strats", DOUBLE, "")
        self.num_output_strats = 5      #number of output strategies
        
        self.createParameter("startyear", DOUBLE, "")
        self.createParameter("prevyear", DOUBLE, "")
        self.createParameter("currentyear", DOUBLE, "")
        self.startyear = 1960  #Retrofit Advanced Parameters - Set by Model Core
        self.prevyear = 1960
        self.currentyear = 1980
        
        #SWH Harvesting algorithms
        self.createParameter("rainfile", STRING, "")    #Rainfall file for SWH
        self.rainfile = "C:/UrbanBEATSv1Dev/ub_modules/resources/MelbourneRain1998-2007-6min.csv"
        self.createParameter("rain_dt", DOUBLE, "")
        self.rain_dt = 6        #[mins]
        self.createParameter("evapfile", STRING, "")
        self.evapfile = "C:/UrbanBEATSv1Dev/ub_modules/resources/MelbourneEvap1998-2007-Day.csv"
        self.createParameter("evap_dt", DOUBLE, "")
        self.evap_dt = 1440     #[mins]
        self.lot_raintanksizes = [1,2,4,5,7.5,10,15,20]       #[kL]
        self.raindata = []      #Globals to contain the data time series
        self.evapdata = []
        self.evapscale = []
        self.sysdepths = {}     #Holds all calculated system depths
        
        self.createParameter("relTolerance", DOUBLE, "")
        self.createParameter("maxSBiterations", DOUBLE, "")
        self.relTolerance = 1
        self.maxSBiterations = 100

        ########################################################################
        
	#Views
	self.blocks = View("Block", FACE,WRITE)
	self.blocks.getAttribute("Status")
        self.blocks.getAttribute("UpstrIDs")
        self.blocks.getAttribute("DownstrIDs")
        self.blocks.addAttribute("wd_Rating")
        self.blocks.addAttribute("wd_RES_K")
        self.blocks.addAttribute("wd_RES_S")
        self.blocks.addAttribute("wd_RES_T")
        self.blocks.addAttribute("wd_RES_L")
        self.blocks.addAttribute("wd_RES_IN")
        self.blocks.addAttribute("wd_RES_OUT")
        self.blocks.addAttribute("wd_HDR_K")
        self.blocks.addAttribute("wd_HDR_S")
        self.blocks.addAttribute("wd_HDR_T")
	self.blocks.addAttribute("wd_HDR_L")
        self.blocks.addAttribute("wd_HDR_IN")
        self.blocks.addAttribute("wd_HDR_OUT")
        self.blocks.addAttribute("wd_PrivIN")
        self.blocks.addAttribute("wd_PrivOUT")
	self.blocks.addAttribute("wd_LI")
	self.blocks.addAttribute("wd_HI")
	self.blocks.addAttribute("wd_COM")
	self.blocks.addAttribute("wd_ORC")
	self.blocks.addAttribute("wd_Nres_IN")
	self.blocks.addAttribute("Apub_irr")
	self.blocks.addAttribute("wd_PubOUT")
        self.blocks.addAttribute("Blk_WD")
        self.blocks.addAttribute("Blk_WD_OUT")

	self.mapattributes = View("GlobalMapAttributes", COMPONENT, WRITE)
	self.mapattributes.getAttribute("NumBlocks")
        self.mapattributes.addAttribute("OutputStrats")
	
	self.sysGlobal = View("SystemGlobal", COMPONENT, READ)
        self.sysGlobal.getAttribute("TotalSystems")
        
        self.sysAttr = View("SystemAttribute", COMPONENT, READ)
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
        
        self.wsudAttr = View("WsudAttr", COMPONENT, WRITE)
	self.wsudAttr.addAttribute("StrategyID")
        self.wsudAttr.addAttribute("posX")
        self.wsudAttr.addAttribute("posY")
	self.wsudAttr.addAttribute("BasinID")
	self.wsudAttr.addAttribute("Location")
	self.wsudAttr.addAttribute("Scale")
	self.wsudAttr.addAttribute("Type")
        self.wsudAttr.addAttribute("Qty")
	self.wsudAttr.addAttribute("GoalQty")
	self.wsudAttr.addAttribute("SysArea")
	self.wsudAttr.addAttribute("Status")
	self.wsudAttr.addAttribute("Year")
	self.wsudAttr.addAttribute("EAFact")
	self.wsudAttr.addAttribute("ImpT")
	self.wsudAttr.addAttribute("CurImpT")
	self.wsudAttr.addAttribute("Upgrades")
	self.wsudAttr.addAttribute("WDepth")
	self.wsudAttr.addAttribute("FDepth")
	
	#Datastream
	datastream = []
	datastream.append(self.mapattributes)
	datastream.append(self.blocks)
        datastream.append(self.sysGlobal)
        datastream.append(self.sysAttr)
        datastream.append(self.wsudAttr)
        
	self.addData("City", datastream)
	
	self.BLOCKIDtoUUID = {}

    def run(self):
        city = self.getData("City")
	self.initBLOCKIDtoUUID(city)
        strvec = city.getUUIDsOfComponentsInView(self.mapattributes)
        map_attr = city.getComponent(strvec[0])
        
        #CALCULATE SOME GLOBAL VARIABLES RELATING TO TARGETS
        self.system_tarQ = self.ration_runoff * self.targets_runoff
        self.system_tarTSS = self.ration_pollute * self.targets_TSS
        self.system_tarTP = self.ration_pollute * self.targets_TP
        self.system_tarTN = self.ration_pollute * self.targets_TN
        self.system_tarREL = self.ration_harvest * self.targets_reliability
        self.targetsvector = [self.system_tarQ, self.system_tarTSS, self.system_tarTP, self.system_tarTN, self.system_tarREL]
        self.servicevector = [self.service_swmQty* self.ration_runoff,
                              self.service_swmWQ * self.ration_pollute,
                              self.service_rec * self.ration_harvest]
        self.sysdepths = {"RT": self.RT_maxdepth - self.RT_mindead, "GW": 1, "WSUR": self.WSURspec_EDD, "PB": self.PBspec_MD}
        #---> targetsvector TO BE USED TO ASSESS OPPORTUNITIES
        
        #SET DESIGN CURVES DIRECTORY        
#	homeDir = os.environ['HOME']
#	dcvdirectory = homeDir + '/Documents/UrbanBEATS/UrbanBeatsModules/wsuddcurves/'
#	print dcvdirectory
	#dcvdirectory = "C:\\Users\\Peter M Bach\\Documents\\UrbanBEATS Development\\__urbanBEATS\\wsuddcurves\\"
	#dcvdirectory = "./UrbanBEATS/UrbanBeatsModules/wsuddcurves/"
	#dcvdirectory = "C:\\Heiko\\WSC\\data\\wsuddcurves\\"
	
        #GET NECESSARY GLOBAL DATA TO DO ANALYSIS
        blocks_num = map_attr.getAttribute("NumBlocks").getDouble()     #number of blocks to loop through
        self.block_size = map_attr.getAttribute("BlockSize").getDouble()    #size of block
        map_w = map_attr.getAttribute("WidthBlocks").getDouble()        #num of blocks wide
        map_h = map_attr.getAttribute("HeightBlocks").getDouble()       #num of blocks tall
        input_res = map_attr.getAttribute("InputReso").getDouble()      #resolution of input data
        basins = map_attr.getAttribute("TotalBasins").getDouble()
        map_attr.addAttribute("OutputStrats", self.num_output_strats)
        
        #Create Technologies Shortlist - THIS IS THE USER'S CUSTOMISED SHORTLIST
        userTechList = self.compileUserTechList()               #holds the active technologies selected by user for simulation
        #print userTechList
        
        #Create technology list for scales
        techListLot = self.fillScaleTechList("lot", userTechList)
        techListStreet = self.fillScaleTechList("street", userTechList)
        techListNeigh = self.fillScaleTechList("neigh", userTechList)
        techListSubbas = self.fillScaleTechList("subbas", userTechList)
        
        print techListLot
        print techListStreet
        print techListNeigh
        print techListSubbas
        
        #PROCESS MCA Parameters and Scoring Details
        self.mca_techlist, self.mca_tech, self.mca_env, self.mca_ecn, self.mca_soc = self.retrieveMCAscoringmatrix()
        
        #Calculate MCA weightings for different PURPOSES - used to penalize MCA score if tech does not meet particular purpose
        self.priorities = [int(self.ration_runoff)*float(self.runoff_pri), 
                   int(self.ration_pollute)*float(self.pollute_pri),
                   int(self.ration_harvest)*float(self.harvest_pri)]
        prioritiessum = sum(self.priorities)
        for i in range(len(self.priorities)):                        #e.g. ALL and priorities 3,2,1 --> [3/6, 2/6, 1/6]
            self.priorities[i] = self.priorities[i]/prioritiessum               #1, 2 and priorities 3,2,1 --> [3/5, 2/5, 0]
        
        ###-------------------------------------------------------------------###
        #  FIRST LOOP - WATER DEMANDS AND EFFICIENCY                            #
        ###-------------------------------------------------------------------###
        for i in range(int(blocks_num)):
            currentID = i+1
            currentAttList = self.getBlockUUID(currentID, city)
            if currentAttList.getAttribute("Status").getDouble() == 0:
                continue
            wdDict = self.calculateBlockWaterDemand(currentAttList)
            currentAttList.addAttribute("wd_Rating", wdDict["Efficiency"])      #[stars]
            currentAttList.addAttribute("wd_RES_K", wdDict["RESkitchen"])       #[L/day]
            currentAttList.addAttribute("wd_RES_S", wdDict["RESshower"])        #[L/day]
            currentAttList.addAttribute("wd_RES_T", wdDict["REStoilet"])        #[L/day]
            currentAttList.addAttribute("wd_RES_L", wdDict["RESlaundry"])       #[L/day]
            currentAttList.addAttribute("wd_RES_I", wdDict["RESirrigation"])    #[kL/yr]
            currentAttList.addAttribute("wd_RES_IN", wdDict["REStotalIN"])      #[kL/yr]
            currentAttList.addAttribute("wd_RES_OUT", wdDict["REStotalOUT"])    #[kL/yr]
            currentAttList.addAttribute("wd_HDR_K", wdDict["HDRkitchen"])       #[L/day]
            currentAttList.addAttribute("wd_HDR_S", wdDict["HDRshower"])        #[L/day]
            currentAttList.addAttribute("wd_HDR_T", wdDict["HDRtoilet"])        #[L/day]
            currentAttList.addAttribute("wd_HDR_L", wdDict["HDRlaundry"])       #[L/day]
            currentAttList.addAttribute("wd_HDR_I", wdDict["HDRirrigation"])    #[kL/yr]
            currentAttList.addAttribute("wd_HDR_IN", wdDict["HDRtotalIN"])      #[kL/yr]
            currentAttList.addAttribute("wd_HDR_OUT", wdDict["HDRtotalOUT"])    #[kL/yr]
            currentAttList.addAttribute("wd_PrivIN", wdDict["TotalPrivateIN"])  #[kL/yr]
            currentAttList.addAttribute("wd_PrivOUT", wdDict["TotalPrivateOUT"])#[kL/yr]
            
            currentAttList.addAttribute("wd_LI", wdDict["LIDemand"])            #[L/day]
            currentAttList.addAttribute("wd_HI", wdDict["HIDemand"])            #[L/day]
            currentAttList.addAttribute("wd_COM", wdDict["COMDemand"])          #[L/day]
            currentAttList.addAttribute("wd_ORC", wdDict["ORCDemand"])          #[L/day]
            currentAttList.addAttribute("wd_Nres_IN", wdDict["TotalNonResDemand"]) #[kL/yr]
            
            currentAttList.addAttribute("Apub_irr", wdDict["APublicIrrigate"])  #[sqm]
            currentAttList.addAttribute("wd_PubOUT", wdDict["TotalOutdoorPublicWD"]) #[kL/yr]
            currentAttList.addAttribute("Blk_WD", wdDict["TotalBlockWD"])       #[kL/yr]
            currentAttList.addAttribute("Blk_WD_OUT", wdDict["TotalOutdoorWD"]) #[kL/yr]
            
        ###-------------------------------------------------------------------###
        #  SECOND LOOP - RETROFIT ALGORITHM                                     #
        ###-------------------------------------------------------------------###
        strvec = city.getUUIDsOfComponentsInView(self.sysGlobal)
        totsystems = city.getComponent(strvec[0]).getAttribute("TotalSystems").getDouble()
        ubeatsfile = city.getComponent(strvec[0]).getAttribute("UBFile").getDouble()
        print "Total Systems in Map: ", totsystems
        
        sysuuids = city.getUUIDsOfComponentsInView(self.sysAttr)
        print sysuuids
        #Grab the list of systems and sort them based on location into a dictionary
        system_list = {}        #Dictionary
        for i in range(int(blocks_num)):
            system_list[i+1] = []
        for i in range(len(sysuuids)):
            curSys = city.getComponent(sysuuids[i])
            locate = int(curSys.getAttribute("Location").getDouble())
            system_list[locate].append(curSys)  #Block ID [5], [curSys, curSys, curSys]
            
        #Do the retrofitting
        for i in range(int(blocks_num)):
            currentID = i+1
            currentAttList = self.getBlockUUID(currentID, city) #QUIT CONDITION #1 - status=0
            if currentAttList.getAttribute("Status").getDouble() == 0:
                continue
            
            sys_implement = system_list[currentID]
            if len(sys_implement) == 0:
                continue
            
            if self.retrofit_scenario == "N":
                self.retrofit_DoNothing(currentID, sys_implement, city)
            elif self.retrofit_scenario == "R":
                self.retrofit_WithRenewal(currentID, sys_implement, city)
            elif self.retrofit_scenario == "F":
                self.retrofit_Forced(currentID, sys_implement, city)
        
        ###-------------------------------------------------------------------###
        #  THIRD LOOP - OPPORTUNITIES ASSESSMENT ACROSS SCALES & IN-BLOCK TOP   #
        #                RANKED OPTIONS (ACROSS BLOCKS)                         #
        ###-------------------------------------------------------------------###
        #Initialize the database
        if os.path.isfile(r"D:\ubeatsdb2.db"):
            os.remove(r"D:\ubeatsdb2.db")
        self.sqlDB = sqlite3.connect(r"D:\ubeatsdb2.db")
        self.dbcurs = self.sqlDB.cursor()
        
        #Create Table for Individual Systems
        self.dbcurs.execute('''CREATE TABLE watertechs(BlockID, Type, Size, Scale, Service, Areafactor, Landuse, Designdegree)''')
        self.dbcurs.execute('''CREATE TABLE blockstrats(BlockID, Bin, RESType, RESQty, RESservice, HDRType, HDRQty, HDRService,
                            LIType, LIQty, LIService, HIType, HIQty, HIService, COMType, COMQty, COMService, StreetType, StreetQty, 
                            StreetService, NeighType, NeighQty, NeighService, TotService, MCATech, MCAEnv, MCAEcn, MCASoc, MCATotal)''')
        self.dbcurs.execute('''CREATE TABLE blockstratstop(BlockID, Bin, RESType, RESQty, RESservice, HDRType, HDRQty, HDRService,
                            LIType, LIQty, LIService, HIType, HIQty, HIService, COMType, COMQty, COMService, StreetType, StreetQty, 
                            StreetService, NeighType, NeighQty, NeighService, TotService, MCATech, MCAEnv, MCAEcn, MCASoc, MCATotal)''')
        
        inblock_options = {}
        subbas_options = {}
        
        #Initialize increment variables
        self.lot_incr = self.setupIncrementVector(self.lot_rigour)
        self.street_incr = self.setupIncrementVector(self.street_rigour)
        self.neigh_incr = self.setupIncrementVector(self.neigh_rigour)
        self.subbas_incr = self.setupIncrementVector(self.subbas_rigour)
        
        if bool(self.ration_harvest):   #if harvest is a management objective
            #Initialize meteorological data vectors: Load rainfile and evaporation files, 
            #create the scaling factors for evap data
            print "Loading Climate Data... "
            self.raindata = ubseries.loadClimateFile(self.rainfile, "csv", self.rain_dt, 1440, self.rain_length)
            self.evapdata = ubseries.loadClimateFile(self.evapfile, "csv", self.evap_dt, 1440, self.rain_length)
            self.evapscale = ubseries.convertVectorToScalingFactors(self.evapdata)
            self.raindata = ubseries.removeDateStampFromSeries(self.raindata)             #Remove the date stamps
            
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
            
            subbas_options["BlockID"+str(currentID)] = subbas_tech
            inblock_options["BlockID"+str(currentID)] = self.constructInBlockOptions(currentAttList, lot_techRES, lot_techHDR, lot_techLI, lot_techHI, lot_techCOM, street_tech, neigh_tech)
            
        self.sqlDB.commit()
        
        ###-------------------------------------------------------------------###
        #  FOURTH LOOP - MONTE CARLO (ACROSS BASINS)                            #
        ###-------------------------------------------------------------------###
        gc.collect()
        #self.dbcurs.execute('''CREATE TABLE basinbrainstorm(BasinID, )''')
#        output_log_file = open("UB_BasinStrategies.csv", 'w')
#        output_log_file.write("UrbanBEATS Basin Strategies Evaluation File \n\n")
#        output_log_file.write("Lost of all Basin Strategies \n\n")
#        output_log_file.write("Basin ID, Strategy No., Service [%], TotalMCAScore, # Precinct, # Blocks Local\n")
        
        for i in range(int(basins)):
            currentBasinID = i+1
            print "Currently on Basin ID"+str(currentBasinID)
            
            basinBlockIDs, outletID = self.getBasinBlockIDs(currentBasinID, blocks_num, city)
            
            dP_QTY, basinRemainQTY, basinTreatedQTY, basinEIA = self.calculateRemainingService("QTY", basinBlockIDs, city)
            dP_WQ, basinRemainWQ, basinTreatedWQ, basinEIA = self.calculateRemainingService("QTY", basinBlockIDs, city)
            dP_REC, basinRemainREC, basinTreatedREC, basinDem = self.calculateRemainingService("QTY", basinBlockIDs, city)
            
            print "Previous Treated Efficiency for: ", [basinTreatedQTY / basinEIA, basinTreatedWQ / basinEIA, basinTreatedREC/basinDem]
            print "Must choose a strategy now that treats: ", [dp_QTY*100, dp_WQ*100, dp_REC*100], "% of basin"
            
            subbasPartakeIDs = self.findSubbasinPartakeIDs(basinBlockIDs, subbas_options) #Find locations of possible WSUD
            
            updatedService = [dP_QTY, dP_WQ, dP_REC]
            
            #SKIP CONDITIONS
            if basinRemainQTY == 0 and basinRemainWQ == 0 and basinRemainREC == 0:
                #print "Basin ID: ", currentBasinID, " has no remaining service requirements, skipping!"
                continue
            if sum(updatedService) == 0:
                continue
            
            iterations = 1000   #MONTE CARLO ITERATIONS - CAN SET TO SENSITIVITY VALUE IN FUTURE RELATIVE TO BASIN SIZE
            
            if len(basinBlockIDs) == 1: #if we are dealing with a single-block basin, reduce the number of iterations
                iterations = 100        #If only one block in basin, do different/smaller number of iterations
            #Begin Monte Carlo
            basin_strategies = []
            for iteration in range(iterations):   #1000 monte carlo simulations
                print "Current Iteration No. ", iteration+1

                #Create template arrays for sampling and tracking
                partakeIDstracker = []
                partakeIDssampler = []
                basinblockIDssampler = []
                #subbasID_treatedAimp = []
                for id in subbasPartakeIDs:
                    partakeIDstracker.append(id)
                    partakeIDssampler.append(id)
                    #subbasID_treatedAimp.append(0)
                for id in basinBlockIDs:
                    basinblockIDssampler.append(id)
                
                #Draw Samples
                subbas_chosenIDs, inblocks_chosenIDs = self.selectTechLocationsByRandom(partakeIDssampler, basinblockIDssampler)
                #print subbas_chosenIDs
                
                #Create the Basin Management Strategy Object
                current_bstrategy = tt.BasinManagementStrategy(iteration+1, currentBasinID, 
                                                               basinBlockIDs, subbasPartakeIDs, 
                                                               [basinRemainQTY, basinRemainWQ, basinRemainDEM])
                
                #Populate Basin Management Strategy Object based on the current sampled values
                self.populateBasinWithTech(current_bstrategy, subbas_chosenIDs, inblocks_chosenIDs, 
                                           partakeIDstracker, inblock_options, subbas_options, basinBlockIDs, city)
                
                tt.updateBasinService(current_bstrategy)
                
                tt.calculateBasinStrategyMCAScores(current_bstrategy,self.priorities, self.mca_techlist, self.mca_tech, \
                                                  self.mca_env, self.mca_ecn, self.mca_soc, \
                                                      [self.bottomlines_tech_w, self.bottomlines_env_w, \
                                                               self.bottomlines_ecn_w, self.bottomlines_soc_w])
                
                #Add basin strategy to list of possibilities
                service_objfunc = self.evaluateServiceObjectiveFunction(current_bstrategy, updatedService)        #Calculates how well it meets the total service

                basin_strategies.append([service_objfunc,current_bstrategy.getServicePvalues(), current_bstrategy.getTotalMCAscore(), current_bstrategy])
            
            #Pick the final option by narrowing down the list and choosing (based on how many
            #need to be chosen), sort and grab the top ranking options
            basin_strategies.sort()
            print basin_strategies
            self.debugPlanning(basin_strategies)
            acceptable_options = []
            for j in range(len(basin_strategies)):
                if basin_strategies[j][0] < 0:  #if the OF is <0 i.e. -1, skip
                    continue
                else:
                    acceptable_options.append(basin_strategies[j])
            print acceptable_options
            if self.ranktype == "RK":
                acceptable_options = acceptable_options[0:int(self.topranklimit)]
            elif self.ranktype == "CI":
                acceptableN = int(len(acceptable_options)*(1.0-float(self.conf_int)/100.0))
                acceptable_options = acceptable_options[0:acceptableN]
            
            topcount = len(acceptable_options)
            acceptable_options.sort(key=lambda score: score[2])
            print acceptable_options
            #Choose final option
            numselect = min(topcount, self.num_output_strats)   #Determines how many options out of the matrix it should select
            final_selection = []
            for j in range(int(numselect)):            
                score_matrix = []       #Create the score matrix
                for opt in acceptable_options:
                    score_matrix.append(opt[2])
                selection_cdf = self.createCDF(score_matrix)    #Creat the CDF
                choice = self.samplefromCDF(selection_cdf)
                final_selection.append(acceptable_options[choice][3])   #Add ONLY the strategy_object
                acceptable_options.pop(choice)  #Pop the option at the selected index from the matrix
                #Repeat for as many options as requested
            
            #Write WSUD strategy attributes to output vector for that block
            print final_selection
            if len(final_selection) == 0:
                self.transferExistingSystemsToOutput(city, 1)   
                #If there are no additional plans, just tranfer systems across, only one output as StrategyID1
                
            for j in range(len(final_selection)):       #Otherwise it'll loop
                cur_strat = final_selection[j]
                stratID = j+1
                self.writeStrategyView(city, stratID, currentBasinID, basinBlockIDs, cur_strat)
                self.transferExistingSystemsToOutput(city, stratID)
            #Clear the array and garbage collect
            basin_strategies = []
            acceptable_options = []
            final_selection = []
            gc.collect()
            #END OF BASIN LOOP, continues to next basin
        
#        output_log_file.write("End of Basin Strategies Log \n\n")
#        output_log_file.close()
        
        self.sqlDB.close()      #Close the database
        #END OF MODULE
    
    ########################################################
    #TECHPLACEMENT SUBFUNCTIONS                            #
    ########################################################
    def locatePlannedSystems(self, system_list, scale, city):
        """Searches the input planned technologies list for a system that fits the scale in the block
        Returns the system attribute list. System_list is a vector of Components [curSys, curSys, curSys]
        """
        for curSys in system_list:
            if curSys.getAttribute("Scale").getString() == scale:
                return curSys
        return None

    def findDCVpath(self, type, sys_descr):
        #Finds the correct pathname of the design curve file based on system type and specs
        if type in ["IS", "BF"]: #then file = BF-EDDx.xm-FDx.xm.dcv
            pathname = 0
        elif type in ["WSUR"]: #then file = WSUR-EDDx.xm.dcv
            pathname = 0
        elif type in ["PB"]: #then file = PB-MDx.xm.dcv
            pathname = 0
        return pathname
    
    def retrieveNewAimpTreated(self, ID, scale, sys_descr,city):
        """Retrieves the system information for the given scale from the city datastream and
        assesses how well the current system's design can meet the current targets by comparing its
        performance on the design curves.
        """
        #Determine impervious area to deal with depending on scale
        currentAttList = self.getBlockUUID(ID,city)
        ksat = currentAttList.getAttribute("Soil_k").getDouble()
        Asyseff = sys_descr.getAttribute("SysArea").getDouble()/sys_descr.getAttribute("EAFact").getDouble()
        type = sys_descr.getAttribute("Type").getString()
        #need to be using the effective area, not the planning area
        
        print "Type: ", type, " AsysEffective: ", Asyseff, "ksat: ", ksat
        
        ### EXCEPTION FOR SWALES AT THE MOMENT WHILE THERE ARE NO DESIGN CURVE FILES ###
        if type == "SW":
            return 0
        ### END OF EXCEPTION - CHANGE WHEN DESIGN CURVES ARE AVAILABLE ###
        
        #Grab targets and adjust for particular system type
        print "Targets: ", self.targetsvector
        
        #Piece together the pathname from current system information: FUTURE
        #NOTE: CURRENT TECH DESIGNS WILL NOT BE CHANGED! THEREFORE PATHNAME WE RETRIEVE FROM
        #DESIGN DETAILS VECTOR LIST

        #Depending on the type of system and classification, will need to retrieve design in different
        #ways
        if type in ["BF", "SW", "WSUR", "PB", "IS"]:    #DESIGN by DCV Systems
            sys_perc = dcv.retrieveDesign(self.getDCVPath(type), type, ksat, self.targetsvector)
            print "Sys Percentage: ", sys_perc
        elif type in ["RT", "PP", "ASHP", "GW"]:        #DESIGN by EQN or SIM Systems
            #Other stuff
            sys_perc = np.inf #deq.retrieveDesign(...)
        
        if sys_perc == np.inf:
            #Results - new targets cannot be met, system will not be considered
            #release the imp area, but mark the space as taken!
            imptreatedbysystem = 0
        else:
            #Calculate the system's current Atreated
            imptreatedbysystem = Asyseff/sys_perc
            
#            #Account for Lot Scale as exception
#            if scale in ["L_RES", "L_HDR", "L_LI", "L_HI", "L_COM"]:
#                imptreatedbysystem *= goalqty #imp treated by ONE lot system * the desired qty that can be implemented
#            else:
#                imptreated += imptreatedbysystem
        print "impervious area treated by system: "+str(imptreatedbysystem)
        return imptreatedbysystem

    def dealWithSystem(self, currentAttList, sys_descr, scale,city):
        """Checks the system's feasibility on a number of categories and sets up a decision matrix
        to determine what should be done with the system (i.e. keep, upgrade, decommission). Returns
        a final decision and the newly treated impervious area.
        """
        
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        scalecheck = [[self.lot_renew, self.lot_decom], 
                      [self.street_renew, self.street_decom], 
                      [self.neigh_renew, self.neigh_decom], 
                      [self.prec_renew, self.prec_decom]]
        
        if scale in ["L_RES", "L_HDR", "L_LI", "L_HI", "L_COM"]:
            scaleconditions = scalecheck[0]
        else:
            scalematrix = ["L", "S", "N", "B"]
            scaleconditions = scalecheck[scalematrix.index(scale)]
        
        decision_matrix = [] #contains numbers of each decision 1=Keep, 2=Renew, 3=Decom
                                    #1st pass: decision based on the maximum i.e. if [1, 3], decommission
        
        ###-------------------------------------------------------
        ### DECISION FACTOR 1: SYSTEM AGE
        ### Determine where the system age lies
        ###-------------------------------------------------------
        sys_yearbuilt = sys_descr.getAttribute("Year").getDouble()
        sys_type = sys_descr.getAttribute("Type").getString()
        avglife = eval("self."+str(sys_type)+"avglife")
        age = self.currentyear - sys_yearbuilt
        #print "System Age: "+str(age)
        
        if scaleconditions[1] == 1 and age > avglife: #decom
            #print "System too old, decommission"
            decision_matrix.append(3)
        elif scaleconditions[0] == 1 and age > avglife/2: #renew
            #print "System needs renewal because of age"
            decision_matrix.append(2)
        else: #keep
            decision_matrix.append(1)
        
        ###-------------------------------------------------------
        ### DECISION FACTOR 2: DROP IN PERFORMANCE
        ### Determine where the system performance lies
        ###-------------------------------------------------------
        old_imp = sys_descr.getAttribute("ImpT").getDouble()
        if old_imp == 0: #This can happen if for example it was found previously that
            perfdeficit = 1.0 #the system can no longer meet new targets, but is not retrofitted because of renewal cycles.
            new_imp = 0
        else:           #Need to catch this happening or else there will be a float division error!
            new_imp = self.retrieveNewAimpTreated(currentID, scale, sys_descr, city)
            perfdeficit = (old_imp - new_imp)/old_imp
            
        #print "Old Imp: "+str(old_imp)
        #print "New Imp: "+str(new_imp)
        #print "Performance Deficit of System: "+str(perfdeficit)
        
        if scaleconditions[1] == 1 and perfdeficit >= (float(self.decom_thresh)/100.0): #Decom = Checked, threshold exceeded
            #print "System's performance not up to scratch, decommission"
            decision_matrix.append(3)
        elif scaleconditions[0] == 1 and perfdeficit >= (float(self.renewal_thresh)/100.0): #Renew = checked, threshold exceeded
            #print "System's performance ok, needs renewal"
            decision_matrix.append(2)
        else:
            decision_matrix.append(1)
        
        ### MAKE FINAL DECISION ###
        #print decision_matrix
        final_decision = max(decision_matrix)           #worst-case chosen, i.e. maximum
                                                    #future passes: more complex decision-making
        return final_decision, new_imp
    
    def redesignSystem(self, currentAttList, sys_descr, scale, originalAimpTreated,city):
        """Redesigns the system for BlockID at the given 'scale' for the original Impervious
        Area that it was supposed to treat, but now according to new targets.
            - ID: BlockID, i.e. the system's location
            - sys_descr: the original vector of the system
            - scale: the letter denoting system scale
            - originalAimpTreated: the old impervious area the system was meant to treat
        """
	type = sys_descr.getAttribute("Type").getString()
        
        #TO BE CHANGED LATER ON, BUT FOR NOW WE ASSUME THIS IS THE SAME PATH
        dcvpath = self.getDCVPath(type)
        #GET THE DCV FILENAME
        #dcvpath = self.findDCVpath(type, sys_descr)
        
        #Some additional arguments for the design function
        maxsize = eval("self."+str(type)+"maxsize")                     #FUTURE >>>>>> MULTI-oBJECTIVE DESIGN
        minsize = eval("self."+str(type)+"minsize")
        soilK = currentAttList.getAttribute("Soil_k").getDouble()
        
        #Current targets
        targets = self.targetsvector
        tech_applications = self.getTechnologyApplications(type)
        purpose = [0, tech_applications[1], 0]

        #Call the design function using eval, due to different system Types
        newdesign = eval('td.design_'+str(type)+'('+str(originalAimpTreated)+',"'+str(dcvpath)+'",'+str(self.targetsvector)+','+str(purpose)+','+str(soilK)+','+str(minsize)+','+str(maxsize)+')')    
        
        Anewsystem = newdesign[0]
        newEAFactor = newdesign[1]
        
        return Anewsystem, newEAFactor

    def defineUpgradedSystemAttributes(self, sys_descr, newAsys, newEAFact, impT):
        """Updates the current component with new attributes based on the newly designed/upgraded
        system at a particular location.
        """
        sys_descr.changeAttribute("SysArea", newAsys)
        sys_descr.changeAttribute("EAFact", newEAFact)
        sys_descr.changeAttribute("ImpT", impT)
        sys_descr.changeAttribute("CurImpT", impT*sys_descr.getAttribute("GoalQty").getDouble())
        
        #System was upgraded, add one to the upgrade count
        sys_descr.changeAttribute("Upgrades", sys_descr.getAttribute("Upgrades").getDouble() + 1)
        return True
    
    def updateForBuildingStockRenewal(self, currentAttList, sys_descr):
        """Number of houses removed from area = total currently there * lot_perc
        evenly distribute this across those that have lot system and those that don't
        we therefore end up calculate how many systems lost as lot-perc * how many in place
        """
        print "YEARS"
        print self.currentyear, self.prevyear, self.renewal_lot_years
        cycles = (float(self.currentyear) - float(self.prevyear)) // float(self.renewal_lot_years)
        print "CYcles", cycles
        currentQty = float(sys_descr.getAttribute("Qty").getDouble())
        num_lots_lost = currentQty*self.renewal_lot_perc/100*cycles
        newQty = currentQty - num_lots_lost
        goalquantity = sys_descr.getAttribute("GoalQty").getDouble()
        
        adjustedgoalQty = goalquantity - num_lots_lost
        #Update goal quantity: This is how many we can only reach now because we lost some
        sys_descr.changeAttribute("GoalQty", int(adjustedgoalQty))
        
        #Update current quantity: This is how many current exist in the map
        sys_descr.changeAttribute("Qty", int(newQty))
        return sys_descr
    
    def retrofit_DoNothing(self, ID, sys_implement,city):
        """Implements the "DO NOTHING" Retrofit Scenario across the entire map Do Nothing: 
            Technologies already in place will be left as is
         - The impervious area they already treat will be removed from the outstanding impervious 
            area to be treated
         - The Block will be marked at the corresponding scale as "occupied" so that techopp 
            functions cannot place anything there ('no space case')
        """
        print "Block: "+str(ID)
        print sys_implement     #[curSys, curSys, curSys, ...]
        
        currentAttList = self.getBlockUUID(ID,city)
        inblock_imp_treated = 0 #Initialize to keep track of treated in-block imperviousness
        
        #LOT, STREET, NEIGH Systems
        for luc_code in ["L_RES", "L_HDR", "L_LI", "L_HI", "L_COM", "S", "N"]:
            sys_descr = self.locatePlannedSystems(sys_implement, luc_code,city)
            if sys_descr == None:       #None found for that particular land use
                inblock_imp_treated += 0
                currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 0)
            else:
                currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1) #mark the system as having been taken
                print luc_code+" Location: ", str(sys_descr.getAttribute("Location").getDouble())
                Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
                if luc_code == "L_RES":
                    imptreated = min(self.retrieveNewAimpTreated(ID, luc_code, sys_descr, city), Aimplot)
                else:
                    imptreated = self.retrieveNewAimpTreated(ID, luc_code, sys_descr, city)
                inblock_imp_treated += imptreated * sys_descr.getAttribute("GoalQty").getDouble()
                sys_descr.changeAttribute("ImpT", imptreated)   #UNIT IMPERVIOUSNESS TREATED
                sys_descr.changeAttribute("CurImpT", imptreated * sys_descr.getAttribute("Qty").getDouble())
                #Do Nothing Scenario: ImpT changes and CurImpT changes, but Status remains 1
                
        currentAttList.addAttribute("ServWQ", inblock_imp_treated)
        inblock_impdeficit = max(currentAttList.getAttribute("Blk_EIA").getDouble() - inblock_imp_treated, 0)
        currentAttList.addAttribute("DeficitWQ", inblock_impdeficit)
        print "Deficit Area still to treat inblock: ", str(inblock_impdeficit)
        
        #Calculate the maximum degree of lot implementation allowed (no. of houses)
        allotments = currentAttList.getAttribute("ResAllots").getDouble()
        Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
        print "Allotments = "+str(allotments)+" of each "+str(Aimplot)+" sqm impervious"
        max_houses = min((inblock_impdeficit/Aimplot)/allotments, 1)
        print "A Lot Strategy in this Block would permit a maximum implementation in: "+str(max_houses*100)+"% of houses"
        currentAttList.addAttribute("MaxLotDeg", max_houses)
        
        #PRECINCT SYSTEMS
        sys_descr = self.locatePlannedSystems(sys_implement, "B",city)
        if sys_descr == None:
            currentAttList.addAttribute("HasBSys", 0)
            currentAttList.addAttribute("ServUpWQ", 0)
        else:
            currentAttList.addAttribute("HasBSys", 1)
            subbasimptreated = self.retrieveNewAimpTreated(ID, "B", sys_descr,city)
            print "Subbasin Location: ", str(sys_descr.getAttribute("Location").getDouble())
            currentAttList.addAttribute("ServUpWQ", subbasimptreated)
            sys_descr.changeAttribute("ImpT", subbasimptreated)
            sys_descr.changeAttribute("CurImpT", subbasimptreated * sys_descr.getAttribute("Qty").getDouble())
        return True
    
    def retrofit_Forced(self, ID, sys_implement,city):
        """Implements the "FORCED" Retrofit Scenario across the entire map
        Forced: Technologies at the checked scales are retrofitted depending on the three
         options available: keep, upgrade, decommission
         - See comments under "With Renewal" scenario for further details
        """
        print "Block: "+str(ID)
        print sys_implement
        
        currentAttList = self.getBlockUUID(ID,city)
        inblock_imp_treated = 0 #Initialize to keep track of treated in-block imperviousness
        
        #LOT, STREET & NEIGH
        for luc_code in ["L_RES", "L_HDR", "L_LI", "L_HI", "L_COM", "S", "N"]:
            sys_descr = self.locatePlannedSystems(sys_implement, luc_code,city)
            
            if sys_descr == None: #Skip condition, no system at the particular scale/luc-code
                inblock_imp_treated += 0
                currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 0)
                continue
            
            oldImp = sys_descr.getAttribute("ImpT").getDouble()
            decision, newImpT = self.dealWithSystem(currentAttList, sys_descr, luc_code, city)
            
            #CONDITIONS THAT WILL FORCE A DECISION == 1
            if luc_code in ["L_RES", "L_HDR", "L_LI", "L_HI", "L_COM"]:
                decision = 1 #YOU CANNOT FORCE RETROFIT ON LOT, SO KEEP THE SYSTEMS
            if luc_code == "S" and self.force_street == 0: #if we do not force retrofit on neighbourhood, just keep the system
                decision = 1
            if luc_code == "N" and self.force_neigh == 0: #if we do not force retrofit on neighbourhood, just keep the system
                decision = 1
        
            if decision == 1:   #KEEP SYSTEM
                currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1)
                Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
                if luc_code == "L_RES":
                    imptreated = min(newImpT, Aimplot)
                else:
                    imptreated = newImpT
                inblock_imp_treated += imptreated
                sys_descr.changeAttribute("ImpT", imptreated)
                sys_descr.changeAttribute("CurImpT", imptreated * sys_descr.getAttribute("Qty").getDouble())
            
            elif decision == 2: #RENEWAL
                print "Renewing the System - Redesigning and Assessing Space Requirements"
                newAsys, newEAFact = self.redesignSystem(currentAttList, sys_descr, luc_code, oldImp,city) #get new system size & EA
                
                #Get available space - depends on scale/luc-code
                if luc_code == "S":
                    avlSpace = currentAttList.getAttribute("avSt_RES").getDouble()
                elif luc_code == "N":
                    avlSpace = currentAttList.getAttribute("PG_av").getDouble() + currentAttList.getAttribute("REF_av").getDouble()
                
                if newAsys > avlSpace and self.renewal_alternative == "K": #if system does not fit and alternative is 'Keep'
                    print "Cannot fit new system design, keeping old design instead"
                    currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1)
                    inblock_imp_treated += newImpT
                    sys_descr.changeAttribute("ImpT", newImpT)
                    sys_descr.changeAttribute("CurImpT", newImpT * sys_descr.getAttribute("Qty").getDouble())
                elif newAsys > avlSpace and self.renewal_alternative == "D": #if system does not fit and alternative is 'Decommission'
                    print "Cannot fit new system design, decommissioning instead"
                    inblock_imp_treated += 0 #quite self-explanatory but is added here for clarity
                    currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1)
                    sys_implement.remove(sys_descr)
                    city.removeComponent(sys_descr.getUUID())
                else: #otherwise it'll fit, transfer new information
                    print "New System Upgrades fit, transferring this information to output"
                    currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1)
                    self.defineUpgradedSystemAttributes(sys_descr, newAsys, newEAFact, oldImp)
                    inblock_imp_treated += oldImp
                
            elif decision == 3: #DECOMMISSIONING
                print "Decommissioning the system"
                inblock_imp_treated += 0 #quite self-explanatory but is added here for clarity
                #remove all attributes, wipe the attributes entry in techconfigout with a blank attribute object
                currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 0) #Remove system placeholder
                sys_implement.remove(sys_descr)
                city.removeComponent(sys_descr.getUUID())
                
        currentAttList.addAttribute("ServWQ", inblock_imp_treated)
        inblock_impdeficit = max(currentAttList.getAttribute("Blk_EIA").getDouble() - inblock_imp_treated, 0)
        currentAttList.addAttribute("DeficitIA", inblock_impdeficit)
        
        allotments = currentAttList.getAttribute("ResAllots").getDouble()
        Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
        print "Allotments = "+str(allotments)+" of each "+str(Aimplot)+" sqm impervious"
        max_houses = min((inblock_impdeficit/Aimplot)/allotments, 1)
        print "A Lot Strategy in this Block would permit a maximum implementation in: "+str(max_houses*100)+"% of houses"
        currentAttList.addAttribute("MaxLotDeg", max_houses)
        
        #SUBBASIN
        sys_descr = self.locatePlannedSystems(sys_implement, "B", city)
        if sys_descr == None:
            currentAttList.addAttribute("HasBSys", 0)
        else:
            oldImp = sys_descr.getAttribute("ImpT").getDouble()
            decision, newImpT = self.dealWithSystem(currentAttList, sys_descr, "B",city)
            if self.force_prec == 0: #if we do not force retrofit on precinct, just keep the system
                decision = 1
                
            if decision == 1: #KEEP
                print "Keeping the System"
                currentAttList.addAttribute("HasBSys", 1)
                currentAttList.addAttribute("ServUpWQ", newImpT)
                sys_descr.changeAttribute("ImpT", newImpT)
                sys_descr.changeAttribute("CurImpT", newImpT * sys_descr.getAttribute("Qty").getDouble())
            
            elif decision == 2: #RENEWAL
                print "Renewing the System - Redesigning and Assessing Space Requirements"
                newAsys, newEAFact = self.redesignSystem(currentAttList, sys_descr, "B", oldImp,city) #get new system size & EA
                avlSpace = currentAttList.getAttribute("PG_av").getDouble() + currentAttList.getAttribute("REF_av").getDouble()
                if newAsys > avlSpace and self.renewal_alternative == "K": #if system does not fit and alternative is 'Keep'
                    print "Cannot fit new system design, keeping old design instead"
                    currentAttList.addAttribute("HasBSys", 1)
                    currentAttList.addAttribute("ServUpWQ", newImpT)
                    sys_descr.changeAttribute("ImpT", newImpT)
                    sys_descr.changeAttribute("CurImpT", newImpT * sys_descr.getAttribute("Qty").getDouble())
                elif newAsys > avlSpace and self.renewal_alternative == "D": #if system does not fit and alternative is 'Decommission'
                    print "Cannot fit new system design, decommissioning instead"
                    currentAttList.addAttribute("ServUpWQ", 0)
                    currentAttList.addAttribute("HasBSys", 0) #Remove system placeholder
                    sys_implement.remove(sys_descr)
                    city.removeComponent(sys_descr.getUUID())
                else: #otherwise it'll fit, transfer new information
                    print "New System Upgrades fit, transferring this information to output"
                    currentAttList.addAttribute("HasBSys", 1)
                    self.defineUpgradedSystemAttributes(sys_descr, newAsys, newEAFact, oldImp)
                    currentAttList.addAttribute("ServUpWQ", oldImp)        #OLD IMP BECAUSE THE REDESIGNED SYSTEM IS NOW LARGER
                                                                                #AND BETTER TO HANDLE SAME IMP AREA AS BEFORE!
            elif decision == 3: #DECOMMISSIONING
                print "Decommissioning the system"
                currentAttList.addAttribute("ServUpWQ", 0)
                #remove all attributes, wipe the attributes entry in techconfigout with a blank attribute object
                currentAttList.addAttribute("HasSubbasS", 0)
                sys_implement.remove(sys_descr)
                city.removeComponent(sys_descr.getUUID())
        return True

    def retrofit_WithRenewal(self, ID, sys_implement,city):
        """Implements the "WITH RENEWAL" Retrofit Scenario across the entire map
        With Renewal: Technologies at different scales are selected for retrofitting
         depending on the block's age and renewal cycles configured by the user
         - Technologies are first considered for keeping, upgrading or decommissioning
         - Keep: impervious area they already treat will be removed from the outstanding
         impervious area to be treated and that scale in said Block marked as 'taken'
         - Upgrade: technology targets will be looked at and compared, the upgraded technology
         is assessed and then implemented. Same procedures as for Keep are subsequently
         carried out with the new design
         - Decommission: technology is removed from the area, impervious area is freed up
         scale in said block is marked as 'available'"""

        time_passed = self.currentyear - self.prevyear
        
        print "Block: "+str(ID)
        print sys_implement
        
        currentAttList = self.getBlockUUID(ID,city)
        inblock_imp_treated = 0
        
        if self.renewal_cycle_def == 0:
            self.retrofit_DoNothing(ID, sys_implement,city) #if no renewal cycle was defined
            return True #go through the Do Nothing Loop instead
            
        #LOT, STREET, NEIGH
        for luc_code in ["L_RES", "L_HDR", "L_LI", "L_HI", "L_COM", "S", "N"]:
            sys_descr = self.locatePlannedSystems(sys_implement, luc_code,city)
            if sys_descr == None:
                inblock_imp_treated += 0
                currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 0)
                continue
            
            #Get Renewal Cycle Variable
            if luc_code in ["L_RES", "L_HDR", "L_LI", "L_HI", "L_COM"]:
                renewalyears = self.renewal_lot_years
            elif luc_code == "S":
                renewalyears = self.renewal_street_years
            elif luc_code == "N":
                renewalyears = self.renewal_neigh_years
            
            #DO SOMETHING TO DETERMINE IF YES/NO RETROFIT, then check the decision
            if time_passed - (time_passed // renewalyears)*renewalyears == 0:
                go_retrofit = 1 #then it's time for renewal
                print "Before: "+str(sys_descr.getAttribute("GoalQty").getDouble())
                #modify the current sys_descr attribute to take into account lot systems that have disappeared.
                #If systems have disappeared the final quantity of lot implementation (i.e. goalqty) will drop
                if luc_code == "L_RES":
                    sys_descr = self.updateForBuildingStockRenewal(currentAttList, sys_descr)
                print "After: "+str(sys_descr.getAttribute("GoalQty").getDouble())
            else:
                go_retrofit = 0
                
            #NOW DETERMINE IF ARE RETROFITTING OR NOT: IF NOT READY FOR RETROFIT, KEEP, ELSE GO INTO CYCLE
            oldImp = sys_descr.getAttribute("ImpT").getDouble() #Old ImpT using the old GoalQty value
            decision, newImpT = self.dealWithSystem(currentAttList, sys_descr, luc_code ,city) #gets the new ImpT using new GoalQty value (if it changed)
            if go_retrofit == 0:        #If the decision is to NOT retrofit yet, then KEEP the system
                decision = 1
                
            if decision == 1: #KEEP
                print "Keeping the System"
                currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1)
                Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
                if luc_code == "L_RES":
                    imptreated = min(newImpT, Aimplot)
                else:
                    imptreated = newImpT
                inblock_imp_treated += imptreated
                sys_descr.changeAttribute("ImpT", imptreated)
                sys_descr.changeAttribute("CurImpT", imptreated * sys_descr.getAttribute("Qty").getDouble())
                
            elif decision == 2: #RENEWAL
                if luc_code in ["L_RES", "L_HDR", "L_COM", "L_LI", "L_HI"]:
                    print "Lot-scale systems will not allow renewal, instead the systems will be kept as is until plan is abandoned"
                    currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1)
                    Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
                    if luc_code == "L_RES":
                        imptreated = min(newImpT, Aimplot)
                    else:
                        imptreated = newImpT
                    inblock_imp_treated += imptreated
                    sys_descr.changeAttribute("ImpT", imptreated)
                    sys_descr.changeAttribute("CurImpT", imptreated * sys_descr.getAttribute("Qty").getDouble())
                    #FUTURE DYNAMICS TO BE INTRODUCED
                else:
                    print "Renewing the System - Redesigning and Assessing Space Requirements"
                    newAsys, newEAFact = self.redesignSystem(currentAttList, sys_descr, luc_code, oldImp,city) #get new system size & EA
                
                    #Get available space - depends on scale/luc-code
                    if luc_code == "S":
                        avlSpace = currentAttList.getAttribute("avSt_RES").getDouble()
                    elif luc_code == "N":
                        avlSpace = currentAttList.getAttribute("PG_av").getDouble() + currentAttList.getAttribute("REF_av").getDouble()
                    
                    if newAsys > avlSpace and self.renewal_alternative == "K": #if system does not fit and alternative is 'Keep'
                        print "Cannot fit new system design, keeping old design instead"
                        currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1)
                        inblock_imp_treated += newImpT
                        sys_descr.changeAttribute("ImpT", newImpT)
                        sys_descr.changeAttribute("CurImpT", newImpT * sys_descr.getAttribute("Qty").getDouble())
                    elif newAsys > avlSpace and self.renewal_alternative == "D": #if system does not fit and alternative is 'Decommission'
                        print "Cannot fit new system design, decommissioning instead"
                        inblock_imp_treated += 0 #quite self-explanatory but is added here for clarity
                        currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1)
                        sys_implement.remove(sys_descr)
                        city.removeComponent(sys_descr.getUUID())
                    else: #otherwise it'll fit, transfer new information
                        print "New System Upgrades fit, transferring this information to output"
                        currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 1)
                        self.defineUpgradedSystemAttributes(sys_descr, newAsys, newEAFact, oldImp)
                        inblock_imp_treated += oldImp

            elif decision == 3: #DECOMMISSIONING
                print "Decommissioning the system"
                inblock_imp_treated += 0 #quite self-explanatory but is added here for clarity
                #remove all attributes, wipe the attributes entry in techconfigout with a blank attribute object
                currentAttList.addAttribute("Has"+str(luc_code)+"Sys", 0) #Remove system placeholder
                sys_implement.remove(sys_descr)
                city.removeComponent(sys_descr.getUUID())
                
        currentAttList.addAttribute("ServWQ", inblock_imp_treated)
        inblock_impdeficit = max(currentAttList.getAttribute("Blk_EIA").getDouble() - inblock_imp_treated, 0)
        currentAttList.addAttribute("DeficitIA", inblock_impdeficit)
        
        allotments = currentAttList.getAttribute("ResAllots").getDouble()
        Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble()
        print "Allotments = "+str(allotments)+" of each "+str(Aimplot)+" sqm impervious"
        max_houses = min((inblock_impdeficit/Aimplot)/allotments, 1)
        print "A Lot Strategy in this Block would permit a maximum implementation in: "+str(max_houses*100)+"% of houses"
        currentAttList.addAttribute("MaxLotDeg", max_houses)
        
        #SUBBASIN
        sys_descr = self.locatePlannedSystems(sys_implement, "B",city)
        if sys_descr == None:
            currentAttList.addAttribute("HasBSys", 0)
        else:
            #DO SOMETHING TO DETERMINE IF YES/NO RETROFIT, then check the decision
            if time_passed - (time_passed // self.renewal_neigh_years)*self.renewal_neigh_years == 0:
                go_retrofit = 1 #then it's time for renewal
            else:
                go_retrofit = 0 #otherwise do not do anything
                
            #NOW DETERMINE IF ARE RETROFITTING OR NOT: IF NOT READY FOR RETROFIT, KEEP, ELSE GO INTO CYCLE
            oldImp = sys_descr.getAttribute("ImpT").getDouble()
            decision, newImpT = self.dealWithSystem(currentAttList, sys_descr, "B",city)
            if go_retrofit == 0:
                decision = 1
                
            if decision == 1: #keep
                print "Keeping the System"
                currentAttList.addAttribute("HasBSys", 1)
                currentAttList.addAttribute("ServUpWQ", newImpT)
                sys_descr.changeAttribute("ImpT", newImpT)
                sys_descr.changeAttribute("CurImpT", newImpT * sys_descr.getAttribute("Qty").getDouble())
            
            elif decision == 2: #renewal
                print "Renewing the System - Redesigning and Assessing Space Requirements"
                newAsys, newEAFact = self.redesignSystem(currentAttList, sys_descr, "B", oldImp,city) #get new system size & EA
                avlSpace = currentAttList.getAttribute("PG_av").getDouble() + currentAttList.getAttribute("REF_av").getDouble()
                if newAsys > avlSpace and self.renewal_alternative == "K": #if system does not fit and alternative is 'Keep'
                    print "Cannot fit new system design, keeping old design instead"
                    currentAttList.addAttribute("HasBSys", 1)
                    currentAttList.addAttribute("ServUpWQ", newImpT)
                    sys_descr.changeAttribute("ImpT", newImpT)
                    sys_descr.changeAttribute("CurImpT", newImpT * sys_descr.getAttribute("Qty").getDouble())
                elif newAsys > avlSpace and self.renewal_alternative == "D": #if system does not fit and alternative is 'Decommission'
                    print "Cannot fit new system design, decommissioning instead"
                    currentAttList.addAttribute("ServUpWQ", 0)
                    currentAttList.addAttribute("HasBSys", 0) #Remove system placeholder
                    sys_implement.remove(sys_descr)
                    city.removeComponent(sys_descr.getUUID())
                else: #otherwise it'll fit, transfer new information
                    print "New System Upgrades fit, transferring this information to output"
                    currentAttList.addAttribute("HasBSys", 1)
                    self.defineUpgradedSystemAttributes(sys_descr, newAsys, newEAFact, oldImp)
                    currentAttList.addAttribute("ServUpWQ", oldImp)        #OLD IMP BECAUSE THE REDESIGNED SYSTEM IS NOW LARGER
                                                                                #AND BETTER TO HANDLE SAME IMP AREA AS BEFORE!
            elif decision == 3: #DECOMMISSIONING
                print "Decommissioning the system"
                currentAttList.addAttribute("ServUpWQ", 0)
                #remove all attributes, wipe the attributes entry in techconfigout with a blank attribute object
                currentAttList.addAttribute("HasSubbasS", 0)
                sys_implement.remove(sys_descr)
                city.removeComponent(sys_descr.getUUID())
        return True
    
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
            if purposeQ == None:
                purposeQ = 0
        except NameError:
            purposeQ = 0
        try:
            purposeWQ = eval("self."+j+"pollute")
            if purposeWQ == None:
                purposeWQ = 0
        except NameError:
            purposeWQ = 0
        try:
            purposeREC = eval("self."+j+"recycle")
            if purposeREC == None:
                purposeREC = 0
        except NameError:
            purposeREC = 0
        purposes = [purposeQ, purposeWQ, purposeREC]
        purposebooleans = [int(self.ration_runoff), int(self.ration_pollute), int(self.ration_harvest)]
        for i in range(len(purposes)):
            purposes[i] *= purposebooleans[i]
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
            incr_matrix.append(round(float(1/increment)*(i+1),3))
        return incr_matrix
    
    def retrieveStreamBlockIDs(self, currentAttList, direction):
        """Returns a vector containing all upstream block IDs, allows quick collation of 
        details.
        """
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
            return []
        else:
            return streamIDs

    def retrieveAttributeFromIDs(self, city, listIDs, attribute, calc):
        """Retrieves all values from the list of upstreamIDs with the attribute name
        <attribute> and calculates whatever <calc> specifies
            Input:
                - city: the city datastream with the block Views
                - listIDs: the vector list of upstream IDs e.g. [3, 5, 7, 8, 10, 15, 22]
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
        
        for i in listIDs:
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
            print "No lot units to build on"
            return tdRES, tdHDR, tdLI, tdHI, tdCOM
        
        lot_avail_sp = currentAttList.getAttribute("avLt_RES").getDouble() * int(self.service_res)
        hdr_avail_sp = currentAttList.getAttribute("av_HDRes").getDouble() * int(self.service_hdr)
        LI_avail_sp = currentAttList.getAttribute("avLt_LI").getDouble() * int(self.service_li)
        HI_avail_sp = currentAttList.getAttribute("avLt_HI").getDouble() * int(self.service_hi)
        com_avail_sp = currentAttList.getAttribute("avLt_COM").getDouble() * int(self.service_com)
        if lot_avail_sp + hdr_avail_sp + LI_avail_sp + HI_avail_sp + com_avail_sp < 0.0001:    #if there is absolutely no space, then continue
            print "No lot space to build on"
            return tdRES, tdHDR, tdLI, tdHI, tdCOM
        
        #Reinitialize Technology vectors, this time as empty
        tdRES = []     #empty vectors to be filled out with technologies, if there is NO technology, then the vector
        tdHDR = []      #is given only one value of zero, if there is at least one technology, zero disappears.
        tdLI = []
        tdHI = []
        tdCOM = []
        
        #GET INFORMATION FROM VECTOR DATA
        soilK = currentAttList.getAttribute("Soil_k").getDouble()                       #soil infiltration rate on area
        #print "Soil infiltration rate (mm/hr): "+str(soilK)
        Aimplot = currentAttList.getAttribute("ResLotEIA").getDouble() #effective impervious area of one residential allotment
        Aimphdr = currentAttList.getAttribute("HDR_EIA").getDouble()
        AimpLI = currentAttList.getAttribute("LIAeEIA").getDouble()
        AimpHI = currentAttList.getAttribute("HIAeEIA").getDouble()
        AimpCOM = currentAttList.getAttribute("COMAeEIA").getDouble()
                                                                    #>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> POP
        #print "Impervious Area on Lot: ", Aimplot
        #print "Impervious Area on HDR: ", Aimphdr
        #print "Impervious Area on LI: ", AimpLI
        #print "Impervious Area on HI: ", AimpHI
        #print "Impervious Area on COM: ", AimpCOM
        
        #Size the required store to achieve the required potable supply substitution.
        storeVols = []
        if bool(int(self.ration_harvest)):
            store_volRES = self.determineStorageVolForLot(currentAttList, self.raindata, self.evapscale, "RW", "RES")
            store_volHDR = self.determineStorageVolForLot(currentAttList, self.raindata, self.evapscale, "RW", "HDR")
            storeVols = [store_volRES, store_volHDR] #IF 100% service is to occur
            #print storeVols
        else:
            storeVols = [np.inf, np.inf]        #By default it is "not possible"
        
        for j in techList:
            #print "Current Tech: ", j
            tech_applications = self.getTechnologyApplications(j)
            minsize = eval("self."+j+"minsize")         #gets the specific system's minimum allowable size
            maxsize = eval("self."+j+"maxsize")          #gets the specific system's maximum size
            #Design curve path
            dcvpath = self.getDCVPath(j)            #design curve file as a string
            hasRESsystems = int(currentAttList.getAttribute("HasL_RESSys").getDouble())
            if hasRESsystems == 0 and hasHouses != 0 and Aimplot > 0.0001 and j not in ["banned","list","of","tech"]:    #Do lot-scale house system
                sys_object = self.designTechnology(1.0, Aimplot, j, dcvpath, tech_applications, soilK, minsize, maxsize, lot_avail_sp, "RES", currentID, storeVols[0])
                if sys_object == 0:
                    pass
                else:
                    tdRES.append(sys_object)
            if len(tdRES) == 0:
                tdRES.append(0) #if the array is completely empty, append zero, otherwise leave zero out
            
            hasHDRsystems = int(currentAttList.getAttribute("HasL_HDRSys").getDouble())
            if hasHDRsystems == 0 and hasApts != 0 and Aimphdr > 0.0001 and j not in ["banned","list","of","tech"]:    #Do apartment lot-scale system
                for i in self.lot_incr:
                    if i == 0:
                        continue
                    sys_object = self.designTechnology(i, Aimphdr, j, dcvpath, tech_applications, soilK, minsize, maxsize, hdr_avail_sp, "HDR", currentID, np.inf)
                    if sys_object == 0:
                        pass
                    else:
                        tdHDR.append(sys_object)
            if len(tdHDR) == 0:
                tdHDR.append(0)
            
            hasLIsystems = int(currentAttList.getAttribute("HasL_LISys").getDouble())  
            if hasLIsystems == 0 and hasLI != 0 and AimpLI > 0.0001 and j not in ["banned","list","of","tech"]:
                for i in self.lot_incr:
                    if i == 0:
                        continue
                    sys_object = self.designTechnology(i, AimpLI, j, dcvpath, tech_applications, soilK, minsize, maxsize, LI_avail_sp, "LI", currentID, np.inf)
                    if sys_object == 0:
                        pass
                    else:
                        tdLI.append(sys_object)
            if len(tdLI) == 0:
                tdLI.append(0)
            
            hasHIsystems = int(currentAttList.getAttribute("HasL_HISys").getDouble())
            if hasHIsystems == 0 and hasHI != 0 and AimpHI > 0.0001 and j not in ["banned","list","of","tech"]:
                for i in self.lot_incr:
                    if i == 0:
                        continue
                    sys_object = self.designTechnology(i, AimpHI, j, dcvpath, tech_applications, soilK, minsize, maxsize, HI_avail_sp, "HI", currentID, np.inf)
                    if sys_object == 0:
                        pass
                    else:
                        tdHI.append(sys_object)
            if len(tdHI) == 0:
                tdHI.append(0)
            
            hasCOMsystems = int(currentAttList.getAttribute("HasL_COMSys").getDouble())
            if hasCOMsystems == 0 and hasCOM != 0 and AimpCOM > 0.0001 and j not in ["banned","list","of","tech"]:
                for i in self.lot_incr:
                    if i == 0:
                        continue
                    sys_object = self.designTechnology(i, AimpCOM, j, dcvpath, tech_applications, soilK, minsize, maxsize, com_avail_sp, "COM", currentID, np.inf)
                    if sys_object == 0:
                        pass
                    else:
                        tdCOM.append(sys_object)
            if len(tdCOM) == 0:
                tdCOM.append(0)
            
            #Can insert more land uses here in future e.g. municipal
        return tdRES, tdHDR, tdLI, tdHI, tdCOM
    
    def designTechnology(self, incr, Aimp, techabbr, dcvpath, tech_applications, soilK, minsize, maxsize, avail_sp, landuse, currentID, storeObj):
        """Carries out the lot-scale design for a given system type on a given land use. This function is
        used for the different land uses that can accommodate lot-scale technologies in the model.
        """            
        scalematrix = {"RES":'L', "HDR":'L', "LI":'L', "HI":'L', "COM":'L', "Street":'S', "Neigh":'N', "Subbas":'B'}
        try:
            curscale = scalematrix[landuse]
        except KeyError:
            curscale = 'NA'
        Adesign_imp = Aimp * incr
        #print storeObj
        if storeObj != np.inf:
            design_Dem = storeObj.getSupply()
            #print "Size of Tank: ", storeObj.getSize()
        else:
            design_Dem = 0
        #print "Design Demand :", design_Dem
        
        #print techabbr
        #OBJECTIVE 1 - Design for Runoff Control
        if tech_applications[0] == 1:
            purpose = [tech_applications[0], 0, 0]
            AsystemQty = eval('td.design_'+str(techabbr)+'('+str(Adesign_imp)+',"'+str(dcvpath)+'",'+str(self.targetsvector)+','+str(purpose)+','+str(soilK)+','+str(minsize)+','+str(maxsize)+')')
            #print AsystemQty
        else:
            AsystemQty = [None, 1]
        Asystem = AsystemQty    #First target, set as default system size, even if zero
        
        #OBJECTIVE 2 - Design for WQ Control
        if tech_applications[1] == 1:
            purpose = [0, tech_applications[1], 0]
            AsystemWQ = eval('td.design_'+str(techabbr)+'('+str(Adesign_imp)+',"'+str(dcvpath)+'",'+str(self.targetsvector)+','+str(purpose)+','+str(soilK)+','+str(minsize)+','+str(maxsize)+')')    
            #print AsystemWQ
        else:
            AsystemWQ = [None, 1]
        if AsystemWQ[0] > Asystem[0]:
            Asystem = AsystemWQ #if area for water quality is greater, choose the governing one as the final system size
        
        #OBJECTIVE 3 - If system type permits storage, design for Recycling
        if tech_applications[2] == 1 and storeObj != np.inf:
            if techabbr in ["RT", "GW", "WSUR", "PB"]:        #Then design storage
                addstore = True
                sysdepth = self.sysdepths[techabbr]
                vol = storeObj.getSize()
                AsystemRec = eval('td.sizeStoreArea_'+str(techabbr)+'('+str(vol)+','+str(sysdepth)+','+str(0)+','+str(9999)+')')
            else:
                addstore = False
                AsystemRec = [None, 1]
        else:
            addstore = False
            AsystemRec = [None, 1]        #[surface area, area factor, storage volume], the only exception
        
        if AsystemRec[0] > Asystem[0]:
            Asystem = AsystemRec        #If area for recycling is bigger, choose that instead
        #print "Final design outcome for :", techabbr, Asystem
        if Asystem[0] < avail_sp and Asystem[0] != None:        #if it fits and is NOT a NoneType
            #print "Fits"
            servicematrix = [0,0,0]
            if AsystemQty[0] != None:
                servicematrix[0] = Adesign_imp
            if AsystemWQ[0] != None:
                servicematrix[1] = Adesign_imp
            if AsystemRec[0] != None:
                servicematrix[2] = design_Dem
            servicematrixstring = tt.convertArrayToDBString(servicematrix)
            self.dbcurs.execute("INSERT INTO watertechs VALUES ("+str(currentID)+",'"+str(techabbr)+"',"+str(Asystem[0])+",'"+curscale+"','"+str(servicematrixstring)+"',"+str(Asystem[1])+",'"+str(landuse)+"',"+str(incr)+")")
            sys_object = tt.WaterTech(techabbr, Asystem[0], curscale, servicematrix, Asystem[1], landuse, currentID)
            if addstore:
                sys_object.addRecycledStoreToTech(storeObj)     #If analysis showed that system can accommodate store, add the store object
            sys_object.setDesignIncrement(incr)
            return sys_object
        else:
            #print "Does not fit or not feasible"
            return 0
    
    def assessStreetOpportunities(self, techList, currentAttList):
        """Assesses if the shortlist of street-scale technologies can be put into the streetscape
        Does this for one block at a time, depending on the currentAttributesList and the techlist
        """
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        technologydesigns = []
        #Check first if there is residential lot to manage
        hasHouses = int(currentAttList.getAttribute("HasHouses").getDouble())
        hasSsystems = int(currentAttList.getAttribute("HasSSys").getDouble())
        if hasHouses == 0 or hasSsystems == 1:
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
        
        storeObj = np.inf       #No storage recycling for this scale
        
        for j in techList:
            tech_applications = self.getTechnologyApplications(j)
            minsize = eval("self."+j+"minsize")
            maxsize = eval("self."+j+"maxsize")          #gets the specific system's maximum size
            #Design curve path
            dcvpath = self.getDCVPath(j)
            
            for lot_deg in self.lot_incr:
                AimpremainRes = AimpstRes + (AimpRes - Aimplot * allotments * lot_deg) #street + remaining lot
                AimpremainHdr = Aimphdr*(1.0-lot_deg)
                
                for street_deg in self.street_incr:
                    #print "CurrentStreet Deg: ", street_deg, "for lot-deg ", lot_deg
                    if street_deg == 0:
                        continue
                    AimptotreatRes = AimpremainRes * street_deg
                    AimptotreatHdr = AimpremainHdr * street_deg
                    #print "Aimp to treat: ", AimptotreatRes
                    if hasHouses != 0 and AimptotreatRes > 0.0001:
                        sys_object = self.designTechnology(street_deg, AimptotreatRes, j, dcvpath, 
                                                           tech_applications, soilK, minsize, maxsize, 
                                                           street_avail_Res, "Street", currentID, storeObj)
                        if sys_object == 0:
                            pass
                        else:
                            sys_object.setDesignIncrement([lot_deg, street_deg])
                            technologydesign.append(sys_object)
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
        hasNsystems = int(currentAttList.getAttribute("HasNSys").getDouble())
        hasBsystems = int(currentAttList.getAttribute("HasBSys").getDouble())
        if AblockEIA <= 0.0001 or hasNsystems == 1 or hasBsystems == 1:
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
        
        #Size a combination of stormwater harvesting stores
        if bool(int(self.ration_harvest)):
            neighSWstores = self.determineStorageVolNeigh(currentAttList, self.raindata, self.evapscale, "SW")
            #print neighSWstores
                
        for j in techList:
            tech_applications = self.getTechnologyApplications(j)
            minsize = eval("self."+j+"minsize")
            maxsize = eval("self."+j+"maxsize")         #Gets the specific system's maximum size
            #Design curve path
            dcvpath = self.getDCVPath(j)
            for neigh_deg in self.neigh_incr:
                #print "Current Neigh Deg: ", neigh_deg
                if neigh_deg == 0: continue
                Aimptotreat = neigh_deg * AblockEIA
                if bool(int(self.ration_harvest)):
                    curStoreObjs = neighSWstores[neigh_deg]
                    for supplyincr in self.neigh_incr:
                        if supplyincr == 0 or Aimptotreat < 0.0001: 
                            continue
                        storeObj = curStoreObjs[supplyincr]
                        sys_object = self.designTechnology(neigh_deg, Aimptotreat, j, dcvpath, tech_applications,
                                         soilK, minsize, maxsize, totalavailable, "Neigh", currentID, storeObj)
                        if sys_object != 0:
                            sys_object.setDesignIncrement(neigh_deg)
                            technologydesigns.append(sys_object)
                else:
                    if Aimptotreat < 0.0001:
                        continue
                    storeObj = np.inf
                    sys_object = self.designTechnology(neigh_deg, Aimptotreat, j, dcvpath, tech_applications,
                                                       soilK, minsize, maxsize, totalavailable, "Neigh", currentID, storeObj) 
                    if sys_object != 0:
                        sys_object.setDesignIncrement(neigh_deg)
                        technologydesigns.append(sys_object)
                    
#            for lot_deg in self.lot_incr:
#                Aimpremain = AblockEIA - lot_deg*allotments*Aimplot - lot_deg*Aimphdr
#                for neigh_deg in self.neigh_incr:
#                    #print "CurrentNeigh Deg: ", neigh_deg, "for lot-deg ", lot_deg
#                    if neigh_deg == 0:
#                        continue
#                    Aimptotreat=  neigh_deg * Aimpremain
#                    #print "Aimp to treat: ", Aimptotreat
#                    if Aimptotreat > 0.0001:
#                        sys_object = self.designTechnology(neigh_deg, Aimptotreat, 0, j,
#                                                           dcvpath, tech_applications, soilK, minsize,
#                                                           maxsize, totalavailable, "Neigh", currentID, storeObj)
#                        if sys_object == 0:
#                            pass
#                        else:
#                            sys_object.setDesignIncrement([lot_deg, neigh_deg])
#                            technologydesigns.append(sys_object)
        return technologydesigns

    def assessSubbasinOpportunities(self, techList, currentAttList, city):
        """Assesses if the shortlist of sub-basin-scale technologies can be put in local parks 
        & other areas. Does this for one block at a time, depending on the currentAttributesList 
        and the techlist
        """
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        
        technologydesigns = {}  #Three Conditions: 1) there must be upstream blocks
                                                 # 2) there must be space available, 
                                                 # 3) there must be impervious to treat
        soilK = currentAttList.getAttribute("Soil_k").getDouble()
        #CONDITION 1: Grab Block's Upstream Area
        upstreamIDs = self.retrieveStreamBlockIDs(currentAttList, "upstream")
        hasBsystems = int(currentAttList.getAttribute("HasBSys").getDouble())
        hasNsystems = int(currentAttList.getAttribute("HasBSys").getDouble())
        if len(upstreamIDs) == 0 or hasBsystems == 1 or hasNsystems == 1:
            #print "Current Block has no upstream areas, skipping"
            return technologydesigns
        
        #CONDITION 2: Grab Total available space, if there is none, no point continuing
        av_PG = currentAttList.getAttribute("PG_av").getDouble()
        av_REF = currentAttList.getAttribute("REF_av").getDouble()
        totalavailable = av_PG + av_REF
        if totalavailable < 0.0001:
            #print "Total Available Space in Block to do STUFF: ", totalavailable, "less than threshold"
            return technologydesigns
        
        #CONDITION 3: Get Block's upstream Impervious area
        upstreamImp = self.retrieveAttributeFromIDs(city, upstreamIDs, "Blk_EIA", "sum")
        if upstreamImp < 0.0001:
            #print "Total Upstream Impervious Area: ", upstreamImp, "less than threshold"
            return technologydesigns
        
        #Initialize techdesignvector's dictionary keys
        for j in self.subbas_incr:
            technologydesigns[j] = []

        if bool(int(self.ration_harvest)):
            subbasSWstores = self.determineStorageVolSubbasin(currentAttList, city, self.raindata, self.evapscale, "SW")
            #print "Subbasin: ", subbasSWstores
        
        for j in techList:
            #print j
            tech_applications = self.getTechnologyApplications(j)
            minsize = eval("self."+j+"minsize")
            maxsize = eval("self."+j+"maxsize")     #Gets the specific system's maximum allowable size
            #Design curve path
            dcvpath = self.getDCVPath(j)
            for bas_deg in self.subbas_incr:
                #print "Current Basin Deg: ", bas_deg
                if bas_deg == 0:
                    continue
                Aimptotreat = upstreamImp * bas_deg
#                print "Aimp to treat: ", Aimptotreat
                #Loop across all options in curStoreObj
                if bool(int(self.ration_harvest)):
                    curStoreObjs = subbasSWstores[bas_deg]  #current dict of possible stores based on harvestable area (bas_Deg)
                    for supplyincr in self.subbas_incr:
                        if supplyincr == 0 or Aimptotreat < 0.0001: 
                            continue
                        storeObj = curStoreObjs[supplyincr]
                        sys_object = self.designTechnology(bas_deg, Aimptotreat, j, dcvpath, tech_applications, 
                                        soilK, minsize, maxsize, totalavailable, "Subbas", currentID, storeObj)
                        if sys_object != 0:
                            sys_object.setDesignIncrement(bas_deg)
                            technologydesigns[bas_deg].append(sys_object)
                else:
                    storeObj = np.inf
                    sys_object = self.designTechnology(bas_deg, Aimptotreat, j, dcvpath, tech_applications, 
                                        soilK, minsize, maxsize, totalavailable, "Subbas", currentID, storeObj)
                    if sys_object != 0:
                        sys_object.setDesignIncrement(bas_deg)
                        technologydesigns[bas_deg].append(sys_object)
        return technologydesigns

    def constructInBlockOptions(self, currentAttList, lot_techRES, lot_techHDR, lot_techLI, 
                                lot_techHI, lot_techCOM, street_tech, neigh_tech):
        """Tries every combination of technology and narrows down the list of in-block
        options based on MCA scoring and the Top Ranking Configuration selected by the
        user. Returns an array of the top In-Block Options for piecing together with
        sub-basin scale systems
        """
        allInBlockOptions = {}
        currentID = int(currentAttList.getAttribute("BlockID").getDouble())
        blockarea = pow(self.block_size,2)*currentAttList.getAttribute("Active").getDouble()
        for i in range(len(self.subbas_incr)):         #[0, 0.25, 0.5, 0.75, 1.0]
            allInBlockOptions[self.subbas_incr[i]] = []       #Bins are: 0 to 25%, >25% to 50%, >50% to 75%, >75% to 100% of block treatment
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
        
        AblockEIA = currentAttList.getAttribute("Blk_EIA").getDouble()          #Total block imp area
        blockDem = currentAttList.getAttribute("Blk_WD").getDouble() - currentAttList.getAttribute("wd_Nres_IN").getDouble()
        
        lot_tech = []
        for a in range(len(self.lot_incr)):     #lot_incr = [0, ....., 1.0]
            lot_deg = self.lot_incr[a]   #currently working on all lot-scale systems of increment lot_deg
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
        combocheck =[]
        for a in lot_tech:
            for b in street_tech:
                for c in neigh_tech:
                    lot_deg = a[0]
                    combo = [a[1], a[2], a[3], a[4], a[5], b, c]
                    #if combo in combocheck:
                    #    continue
                    combocheck.append(combo)
                    #print "Combo: ", combo, "at lot deg: ", lot_deg
                    lotcounts = [int(lot_deg * allotments), int(1), int(estatesLI), int(estatesHI), int(estatesCOM),int(1),int(1)]
                    
                    if allotments != 0 and int(lot_deg*allotments) == 0:
                        continue        #the case of minimal allotments on-site where multiplying by lot-deg and truncation returns zero
                                        #this results in totalimpserved = 0, therefore model crashes on ZeroDivisionError
                    
                    #Check if street + lot systems exceed the requirements
                    if a[1] != 0 and b != 0 and (a[1].getService("Qty")*allotments + b.getService("Qty")) > (AimpRes+AimpstRes):
                        continue    #Overtreatment occurring in residential district at the lot scale for "Qty"
                    if a[1] != 0 and b != 0 and (a[1].getService("WQ")*allotments + b.getService("WQ")) > (AimpRes+AimpstRes):
                        continue    #Overtreatment occurring in residential district at the lot scale for "WQ"
                    if combo.count(0) == 7:
                        continue
                    
                    servicematrix = self.getTotalComboService(combo, lotcounts)
                    #print servicematrix
                    
                    if servicematrix[0] > AblockEIA or servicematrix[1] > AblockEIA:
                        #print "Overtreatment on Qty or WQ side"
                        continue
                    elif servicematrix[2] > blockDem: #CHANGE TO DEMAND!
                        #print "Oversupply of demand"
                        continue
                    else:
                        #print "Strategy is fine"
                        #Create Block Strategy and put it into one of the subbas bins of allInBlockOptions
                        servicebin = self.identifyBin(servicematrix, AblockEIA, blockDem)
                        blockstrat = tt.BlockStrategy(combo, servicematrix, lotcounts, currentID, servicebin)
                        
                        tt.CalculateMCATechScores(blockstrat,[AblockEIA, AblockEIA, blockDem],self.priorities, \
                                                    self.mca_techlist, self.mca_tech, self.mca_env, self.mca_ecn, \
                                                    self.mca_soc)
                        
                        tt.CalculateMCAStratScore(blockstrat, [self.bottomlines_tech_w, self.bottomlines_env_w, \
                                                               self.bottomlines_ecn_w, self.bottomlines_soc_w])
                        #Write to DB file
                        dbs = tt.createDataBaseString(blockstrat)
                        self.dbcurs.execute("INSERT INTO blockstrats VALUES ("+str(dbs)+")")
                        
                    if len(allInBlockOptions[servicebin]) < 10:         #If there are less than ten options in each bin...
                        allInBlockOptions[servicebin].append(blockstrat)        #append the current strategy to the list of that bin
                    else:               #Otherwise get bin's lowest score, compare and replace if necessary
                        lowestscore, lowestscoreindex = self.getServiceBinLowestScore(allInBlockOptions[servicebin])
                        if blockstrat.getTotalMCAscore() > lowestscore:
                            allInBlockOptions[servicebin].pop(lowestscoreindex)      #Pop the lowest score and replace
                            allInBlockOptions[servicebin].append(blockstrat)
                            #dbs = tt.createDataBaseString(blockstrat)
                        else:
                            blockstrat = 0      #set null reference
        
        #Transfer all to database table
        for key in allInBlockOptions.keys():
            for i in range(len(allInBlockOptions[key])):
                dbs = tt.createDataBaseString(allInBlockOptions[key][i])
                self.dbcurs.execute("INSERT INTO blockstratstop VALUES ("+str(dbs)+")")
        
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
        service_abbr = ["Qty", "WQ", "Rec"]
        service_booleans = [int(self.ration_runoff), int(self.ration_pollute), int(self.ration_harvest)]
        servicematrix = [0,0,0]
        for j in range(len(servicematrix)):
            if service_booleans[j] == 0:        #If not interested in that particular part
                servicematrix[j] = 0    #Set that service matrix entry to zero and continue
                continue
            abbr = service_abbr[j]
            for tech in techarray:
                if tech == 0:
                    continue
                if tech.getScale() == "L" and tech.getLandUse() == "RES":
                    servicematrix[j] += tech.getService(abbr) * lotcounts[0]
                elif tech.getScale() == "L" and tech.getLandUse() == "LI":
                    servicematrix[j] += tech.getService(abbr) * lotcounts[2]
                elif tech.getScale() == "L" and tech.getLandUse() == "HI":
                    servicematrix[j] += tech.getService(abbr) * lotcounts[3]
                elif tech.getScale() == "L" and tech.getLandUse() == "COM":
                    servicematrix[j] += tech.getService(abbr) * lotcounts[4]
                else:
                    servicematrix[j] += tech.getService(abbr)
        return servicematrix

    def identifyBin(self, servicematrix, AblockEIA, totdemand):
        """Determines what bin to sort a particular service into, used when determining
        which bin a BlockStrategy should go into"""
        servicelevels = [servicematrix[0]/AblockEIA, servicematrix[1]/AblockEIA, servicematrix[2]/totdemand]
        
        #bracketwidth = 1.0/float(self.subbas_rigour)   #Used to bin the score within the bracket and penalise MCA score
        blockstratservice = max(servicelevels)
        #print "Maximum service achieved is: ", blockstratservice, servicelevels
        for i in self.subbas_incr:      #[0(skip), 0.25, 0.5, 0.75, 1.0]
            if i == 0:
                continue        #Skip the zero increment
            if blockstratservice < i:   #bins will go from 0 to 0.25, 0.25, to 0.5 etc. (similar for other incr)
                return i
#            if i == 0:
#                if blockstratservice < i:
#                    return i
#                else:
#                    continue
#            if servicelevel > (i-(bracketwidth/2)) and servicelevel < (i+(bracketwidth/2)):
#                return i
#            if i == 1:
#                if servicelevel > (i-(bracketwidth/2)) and servicelevel < i:
#                    return i
#                else:
#                    continue
        return max(self.subbas_incr)
        
    def getBasinBlockIDs(self, currentBasinID, numblocks, city):
        """Retrieves all blockIDs within the single basin and returns them in the order
        of upstream to downstream based on the length of the upstream strings."""
        basinblocksortarray = []
        basinblockIDs = []
        outletID = 0
        for i in range(int(numblocks)):
            currentID = i+1
            currentAttList = self.getBlockUUID(currentID, city)
            if currentAttList.getAttribute("BasinID").getDouble() != currentBasinID:
                continue
            else:
                upstr = currentAttList.getAttribute("UpstrIDs").getString()
                upstreamIDs = upstr.split(',')
                upstreamIDs.remove('')
                basinblocksortarray.append([len(upstreamIDs),currentID])
            if currentAttList.getAttribute("Outlet").getDouble() == 1:
                outletID = currentID
        basinblocksortarray.sort()      #sort ascending based on length of upstream string
        for i in range(len(basinblocksortarray)):
            basinblockIDs.append(basinblocksortarray[i][1])     #append just the ID of block
        return basinblockIDs, outletID

    
    def findSubbasinPartakeIDs(self, basinBlockIDs, subbas_options):
        """Searches the blocks within the basin for locations of possible sub-basin scale
        technologies and returns a list of IDs"""
        partake_IDs = []
        for i in range(len(basinBlockIDs)):
            currentID = int(basinBlockIDs[i])
            try:
                if len(subbas_options["BlockID"+str(currentID)]) != 0:
                    partake_IDs.append(currentID)
                else:
                    continue
            except KeyError:
                continue
        return partake_IDs

    
    def selectTechLocationsByRandom(self, partakeIDs, basinblockIDs):
        """Samples by random a number of sub-basin scale technologies and in-block locations
        for the model to place technologies in, returns two arrays: one of the chosen
        sub-basin IDs and one of the chosen in-block locations"""
        techs_subbas = random.randint(0,len(partakeIDs))
        subbas_chosenIDs = []
        for j in range(techs_subbas):
            sample_index = random.randint(0,len(partakeIDs)-1)
            subbas_chosenIDs.append(partakeIDs[sample_index])
            basinblockIDs.remove(partakeIDs[sample_index]) #remove from blocks posisbilities
            partakeIDs.pop(sample_index) #pop the value from the partake list
        
        techs_blocks = random.randint(0, len(basinblockIDs))
        inblocks_chosenIDs = []
        for j in range(techs_blocks):
            sample_index = random.randint(0,len(basinblockIDs)-1)       #If sampling an index, must subtract 1 from len()
            inblocks_chosenIDs.append(basinblockIDs[sample_index])
            basinblockIDs.pop(sample_index)
        
        #Reset arrays
        basinblockIDs = []
        partakeIDs = []
    
        return subbas_chosenIDs, inblocks_chosenIDs
    
    def calculateRemainingService(self, type, basinBlockIDs, city):
        """Assesses the alread treated area/demand for the current basin and returns
        the remaining area/demand to be treated with a strategy.
            - Type: refers to the type of objective "QTY" = quantity, WQ = quality, 
                    REC = recycling
            - basinBlockIDs: array containing all IDs within the current basin
            - city: city datastream variable
        """
        if type in ["WQ", "QTY"]:
            total = self.retrieveAttributeFromIDs(city, basinBlockIDs, "Blk_EIA", "sum")
        elif type in ["REC"]:
            total = self.retrieveAttributeFromIDs(city, basinBlockIDs, "Blk_WD", "sum") - \
                    self.retrieveAttributeFromIDs(city, basinBlockIDs, "wd_Nres_IN")
        
        basinTreated = self.retrieveAttributeFromIDs(city, basinBlockIDs, "Serv"+str(type), "sum")
        basinTreated += self.retrieveAttributeFromIDs(city, basinBlockIDs, "ServUp"+str(type), "sum")
        
        rationales = {"QTY": bool(int(self.ration_runoff)), "WQ": bool(int(self.ration_pollute)),
                      "REC": bool(int(self.ration_harvest)) }
        services = {"QTY": self.servicevector[0], "WQ": self.servicevector[0], "REC": self.servicevector[0]}
        
        if rationales[type]:
            basinRemain = max(total - basinTreated, 0)
        else:
            basinRemain = 0
        
        prevService = basinTreated/total
        if max(1- prevService, 0) == 0:
            delta_percent = 0
        else:
            delta_percent = max(services[type]/100 - prevService,0) / (1 - prevService)
        
        print "Previous Treated Efficiency for ", type, ": ", prevService
        print "Must choose a strategy now that treats: ", (delta_percent*100), "% of basin"
        return delta_percent, basinRemain, basinTreated, total
    
    def populateBasinWithTech(self, current_bstrategy, subbas_chosenIDs, inblocks_chosenIDs, 
                              partakeIDstracker, inblock_options, subbas_options, basinBlockIDs, city):
        """Scans through all blocks within a basin from upstream to downstream end and populates the
        various areas selected in chosenIDs arrays with possible technologies available from the 
        options arrays. Returns an updated current_bstrategy object completed with all details.
        """
        partakeIDs = current_bstrategy.getSubbasPartakeIDs()    #returned in order upstream-->downstream
        
        #Initialize treated Tracking Variable
        subbasID_treatedQTY = {}
        subbasID_treatedWQ = {}
        subbasID_treatedREC = {}        #Depending on the recycling scheme will relate to each block
        
        for i in range(len(partakeIDs)):
            subbasID_treatedQTY[partakeIDs[i]] = 0
            subbasID_treatedWQ[partakeIDs[i]] = 0
            subbasID_treatedREC[partakeIDs[i]] = 0
        
        #Loop across all precinct blocks partaking in possible sub-basin technologies
        for i in range(len(partakeIDs)):
            currentBlockID = partakeIDs[i]
            currentAttList = self.getBlockUUID(currentBlockID, city)
            print "ID: ", currentBlockID
            upstreamIDs = self.retrieveStreamBlockIDs(currentAttList, "upstream")
            upstreamIDs.append(currentBlockID)
            downstreamIDs = self.retrieveStreamBlockIDs(currentAttList, "downstream")
            downstreamIDs.append(currentBlockID)
            
            remain_upIDs = []   #Make a copy of upstreamIDs to track Blocks
            for j in upstreamIDs:
                remain_upIDs.append(j)
            
            #(1) CHECK FOR SUBBASINS WITHIN BLOCK'S UPSTREAM REGION
            subbasinIDs = []
            for sbID in partakeIDstracker:      #Loop across the possible sub-basin locations
                if sbID in upstreamIDs:         #If a location is upstream of the current block
                    subbasinIDs.append(sbID)    #add it.
            if len(subbasinIDs) > 0:   #are there upstream sub-basins?
                for sbID in subbasinIDs:                #then loop over the locations found and
                    partakeIDstracker.remove(sbID)      #remove these from the tracker list so
                                                        #that they are not doubled up
            print "SubbasinIDs: ", subbasinIDs
            
            #Refine the remainIDs list (only the blocks unique to that particular point in basin)
            for sbID in subbasinIDs:            #now loop across the found sub-basin locations
                remain_upIDs.remove(sbID)       #remove these from the remaining IDs
                upstrIDs = self.retrieveStreamBlockIDs(self.getBlockUUID(sbID, city), "upstream") 
                for uID in upstrIDs:
                    remain_upIDs.remove(uID)    #also remove each of their upstream blocks from the list
            
            #(2) OBTAIN HIGHEST ALLOWABLE DEGREE OF TREATMENT (MAX-DEGREE)
            #------ 2.1 Get total imp/dem needing to be treated at the current point in basin
            dP, totalAimpQTY, sv, cp = self.calculateRemainingService("QTY", upstreamIDs, city)
            dP, totalAimpWQ, sv, cp = self.calculateRemainingService("WQ", upstreamIDs, city)
            
            if self.hs_strategy == "ud":
                dP, totalDemREC, sv,cp = self.calculateRemainingService("REC", downstreamIDs, city)
            elif self.hs_strategy == "uu":
                dP, totalDemREC, sv, cp = self.calculateRemainingService("REC", upstreamIDs, city)
            elif self.hs_strategy == "ua":
                dP, totalDemREC, sv, cp = self.calculateRemainingService("REC", basinBlockIDs, city)
                
            #------ 2.2 Subtract the already serviced parts from upstream sub-basin blocks
            subbas_treatedAimpQTY = 0  #Sum of already treated imp area in upstream sub-basins and the now planned treatment
            subbas_treatedAimpWQ = 0
            subbas_treatedDemREC = 0
            
            for sbID in subbasinIDs:
                subbas_treatedAimpQty += subbasID_treatedQTY[sbID]    #Check all upstream sub-basins for their treated Aimp            
                subbas_treatedAimpWQ += subbasID_treatedWQ[sbID]    #Check all upstream sub-basins for their treated Aimp            

            remainAimp_subbasinQTY = max(totalAimpQTY - subbas_treatedAimpQTY, 0)
            remainAimp_subbasinWQ = max(totalAimpWQ - subbas_treatedAimpWQ, 0)

            if self.hs_strategy == 'ud':
                totSupply = 0
                downstreamIDs = []      #the complete matrix of all downstream IDs from all upstream sbIDs
                for sbID in subbasinIDs:
                    totSupply += subbasID_treatedREC[sbID]      #Get total supply of all combined upstream systems
                    sbIDattList = self.getBlockUUID(sbID, city)
                    downIDs = self.retrieveStreamBlockIDs(sbIDattList, "downstream")
                    downIDs.append(sbID)
                    for dID in downIDs:
                        if dID not in downstreamIDs:
                            downstreamIDs.append(dID)
                #Get all blocks between currentID's upstream and sbIDs downstream blocks
                shareIDs = []
                for dID in downstreamIDs:
                    if dID in upstreamIDs and dID not in shareIDs:
                        shareIDs.append(dID)
                #Calculate Total Water Demand of Blocks in between the current point and highest upstream point
                totBetweenDem = self.retrieveAttributeFromIDs(city, shareIDs, "Blk_WD", "sum") - \
                    self.retrieveAttributeFromIDs(city, shareIDs, "wd_Nres_IN", "sum")
                #Remaining demand is total downstream demand minus the higher of (total upstream supply excess and zero)
                remainDem_subbasinRec = totalDemREC - max(totSupply - totBetweenDem, 0)       #<<< NEED TO CALCULATE THIS
            elif self.hs_strategy in ['uu', 'ua']:
                for sbID in subbasinIDs:
                    subbas_treatedDem += subbasID_treatedREC[sbID]
                remainDem_subbasinRec = max(totalDemREC - subbas_treatedDem, 0)
            
            max_degreeQty = 0
            max_degreeWQ = 0
            max_degreeREC = 0
            if totalAimpQTY != 0: max_degreeQty = remainAimp_subbasinQty/totalAimpQTY
            if totalAimpWQ != 0: max_degreeWQ = remainAimp_subbasinWQ/totalAimpWQ
            if totalDemREC != 0: max_degreeREC = remainDem_subbasinRec/totalDemREC
            
            print "Max Degree QTY: ", max_degreeQty
            print "Max Degree WQ: ", max_degreeWQ
            print "Max Degree REC: ", max_degreeREC
            
            max_degree = min(max_degreeQty, max_degreeWQ, max_degreeREC)+float(self.service_redundancy/100.0)  
            #choose the minimum, bring in allowance using redundancy parameter
            
            current_bstrategy.addSubBasinInfo(currentBlockID, upstreamIDs, subbasinIDs, [totalAimp_subbasin,0,0])       #>>>Add on population and public area in future
            
            #(3) PICK A SUB-BASIN TECHNOLOGY
            if currentBlockID in subbas_chosenIDs:              #PART A - first the degree
                deg, obj, treatedQTY, treatedWQ, treatedREC = self.pickOption(currentBlockID, max_degree, subbas_options, [totalAimpQTY, totalAimpWQ, totalDemREC]) 
                subbas_treatedAimpQTY += treatedQTY
                subbas_treatedAimpWQ += treatedWQ
                subbas_treatedDemREC += treatedREC
                remainAimp_subbasinQTY = max(remainAimp_subbasinQTY - treatedQTY, 0)
                remainAimp_subbasinWQ = max(remainAimp_subbasinWQ - treatedWQ, 0)
                remainDem_subbasinRec = max(remainDem_subbasinRec - treatedREC, 0)
                if deg != 0 and obj != 0:
                    current_bstrategy.appendTechnology(currentBlockID, deg, obj, "s")
            
            #(4) PICK AN IN-BLOCK STRATEGY IF IT IS HAS BEEN CHOSEN
            for rbID in remain_upIDs:
                if rbID not in inblocks_chosenIDs:        #If the Block ID hasn't been chosen,
                    continue                            #then skip to next one, no point otherwise
                
                block_Aimp = self.getBlockUUID(rbID, city).getAttribute("Blk_EIA").getDouble()
                block_Dem = self.getBlockUUID(rbID, city).getAttribute("Blk_WD").getDouble() - self.getBlockUUID(rbID, city).getAttribute("wd_Nres_IN").getDouble()
                if block_Aimp == 0:     #Impervious governs pretty much everything, if it is zero, don't even bother
                    continue
                if block_Dem == 0 and bool(int(self.ration_harvest)):   #If demand is zero and we are planning for recycling, skip
                    continue
                else:
                    block_Dem = np.inf  #otherwise set it to something that will allow the division and result in zero degree
                
                max_degree = min(remainAimp_subbasinQTY/block_Aimp, 
                                 remainAimp_subbasinWQ/block_Aimp, remainDem_subbasinRec/block_Dem, 1.0)+float(self.service_redundancy/100.0)
                
                deg, obj, treatedQTY, treatedWQ, treatedREC = self.pickOption(rbID,max_degree,inblock_options, [block_Aimp, block_Aimp, block_Dem]) 
                subbas_treatedAimpQTY += treatedQTY
                subbas_treatedAimpWQ += treatedWQ
                subbas_treatedDemREC += treatedREC
                remainAimp_subbasinQTY = max(remainAimp_subbasinQTY - treatedQTY, 0)
                remainAimp_subbasinWQ = max(remainAimp_subbasinWQ - treatedWQ, 0)
                remainDem_subbasinRec = max(remainDem_subbasinRec - treatedREC, 0)
                if deg != 0 and obj != 0:
                    current_bstrategy.appendTechnology(rbID, deg, obj, "b")
            
            #(5) FINALIZE THE SERVICE VALUES FOR QTY, WQ, REC BEFORE NEXT LOOP
            subbasID_treatedQTY[i] = subbas_treatedAimpQTY
            subbasID_treatedWQ[i] = subbas_treatedAimpWQ
            subbasID_treatedREC[i] = subbas_treatedDemREC
        return True
    
    def evaluateServiceObjectiveFunction(self, basinstrategy, updatedservice):
        """Calculates how close the basinstrategy meets the required service
        levels set by the user. A performance metric is returned. If one of the
        service levels has not been met, performance is automatically assigned
        a value of -1. It will then be removed in the main program.
        The objective function used to find the optimum strategies is calculated
        as:
            choice = min { sum(serviceProvided - serviceRequired) }, OF >0
            updatedservice = [serviceQty, serviceWQ, serviceREC] based on delta_percent
        """
        serviceQty = float(int(self.ration_runoff))*float(updatedservice[0])
        serviceWQ = float(int(self.ration_pollute))*float(updatedservice[1])
        serviceRec = float(int(self.ration_harvest))*float(updatedservice[2])
        serviceRequired = [serviceQty, serviceWQ, serviceRec]
        serviceBooleans = [int(self.ration_runoff), int(self.ration_pollute), int(self.ration_harvest)]
        
        serviceProvided = basinstrategy.getServicePvalues() #[0,0,0] P values for service
        for i in range(len(serviceProvided)):
            serviceProvided[i] *= float(serviceBooleans[i])     #Rescale to ensure no service items are zero
            
        #Objective Criterion: A strategy is most suitable to the user's input
        #requirements if the sum(service-provided - service-required) is a minimum
        #and >0
        negative = False
        performance = 0
        for i in range(len(serviceProvided)):
            performance += (serviceProvided[i] - serviceRequired[i])
            if (serviceProvided[i] - serviceRequired[i]) < 0:
                negative = True
        if negative:
            performance = -1       #One objective at least, not fulfilled
        return performance
    
    def pickOption(self, blockID, max_degree, options_collection, totals):
        """Picks and returns a random option based on the input impervious area and maximum
        treatment degree. Can be used on either the in-block strategies or larger precinct 
        strategies. If it cannot pick anything, it will return zeros all around.
        """
        AimpQTY = totals[0]
        AimpWQ = totals[1]
        DemREC = totals[2]
        indices = []
        for deg in self.subbas_incr:
            if deg <= max_degree:
                indices.append(deg)
        if len(indices) != 0:
            choice = random.randint(0, len(indices)-1)
            chosen_deg = self.subbas_incr[choice]
        else:
            return 0, 0, 0, 0, 0
        
        Nopt = len(options_collection["BlockID"+str(blockID)][chosen_deg])
        if chosen_deg != 0 and Nopt != 0:
            treatedAimpQTY = chosen_deg * AimpQTY
            treatedAimpWQ = chosen_deg * AimpWQ
            treatedDemREC = chosen_deg * DemREC
            choice = random.randint(0, Nopt-1)
            chosen_obj = options_collection["BlockID"+str(blockID)][chosen_deg][choice]
            return chosen_deg, chosen_obj, treatedAimpQTY, treatedAimpWQ, treatedDemREC
        else:
            return 0, 0, 0, 0, 0
    
    def createCDF(self, score_matrix):
        """Creates a cumulative distribution for an input list of values by normalizing
        these first and subsequently summing probabilities.
        """
        pdf = []
        cdf = []
        for i in range(len(score_matrix)):
            pdf.append(score_matrix[i]/sum(score_matrix))
        cumu_p = 0
        for i in range(len(pdf)):
            cumu_p += pdf[i]
            cdf.append(cumu_p)
        cdf[len(cdf)-1] = 1.0   #Adjust for rounding errors
        return cdf
        return cdf
    
    def samplefromCDF(self, selection_cdf):
        """Samples one sample from a cumulative distribution function and returns
        the index. Sampling is uniform, probabilities are determined by the CDF"""
        p_sample = random.random()
        for i in range(len(selection_cdf)):
            if p_sample <= selection_cdf[i]:
                return i
        return (len(selection_cdf)-1)
    
    def writeStrategyView(self, city, id, basinID, basinBlockIDs, strategyobject):
        """Writes the output view of the selected WSUD strategy and saves it to the 
        self.wsudAttr View.
        """
        for i in range(len(basinBlockIDs)):
            currentID = basinBlockIDs[i]
            currentAttList = self.getBlockUUID(currentID, city)
            centreX = currentAttList.getAttribute("CentreX").getDouble()
            centreY = currentAttList.getAttribute("CentreY").getDouble()
            #Grab the strategy objects
            inblock_strat = strategyobject.getIndividualTechStrat(currentID, "b")
            
            if inblock_strat == None:
                inblock_systems = [0,0,0,0,0,0,0]
                inblock_degs = [0,0,0,0,0,0,0]
                inblock_lotcount = [0,0,0,0,0,0,0]
            else:
                inblock_systems = inblock_strat.getTechnologies()
                inblock_degs = [0,0,0,0,0,0,0]
                inblock_lotcount = inblock_strat.getQuantity("all")
                
                for j in range(len(inblock_systems)):
                    if inblock_systems[j] != 0:
                        inblock_degs[j] = inblock_systems[j].getDesignIncrement()
                        
            offsets_matrix = [[centreX+float(self.block_size)/16.0, centreY+float(self.block_size)/4.0],
                              [centreX+float(self.block_size)/12.0, centreY+float(self.block_size)/4.0],
                              [centreX+float(self.block_size)/8.0, centreY+float(self.block_size)/4.0],
                              [centreX+float(self.block_size)/4.0, centreY+float(self.block_size)/4.0],
                              [centreX+float(self.block_size)/3.0, centreY+float(self.block_size)/4.0],
                              [centreX+float(self.block_size)/4.0, centreY-float(self.block_size)/8.0],
                              [centreX-float(self.block_size)/8.0, centreY-float(self.block_size)/4.0],
                              [centreX-float(self.block_size)/4.0, centreY-float(self.block_size)/8.0]]
                                #[Res, HDR, LI, HI, COM, ORC, Street, Neigh, Subbas]
            blockscale_names = ["L_RES", "L_HDR", "L_LI", "L_HI", "L_COM", "S", "N"]
            
            for j in range(len(blockscale_names)):
                if inblock_strat == None or inblock_systems[j] == 0:
                    continue
                current_wsud = inblock_systems[j]
                scale = blockscale_names[j]
                coordinates = offsets_matrix[j]
                goalqty = inblock_lotcount[j]
                
                loc = Component()
                #loc = city.addNode(coordinates[0], coordinates[1], 0, self.wsudAttr)
                loc.addAttribute("StrategyID", id)
                loc.addAttribute("posX", coordinates[0])
                loc.addAttribute("posY", coordinates[1])
                loc.addAttribute("BasinID", basinID)
                loc.addAttribute("Location", currentID)
                loc.addAttribute("Scale", scale)
                loc.addAttribute("Type", current_wsud.getType())
                loc.addAttribute("Qty", 0)      #Currently none available
                loc.addAttribute("GoalQty", goalqty)  #lot scale mainly - number of lots to build
                loc.addAttribute("SysArea", current_wsud.getSize())
                loc.addAttribute("Status", 0)   #0 = not built, 1 = built
                loc.addAttribute("Year", 9999)
                loc.addAttribute("EAFact", current_wsud.getAreaFactor())
                loc.addAttribute("ImpT", current_wsud.getService("WQ"))
                loc.addAttribute("CurImpT", 0)  #New systems don't treat anything yet, not implemented
                loc.addAttribute("Upgrades", 0) #Done in the retrofit/implementation part
                city.addComponent(loc, self.wsudAttr)
                #Transfer the key system specs
                if current_wsud.getType() in ["BF", "IS", "WSUR"]:
                    loc.addAttribute("WDepth", eval("self."+str(current_wsud.getType())+"spec_EDD"))
                if current_wsud.getType() in ["PB"]:
                    loc.addAttribute("WDepth", float(eval("self."+str(current_wsud.getType())+"spec_MD")))
                if current_wsud.getType() in ["BF", "IS"]:
                    loc.addAttribute("FDepth", eval("self."+str(current_wsud.getType())+"spec_FD"))
                
            outblock_strat = strategyobject.getIndividualTechStrat(currentID, "s")
            if outblock_strat != None:
                scale = "B"
                coordinates = offsets_matrix[7]
                
                loc = Component()
                #loc = city.addNode(coordinates[0], coordinates[1], 0, self.wsudAttr)
                loc.addAttribute("StrategyID", id)
                loc.addAttribute("posX", coordinates[0])
                loc.addAttribute("posY", coordinates[1])
                loc.addAttribute("BasinID", basinID)
                loc.addAttribute("Location", currentID)
                loc.addAttribute("Scale", scale)
                loc.addAttribute("Type", outblock_strat.getType())
                loc.addAttribute("Qty", 0)      #currently none available
                loc.addAttribute("GoalQty", 1)  #lot scale mainly - number of lots to build
                loc.addAttribute("SysArea", outblock_strat.getSize())
                loc.addAttribute("Status", 0)
                loc.addAttribute("Year", 9999)
                loc.addAttribute("EAFact", outblock_strat.getAreaFactor())
                loc.addAttribute("ImpT", outblock_strat.getService("WQ"))
                loc.addAttribute("CurImpT", 0)  #New systems don't treat anything yet before implemented
                loc.addAttribute("Upgrades", 0)
                city.addComponent(loc, self.wsudAttr)

                #Transfer the key system specs
                if outblock_strat.getType() in ["BF", "IS", "WSUR"]:
                    loc.addAttribute("WDepth", eval("self."+str(outblock_strat.getType())+"spec_EDD"))
                if outblock_strat.getType() in ["PB"]:
                    loc.addAttribute("WDepth", float(eval("self."+str(outblock_strat.getType())+"spec_MD")))
                if outblock_strat.getType() in ["BF", "IS"]:
                    loc.addAttribute("FDepth", eval("self."+str(outblock_strat.getType())+"spec_FD"))
        return True
    
    def transferExistingSystemsToOutput(self, city, stratID):
        """Writes all existing systems to the new output view under a new strategyID as they
        will accompany all newly planned systems under a future alternative"""
        existSys = city.getUUIDsOfComponentsInView(self.sysAttr)
        for uuid in existSys:
            curSys = city.getComponent(uuid)    #curSys holds the current Component() object
            if curSys == None:
                continue        #RemoveComponent only removes the components, not the UUID, must therefore catch this
            loc = Component()   #Create a new placeholder for a component object, save it to self.wsudAttr View
            loc.addAttribute("StrategyID", stratID)
            loc.addAttribute("posX", curSys.getAttribute("posX").getDouble())
            loc.addAttribute("posY", curSys.getAttribute("posY").getDouble())
            loc.addAttribute("BasinID", int(curSys.getAttribute("BasinID").getDouble()))
            loc.addAttribute("Location", int(curSys.getAttribute("Location").getDouble()))
            loc.addAttribute("Scale", curSys.getAttribute("Scale").getString())
            loc.addAttribute("Type", curSys.getAttribute("Type").getString())
            loc.addAttribute("Qty", curSys.getAttribute("Qty").getDouble())      #currently none available
            loc.addAttribute("GoalQty", curSys.getAttribute("GoalQty").getDouble())  #lot scale mainly - number of lots to build
            loc.addAttribute("SysArea", curSys.getAttribute("SysArea").getDouble())
            loc.addAttribute("Status", int(curSys.getAttribute("Status").getDouble()))
            loc.addAttribute("Year", int(curSys.getAttribute("Year").getDouble()))
            loc.addAttribute("EAFact", curSys.getAttribute("EAFact").getDouble())
            loc.addAttribute("ImpT", curSys.getAttribute("ImpT").getDouble())
            loc.addAttribute("CurImpT", curSys.getAttribute("CurImpT").getDouble())  #New systems don't treat anything yet before implemented
            loc.addAttribute("Upgrades", int(curSys.getAttribute("Upgrades").getDouble()))
            loc.addAttribute("WDepth", curSys.getAttribute("WDepth").getDouble())
            loc.addAttribute("FDepth", curSys.getAttribute("FDepth").getDouble())
            city.addComponent(loc, self.wsudAttr)
        return True
    
    def determineBlockWaterRating(self):
        """Determine the efficiency of the indoor appliances based on user 
        inputs. Several options available including different sampling distirbutions."""
        if self.WEFstatus == 0:
            return 0
        elif self.WEF_method == "C":
            return self.WEF_c_rating
        elif self.WEF_method == "D":
            maxrating = self.WEF_d_rating
            minrating = 1   #initialize then check if zero is to be included and revise
            if self.WEF_includezero:
                minrating = 0
            if self.WEF_distribution == "UF":
                return int(random.randint(minrating, maxrating))
            #Not uniform distribution --> Use Normal Variations instead
            mu = (minrating + maxrating)/2         #mean is in the 'centre of the distribution'
            sigma = (maxrating - minrating)*0.63/2      #63% of data lies within +/- 1 stdev of the mean
            samplerating = -1   #initialize
            while samplerating < minrating or samplerating > maxrating:
                if self.WEF_distribution == "NM":
                    samplerating = int(random.normalvariate(mu, sigma))
                elif self.WEF_distribution == "LL":
                    samplerating = int(random.normalvariate(log(mu), log(sigma)))
                elif self.WEF_distribution == "LH":
                    samplerating = int(random.normalvariate(log(mu), log(sigma)))
                    samplerating = (maxrating + minrating) - samplerating #Reverse the rating
            return samplerating
        print "Error with blockwater rating function"
        return 0

    def retrieveFlowRates(self, rating):
        """Retrieves the flow rates for the given rating input from the collection of flow 
        rates depending on the type of rating system used."""
        #AS6400 Rating - Units in [L/min] for end uses with duration and L for the rest
        #       - Toilet : Average flush volume used (do not differentiate between full/half)
        #       - Laundry: 5kg Load capacity assumes as the mid-range
        frdAS6400 = {"Kitchen": [16.0,12.0,9.0,7.5,6,4.5,4.5],
                    "Toilet": [11,5.5,4.5,4.0,3.5,3.0,2.5],
                    "Shower": [16.0,12.0,9.0,7.5,6.0,4.5,4.5],
                    "Laundry": [200,150,105,73.5,51.5,36.0,25.2] }
        
        #Other ratings dictionaries
        if self.WEF_rating_system == "AS":
            return [frdAS6400["Kitchen"][int(rating)], frdAS6400["Toilet"][int(rating)],
                    frdAS6400["Shower"][int(rating)], frdAS6400["Laundry"][int(rating)]]
        elif self.WEF_rating_system == "Others":
            return [frdAS6400["Kitchen"][int(rating)], frdAS6400["Toilet"][int(rating)],
                    frdAS6400["Shower"][int(rating)], frdAS6400["Laundry"][int(rating)]]
        return True

    def getResIndoorDemands(self, occup, flowrates, flowvary):
        """Calculates and varies indoor demands based on input occupancy and flowrates.
        Returns four values of demands for kitchen, shower, toilet and laundry end uses"""
        kitchendem = self.freq_kitchen * self.dur_kitchen * occup * flowrates[0]
        showerdem = self.freq_shower * self.dur_shower * occup * flowrates[1]
        toiletdem = self.freq_toilet * occup * flowrates[2]
        laundrydem = self.freq_laundry * flowrates[3]    #for total household
       
        #Vary demands
        kitchendemF = -1
        while kitchendemF <= 0:
            kitchendemF = kitchendem + random.uniform(kitchendem*flowvary[0]*(-1),
                                                 kitchendem*flowvary[0])
        showerdemF = -1
        while showerdemF <= 0:
            showerdemF = showerdem + random.uniform(showerdem*flowvary[1]*(-1),
                                               showerdem*flowvary[1])
        toiletdemF = -1
        while toiletdemF <= 0:
            toiletdemF = toiletdem + random.uniform(toiletdem*flowvary[2]*(-1),
                                               toiletdem*flowvary[2])
        laundrydemF = -1
        while laundrydemF <= 0:
            laundrydemF = laundrydem + random.uniform(laundrydem*flowvary[3]*(-1),
                                                 laundrydem*flowvary[3])
        return kitchendemF, showerdemF, toiletdemF, laundrydemF
    
    def getNonResIndoorDemand(self, unitvariable, demand, vary):
        """Calculates the total indoor demand based on a single value of [L/sqm/day] and
        adds variation to this value if specified
            - unitvariable = total floor space of the facility [sqm] or total employed at facility [cap]
            - demand = total indoor demand rate [L/sqm/day]
            - vary = proportionate variation +/- value * demand
        """
        demand = unitvariable * demand  #either L/cap/day x capita or L/sqm/day x sqm
        demandF = -1
        while demandF < 0:
            demandF = demand + random.uniform(demand*vary*(-1), demand*vary)
        return demandF

    def calculateBlockWaterDemand(self, currentAttList):
        """Calculates the sub-components and total water demand for the current
        Block and writes the information to the attributes list based on current
        settings for usage patterns, water efficiency, etc. Returns a dictionary with
        all the water demand information for the Block"""
        
        block_TInWD = 0             #Block total indoor water demand
        block_TOutWD = 0            #Block total outdoor water demand
        block_TInPrivWD = 0         #Block total indoor private water demand
        block_TOutPrivWD = 0        #Block Total outdoor private water demand
        block_TOutPubWD = 0         #Block total outdoor public water demand
        block_TotalWD = 0           #Block total water demand
        totalBlockNonResWD = 0      #Block total nonresidential demand
        waterDemandDict = {}
        
        #Determine Efficiency
        blockrating = self.determineBlockWaterRating()
        waterDemandDict["Efficiency"] = blockrating
        flowratesEff = self.retrieveFlowRates(blockrating)  #for areas with water efficiency
        flowratesZero = self.retrieveFlowRates(0)        #for areas without water efficiency
        flowratesVary = [self.demandvary_kitchen/100, self.demandvary_shower/100, self.demandvary_toilet/100, self.demandvary_laundry/100]

        #Residential Water Demand
        if int(currentAttList.getAttribute("HasHouses").getDouble()):
            #Indoor demands
            if self.WEF_loc_house:
                resflows = flowratesEff
            else:
                resflows = flowratesZero
                
            occup = currentAttList.getAttribute("HouseOccup").getDouble()
            kitchendem, showerdem, toiletdem, laundrydem = self.getResIndoorDemands(occup, resflows, flowratesVary)
            totalHouseIndoor = (kitchendem + showerdem + toiletdem + laundrydem)/1000 #[kL/hh/day]
            totalIndoorAnn = totalHouseIndoor*365*currentAttList.getAttribute("ResHouses").getDouble()
            waterDemandDict["RESkitchen"] = round(kitchendem,2)
            waterDemandDict["RESshower"] = round(showerdem,2)
            waterDemandDict["REStoilet"] = round(toiletdem,2)
            waterDemandDict["RESlaundry"] = round(laundrydem,2)
            
            #Irrigation demand
            gardenSpace = currentAttList.getAttribute("ResGarden").getDouble()
            irrigationDem = (self.priv_irr_vol * gardenSpace/10000) * 1000  #[kL/year]
            waterDemandDict["RESirrigation"] = round(irrigationDem,2)
            totalHouseOutdoor = irrigationDem/365   #[kL/day]
            totalOutdoorAnn = irrigationDem*currentAttList.getAttribute("ResAllots").getDouble()
            
            waterDemandDict["REStotalIN"] = round(totalIndoorAnn,2)
            waterDemandDict["REStotalOUT"] = round(totalOutdoorAnn,2)
            totalRES = totalIndoorAnn + totalOutdoorAnn     #[kL/yr]
            block_TInPrivWD += totalIndoorAnn       #[kL/yr]
            block_TOutPrivWD += totalOutdoorAnn     #[kL/yr]
            block_TInWD += totalIndoorAnn
            block_TOutWD += totalOutdoorAnn
            block_TotalWD += totalRES
        else:
            waterDemandDict["RESkitchen"] = 0
            waterDemandDict["RESshower"] = 0
            waterDemandDict["REStoilet"] = 0
            waterDemandDict["RESlaundry"] = 0
            waterDemandDict["RESirrigation"] = 0
            waterDemandDict["REStotalIN"] = 0
            waterDemandDict["REStotalOUT"] = 0
            
        #HDR Water Demand
        if int(currentAttList.getAttribute("HasFlats").getDouble()):
            #Indoor Demands
            if self.WEF_loc_apart:
                resflows = flowratesEff
            else:
                resflows = flowratesZero
            
            occup = currentAttList.getAttribute("HDROccup").getDouble()
            kitchendem, showerdem, toiletdem, laundrydem = self.getResIndoorDemands(occup, resflows, flowratesVary)
            totalFlatIndoor = (kitchendem + showerdem + toiletdem + laundrydem)/1000        #[kL/day]
            totalIndoorAnn = totalFlatIndoor*365*currentAttList.getAttribute("HDRFlats").getDouble()
            waterDemandDict["HDRkitchen"] = round(kitchendem,2)
            waterDemandDict["HDRshower"] = round(showerdem,2)
            waterDemandDict["HDRtoilet"] = round(toiletdem,2)
            waterDemandDict["HDRlaundry"] = round(laundrydem,2)
            
            #Irrigation demand
            gardenSpace = currentAttList.getAttribute("HDRGarden").getDouble()
            irrigationDem = (gardenSpace/10000 * self.priv_irr_vol) * 1000        #[kL/year]
            waterDemandDict["HDRirrigation"] = round(irrigationDem,2)
            totalHDROutdoorDaily = irrigationDem/365
            totalOutdoorAnn = irrigationDem
            
            waterDemandDict["HDRtotalIN"] = round(totalIndoorAnn,2)
            waterDemandDict["HDRtotalOUT"] = round(totalOutdoorAnn,2)
            totalHDR = totalIndoorAnn + totalOutdoorAnn
            block_TInPrivWD += totalIndoorAnn       #[kL/yr]
            block_TOutPrivWD += totalOutdoorAnn     #[kL/yr]
            block_TInWD += totalIndoorAnn
            block_TOutWD += totalOutdoorAnn
            block_TotalWD += totalHDR
        else:
            waterDemandDict["HDRkitchen"] = 0
            waterDemandDict["HDRshower"] = 0
            waterDemandDict["HDRtoilet"] = 0
            waterDemandDict["HDRlaundry"] = 0
            waterDemandDict["HDRirrigation"] = 0
            waterDemandDict["HDRtotalIN"] = 0
            waterDemandDict["HDRtotalOUT"] = 0
        
        waterDemandDict["TotalPrivateIN"] = round(block_TInPrivWD,2)
        waterDemandDict["TotalPrivateOUT"] = round(block_TOutPrivWD, 2)

        #Non-Res Water Demand
        lipublic, hipublic, compublic, orcpublic = 0,0,0,0  #initialize public space variables
        if int(currentAttList.getAttribute("Has_LI").getDouble()):    
            if self.li_demandunits == 'sqm':
                Afloor = currentAttList.getAttribute("LIAeBldg").getDouble() * \
                    currentAttList.getAttribute("LIFloors").getDouble() * \
                        currentAttList.getAttribute("LIestates").getDouble()
                demand = self.getNonResIndoorDemand(Afloor, self.li_demand, self.li_demandvary/100)
            elif self.li_demandunits == 'cap':
                employed = currentAttList.getAttribute("LIjobs").getDouble()
                demand = self.getNonResIndoorDemand(employed, self.li_demand, self.li_demandvary/100)
            lipublic = currentAttList.getAttribute("avLt_LI").getDouble()*currentAttList.getAttribute("LIestates").getDouble()
            waterDemandDict["LIDemand"] = demand/1000
            totalBlockNonResWD += demand/1000
        else:
            waterDemandDict["LIDemand"] = 0

        if int(currentAttList.getAttribute("Has_HI").getDouble()):
            if self.hi_demandunits == 'sqm':
                Afloor = currentAttList.getAttribute("HIAeBldg").getDouble() * \
                    currentAttList.getAttribute("HIFloors").getDouble()* \
                        currentAttList.getAttribute("HIestates").getDouble()
                demand = self.getNonResIndoorDemand(Afloor, self.hi_demand, self.hi_demandvary/100)
            elif self.hi_demandunits == 'cap':
                employed = currentAttList.getAttribute("HIjobs").getDouble()
                demand = self.getNonResIndoorDemand(employed, self.hi_demand, self.hi_demandvary/100)
            hipublic = currentAttList.getAttribute("avLt_HI").getDouble()*currentAttList.getAttribute("HIestates").getDouble()
            waterDemandDict["HIDemand"] = demand/1000
            totalBlockNonResWD += demand/1000
        else:
            waterDemandDict["HIDemand"] = 0
            
        if int(currentAttList.getAttribute("Has_Com").getDouble()):
            if self.com_demandunits == 'sqm':
                Afloor = currentAttList.getAttribute("COMAeBldg").getDouble() * \
                    currentAttList.getAttribute("COMFloors").getDouble()* \
                        currentAttList.getAttribute("COMestates").getDouble()
                demand = self.getNonResIndoorDemand(Afloor, self.com_demand, self.com_demandvary/100)
            elif self.com_demandunits == 'cap':
                employed = currentAttList.getAttribute("COMjobs").getDouble()
                demand = self.getNonResIndoorDemand(employed, self.com_demand, self.com_demandvary/100)
            compublic = currentAttList.getAttribute("avLt_COM").getDouble()*currentAttList.getAttribute("COMestates").getDouble()
            waterDemandDict["COMDemand"] = demand/1000
            totalBlockNonResWD += demand/1000
        else:
            waterDemandDict["COMDemand"] = 0
            
        if int(currentAttList.getAttribute("Has_ORC").getDouble()):
            if self.com_demandunits == 'sqm':
                Afloor = currentAttList.getAttribute("ORCAeBldg").getDouble() * \
                    currentAttList.getAttribute("ORCFloors").getDouble() * \
                        currentAttList.getAttribute("ORCestates").getDouble()
                demand = self.getNonResIndoorDemand(Afloor, self.com_demand, self.com_demandvary/100)
            elif self.com_demandunits == 'cap':
                employed = currentAttList.getAttribute("ORCjobs").getDouble()
                demand = self.getNonResIndoorDemand(employed, self.com_demand, self.com_demandvary/100)
            orcpublic = currentAttList.getAttribute("avLt_ORC").getDouble()*currentAttList.getAttribute("ORCestates").getDouble()
            waterDemandDict["ORCDemand"] = demand/1000
            totalBlockNonResWD += demand/1000
        else:
            waterDemandDict["ORCDemand"] = 0
            
        waterDemandDict["TotalNonResDemand"] = totalBlockNonResWD*(52*5)        #52 weeks a yr, 5 days a week working [kL/yr]
        block_TotalWD += totalBlockNonResWD*(52*5)

        pa_nonres = (lipublic + hipublic + compublic + orcpublic)*self.irrigate_nonres     #pa = public area outdoor
        waterDemandDict["APublicNonRes"] = pa_nonres
        
        #Public Open Space
        pa_parks = currentAttList.getAttribute("AGardens").getDouble()* self.irrigate_parks
        pa_ref = currentAttList.getAttribute("REF_av").getDouble()*self.irrigate_refs
        waterDemandDict["APublicPG"] = pa_parks
        waterDemandDict["APublicRef"] = pa_ref

        totalPublicSpace = pa_nonres + pa_parks + pa_ref
        waterDemandDict["APublicIrrigate"] = totalPublicSpace
        if totalPublicSpace <= 0:
            pass    #No irrigation demand
        else:
            block_TOutPubWD += totalPublicSpace/10000 * self.public_irr_vol * 1000  #[kL/yr]
            block_TOutWD += block_TOutPubWD
            block_TotalWD += block_TOutPubWD
        
        waterDemandDict["TotalOutdoorPublicWD"] = block_TOutPubWD
        waterDemandDict["TotalOutdoorWD"] = block_TOutWD
        waterDemandDict["TotalBlockWD"] = block_TotalWD
        return waterDemandDict

    def determineStorageVolForLot(self, currentAttList, rain, evapscale, wqtype, lottype):
        """Uses information of the Block's lot-scale to determine what the required
        storage size of a water recycling system is to meet the required end uses
        and achieve the user-defined potable water reduction
            - currentAttList:  current Attribute list of the block in question
            - rain: rainfall data for determining inflows if planning SW harvesting
            - evapscale: scaling factors for outdoor irrigation demand scaling
            - wqtype: the water quality being harvested (determines the type of end
                                                        uses acceptable)
        
        Function returns a storage volume based on the module's predefined variables
        of potable water supply reduction, reliability, etc."""
        
        if int(currentAttList.getAttribute("HasRes").getDouble()) == 0:
            return np.inf       #Return infinity if there is no res land use
            #First exit
        if lottype == "RES" and int(currentAttList.getAttribute("HasHouses").getDouble()) == 0:
            return np.inf
        if lottype == "HDR" and int(currentAttList.getAttribute("HasFlats").getDouble()) == 0:
            return np.inf
        
        #WORKING IN [kL/yr] for single values and [kL/day] for timeseries
        
        #Use the FFP matrix to determine total demands and suitable end uses
        wqlevel = self.ffplevels[wqtype]    #get the level and determine the suitable end uses
        if lottype == "RES":    #Demands based on a single house
            lotdemands = {"Kitchen":currentAttList.getAttribute("wd_RES_K").getDouble()*365/1000,
                      "Shower":currentAttList.getAttribute("wd_RES_S").getDouble()*365/1000,
                      "Toilet":currentAttList.getAttribute("wd_RES_T").getDouble()*365/1000,
                      "Laundry":currentAttList.getAttribute("wd_RES_L").getDouble()*365/1000,
                      "Irrigation":currentAttList.getAttribute("wd_RES_I").getDouble() }
        elif lottype == "HDR": #Demands based on entire apartment sharing a single roof
            lotdemands = {"Kitchen":currentAttList.getAttribute("wd_HDR_K").getDouble()*365/1000,
                      "Shower":currentAttList.getAttribute("wd_HDR_S").getDouble()*365/1000,
                      "Toilet":currentAttList.getAttribute("wd_HDR_T").getDouble()*365/1000,
                      "Laundry":currentAttList.getAttribute("wd_HDR_L").getDouble()*365/1000,
                      "Irrigation":currentAttList.getAttribute("wd_HDR_I").getDouble() }
        totalhhdemand = sum(lotdemands.values())    #Total House demand, [kL/yr]
        
        enduses = {}        #Tracks all the different types of end uses
        objenduses = []
        if self.ffplevels[self.ffp_kitchen] >= wqlevel:
            enduses["Kitchen"] = lotdemands["Kitchen"]
            objenduses.append('K')
        if self.ffplevels[self.ffp_shower] >= wqlevel:
            enduses["Shower"] = lotdemands["Shower"]
            objenduses.append('S')
        if self.ffplevels[self.ffp_toilet] >= wqlevel:
            enduses["Toilet"] = lotdemands["Toilet"]
            objenduses.append('T')
        if self.ffplevels[self.ffp_laundry] >= wqlevel:
            enduses["Laundry"] = lotdemands["Laundry"]
            objenduses.append('L')
        if self.ffplevels[self.ffp_garden] >= wqlevel:
            enduses["Irrigation"] = lotdemands["Irrigation"]
            objenduses.append('I')
        totalsubdemand = sum(enduses.values())
        
        if totalsubdemand == 0:
            return np.inf
        
        #Determine what the maximum substitution can be, supply the smaller of total substitutable demand
        #or the desired target.
        recdemand = min(totalsubdemand, self.service_rec/100*totalhhdemand)     #the lower of the two
        #print "Recycled Demand Lot: ", recdemand
        #Determine inflow/demand time series
        if lottype == "RES":
            Aroof = currentAttList.getAttribute("ResRoof").getDouble()
        elif lottype == "HDR":
            Aroof = currentAttList.getAttribute("HDRRoofA").getDouble()
        
        #Determine demand time series
        if "Irrigation" in enduses.keys():
            #Scale to evap pattern
            demandseries = ubseries.createScaledDataSeries(recdemand, evapscale, False)
        else:
            #Scale to constant pattern
            demandseries = ubseries.createConstantDataSeries(recdemand/365, len(rain))
        
        #Generate the inflow series based on the kind of water being harvested
        if wqtype in ["RW", "SW"]:      #Use rainwater to generate inflow
            inflow = ubseries.convertDataToInflowSeries(rain, Aroof, False)     #Convert rainfall to inflow
            maxinflow = sum(rain)/1000 * Aroof / self.rain_length         #average annual inflow using whole roof
            tank_templates = self.lot_raintanksizes     #Use the possible raintank sizes
        elif wqtype in ["GW"]:  #Use greywater to generate inflow
            inflow = 0
            maxinflow = 0
            tank_templates = [] #use the possible greywater tank sizes
        
        if maxinflow < recdemand:       #If Vsupp < Vdem
            return np.inf       #cannot size a store that is supplying more than it is getting
        
        #Depending on Method, size the store
        if self.sb_method == "Sim":
            mintank_found = 0
            storageVol = np.inf      #Assume infinite storage for now
            for i in tank_templates:        #Run through loop
                if mintank_found == 1:
                    continue
                rel = dsim.calculateTankReliability(inflow, demandseries, i)
                if rel > self.targets_reliability:
                    mintank_found = 1
                    storageVol = i
        
        elif self.sb_method == "Eqn":
            vdemvsupp = recdemand / maxinflow
            storagePerc = deq.loglogSWHEquation(self.regioncity, self.targets_reliability, inflow, demandseries)
            reqVol = storagePerc/100*maxinflow  #storagePerc is the percentage of the avg. annual inflow
            
            #Determine where this volume ranks in reliability
            storageVol = np.inf     #Assume infinite storage for now, readjust later
            tank_templates.reverse()        #Reverse the series for the loop
            for i in range(len(tank_templates)):
                if reqVol < tank_templates[i]: #Begins with largest tank
                    storageVol = tank_templates[i] #Begins with largest tank    #if the volume is below the current tank size, use the 'next largest'
            tank_templates.reverse()        #Reverse the series back in case it needs to be used again
        storeObj = tt.RecycledStorage(wqtype, storageVol,  objenduses, Aroof, self.targets_reliability, recdemand, "L")
        #End of function: returns storageVol as either [1kL, 2kL, 5kL, 10kL, 15kL, 20kL] or np.inf
        return storeObj
    
    def determineEndUses(self, wqtype):
        """Returns an array of the allowable water end uses for the given water
        quality type 'wqtype'. Array is dependent on user inputs and is subsequently
        used to determine water demands substitutable by that water source. This 
        function is only for neighbourhood and sub-basin scales"""
        wqlevel = self.ffplevels[wqtype]
        enduses = []
        if self.ffplevels[self.ffp_kitchen] >= wqlevel: enduses.append("K")
        if self.ffplevels[self.ffp_shower] >= wqlevel: enduses.append("S")
        if self.ffplevels[self.ffp_toilet] >= wqlevel: enduses.append("T")
        if self.ffplevels[self.ffp_laundry] >= wqlevel: enduses.append("L")
        if self.ffplevels[self.ffp_garden] >= wqlevel: enduses.append("I")
        if self.ffplevels[self.public_irr_wq] >= wqlevel: enduses.append("PI")
        return enduses
    
    def determineStorageVolNeigh(self, currentAttList, rain, evapscale, wqtype):
        """Uses information of the Block to determine the required storage size of
        a water recycling system to meet required end uses and achieve the user-defined
        potable water reduction and reliability targets
            - currentAttList:  current Attribute list of the block in question
            - rain: rainfall data for determining inflows if planning SW harvesting
            - evapscale: scaling factors for outdoor irrigation demand scaling
            - wqtype: water quality being harvested (determines the type of end
                                                        uses acceptable)
        
        Function returns an array of storage volumes in dictionary format identified
        by the planning increment."""
        
        #WORKING IN [kL/yr] for single values and [kL/day] for time series
        if currentAttList.getAttribute("Blk_EIA").getDouble() == 0:
            return np.inf
        
        enduses = self.determineEndUses(wqtype)
        houses = currentAttList.getAttribute("ResHouses").getDouble()
        
        #Total water demand (excluding non-residential areas)
        storageVol = {}
        
        #Get the entire Block's Water Demand
        blk_demands = self.getTotalWaterDemandEndUse(currentAttList, ["K","S","T", "L", "I", "PI"])
        #print "Block demands: ", blk_demands
        
        #Get the entire Block's substitutable water demand
        totalsubdemand = self.getTotalWaterDemandEndUse(currentAttList, enduses)
        #print "Total Demand Substitutable: ", totalsubdemand
        
        if totalsubdemand == 0: #If nothing can be substituted, return infinity
            return np.inf    
        
        #Loop across increments: Storage that harvests all area/WW to supply [0.25, 0.5, 0.75, 1.0] of demand
        for i in range(len(self.neigh_incr)):   #Loop across harvestable area
            if self.neigh_incr[i] == 0:
                continue
            harvestincr = self.neigh_incr[i]
            storageVol[harvestincr] = {} #Initialize container dictionary
            
            for j in range(len(self.neigh_incr)):   #Loop across substitutable demands
                if self.neigh_incr[j] == 0:
                    continue
                
                supplyincr = self.neigh_incr[j]
                recdemand = supplyincr*blk_demands  #x% of total block demand
                if recdemand > totalsubdemand:      #if that demand is greater than what can be substituted, then
                    storageVol[harvestincr][supplyincr] = np.inf         
                    #make it impossible to size a system for that combo
                    continue
                #print "Recycled Demand: ", recdemand
                
                if recdemand == 0:
                    #If there is no demand to substitute, then storageVol is np.inf
                    storageVol[harvestincr][supplyincr] = np.inf
                    continue
                    
                #Harvestable area
                Aharvest = currentAttList.getAttribute("Blk_EIA").getDouble()*harvestincr   #Start with this
                #print "Harvestable Area :", Aharvest
                
                if "I" in enduses:      #If irrigation is part of end uses
                    #Scale to evap pattern
                    demandseries = ubseries.createScaledDataSeries(recdemand, evapscale, False)
                else:
                    #Scale to constant pattern
                    demandseries = ubseries.createScaledDataSeries(recdemand/365, len(rain))
                
                #Generate the inflow series based on kind of water being harvested
                if wqtype in ["RW", "SW"]:
                    inflow = ubseries.convertDataToInflowSeries(rain, Aharvest, False)
                    maxinflow = sum(rain)/1000*Aharvest / self.rain_length
                    #print "Average annual inflow: ", maxinflow
                elif wqtype in ["GW"]:
                    inflow = 0
                    maxinflow = 0
                
                if maxinflow < recdemand:
                    storageVol[harvestincr][supplyincr] = np.inf 
                    #Cannot size a store to supply more than it is getting
                    continue
                
                #Size the store depending on method
                if self.sb_method == "Sim":
                    reqVol = dsim.estimateStoreVolume(inflow, demandseries, self.targets_reliability, self.relTolerance, self.maxSBiterations)
                    #print "reqVol: ", reqVol
                elif self.sb_method == "Eqn":
                    vdemvsupp = recdemand / maxinflow
                    storagePerc = deq.loglogSWHEquation(self.regioncity, self.targets_reliability, inflow, demandseries)
                    reqVol = storagePerc/100*maxinflow  #storagePerc is the percentage of the avg. annual inflow
                storeObj = tt.RecycledStorage(wqtype, reqVol, enduses, Aharvest, self.targets_reliability, recdemand, "N")
                storageVol[harvestincr][supplyincr] = storeObj       #at each lot incr: [ x options ]
            #print storageVol[harvestincr]
        return storageVol

    def getTotalWaterDemandEndUse(self, currentAttList, enduse):
        """Retrieves all end uses for the current Block based on the end use matrix
        and the lot-increment. 
        """
        demand = 0
        #End use in houses and apartments - indoors + garden irrigation
        for i in enduse:    #Get Indoor demands first
            if i == "PI" or i == "I":
                continue    #Skip the public irrigation
            demand += currentAttList.getAttribute("wd_RES_"+str(i)).getDouble()*365/1000 * \
                currentAttList.getAttribute("ResHouses").getDouble()
            demand += currentAttList.getAttribute("wd_HDR_"+str(i)).getDouble()*365/1000 * \
                currentAttList.getAttribute("HDRFlats").getDouble()
        #Add irrigation of public open space
        if "I" in enduse:
            demand += currentAttList.getAttribute("wd_RES_I").getDouble()
            demand += currentAttList.getAttribute("wd_HDR_I").getDouble() #Add all HDR irrigation
        if "PI" in enduse:
            demand += currentAttList.getAttribute("wd_PubOUT").getDouble()
        return demand
    
    def determineStorageVolSubbasin(self, currentAttList, city, rain, evapscale, wqtype):
        """Uses information of the current Block and the broader sub-basin to determine
        the required storage size of a water recycling system to meet required end uses
        and achieve user-defined potable water reduction and reliability targets. It does
        this for a number of combinations, but finds the worst case first e.g.
        
            4 increments: [0.25, 0.5, 0.75, 1.00] of the catchment harvested to treat
                          [0.25, 0.5, 0.75, 1.00] portion of population and public space
                          worst case scenario: 0.25 harvest to supply 1.00 of area
        
        Input parameters:
            - currentAttList: current Attribute list of the block in question
            - city: the city View so that the model can get all necessary basin blocks
            - rain: rainfall data for determining inflows if planning SW harvesting
            - evapscale: scaling factors for outdoor irrigation demand scaling
            - wqtype: water quality being harvested (determines the type of end uses
                                                     accepable)
        
        Model also considers the self.hs_strategy at this scale, i.e. harvest upstream
        to supply downstream? harvest upstream to supply upstream? harvest upstream to
        supply basin?
        
        Function returns an array of storage volumes in dictionary format identified by
        planning increment."""
        
        #WORKING IN [kL/yr] for single values and [kL/day] for time series
        #(1) Get all Blocks based on the strategy
        harvestblockIDs = self.retrieveStreamBlockIDs(currentAttList, "upstream")
        harvestblockIDs.append(currentAttList.getAttribute("BlockID").getDouble())
        if self.hs_strategy == "ud":
            supplytoblockIDs = self.retrieveStreamBlockIDs(currentAttList, "downstream")
            supplytoblockIDs.append(currentAttList.getAttribute("BlockID").getDouble())
        elif self.hs_strategy == "uu":
            supplytoblockIDs = harvestblockIDs        #Try ref copy first
    #        supplytoblockIDs = []
    #        for i in range(len(harvestblockIDs)):
    #            supplytoblockIDs.append(harvestblockIDs[i])   #make a direct copy
        elif self.hs_strategy == "ua":
            supplytoblockIDs = self.retrieveStreamBlockIDs(currentAttList, "downstream")
            for i in range(len(harvestblockIDs)):   #To get all basin IDs, simply concatenate the strings
                supplytoblockIDs.append(harvestblockIDs[i])   
        
        #print "HarvestBlocKIDs: ", harvestblockIDs
        #print "SupplyBlockIDs:" , supplytoblockIDs
        
        #(2) Prepare end uses and obtain full demands
        enduses = self.determineEndUses(wqtype)
        bas_totdemand = 0
        bas_subdemand = 0
        for i in supplytoblockIDs:
            block_attr = self.getBlockUUID(i, city)
            bas_totdemand += self.getTotalWaterDemandEndUse(block_attr, ["K","S","T", "L", "I", "PI"])
            bas_subdemand += self.getTotalWaterDemandEndUse(block_attr, enduses)
        
        #print "Total basin demands/substitutable ", bas_totdemand, bas_subdemand
        
        #(3) Grab total harvestable area
        AharvestTot = self.retrieveAttributeFromIDs(city, harvestblockIDs, "Blk_EIA", "sum")
        #print "AharvestTotal: ", AharvestTot
        if AharvestTot == 0:    #no area to harvest
            return np.inf
            #Future - add something to deal with retrofit
        
        storageVol = {}
        #(4) Generate Demand Time Series
        for i in range(len(self.subbas_incr)):          #HARVEST x% LOOP
            if self.subbas_incr[i] == 0:
                continue        #Skip 0 increment

            harvestincr = self.subbas_incr[i]
            storageVol[harvestincr] = {}    #initialize container
            for j in range(len(self.subbas_incr)):      #SUPPLY y% LOOP
                if self.subbas_incr[j] == 0:
                    continue    #Skip 0 increment
                
                supplyincr = self.subbas_incr[j]
                recdemand = bas_totdemand * supplyincr
                if recdemand > bas_subdemand:      #if that demand is greater than what can be substituted, then
                    storageVol[harvestincr][supplyincr] = np.inf         
                    #make it impossible to size a system for that combo
                    continue
                
                Aharvest = AharvestTot * harvestincr
                #print "Required demand: ", recdemand
                if "I" in enduses:
                    demandseries = ubseries.createScaledDataSeries(recdemand, evapscale, False)
                else:
                    demandseries = ubseries.createScaledDataSeries(recdemand/365, len(rain))
                
                if wqtype in ["RW", "SW"]:
                    inflow = ubseries.convertDataToInflowSeries(rain, Aharvest, False)
                    maxinflow = sum(rain)/1000*Aharvest / self.rain_length
                    #print "Average annual inflow: ", maxinflow
                elif wqtype in ["GW"]:
                    inflow = 0
                    maxinflow = 0
                
                if maxinflow < recdemand:
                    #Cannot design a storage to supply more than it is getting
                    storageVol[harvestincr][supplyincr] = np.inf
                    continue
                
                #(5) Size the store for the current combo
                if self.sb_method == "Sim":
                    reqVol = dsim.estimateStoreVolume(inflow, demandseries, self.targets_reliability, self.relTolerance, self.maxSBiterations)
                    #print "reqVol: ", reqVol
                elif self.sb_method == "Eqn":
                    vdemvsupp = recdemand / maxinflow
                    storagePerc = deq.loglogSWHEquation(self.regioncity, self.targets_reliability, inflow, demandseries)
                    reqVol = storagePerc/100*maxinflow  #storagePerc is the percentage of the avg. annual inflow
                
                storeObj = tt.RecycledStorage(wqtype, reqVol, enduses, Aharvest, self.targets_reliability, recdemand, "B")
                storageVol[harvestincr][supplyincr] = storeObj
        return storageVol
    
    ########################################################
    #DYNAMIND FUNCTIONS                                    #
    ########################################################
    def createInputDialog(self):
        form = activatetechplacementGUI(self, QApplication.activeWindow())
        form.exec_()
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
        return True
    
    def debugPlanning(self, basin_strategies_matrix):
        f = open("D:/Debug.csv", 'w')
        for i in range(len(basin_strategies_matrix)):
            cbs = basin_strategies_matrix[i]
            f.write(str(cbs[0])+","+str(cbs[1])+","+str(cbs[2])+","+str(cbs[3])+"\n")
        f.close()
        return True
            