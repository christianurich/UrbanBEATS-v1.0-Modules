# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 1.0
@section LICENSE

This file is part of UrbanBEATS and DynaMind
Copyright (C) 2011, 2012  Peter M Bach

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
### --- Modules for importing existing shapefile data of systems and blocks and preparing these for later 
###     processes.
# from getsystems import *
# from getpreviousblocks import *



### --- Modules for delineating data into grid of blocks and associating these with
###     properties e.g. basins, patches, flow paths
from delinblocks import *				#creates grid of blocks, finds flow paths, patches and block neighbours (GUI)
# from delinbasins import *				#identifies all upstream blocks for each block in the grid

### GUI Files that go with these modules include:
###		- delinblocks.py - spatial details for block delineation, etc.




### --- Modules for planning urban form and reconstructing cityscape based on planning
###     rules for residential, non-residential, facilities, open spaces and roads
# from urbplanbb import *					#organises the data and inputs (GUI)
# from ubp_residential import *			#plans residential districts
# from ubp_nonres import *				#plans non-res i.e. commercial, industrial districts
# from ubp_facilities import *			#identifies municipal and transport FACILITIES
# from ubp_spaces import *				#plans out open spaces, reserves, etc.
# from urbplansummary import *			#summarizes four output grids for each land use into one

### GUI Files that go with these modules include:
###		- urbplanbbgui.py - urban planning parameters interface




### --- Modules for calculating relevant urban water parameters for planning of water infrastructure
###     water demands, climate data
#from urbwatersettings import *			#contains all the relevant inputs for the integrated water system

### GUI Files that go with these modules include:
###		- urbwatersettingsgui.py - parameters for urban water infrastructure relating to hydrology, pollution, supply, waste, economics, climate, etc.




### --- Modules for technology assessment, opportunities, design and placement
# from techplacement import *				#organises the data and inputs (GUI)
# from techopp_lot import *				#finds opportunities for lot-scale techs in each block
# from techopp_street import *			#finds opportunities for street techs in each block
# from techopp_neigh import *				#finds opportunities for neighbourhood techs in each block
# from techopp_precinct import *			#finds opportunities for precinct tech in groups of blocks
# from techstrategy_eval import *		#collates the three scales into strategies and evaluates these

# from techimplement import *             #implements technology configurations into existing urban environments depending on chosen design
# from techretrofit import * 
# from writeresults2music import * 
# from writeresults2musicSecondary import *
### GUI Files that go with these modules include:
###		- techplacementgui.py - customize technologies
###             - techimplementgui.py - set rules for implementation



### --- Modules for performance assessment of urban water infrastructure, interfaces with
###     commercial packages and preparatory work for simulation
#from performance_config import *		#allows configuration of what performance aspects the model should assess
#from performance_assessment import *	#sets up CityDrain3 simulation file, calls program and runs simulation

### GUI Files that go with these modules include:
###		- performance_config.py - set what software packages to use and what performance to simulate




### --- Modules for reporting results from simulation
#from ubeatsprojectinfo import *			#contains general info about the project for starting out the report
#from ubeatsreport import *				#contains the configuration for output report




### --- Additional Modules
#from checkattributes import *			#Dummy file that allows checking if an attribute in a vector data can traverse modules
#from ExportGISShapeFile import *		#Shapefile Exporter that exports blocks in UTM projection
#from VecDataAttributePrinter import *	#Printer of all vector data attributes
