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
### --- Import & Prep Modules of Systems and Blocks
from getsystems import *
# from getpreviousblocks import *


### --- Spatial Representation Modules
from delinblocks import *				#creates grid of blocks, finds flow paths, patches and block neighbours (GUI)
    #+delinblocksgui.py and delinblocksguic.py
    #+ubconvertcoord.py, ubpatchdelin.py, ubvectormapload.py
from urbplanbb import *			        #organises the data and inputs (GUI)
    #+urbplanbbgui.py and urbplanbbguic.py

	
### --- Modules for technology assessment, opportunities, design and placement
from techplacement import *				#organises the data and inputs (GUI)
    #+techplacementgui.py and techplacementguic.py
    #+tech_assess.py, tech_templates.py, tech_design.py, tech_designbydcv.py
# from techimplement import *             #implements technology configurations into existing urban environments depending on chosen design
from WriteMUSICSim import * 


### --- Additional Modules
from ExportToGISShapeFile import *		#Shapefile Exporter that exports blocks in UTM projection