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
        self.ration_runoff = False                #Design for flood mitigation?
        self.ration_pollute = True               #Design for pollution management?
        self.ration_harvest = False              #Design for harvesting & reuse? Adds storage-sizing to certain systems
        self.runoff_pri = 0                      #Priority of flood mitigation?
        self.pollute_pri = 1                     #Priority of pollution management?
        self.harvest_pri = 0                     #Priority for harvesting & reuse
	
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
        self.service_swmWQ = 80                 #required service level for stormwater management
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
        self.createParameter("BFrecycle", BOOL, "")
        self.BFflow = True
	self.BFpollute = True
        self.BFrecycle = True
	
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
        self.createParameter("BFexfil", DOUBLE,"")
        self.BFspec_EDD = 0.3
        self.BFspec_FD = 0.6
        self.BFminsize = 5              #minimum surface area of the system in sqm
        self.BFmaxsize = 999999         #maximum surface area of system in sqm
	self.BFavglife = 20             #average life span of a biofilter
        self.BFexfil = 0
        
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
        self.createParameter("ISexfil", DOUBLE, "")
        self.ISspec_EDD = 0.2
        self.ISspec_FD = 0.8
        self.ISminsize = 5
        self.ISmaxsize = 99999          #maximum surface area of system in sqm
	self.ISavglife = 20             #average life span of an infiltration system
        self.ISexfil = 3.6
        
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
        self.createParameter("PBexfil", DOUBLE, "")
        self.PBspec_MD = "1.25" 	#need a string for the combo box
        self.PBminsize = 100
        self.PBmaxsize = 9999999           #maximum surface area of system in sqm
	self.PBavglife = 20             #average life span of a pond/basin
        self.PBexfil = 0.36

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
        self.createParameter("WSURexfil", DOUBLE, "") 
        self.WSURspec_EDD = 0.75
        self.WSURminsize = 200
        self.WSURmaxsize = 9999999           #maximum surface area of system in sqm
	self.WSURavglife = 20             #average life span of a wetland
        self.WSURexfil = 0.36

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
        self.createParameter("SWexfil", DOUBLE, "")
        self.SWspec = 0
        self.SWminsize = 20
        self.SWmaxsize = 9999           #maximum surface area of system in sqm
	self.SWavglife = 20             #average life span of a swale
        self.SWexfil = 3.6              
        
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
        self.lot_raintanksizes = [1,2,3,4,5,7.5,10,15,20]       #[kL]
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
        self.sysAttr.getAttribute("Exfil")
        
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
        self.wsudAttr.addAttribute("Exfil")
	
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
        
