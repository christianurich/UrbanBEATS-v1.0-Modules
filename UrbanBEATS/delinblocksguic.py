# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 1.0
@section LICENSE

This file is part of UrbanBEATS (www.urbanbeatsmodel.com), DynaMind
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
from PyQt4 import QtCore, QtGui
from pydynamind import *
from delinblocksgui import Ui_DelinBlocksDialog

class activatedelinblocksGUI(QtGui.QDialog):
    def __init__(self, m, parent=None):
        self.module = Module
        self.module = m
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_DelinBlocksDialog()
        self.ui.setupUi(self)
        
        self.cities = ["Adelaide", "Brisbane", "Cairns", "Canberra", "Copenhagen", "Innsbruck", "Kuala Lumpur", "London", "Melbourne", "Munich", "Perth", "Singapore", "Sydney", "Vienna"]
        
        #Set all default parameters contained in the module file into the GUI's fields
        
        #----------------------------------------------------------------------#
        #-------- GENERAL SIMULATION INPUTS------------------------------------#
        #----------------------------------------------------------------------#
        self.ui.blocksize_in.setValue(int(self.module.getParameterAsString("BlockSize")))
        
        if self.module.getParameterAsString("blocksize_auto") == "1":
            self.ui.blocksize_auto.setChecked(1)
            self.ui.blocksize_in.setEnabled(0)
        else:
            self.ui.blocksize_auto.setChecked(0)
            self.ui.blocksize_in.setEnabled(1)
        
        QtCore.QObject.connect(self.ui.blocksize_auto, QtCore.SIGNAL("clicked()"), self.block_auto_size)
        
        #UrbanSim Option - Old Legacy Code, used in DAnCE4Water Integration of UrbanBEATS Code
        #if self.module.getParameterAsString("input_from_urbansim") == "1":
        #    self.ui.urbansim_in_check.setChecked(1)
        #    self.ui.soc_par1_check.setEnabled(0)
        #    self.ui.soc_par2_check.setEnabled(0)
        #    self.ui.soc_par1_box.setEnabled(0)
        #    self.ui.soc_par2_box.setEnabled(0)
        #else:
        #    self.ui.urbansim_in_check.setChecked(0)
        #    self.ui.soc_par1_check.setEnabled(1)
        #    self.ui.soc_par2_check.setEnabled(1)
        #    self.ui.soc_par1_box.setEnabled(1)
        #    self.ui.soc_par2_box.setEnabled(1)
        #QtCore.QObject.connect(self.ui.urbansim_in_check, QtCore.SIGNAL("clicked()"), self.social_parameters_urbansim)
        
        #----------------------------------------------------------------------#
        #-------- PROCESSING INPUT DATA ---------------------------------------#
        #----------------------------------------------------------------------#
        if self.module.getParameterAsString("popdatatype") == "C":
            self.ui.popdata_totradio.setChecked(True)
        elif self.module.getParameterAsString("popdatatype") == "D":
            self.ui.popdata_densradio.setChecked(True)
        
        if self.module.getParameterAsString("soildatatype") == "C":
            self.ui.soildata_classify.setChecked(True)
            self.ui.soildata_unitscombo.setEnabled(False)
        elif self.module.getParameterAsString("soildatatype") == "I":
            self.ui.soildata_infil.setChecked(True)
            self.ui.soildata_unitscombo.setEnabled(True)
        
        if self.module.getParameterAsString("soildataunits") == "hrs":
            self.ui.soildata_unitscombo.setCurrentIndex(0)
        elif self.module.getParameterAsString("soildataunits") == "sec":
            self.ui.soildata_unitscombo.setCurrentIndex(1)
        
        QtCore.QObject.connect(self.ui.soildata_classify, QtCore.SIGNAL("clicked()"), self.soildata_modify)
        QtCore.QObject.connect(self.ui.soildata_infil, QtCore.SIGNAL("clicked()"), self.soildata_modify)
        
        if self.module.getParameterAsString("elevdatadatum") == "S":
            self.ui.elev_sealevel.setChecked(True)
            self.ui.elev_referencebox.setEnabled(False)
        elif self.module.getParameterAsString("elevdatadatum") == "C":
            self.ui.elev_custom.setChecked(True)
            self.ui.elev_referencebox.setEnabled(True)
            
        QtCore.QObject.connect(self.ui.elev_sealevel, QtCore.SIGNAL("clicked()"), self.elevCustomDatum_modify)
        QtCore.QObject.connect(self.ui.elev_custom, QtCore.SIGNAL("clicked()"), self.elevCustomDatum_modify)
        
        self.ui.elev_referencebox.setText(self.module.getParameterAsString("elevdatacustomref"))
        
        self.ui.planmap_check.setChecked(int(self.module.getParameterAsString("include_plan_map")))
        self.ui.localmap_check.setChecked(int(self.module.getParameterAsString("include_local_map")))
        
        if self.module.getParameterAsString("include_employment") == "1":
            self.ui.employment_check.setChecked(True)
            self.ui.jobdata_totradio.setEnabled(True)
            self.ui.jobdata_densradio.setEnabled(True)
        else:
            self.ui.employment_check.setChecked(False)
            self.ui.jobdata_totradio.setEnabled(False)
            self.ui.jobdata_densradio.setEnabled(False)        
        
        if self.module.getParameterAsString("jobdatatype") == "C":
            self.ui.jobdata_totradio.setChecked(True)
        elif self.module.getParameterAsString("jobdatatype") == "D":
            self.ui.jobdata_densradio.setChecked(True)
        
        QtCore.QObject.connect(self.ui.employment_check, QtCore.SIGNAL("clicked()"), self.employment_modify)
        
        self.ui.rivers_check.setChecked(int(self.module.getParameterAsString("include_rivers")))
        self.ui.lakes_check.setChecked(int(self.module.getParameterAsString("include_lakes")))
        
        if self.module.getParameterAsString("include_groundwater") == "1":
            self.ui.groundwater_check.setChecked(True)
            self.ui.groundwater_datumcombo.setEnabled(True)
        else:
            self.ui.groundwater_check.setChecked(False)
            self.ui.groundwater_datumcombo.setEnabled(False)
        
        if self.module.getParameterAsString("groundwater_datum") == "Sea":
            self.ui.groundwater_datumcombo.setCurrentIndex(0)
        elif self.module.getParameterAsString("groundwater_datum") == "Surf":
            self.ui.groundwater_datumcombo.setCurrentIndex(1)
        
        QtCore.QObject.connect(self.ui.groundwater_check, QtCore.SIGNAL("clicked()"), self.groundwaterDatum_modify)
        
        self.ui.roadnet_check.setChecked(int(self.module.getParameterAsString("include_road_net")))     #Future version
        self.ui.sewermains_check.setChecked(int(self.module.getParameterAsString("include_sewer_net")))
        self.ui.supplymains_check.setChecked(int(self.module.getParameterAsString("include_supply_net")))
        
        #conditions for what user inputs from main module are
        if self.module.getParameterAsString("include_soc_par1") == "1":
            self.ui.soc_par1_check.setChecked(1)
            self.ui.soc_par1_box.setText(self.module.getParameterAsString("social_par1_name"))
            self.ui.socpar1binary_radio.setEnabled(1)
            self.ui.socpar1prop_radio.setEnabled(1)
        else:
            self.ui.soc_par1_check.setChecked(0)
            self.ui.soc_par1_box.setEnabled(0)
            self.ui.soc_par1_box.setText(self.module.getParameterAsString("social_par1_name"))
            self.ui.socpar1binary_radio.setEnabled(0)
            self.ui.socpar1prop_radio.setEnabled(0)
        
        if self.module.getParameterAsString("socpar1_type") == "B":
            self.ui.socpar1binary_radio.setChecked(True)
        elif self.module.getParameterAsString("socpar1_type") == "P":
            self.ui.socpar1prop_radio.setChecked(True)
            
        if self.module.getParameterAsString("include_soc_par2") == "1":
            self.ui.soc_par2_check.setChecked(1)
            self.ui.soc_par2_box.setText(self.module.getParameterAsString("social_par2_name"))
            self.ui.socpar2binary_radio.setEnabled(1)
            self.ui.socpar2prop_radio.setEnabled(1)
        else:
            self.ui.soc_par2_check.setChecked(0)
            self.ui.soc_par2_box.setEnabled(0)
            self.ui.soc_par2_box.setText(self.module.getParameterAsString("social_par2_name"))
            self.ui.socpar2binary_radio.setEnabled(0)
            self.ui.socpar2prop_radio.setEnabled(0)
        
        if self.module.getParameterAsString("socpar2_type") == "B":
            self.ui.socpar2binary_radio.setChecked(True)
        elif self.module.getParameterAsString("socpar2_type") == "P":
            self.ui.socpar2prop_radio.setChecked(True)
        
        self.ui.spatialpatches_check.setChecked(int(self.module.getParameterAsString("patchdelin")))
        self.ui.spatialstats_check.setChecked(int(self.module.getParameterAsString("spatialmetrics")))
        
        QtCore.QObject.connect(self.ui.soc_par1_check, QtCore.SIGNAL("clicked()"), self.social_par1_modify)
        QtCore.QObject.connect(self.ui.soc_par2_check, QtCore.SIGNAL("clicked()"), self.social_par2_modify)
        
        #----------------------------------------------------------------------#
        #-------- MAP CONNECTIVITY INPUTS -------------------------------------#
        #----------------------------------------------------------------------#
        if self.module.getParameterAsString("Neighbourhood") == "N":
            self.ui.radioVNeum.setChecked(True)
        if self.module.getParameterAsString("Neighbourhood") == "M":
            self.ui.radioMoore.setChecked(True)
            self.ui.neighb_vnfp_check.setEnabled(0)
            self.ui.neighb_vnpd_check.setEnabled(0)
        
        self.ui.neighb_vnfp_check.setChecked(int(self.module.getParameterAsString("vn4FlowPaths")))
        self.ui.neighb_vnpd_check.setChecked(int(self.module.getParameterAsString("vn4Patches")))
        
        QtCore.QObject.connect(self.ui.radioVNeum, QtCore.SIGNAL("clicked()"), self.vnOptions_modify)
        QtCore.QObject.connect(self.ui.radioMoore, QtCore.SIGNAL("clicked()"), self.vnOptions_modify)
        
        #Flowpath COMBO BOX
        if self.module.getParameterAsString("flow_method") == "DI":
            self.ui.flowpath_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("flow_method") == "D8":
            self.ui.flowpath_combo.setCurrentIndex(1)
        
        if self.module.getParameterAsString("demsmooth_choose") == "1":
            self.ui.demsmooth_check.setChecked(1)
        else:
            self.ui.demsmooth_check.setChecked(0)
            self.ui.demsmooth_spin.setEnabled(0)
            
        self.ui.demsmooth_spin.setValue(int(self.module.getParameterAsString("demsmooth_passes")))
        
        QtCore.QObject.connect(self.ui.demsmooth_check, QtCore.SIGNAL("clicked()"), self.demsmooth_modify)
        
        #----------------------------------------------------------------------#
        #-------- REGIONAL GEOGRAPHY INPUTS -----------------------------------#
        #----------------------------------------------------------------------#    
        
        if self.module.getParameterAsString("locationOption") == "S":
            self.ui.cbdknown_radio.setChecked(True)
            self.ui.cbd_combo.setEnabled(1)
            self.ui.cbdlong_box.setEnabled(0)
            self.ui.cbdlat_box.setEnabled(0)
        if self.module.getParameterAsString("locationOption") == "C":
            self.ui.cbdmanual_radio.setChecked(True)
            self.ui.cbd_combo.setEnabled(0)
            self.ui.cbdlong_box.setEnabled(1)
            self.ui.cbdlat_box.setEnabled(1)
        
        if self.module.getParameterAsString("considerCBD") == "1":
            self.ui.considergeo_check.setChecked(1)
            self.ui.cbdknown_radio.setEnabled(1)
            self.ui.cbdmanual_radio.setEnabled(1)
            self.ui.cbdmark_check.setEnabled(1)
            self.cbdupdate()
        else:
            self.ui.considergeo_check.setChecked(0)
            self.ui.cbdknown_radio.setEnabled(0)
            self.ui.cbdmanual_radio.setEnabled(0)
            self.ui.cbdmark_check.setEnabled(0)
            self.ui.cbd_combo.setEnabled(0)
            self.ui.cbdlong_box.setEnabled(0)
            self.ui.cbdlat_box.setEnabled(0)
        
        try:
            citiesindex = self.cities.index(self.module.getParameterAsString("locationCity"))
        except:
            citiesindex = 0
        self.ui.cbd_combo.setCurrentIndex(citiesindex)
        
        self.ui.cbdlong_box.setText(self.module.getParameterAsString("locationLong"))
        self.ui.cbdlat_box.setText(self.module.getParameterAsString("locationLat"))
        self.ui.cbdmark_check.setChecked(int(self.module.getParameterAsString("marklocation")))
        
        QtCore.QObject.connect(self.ui.considergeo_check, QtCore.SIGNAL("clicked()"), self.geoupdate)
        QtCore.QObject.connect(self.ui.cbdknown_radio, QtCore.SIGNAL("clicked()"), self.cbdupdate)
        QtCore.QObject.connect(self.ui.cbdmanual_radio, QtCore.SIGNAL("clicked()"), self.cbdupdate)
        
        #QTCORE CONNECTS, REAL TIME GUI CHANGE COMMANDS
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.save_values)
        
    #====================================================================================================
    #Enable-Disable functions for social parameters based on QtCore.QObject.connect() lines
    
    def block_auto_size(self):
        if self.ui.blocksize_auto.isChecked() == 1:
            self.ui.blocksize_in.setEnabled(0)
        else:
            self.ui.blocksize_in.setEnabled(1)
    
    #UrbanSim Legacy Code, only in DAnCE4Water Integration ---------------------
    #def social_parameters_urbansim(self):
    #    if self.ui.urbansim_in_check.isChecked() == 1:
    #        self.ui.soc_par1_check.setEnabled(0)
    #        self.ui.soc_par2_check.setEnabled(0)
    #        self.ui.soc_par1_box.setEnabled(0)
    #        self.ui.soc_par2_box.setEnabled(0)
    #    else:
    #        self.ui.soc_par1_check.setEnabled(1)
    #        self.ui.soc_par2_check.setEnabled(1)
    #        self.social_par1_modify()
    #        self.social_par2_modify()
    #---------------------------------------------------------------------------
    
    def soildata_modify(self):
        if self.ui.soildata_infil.isChecked() == 1:
            self.ui.soildata_unitscombo.setEnabled(True)
        else:
            self.ui.soildata_unitscombo.setEnabled(False)
    
    def elevCustomDatum_modify(self):
        if self.ui.elev_sealevel.isChecked() == 1:
            self.ui.elev_referencebox.setEnabled(False)
        elif self.ui.elev_custom.isChecked() == 1:
            self.ui.elev_referencebox.setEnabled(True)
    
    def employment_modify(self):
        if self.ui.employment_check.isChecked() == 1:
            self.ui.jobdata_totradio.setEnabled(True)
            self.ui.jobdata_densradio.setEnabled(True)
        else:
            self.ui.jobdata_totradio.setEnabled(False)
            self.ui.jobdata_densradio.setEnabled(False)
    
    def groundwaterDatum_modify(self):
        if self.ui.groundwater_check.isChecked() == 1:
            self.ui.groundwater_datumcombo.setEnabled(True)
        else:
            self.ui.groundwater_datumcombo.setEnabled(False)
    
    def social_par1_modify(self):
        if self.ui.soc_par1_check.isChecked() == 1:
            self.ui.soc_par1_box.setEnabled(1)
            self.ui.socpar1binary_radio.setEnabled(1)
            self.ui.socpar1prop_radio.setEnabled(1)
        else:
            self.ui.soc_par1_box.setEnabled(0)
            self.ui.socpar1binary_radio.setEnabled(0)
            self.ui.socpar1prop_radio.setEnabled(0)
    
    def social_par2_modify(self):
        if self.ui.soc_par2_check.isChecked() == 1:
            self.ui.soc_par2_box.setEnabled(1)
            self.ui.socpar2binary_radio.setEnabled(1)
            self.ui.socpar2prop_radio.setEnabled(1)
        else:
            self.ui.soc_par2_box.setEnabled(0)
            self.ui.socpar2binary_radio.setEnabled(0)
            self.ui.socpar2prop_radio.setEnabled(0)
            
    def demsmooth_modify(self):
        if self.ui.demsmooth_check.isChecked() == 1:
            self.ui.demsmooth_spin.setEnabled(1)
        else:
            self.ui.demsmooth_spin.setEnabled(0)
    
    def vnOptions_modify(self):
        if self.ui.radioVNeum.isChecked() == 1:
            self.ui.neighb_vnfp_check.setEnabled(1)
            self.ui.neighb_vnpd_check.setEnabled(1)
        else:
            self.ui.neighb_vnfp_check.setEnabled(0)
            self.ui.neighb_vnpd_check.setEnabled(0)
    
    def geoupdate(self):
        if self.ui.considergeo_check.isChecked() == 1:
            self.ui.cbdknown_radio.setEnabled(1)
            self.ui.cbdmanual_radio.setEnabled(1)
            self.ui.cbdmark_check.setEnabled(1)
            self.cbdupdate()
        else:
            self.ui.considergeo_check.setChecked(0)
            self.ui.cbdknown_radio.setEnabled(0)
            self.ui.cbdmanual_radio.setEnabled(0)
            self.ui.cbdmark_check.setEnabled(0)
            self.ui.cbd_combo.setEnabled(0)
            self.ui.cbdlong_box.setEnabled(0)
            self.ui.cbdlat_box.setEnabled(0)
            
    def cbdupdate(self):
        if self.ui.cbdknown_radio.isChecked() == 1:
            self.ui.cbd_combo.setEnabled(1)
            self.ui.cbdlong_box.setEnabled(0)
            self.ui.cbdlat_box.setEnabled(0)
        elif self.ui.cbdmanual_radio.isChecked() == 1:
            
            self.ui.cbdlong_box.setEnabled(1)
            self.ui.cbdlat_box.setEnabled(1)
    
    #====================================================================================================
    
    #Save values function
    def save_values(self):
        #----------------------------------------------------------------------#
        #-------- GENERAL SIMULATION INPUTS------------------------------------#
        #----------------------------------------------------------------------#
        self.module.setParameterValue("BlockSize", str(self.ui.blocksize_in.value()))
        self.module.setParameterValue("blocksize_auto", str(int(self.ui.blocksize_auto.isChecked())))
        
        #UrbanSim Legacy Code, only for DAnCE4Water Integration of UrbanBEATS
        #if self.ui.urbansim_in_check.isChecked() == 1:
        #    input_from_urbansim = 1
        #else:
        #    input_from_urbansim = 0
        #self.module.setParameterValue("input_from_urbansim", str(input_from_urbansim))
        
        #----------------------------------------------------------------------#
        #-------- PROCESSING INPUT DATA ---------------------------------------#
        #----------------------------------------------------------------------#
        if self.ui.popdata_totradio.isChecked() == True:
            popdatatype = "C"
        if self.ui.popdata_densradio.isChecked() == True:
            popdatatype = "D"
        self.module.setParameterValue("popdatatype", popdatatype)
        
        if self.ui.soildata_classify.isChecked() == True:
            soildatatype = "C"
        if self.ui.soildata_infil.isChecked() == True:
            soildatatype = "I"
        self.module.setParameterValue("soildatatype", soildatatype)
        
        soilunits = ["hrs", "sec"]
        self.module.setParameterValue("soildataunits", soilunits[self.ui.soildata_unitscombo.currentIndex()])
        
        if self.ui.elev_sealevel.isChecked() == True:
            elevdatadatum = "S"
        if self.ui.elev_custom.isChecked() == True:
            elevdatadatum = "C"
        self.module.setParameterValue("elevdatadatum", elevdatadatum)
        
        self.module.setParameterValue("elevdatacustomref", str(self.ui.elev_referencebox.text()))
        
        self.module.setParameterValue("include_plan_map", str(int(self.ui.planmap_check.isChecked())))
        self.module.setParameterValue("include_local_map", str(int(self.ui.localmap_check.isChecked())))
        
        self.module.setParameterValue("include_employment", str(int(self.ui.employment_check.isChecked())))
        
        if self.ui.jobdata_totradio.isChecked() == True:
            jobdatatype = "C"
        elif self.ui.jobdata_densradio.isChecked() == True:
            jobdatatype = "D"
        self.module.setParameterValue("jobdatatype", jobdatatype)
        
        self.module.setParameterValue("include_rivers", str(int(self.ui.rivers_check.isChecked())))
        self.module.setParameterValue("include_lakes", str(int(self.ui.lakes_check.isChecked())))
        
        self.module.setParameterValue("include_groundwater", str(int(self.ui.groundwater_check.isChecked())))
        
        gwoptions = ["Sea", "Surf"]
        self.module.setParameterValue("groundwater_datum", gwoptions[self.ui.groundwater_datumcombo.currentIndex()])
        
        #self.module.setParameterValue("include_road_net", str(int(self.ui.roadnet_check.isChecked())))
        #self.module.setParameterValue("include_supply_mains", str(int(self.ui.supplymains_check.isChecked())))
        #self.module.setParameterValue("include_sewer_mains", str(int(self.ui.sewermains_check.isChecked())))
        
        if self.ui.soc_par1_check.isChecked() == 1:
            include_soc_par1 = 1
            
            social_par1_name = str(self.ui.soc_par1_box.text())
            self.module.setParameterValue("social_par1_name", social_par1_name)
            
            if self.ui.socpar1binary_radio.isChecked() == True:
                socpar1_type = "B"
            if self.ui.socpar1prop_radio.isChecked() == True:
                socpar1_type = "P"
            self.module.setParameterValue("socpar1_type", socpar1_type)
            
        else:
            include_soc_par1 = 0
            
        self.module.setParameterValue("include_soc_par1", str(include_soc_par1))
        
        if self.ui.soc_par2_check.isChecked() == 1:
            include_soc_par2 = 1
            
            social_par2_name = str(self.ui.soc_par2_box.text())
            self.module.setParameterValue("social_par2_name", social_par2_name)
            
            if self.ui.socpar2binary_radio.isChecked() == True:
                socpar2_type = "B"
            if self.ui.socpar2prop_radio.isChecked() == True:
                socpar2_type = "P"
            self.module.setParameterValue("socpar2_type", socpar2_type)
            
        else:
            include_soc_par2 = 0
            
        self.module.setParameterValue("include_soc_par2", str(include_soc_par2))
        
        self.module.setParameterValue("patchdelin", str(int(self.ui.spatialpatches_check.isChecked())))
        self.module.setParameterValue("spatialmetrics", str(int(self.ui.spatialstats_check.isChecked())))
        
        #----------------------------------------------------------------------#
        #-------- MAP CONNECTIVITY PARAMETERS----------------------------------#
        #----------------------------------------------------------------------#
        if self.ui.radioMoore.isChecked() == True:
            neighbourhood = "M"
        if self.ui.radioVNeum.isChecked() == True:
            neighbourhood = "N"
        self.module.setParameterValue("Neighbourhood", neighbourhood)
        
        self.module.setParameterValue("vn4FlowPaths", str(int(self.ui.neighb_vnfp_check.isChecked())))
        self.module.setParameterValue("vn4Patches", str(int(self.ui.neighb_vnpd_check.isChecked())))
        
        #Combo Box
        flow_path_matrix = ["DI", "D8"]
        flow_method = flow_path_matrix[self.ui.flowpath_combo.currentIndex()]
        self.module.setParameterValue("flow_method", flow_method)
        
        self.module.setParameterValue("demsmooth_choose", str(int(self.ui.demsmooth_check.isChecked())))
        self.module.setParameterValue("demsmooth_passes", str(self.ui.demsmooth_spin.value()))
        
        #----------------------------------------------------------------------#
        #-------- REGIONAL GEOGRAPHY INPUTS -----------------------------------#
        #----------------------------------------------------------------------#
        self.module.setParameterValue("considerCBD", str(int(self.ui.considergeo_check.isChecked())))
        self.module.setParameterValue("marklocation", str(int(self.ui.cbdmark_check.isChecked())))
        
        if self.ui.cbdknown_radio.isChecked() == True:
            locationOption = "S"        #Selection
        elif self.ui.cbdmanual_radio.isChecked() == True:
            locationOption = "C"        #Coordinates
        self.module.setParameterValue("locationOption", str(locationOption))
        
        cityname = self.cities[self.ui.cbd_combo.currentIndex()]
        self.module.setParameterValue("locationCity", str(cityname))
        
        self.module.setParameterValue("locationLong", str(self.ui.cbdlong_box.text()))
        self.module.setParameterValue("locationLat", str(self.ui.cbdlat_box.text()))

