# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 0.5
@section LICENSE

This file is part of VIBe2
Copyright (C) 2011  Peter M Bach

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
import os

from PyQt4 import QtCore, QtGui
#from pyvibe import *
from pydynamind import *
from techplacementgui import Ui_TechPlace_Dialog

class activatetechplacementGUI(QtGui.QDialog):
    def __init__(self, m, parent=None):
        self.module = Module
        self.module = m
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_TechPlace_Dialog()
        self.ui.setupUi(self)
    
        #Assign Default Values & Connect Signal/Slots
        
        #######################################
        #General Strategy Tab
        #######################################
        
        #-------- DESIGN RATIONALE --------------------------------------------#
        self.ui.ration_runoff_check.setChecked(bool(int(self.module.getParameterAsString("ration_runoff"))))
        self.ui.ration_pollute_check.setChecked(bool(int(self.module.getParameterAsString("ration_pollute"))))
        self.ui.ration_harvest_check.setChecked(bool(int(self.module.getParameterAsString("ration_harvest"))))
        self.ui.runoff_pri_spin.setValue(int(self.module.getParameterAsString("runoff_pri")))
        self.ui.pollute_pri_spin.setValue(int(self.module.getParameterAsString("pollute_pri")))
        self.ui.harvest_pri_spin.setValue(int(self.module.getParameterAsString("harvest_pri")))
        
        #-------- MANAGEMENT TARGETS ------------------------------------------#
        self.ui.targets_runoff_spin.setValue(float(self.module.getParameterAsString("targets_runoff")))
        self.ui.targets_TSS_spin.setValue(float(self.module.getParameterAsString("targets_TSS")))
        self.ui.targets_TN_spin.setValue(float(self.module.getParameterAsString("targets_TN")))
        self.ui.targets_TP_spin.setValue(float(self.module.getParameterAsString("targets_TP")))
        self.ui.targets_reuse_spin.setValue(float(self.module.getParameterAsString("targets_harvest")))
        self.ui.targets_reliability_spin.setValue(float(self.module.getParameterAsString("targets_reliability")))
        
        #-------- SERVICE LEVELS ----------------------------------------------#
        self.ui.service_swm.setValue(float(self.module.getParameterAsString("service_swm")))
        self.ui.service_wr_private.setValue(float(self.module.getParameterAsString("service_wr_private")))
        self.ui.service_wr_public.setValue(float(self.module.getParameterAsString("service_wr_public")))
        
        self.ui.service_res.setChecked(bool(int(self.module.getParameterAsString("service_res"))))
        self.ui.service_hdr.setChecked(bool(int(self.module.getParameterAsString("service_hdr"))))
        self.ui.service_com.setChecked(bool(int(self.module.getParameterAsString("service_com"))))
        self.ui.service_li.setChecked(bool(int(self.module.getParameterAsString("service_li"))))
        self.ui.service_hi.setChecked(bool(int(self.module.getParameterAsString("service_hi"))))
        
        #-------- STRATEGY SETUP ----------------------------------------------#
        if self.module.getParameterAsString("strategy_lot_check") == "1":
            self.ui.strategy_lot_check.setChecked(1)
            self.ui.strategy_lot_rigour.setEnabled(1)
            self.ui.strategy_lot_rigour_box.setEnabled(1)
        else:
            self.ui.strategy_lot_check.setChecked(0)
            self.ui.strategy_lot_rigour.setEnabled(0)
            self.ui.strategy_lot_rigour_box.setEnabled(0)
            
        QtCore.QObject.connect(self.ui.strategy_lot_check, QtCore.SIGNAL("clicked()"), self.enableLotRigour)
        
        self.ui.strategy_lot_rigour.setValue(int(self.module.getParameterAsString("lot_rigour")))
        self.ui.strategy_lot_rigour_box.setText(self.module.getParameterAsString("lot_rigour"))
        QtCore.QObject.connect(self.ui.strategy_lot_rigour, QtCore.SIGNAL("valueChanged(int)"), self.adjustRigourLot)
        
        if self.module.getParameterAsString("strategy_street_check") == "1":
            self.ui.strategy_street_check.setChecked(1)
            self.ui.strategy_street_rigour.setEnabled(1)
            self.ui.strategy_street_rigour_box.setEnabled(1)
        else:
            self.ui.strategy_street_check.setChecked(0)
            self.ui.strategy_street_rigour.setEnabled(0)
            self.ui.strategy_street_rigour_box.setEnabled(0)
            
        QtCore.QObject.connect(self.ui.strategy_street_check, QtCore.SIGNAL("clicked()"), self.enableStreetRigour)
        
        self.ui.strategy_street_rigour.setValue(int(self.module.getParameterAsString("street_rigour")))
        self.ui.strategy_street_rigour_box.setText(self.module.getParameterAsString("street_rigour"))
        QtCore.QObject.connect(self.ui.strategy_street_rigour, QtCore.SIGNAL("valueChanged(int)"), self.adjustRigourStreet)
        
        if self.module.getParameterAsString("strategy_neigh_check") == "1":
            self.ui.strategy_neigh_check.setChecked(1)
            self.ui.strategy_neigh_rigour.setEnabled(1)
            self.ui.strategy_neigh_rigour_box.setEnabled(1)
        else:
            self.ui.strategy_neigh_check.setChecked(0)
            self.ui.strategy_neigh_rigour.setEnabled(0)
            self.ui.strategy_neigh_rigour_box.setEnabled(0)
            
        QtCore.QObject.connect(self.ui.strategy_neigh_check, QtCore.SIGNAL("clicked()"), self.enableNeighRigour)
        
        self.ui.strategy_neigh_rigour.setValue(int(self.module.getParameterAsString("neigh_rigour")))
        self.ui.strategy_neigh_rigour_box.setText(self.module.getParameterAsString("neigh_rigour"))
        QtCore.QObject.connect(self.ui.strategy_neigh_rigour, QtCore.SIGNAL("valueChanged(int)"), self.adjustRigourNeigh)
        
        if self.module.getParameterAsString("strategy_subbas_check") == "1":
            self.ui.strategy_subbas_check.setChecked(1)
            self.ui.strategy_subbas_rigour.setEnabled(1)
            self.ui.strategy_subbas_rigour_box.setEnabled(1)
        else:
            self.ui.strategy_subbas_check.setChecked(0)
            self.ui.strategy_subbas_rigour.setEnabled(0)
            self.ui.strategy_subbas_rigour_box.setEnabled(0)
            
        QtCore.QObject.connect(self.ui.strategy_subbas_check, QtCore.SIGNAL("clicked()"), self.enableSubbasRigour)
        
        self.ui.strategy_subbas_rigour.setValue(int(self.module.getParameterAsString("subbas_rigour")))
        self.ui.strategy_subbas_rigour_box.setText(self.module.getParameterAsString("subbas_rigour"))
        QtCore.QObject.connect(self.ui.strategy_subbas_rigour, QtCore.SIGNAL("valueChanged(int)"), self.adjustRigourSubbas)
        
        self.ui.strategy_specific1_check.setChecked(bool(int(self.module.getParameterAsString("strategy_specific1"))))
        self.ui.strategy_specific2_check.setChecked(bool(int(self.module.getParameterAsString("strategy_specific2"))))
        self.ui.strategy_specific3_check.setChecked(bool(int(self.module.getParameterAsString("strategy_specific3"))))
        self.ui.strategy_specific4_check.setChecked(bool(int(self.module.getParameterAsString("strategy_specific4"))))
        self.ui.strategy_specific5_check.setChecked(bool(int(self.module.getParameterAsString("strategy_specific5"))))
        
        #######################################
        #Retrofit Tab
        #######################################
        if self.module.getParameterAsString("retrofit_scenario") == "N":
            self.ui.area_retrofit_combo.setCurrentIndex(0)
            self.ui.lot_renew_check.setEnabled(0)
            self.ui.lot_decom_check.setEnabled(0)
            self.ui.street_decom_check.setEnabled(0)
            self.ui.street_renew_check.setEnabled(0)
            self.ui.neigh_renew_check.setEnabled(0)
            self.ui.neigh_decom_check.setEnabled(0)
            self.ui.prec_renew_check.setEnabled(0)
            self.ui.prec_decom_check.setEnabled(0)
            self.ui.decom_slider.setEnabled(0)
            self.ui.decom_box.setEnabled(0)
            self.ui.renew_slider.setEnabled(0)
            self.ui.renew_box.setEnabled(0)
            self.ui.radioKeep.setEnabled(0)
            self.ui.radioDecom.setEnabled(0)
        elif self.module.getParameterAsString("retrofit_scenario") == "R":
            self.ui.area_retrofit_combo.setCurrentIndex(1)
            self.ui.lot_renew_check.setEnabled(1)
            self.ui.lot_decom_check.setEnabled(1)
            self.ui.street_decom_check.setEnabled(1)
            self.ui.street_renew_check.setEnabled(1)
            self.ui.neigh_renew_check.setEnabled(1)
            self.ui.neigh_decom_check.setEnabled(1)
            self.ui.prec_renew_check.setEnabled(1)
            self.ui.prec_decom_check.setEnabled(1)
            self.ui.decom_slider.setEnabled(1)
            self.ui.decom_box.setEnabled(1)
            self.ui.renew_slider.setEnabled(1)
            self.ui.renew_box.setEnabled(1)
            self.ui.radioKeep.setEnabled(1)
            self.ui.radioDecom.setEnabled(1)
        elif self.module.getParameterAsString("retrofit_scenario") == "F":
            self.ui.area_retrofit_combo.setCurrentIndex(2)
            self.ui.lot_renew_check.setEnabled(1)
            self.ui.lot_decom_check.setEnabled(1)
            self.ui.street_decom_check.setEnabled(1)
            self.ui.street_renew_check.setEnabled(1)
            self.ui.neigh_renew_check.setEnabled(1)
            self.ui.neigh_decom_check.setEnabled(1)
            self.ui.prec_renew_check.setEnabled(1)
            self.ui.prec_decom_check.setEnabled(1)
            self.ui.decom_slider.setEnabled(1)
            self.ui.decom_box.setEnabled(1)
            self.ui.renew_slider.setEnabled(1)
            self.ui.renew_box.setEnabled(1)
            self.ui.radioKeep.setEnabled(1)
            self.ui.radioDecom.setEnabled(1)
        
        if self.module.getParameterAsString("renewal_cycle_def") == "1":
            self.ui.retrofit_renewal_check.setChecked(1)
        else:
            self.ui.retrofit_renewal_check.setChecked(0)
        
        self.ui.renewal_lot_years.setValue(float(self.module.getParameterAsString("renewal_lot_years")))
        self.ui.renewal_lot_spin.setValue(float(self.module.getParameterAsString("renewal_lot_perc")))
        self.ui.renewal_street_years.setValue(float(self.module.getParameterAsString("renewal_street_years")))
        self.ui.renewal_neigh_years.setValue(float(self.module.getParameterAsString("renewal_neigh_years")))
        
        if self.module.getParameterAsString("force_street") == "1":
            self.ui.retrofit_forced_street_check.setChecked(1)
        else:
            self.ui.retrofit_forced_street_check.setChecked(0)
        
        if self.module.getParameterAsString("force_neigh") == "1":
            self.ui.retrofit_forced_neigh_check.setChecked(1)
        else:
            self.ui.retrofit_forced_neigh_check.setChecked(0)
        
        if self.module.getParameterAsString("force_prec") == "1":
            self.ui.retrofit_forced_prec_check.setChecked(1)
        else:
            self.ui.retrofit_forced_prec_check.setChecked(0)
        
        
        if self.module.getParameterAsString("lot_renew") == "1":
            self.ui.lot_renew_check.setChecked(1)
        else:
            self.ui.lot_renew_check.setChecked(0)
        
        if self.module.getParameterAsString("lot_decom") == "1":
            self.ui.lot_decom_check.setChecked(1)
        else:
            self.ui.lot_decom_check.setChecked(0)
        
        if self.module.getParameterAsString("street_renew") == "1":
            self.ui.street_renew_check.setChecked(1)
        else:
            self.ui.street_renew_check.setChecked(0)
        
        if self.module.getParameterAsString("street_decom") == "1":
            self.ui.street_decom_check.setChecked(1)
        else:
            self.ui.street_decom_check.setChecked(0)
        
        if self.module.getParameterAsString("neigh_renew") == "1":
            self.ui.neigh_renew_check.setChecked(1)
        else:
            self.ui.neigh_renew_check.setChecked(0)
        
        if self.module.getParameterAsString("neigh_decom") == "1":
            self.ui.neigh_decom_check.setChecked(1)
        else:
            self.ui.neigh_decom_check.setChecked(0)
        
        if self.module.getParameterAsString("prec_renew") == "1":
            self.ui.prec_renew_check.setChecked(1)
        else:
            self.ui.prec_renew_check.setChecked(0)
        
        if self.module.getParameterAsString("prec_decom") == "1":
            self.ui.prec_decom_check.setChecked(1)
        else:
            self.ui.prec_decom_check.setChecked(0)
        
        self.ui.decom_slider.setValue(int(self.module.getParameterAsString("decom_thresh")))
        self.ui.decom_box.setText(self.module.getParameterAsString("decom_thresh")+"%")
        self.ui.renew_slider.setValue(int(self.module.getParameterAsString("renewal_thresh")))
        self.ui.renew_box.setText(self.module.getParameterAsString("renewal_thresh")+"%")
        QtCore.QObject.connect(self.ui.decom_slider, QtCore.SIGNAL("valueChanged(int)"), self.decom_update)
        QtCore.QObject.connect(self.ui.renew_slider, QtCore.SIGNAL("valueChanged(int)"), self.renew_update)
        
        if self.module.getParameterAsString("renewal_alternative") == "K":
            self.ui.radioKeep.setChecked(True)
        if self.module.getParameterAsString("renewal_alternative") == "D":
            self.ui.radioDecom.setChecked(True)
        
        QtCore.QObject.connect(self.ui.area_retrofit_combo, QtCore.SIGNAL("currentIndexChanged(int)"), self.update_retrofitoptions)
        
        #######################################
        #Choose & Customize Technologies Tab
        #######################################
        
        #--------- Advanced Stormwater Harvesting Plant -----------------------#
        if self.module.getParameterAsString("ASHPstatus") == "1": 
            self.ui.ASHPstatus_box.setChecked(1)
        else:
            self.ui.ASHPstatus_box.setChecked(0)
        
        #--------- Aquaculture/LivingSystems ----------------------------------#
        if self.module.getParameterAsString("AQstatus") == "1": 
            self.ui.AQstatus_box.setChecked(1)
        else:
            self.ui.AQstatus_box.setChecked(0)
        
        #--------- Aquifer Storage/Recovery -----------------------------------#
        if self.module.getParameterAsString("ASRstatus") == "1":
            self.ui.ASRstatus_box.setChecked(1)
        else:
            self.ui.ASRstatus_box.setChecked(0)
        
        #--------- Biofiltration/Raingardens ----------------------------------#
        if self.module.getParameterAsString("BFstatus") == "1":
            self.ui.BFstatus_box.setChecked(1)
        else:
            self.ui.BFstatus_box.setChecked(0)
        
        #Available Scales
        if self.module.getParameterAsString("BFlot") == "1":
            self.ui.BFlot_check.setChecked(1)
        else:
            self.ui.BFlot_check.setChecked(0)
        
        if self.module.getParameterAsString("BFstreet") == "1":
            self.ui.BFstreet_check.setChecked(1)
        else:
            self.ui.BFstreet_check.setChecked(0)
        
        if self.module.getParameterAsString("BFneigh") == "1":
            self.ui.BFneigh_check.setChecked(1)
        else:
            self.ui.BFneigh_check.setChecked(0)
        
        if self.module.getParameterAsString("BFprec") == "1":
            self.ui.BFprec_check.setChecked(1)
        else:
            self.ui.BFprec_check.setChecked(0)
        
        #Available Applications
        if self.module.getParameterAsString("BFpollute") == "1":
            self.ui.BFpollute_check.setChecked(1)
        else:
            self.ui.BFpollute_check.setChecked(0)
        
        #Design Curves
        if self.module.getParameterAsString("BFdesignUB") == "1":
            self.ui.BFdesignUB_box.setChecked(1)
        else:
            self.ui.BFdesignUB_box.setChecked(0)
        
        if self.module.getParameterAsString("BFdesignUB") == "1":
            self.ui.BFdesignUB_box.setChecked(1)
            self.ui.BFdesigncurve_browse.setEnabled(0)
            self.ui.BFdesigncurve_pathbox.setText("no file")
        else:
            self.ui.BFdesignUB_box.setChecked(0)
            self.ui.BFdesigncurve_browse.setEnabled(1)
            self.ui.BFdesigncurve_pathbox.setText(self.module.getParameterAsString("BFdescur_path"))
        
        QtCore.QObject.connect(self.ui.BFdesigncurve_browse, QtCore.SIGNAL("clicked()"), self.openFileDialog_BF)
        QtCore.QObject.connect(self.ui.BFdesignUB_box, QtCore.SIGNAL("clicked()"), self.BFdesign_enable)
        
        #Design Information
        
        #COMBO BOXES CONTAINING EDD AND FD SPECS
        if self.module.getParameterAsString("BFspec_EDD") == "0":
            self.ui.BFspecs_EDD_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("BFspec_EDD") == "0.1":
            self.ui.BFspecs_EDD_combo.setCurrentIndex(1)
        elif self.module.getParameterAsString("BFspec_EDD") == "0.2":
            self.ui.BFspecs_EDD_combo.setCurrentIndex(2)
        elif self.module.getParameterAsString("BFspec_EDD") == "0.3":
            self.ui.BFspecs_EDD_combo.setCurrentIndex(3)
        elif self.module.getParameterAsString("BFspec_EDD") == "0.4":
            self.ui.BFspecs_EDD_combo.setCurrentIndex(4)
        
        if self.module.getParameterAsString("BFspec_FD") == "0.2":
            self.ui.BFspecs_FD_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("BFspec_FD") == "0.4":
            self.ui.BFspecs_FD_combo.setCurrentIndex(1)
        elif self.module.getParameterAsString("BFspec_FD") == "0.6":
            self.ui.BFspecs_FD_combo.setCurrentIndex(2)
        elif self.module.getParameterAsString("BFspec_FD") == "0.8":
            self.ui.BFspecs_FD_combo.setCurrentIndex(3)
        
        self.ui.BFmaxsize_box.setText(self.module.getParameterAsString("BFmaxsize"))
        
        if self.module.getParameterAsString("BFlined") == "1":
            self.ui.BFlined_check.setChecked(1)
        else:
            self.ui.BFlined_check.setChecked(0)
        
        #futher design info coming soon
        
        #--------- Green Roof -------------------------------------------------#
        if self.module.getParameterAsString("GRstatus") == "1":
            self.ui.GRstatus_box.setChecked(1)
        else:
            self.ui.GRstatus_box.setChecked(0)
        
        #--------- Greywater Tank/Treatment -----------------------------------#
        if self.module.getParameterAsString("GTstatus") == "1":
            self.ui.GTstatus_box.setChecked(1)
        else:
            self.ui.GTstatus_box.setChecked(0)
        
        #--------- Gross Pollutant Trap ---------------------------------------#
        if self.module.getParameterAsString("GPTstatus") == "1":
            self.ui.GPTstatus_box.setChecked(1)
        else:
            self.ui.GPTstatus_box.setChecked(0)
        
        #--------- Infiltration System ----------------------------------------#
        if self.module.getParameterAsString("ISstatus") == "1":
            self.ui.ISstatus_box.setChecked(1)
        else:
            self.ui.ISstatus_box.setChecked(0)
        
        #Available Scales
        if self.module.getParameterAsString("ISlot") == "1":
            self.ui.ISlot_check.setChecked(1)
        else:
            self.ui.ISlot_check.setChecked(0)
        
        if self.module.getParameterAsString("ISstreet") == "1":
            self.ui.ISstreet_check.setChecked(1)
        else:
            self.ui.ISstreet_check.setChecked(0)
        
        if self.module.getParameterAsString("ISneigh") == "1":
            self.ui.ISneigh_check.setChecked(1)
        else:
            self.ui.ISneigh_check.setChecked(0)
        
        #Available Applications
        if self.module.getParameterAsString("ISflow") == "1":
            self.ui.ISflow_check.setChecked(1)
        else:
            self.ui.ISflow_check.setChecked(0)
            
        if self.module.getParameterAsString("ISpollute") == "1":
            self.ui.ISpollute_check.setChecked(1)
        else:
            self.ui.ISpollute_check.setChecked(0)
        
        #Design Curves
        if self.module.getParameterAsString("ISdesignUB") == "1":
            self.ui.ISdesignUB_box.setChecked(1)
            self.ui.ISdesigncurve_browse.setEnabled(0)
            self.ui.ISdesigncurve_pathbox.setText("no file")
        else:
            self.ui.ISdesignUB_box.setChecked(0)
            self.ui.ISdesigncurve_browse.setEnabled(1)
            self.ui.ISdesigncurve_pathbox.setText(self.module.getParameterAsString("ISdescur_path"))
        
        QtCore.QObject.connect(self.ui.ISdesigncurve_browse, QtCore.SIGNAL("clicked()"), self.openFileDialog_IS)
        QtCore.QObject.connect(self.ui.ISdesignUB_box, QtCore.SIGNAL("clicked()"), self.ISdesign_enable)
        
        #Design Information
        
        #COMBO BOXES CONTAINING EDD AND FD SPECS
        if self.module.getParameterAsString("ISspec_EDD") == "0.1":
            self.ui.ISspecs_EDD_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("ISspec_EDD") == "0.2":
            self.ui.ISspecs_EDD_combo.setCurrentIndex(1)
        elif self.module.getParameterAsString("ISspec_EDD") == "0.3":
            self.ui.ISspecs_EDD_combo.setCurrentIndex(2)
        elif self.module.getParameterAsString("ISspec_EDD") == "0.4":
            self.ui.ISspecs_EDD_combo.setCurrentIndex(3)
        
        if self.module.getParameterAsString("ISspec_FD") == "0.2":
            self.ui.ISspecs_FD_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("ISspec_FD") == "0.4":
            self.ui.ISspecs_FD_combo.setCurrentIndex(1)
        elif self.module.getParameterAsString("ISspec_FD") == "0.6":
            self.ui.ISspecs_FD_combo.setCurrentIndex(2)
        elif self.module.getParameterAsString("ISspec_FD") == "0.8":
            self.ui.ISspecs_FD_combo.setCurrentIndex(3)
        
        self.ui.ISmaxsize_box.setText(self.module.getParameterAsString("ISmaxsize"))
        self.ui.ISavglifespin.setValue(int(self.module.getParameterAsString("ISavglife")))
        
        #--------- Packaged Plant ---------------------------------------------#
        if self.module.getParameterAsString("PPLstatus") == "1":
            self.ui.PPLstatus_box.setChecked(1)
        else:
            self.ui.PPLstatus_box.setChecked(0)
        
        #--------- Ponds/Sedimentation Basin ----------------------------------#
        if self.module.getParameterAsString("PBstatus") == "1":
            self.ui.PBstatus_box.setChecked(1)
        else:
            self.ui.PBstatus_box.setChecked(0)
        
        #Available Scales
        if self.module.getParameterAsString("PBneigh") == "1":
            self.ui.PBneigh_check.setChecked(1)
        else:
            self.ui.PBneigh_check.setChecked(0)
        
        if self.module.getParameterAsString("PBprec") == "1":
            self.ui.PBprec_check.setChecked(1)
        else:
            self.ui.PBprec_check.setChecked(0)
        
        #Available Applications
        if self.module.getParameterAsString("PBflow") == "1":
            self.ui.PBflow_check.setChecked(1)
        else:
            self.ui.PBflow_check.setChecked(0)
            
        if self.module.getParameterAsString("PBpollute") == "1":
            self.ui.PBpollute_check.setChecked(1)
        else:
            self.ui.PBpollute_check.setChecked(0)
        
        #Design Curves
        if self.module.getParameterAsString("PBdesignUB") == "1":
            self.ui.PBdesignUB_box.setChecked(1)
        else:
            self.ui.PBdesignUB_box.setChecked(0)
        
        if self.module.getParameterAsString("PBdesignUB") == "1":
            self.ui.PBdesignUB_box.setChecked(1)
            self.ui.PBdesigncurve_browse.setEnabled(0)
            self.ui.PBdesigncurve_pathbox.setText("no file")
        else:
            self.ui.PBdesignUB_box.setChecked(0)
            self.ui.PBdesigncurve_browse.setEnabled(1)
            self.ui.PBdesigncurve_pathbox.setText(self.module.getParameterAsString("PBdescur_path"))
        
        QtCore.QObject.connect(self.ui.PBdesigncurve_browse, QtCore.SIGNAL("clicked()"), self.openFileDialog_PB)
        QtCore.QObject.connect(self.ui.PBdesignUB_box, QtCore.SIGNAL("clicked()"), self.PBdesign_enable)
        
        #Design Information
        
        #combo box with specs
        if self.module.getParameterAsString("PBspec_MD") == "0.25":
            self.ui.PBspecs_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("PBspec_MD") == "0.50":
            self.ui.PBspecs_combo.setCurrentIndex(1)
        elif self.module.getParameterAsString("PBspec_MD") == "0.75":
            self.ui.PBspecs_combo.setCurrentIndex(2)
        elif self.module.getParameterAsString("PBspec_MD") == "1.00":
            self.ui.PBspecs_combo.setCurrentIndex(3)
        elif self.module.getParameterAsString("PBspec_MD") == "1.25":
            self.ui.PBspecs_combo.setCurrentIndex(4)    
        
        self.ui.PBmaxsize_box.setText(self.module.getParameterAsString("PBmaxsize"))
        
        #futher design info coming soon
        
        #---------- Porous/Pervious Pavement ----------------------------------#
        if self.module.getParameterAsString("PPstatus") == "1":
            self.ui.PPstatus_box.setChecked(1)
        else:
            self.ui.PPstatus_box.setChecked(0)
        
        #---------- Rainwater Tank --------------------------------------------#
        if self.module.getParameterAsString("RTstatus") == "1":
            self.ui.RTstatus_box.setChecked(1)
        else:
            self.ui.RTstatus_box.setChecked(0)
        
        self.ui.RT_maxdepth_box.setText(self.module.getParameterAsString("RT_maxdepth"))
        self.ui.RT_mindead_box.setText(self.module.getParameterAsString("RT_mindead"))
        self.ui.RT_firstflush_box.setText(self.module.getParameterAsString("RT_firstflush"))
        
        if self.module.getParameterAsString("RTscale_lot") == "1":
            self.ui.RTscale_lot_box.setChecked(1)
        else:
            self.ui.RTscale_lot_box.setChecked(0)
        
        if self.module.getParameterAsString("RTscale_street") == "1":
            self.ui.RTscale_street_box.setChecked(1)
        else:
            self.ui.RTscale_street_box.setChecked(0)
                
        if self.module.getParameterAsString("RTpurp_flood") == "1":
            self.ui.RTpurp_flood_box.setChecked(1)
        else:
            self.ui.RTpurp_flood_box.setChecked(0)
        
        if self.module.getParameterAsString("RTpurp_recyc") == "1":
            self.ui.RTpurp_recyc_box.setChecked(1)
        else:
            self.ui.RTpurp_recyc_box.setChecked(0)
        
        if self.module.getParameterAsString("RT_shape_circ") == "1":
            self.ui.RT_shape_circ_check.setChecked(1)
        else:
            self.ui.RT_shape_circ_check.setChecked(0)
        
        if self.module.getParameterAsString("RT_shape_rect") == "1":
            self.ui.RT_shape_rect_check.setChecked(1)
        else:
            self.ui.RT_shape_rect_check.setChecked(0)
        
        if self.module.getParameterAsString("RT_sbmodel") == "ybs":
            self.ui.RT_sbmodel_ybs_radio.setChecked(True)
        if self.module.getParameterAsString("RT_sbmodel") == "yas":
            self.ui.RT_sbmodel_yas_radio.setChecked(True)
        
        if self.module.getParameterAsString("RTdesignD4W") == "1":
            self.ui.RTdesignD4W_box.setChecked(1)
            self.ui.RTdesigncurve_browse.setEnabled(0)
            self.ui.RTdesigncurve_pathbox.setText("no file")
        else:
            self.ui.RTdesignD4W_box.setChecked(0)
            self.ui.RTdesigncurve_browse.setEnabled(1)
            self.ui.RTdesigncurve_pathbox.setText(self.module.getParameterAsString("RTdescur_path"))
        
        QtCore.QObject.connect(self.ui.RTdesigncurve_browse, QtCore.SIGNAL("clicked()"), self.openFileDialog_RT)
        QtCore.QObject.connect(self.ui.RTdesignD4W_box, QtCore.SIGNAL("clicked()"), self.RTdesign_enable)
        
        #---------- Sand/Peat/Gravel Filter -----------------------------------#
        if self.module.getParameterAsString("SFstatus") == "1":
            self.ui.SFstatus_box.setChecked(1)
        else:
            self.ui.SFstatus_box.setChecked(0)
                
        #---------- Subsurface Irrigation System ------------------------------#
        if self.module.getParameterAsString("IRRstatus") == "1":
            self.ui.IRRstatus_box.setChecked(1)
        else:
            self.ui.IRRstatus_box.setChecked(0)
        
        #---------- Subsurface Wetland/Reed Bed -------------------------------#
        if self.module.getParameterAsString("WSUBstatus") == "1":
            self.ui.WSUBstatus_box.setChecked(1)
        else:
            self.ui.WSUBstatus_box.setChecked(0)
        
        #---------- Surface Wetland -------------------------------------------#
        if self.module.getParameterAsString("WSURstatus") == "1":
            self.ui.WSURstatus_box.setChecked(1)
        else:
            self.ui.WSURstatus_box.setChecked(0)
        
        #Available Scales
        if self.module.getParameterAsString("WSURneigh") == "1":
            self.ui.WSURneigh_check.setChecked(1)
        else:
            self.ui.WSURneigh_check.setChecked(0)
        
        if self.module.getParameterAsString("PBprec") == "1":
            self.ui.WSURprec_check.setChecked(1)
        else:
            self.ui.WSURprec_check.setChecked(0)
        
        #Available Applications
        if self.module.getParameterAsString("WSURflow") == "1":
            self.ui.WSURflow_check.setChecked(1)
        else:
            self.ui.WSURflow_check.setChecked(0)
            
        if self.module.getParameterAsString("WSURpollute") == "1":
            self.ui.WSURpollute_check.setChecked(1)
        else:
            self.ui.WSURpollute_check.setChecked(0)
        
        #Design Curves
        if self.module.getParameterAsString("WSURdesignUB") == "1":
            self.ui.WSURdesignUB_box.setChecked(1)
        else:
            self.ui.WSURdesignUB_box.setChecked(0)
        
        if self.module.getParameterAsString("WSURdesignUB") == "1":
            self.ui.WSURdesignUB_box.setChecked(1)
            self.ui.WSURdesigncurve_browse.setEnabled(0)
            self.ui.WSURdesigncurve_pathbox.setText("no file")
        else:
            self.ui.WSURdesignUB_box.setChecked(0)
            self.ui.WSURdesigncurve_browse.setEnabled(1)
            self.ui.WSURdesigncurve_pathbox.setText(self.module.getParameterAsString("PBdescur_path"))
        
        QtCore.QObject.connect(self.ui.WSURdesigncurve_browse, QtCore.SIGNAL("clicked()"), self.openFileDialog_WSUR)
        QtCore.QObject.connect(self.ui.WSURdesignUB_box, QtCore.SIGNAL("clicked()"), self.WSURdesign_enable)
        
        #Design Information
        
        #combo box with specs
        if self.module.getParameterAsString("WSURspec_EDD") == "0.25":
            self.ui.WSURspecs_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("WSURspec_EDD") == "0.50":
            self.ui.WSURspecs_combo.setCurrentIndex(1)
        elif self.module.getParameterAsString("WSURspec_EDD") == "0.75":
            self.ui.WSURspecs_combo.setCurrentIndex(2)
        elif self.module.getParameterAsString("WSURspec_EDD") == "0.25":
            self.ui.WSURspecs_combo.setCurrentIndex(3)
        elif self.module.getParameterAsString("WSURspec_EDD") == "0.50":
            self.ui.WSURspecs_combo.setCurrentIndex(4)  
        elif self.module.getParameterAsString("WSURspec_EDD") == "0.75":
            self.ui.WSURspecs_combo.setCurrentIndex(5)
        
        self.ui.WSURmaxsize_box.setText(self.module.getParameterAsString("WSURmaxsize"))
        
        #futher design info coming soon
        
        #---------- Swales/Buffer Strips --------------------------------------#
        if self.module.getParameterAsString("SWstatus") == "1":
            self.ui.SWstatus_box.setChecked(1)
        else:
            self.ui.SWstatus_box.setChecked(0)
        
        #Available Scales
        if self.module.getParameterAsString("SWstreet") == "1":
            self.ui.SWstreet_check.setChecked(1)
        else:
            self.ui.SWstreet_check.setChecked(0)
        
        #Available Applications
        if self.module.getParameterAsString("SWflow") == "1":
            self.ui.SWflow_check.setChecked(1)
        else:
            self.ui.SWflow_check.setChecked(0)
            
        if self.module.getParameterAsString("SWpollute") == "1":
            self.ui.SWpollute_check.setChecked(1)
        else:
            self.ui.SWpollute_check.setChecked(0)
        
        #Design Curves
        if self.module.getParameterAsString("SWdesignUB") == "1":
            self.ui.SWdesignUB_box.setChecked(1)
        else:
            self.ui.SWdesignUB_box.setChecked(0)
        
        if self.module.getParameterAsString("SWdesignUB") == "1":
            self.ui.SWdesignUB_box.setChecked(1)
            self.ui.SWdesigncurve_browse.setEnabled(0)
            self.ui.SWdesigncurve_pathbox.setText("no file")
        else:
            self.ui.SWdesignUB_box.setChecked(0)
            self.ui.SWdesigncurve_browse.setEnabled(1)
            self.ui.SWdesigncurve_pathbox.setText(self.module.getParameterAsString("SWdescur_path"))
        
        QtCore.QObject.connect(self.ui.SWdesigncurve_browse, QtCore.SIGNAL("clicked()"), self.openFileDialog_SW)
        QtCore.QObject.connect(self.ui.SWdesignUB_box, QtCore.SIGNAL("clicked()"), self.SWdesign_enable)
        
        #Design Information
        
        #combo box with specs
        self.ui.SWmaxsize_box.setText(self.module.getParameterAsString("SWmaxsize"))
        
        #futher design info coming soon
        
        #--------- Tree Pits --------------------------------------------------#
        if self.module.getParameterAsString("TPSstatus") == "1": 
            self.ui.TPSstatus_box.setChecked(1)
        else:
            self.ui.TPSstatus_box.setChecked(0)
        
        #---------- Urine-Separation Toilets ----------------------------------#
        if self.module.getParameterAsString("UTstatus") == "1":
            self.ui.UTstatus_box.setChecked(1)
        else:
            self.ui.UTstatus_box.setChecked(0)
        
        #---------- Wastewater Recovery/Recycling Plant -----------------------#
        if self.module.getParameterAsString("WWRRstatus") == "1":
            self.ui.WWRRstatus_box.setChecked(1)
        else:
            self.ui.WWRRstatus_box.setChecked(0)
        
        #---------- Waterless/Composting Toilet -------------------------------#
        if self.module.getParameterAsString("WTstatus") == "1":
            self.ui.WTstatus_box.setChecked(1)
        else:
            self.ui.WTstatus_box.setChecked(0)
        
        #---------- Water Efficient Appliances --------------------------------#
        if self.module.getParameterAsString("WEFstatus") == "1":
            self.ui.WEFstatus_box.setChecked(1)
        else:
            self.ui.WEFstatus_box.setChecked(0)
        
        ### NOTE: Not linking Rating System Combo box, AS6400 the only available system currently
        
        self.ui.LEG_minrate_spin.setValue(int(self.module.getParameterAsString("LEG_minrate")))
        self.ui.PPP_likelihood_spin.setValue(int(self.module.getParameterAsString("PPP_likelihood")))
        
        if self.module.getParameterAsString("WEF_implement_method") == "LEG":
            self.ui.WEF_implement_method_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("WEF_implement_method") == "PPP":
            self.ui.WEF_implement_method_combo.setCurrentIndex(1)
        elif self.module.getParameterAsString("WEF_implement_method") == "SEC":
            self.ui.WEF_implement_method_combo.setCurrentIndex(2)
        elif self.module.getParameterAsString("WEF_implement_method") == "D4W":
            self.ui.WEF_implement_method_combo.setCurrentIndex(3)
        
        if self.module.getParameterAsString("LEG_force") == "1":
            self.ui.LEG_force_check.setChecked(1)
        else:
            self.ui.LEG_force_check.setChecked(0)
            
        if self.module.getParameterAsString("PPP_force") == "1":
            self.ui.PPP_force_check.setChecked(1)
        else:
            self.ui.PPP_force_check.setChecked(0)
        
        if self.module.getParameterAsString("SEC_force") == "1":
            self.ui.SEC_force_check.setChecked(1)
        else:
            self.ui.SEC_force_check.setChecked(0)
        
        if self.module.getParameterAsString("SEC_urbansim") == "1":
            self.ui.SEC_urbansim_check.setChecked(1)
        else:
            self.ui.SEC_urbansim_check.setChecked(0)
            
        if self.module.getParameterAsString("D4W_UDMactive") == "1":
            self.ui.D4W_UDMactive_check.setChecked(1)
        else:
            self.ui.D4W_UDMactive_check.setChecked(0)
        
        if self.module.getParameterAsString("D4W_STMactive") == "1":
            self.ui.D4W_STMactive_check.setChecked(1)
        else:
            self.ui.D4W_STMactive_check.setChecked(0)
        
        if self.module.getParameterAsString("D4W_EVMactive") == "1":
            self.ui.D4W_EVMactive_check.setChecked(1)
        else:
            self.ui.D4W_EVMactive_check.setChecked(0)
        
        if self.module.getParameterAsString("WEF_loc_famhouse") == "1":
            self.ui.WEF_loc_famhouse_check.setChecked(1)
        else:
            self.ui.WEF_loc_famhouse_check.setChecked(0)
        
        if self.module.getParameterAsString("WEF_loc_apart") == "1":
            self.ui.WEF_loc_apart_check.setChecked(1)
        else:
            self.ui.WEF_loc_apart_check.setChecked(0)
            
        if self.module.getParameterAsString("WEF_loc_nonres") == "1":
            self.ui.WEF_loc_nonres_check.setChecked(1)
        else:
            self.ui.WEF_loc_nonres_check.setChecked(0)
        
        if self.module.getParameterAsString("WEF_flow_method") == "M":
            self.ui.WEF_radio_medflow.setChecked(True)
        if self.module.getParameterAsString("WEF_flow_method") == "S":
            self.ui.WEF_radio_stochflow.setChecked(True)
        
        #--- ## --- Regional Information --------------------------------------#
        if self.module.getParameterAsString("regioncity") == "Adelaide":
            self.ui.regioncity_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("regioncity") == "Brisbane":
            self.ui.regioncity_combo.setCurrentIndex(1)
        elif self.module.getParameterAsString("regioncity") == "Melbourne":
            self.ui.regioncity_combo.setCurrentIndex(2)
        elif self.module.getParameterAsString("regioncity") == "Perth":
            self.ui.regioncity_combo.setCurrentIndex(3)
        elif self.module.getParameterAsString("regioncity") == "Sydney":
            self.ui.regioncity_combo.setCurrentIndex(4)
        
        #######################################
        #Select Evaluation Criteria Tab
        #######################################
        #-------- Evaluation Metrics Select------------------------------------#
        if self.module.getParameterAsString("scoringmatrix_default") == "1":
            self.ui.mca_scoringmat_check.setChecked(1)
            self.ui.mca_scoringmat_browse.setEnabled(0)
            self.ui.mca_scoringmat_box.setText("no file")
            self.ui.bottomlines_techN_spin.setEnabled(0)
            self.ui.bottomlines_envN_spin.setEnabled(0)
            self.ui.bottomlines_ecnN_spin.setEnabled(0)
            self.ui.bottomlines_socN_spin.setEnabled(0)
        else:
            self.ui.mca_scoringmat_check.setChecked(0)
            self.ui.mca_scoringmat_browse.setEnabled(1)
            self.ui.mca_scoringmat_box.setText(self.module.getParameterAsString("scoringmatrix_path"))
            self.ui.bottomlines_techN_spin.setEnabled(1)
            self.ui.bottomlines_envN_spin.setEnabled(1)
            self.ui.bottomlines_ecnN_spin.setEnabled(1)
            self.ui.bottomlines_socN_spin.setEnabled(1)
        
        QtCore.QObject.connect(self.ui.mca_scoringmat_browse, QtCore.SIGNAL("clicked()"), self.openFileDialog_mca)
        QtCore.QObject.connect(self.ui.mca_scoringmat_check, QtCore.SIGNAL("clicked()"), self.mca_scoringmat_enable)
    
        #-------- Customize Evaluation Criteria--------------------------------#
        if self.module.getParameterAsString("bottomlines_tech") == "1":
            self.ui.bottomlines_tech_check.setChecked(1)
        else:
            self.ui.bottomlines_tech_check.setChecked(0)
        
        if self.module.getParameterAsString("bottomlines_env") == "1":
            self.ui.bottomlines_env_check.setChecked(1)
        else:
            self.ui.bottomlines_env_check.setChecked(0)
        
        if self.module.getParameterAsString("bottomlines_ecn") == "1":
            self.ui.bottomlines_ecn_check.setChecked(1)
        else:
            self.ui.bottomlines_ecn_check.setChecked(0)
        
        if self.module.getParameterAsString("bottomlines_soc") == "1":
            self.ui.bottomlines_soc_check.setChecked(1)
        else:
            self.ui.bottomlines_soc_check.setChecked(0)

        self.ui.bottomlines_techN_spin.setValue(int(self.module.getParameterAsString("bottomlines_tech_n")))
        self.ui.bottomlines_envN_spin.setValue(int(self.module.getParameterAsString("bottomlines_env_n")))
        self.ui.bottomlines_ecnN_spin.setValue(int(self.module.getParameterAsString("bottomlines_ecn_n")))
        self.ui.bottomlines_socN_spin.setValue(int(self.module.getParameterAsString("bottomlines_soc_n")))
        
        self.ui.bottomlines_techW_spin.setValue(int(self.module.getParameterAsString("bottomlines_tech_w")))
        self.ui.bottomlines_envW_spin.setValue(int(self.module.getParameterAsString("bottomlines_env_w")))
        self.ui.bottomlines_ecnW_spin.setValue(int(self.module.getParameterAsString("bottomlines_ecn_w")))
        self.ui.bottomlines_socW_spin.setValue(int(self.module.getParameterAsString("bottomlines_soc_w")))
        
        #-------- EVALUATION SCOPE & METHOD -----------------------------------#
        if self.module.getParameterAsString("score_method") == "AHP":
            self.ui.eval_method_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("score_method") == "RAHP":
            self.ui.eval_method_combo.setCurrentIndex(1)
        elif self.module.getParameterAsString("score_method") == "WPM":
            self.ui.eval_method_combo.setCurrentIndex(2)
        elif self.module.getParameterAsString("score_method") == "WSM":
            self.ui.eval_method_combo.setCurrentIndex(3)
        
        if self.module.getParameterAsString("scope_stoch") == "1":
            self.ui.scope_stoch_check.setChecked(1)
        else:
            self.ui.scope_stoch_check.setChecked(0)
        
        if self.module.getParameterAsString("ingroup_scoring") == "Avg":
            self.ui.radioScoreAvg.setChecked(True)
        if self.module.getParameterAsString("ingroup_scoring") == "Med":
            self.ui.radioScoreMed.setChecked(True)
        if self.module.getParameterAsString("ingroup_scoring") == "Min":
            self.ui.radioScoreMin.setChecked(True)
        if self.module.getParameterAsString("ingroup_scoring") == "Max":
            self.ui.radioScoreMax.setChecked(True)
 
        #-------- RANKING OF STRATEGIES ---------------------------------------#
        if self.module.getParameterAsString("ranktype") == "RK":
            self.ui.top_score_combo.setCurrentIndex(0)
            self.ui.top_rank_spin.setEnabled(1)
            self.ui.top_CI_spin.setEnabled(0)
        elif self.module.getParameterAsString("ranktype") == "CI":
            self.ui.top_score_combo.setCurrentIndex(1)
            self.ui.top_rank_spin.setEnabled(0)
            self.ui.top_CI_spin.setEnabled(1)
            
        QtCore.QObject.connect(self.ui.top_score_combo, QtCore.SIGNAL("currentIndexChanged(int)"), self.top_score_change)
        
        self.ui.top_rank_spin.setValue(int(self.module.getParameterAsString("topranklimit")))
        self.ui.top_CI_spin.setValue(int(self.module.getParameterAsString("conf_int")))
        
        #CONNECT DETAILS WITH THE OK BUTTON SO THAT GUI UPDATES MODULE
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.save_values)

    ### GENERAL TAB ###
    def enableLotRigour(self):
        if self.ui.strategy_lot_check.isChecked() == True:
            self.ui.strategy_lot_rigour.setEnabled(1)
            self.ui.strategy_lot_rigour_box.setEnabled(1)
        else:
            self.ui.strategy_lot_rigour.setEnabled(0)
            self.ui.strategy_lot_rigour_box.setEnabled(0)

    def enableStreetRigour(self):
        if self.ui.strategy_street_check.isChecked() == True:
            self.ui.strategy_street_rigour.setEnabled(1)
            self.ui.strategy_street_rigour_box.setEnabled(1)
        else:
            self.ui.strategy_street_rigour.setEnabled(0)
            self.ui.strategy_street_rigour_box.setEnabled(0)

    def enableNeighRigour(self):
        if self.ui.strategy_neigh_check.isChecked() == True:
            self.ui.strategy_neigh_rigour.setEnabled(1)
            self.ui.strategy_neigh_rigour_box.setEnabled(1)
        else:
            self.ui.strategy_neigh_rigour.setEnabled(0)
            self.ui.strategy_neigh_rigour_box.setEnabled(0)

    def enableSubbasRigour(self):
        if self.ui.strategy_subbas_check.isChecked() == True:
            self.ui.strategy_subbas_rigour.setEnabled(1)
            self.ui.strategy_subbas_rigour_box.setEnabled(1)
        else:
            self.ui.strategy_subbas_rigour.setEnabled(0)
            self.ui.strategy_subbas_rigour_box.setEnabled(0)

    def adjustRigourLot(self, currentValue):
        self.ui.strategy_lot_rigour_box.setText(str(currentValue))
    
    def adjustRigourStreet(self, currentValue):
        self.ui.strategy_street_rigour_box.setText(str(currentValue))
    
    def adjustRigourNeigh(self, currentValue):
        self.ui.strategy_neigh_rigour_box.setText(str(currentValue))
    
    def adjustRigourSubbas(self, currentValue):
        self.ui.strategy_subbas_rigour_box.setText(str(currentValue))
        
    ### RECYCLE TAB ###
    
    
    
    ### RETROFIT TAB ###
    def decom_update(self, currentValue):
        self.ui.decom_box.setText(str(currentValue)+"%")
        self.module.setParameterValue("decom_thresh", str(currentValue))
        if self.ui.renew_slider.value() > self.ui.decom_slider.value():
            self.renew_all_update(self.ui.decom_slider.value())
    
    def renew_update(self, currentValue):
        self.ui.renew_box.setText(str(currentValue)+"%")
        self.module.setParameterValue("renewal_thresh", str(currentValue))
        if self.ui.renew_slider.value() > self.ui.decom_slider.value():
            self.renew_all_update(self.ui.decom_slider.value())
    
    def renew_all_update(self, currentValue):
        self.ui.renew_box.setText(str(currentValue)+"%")
        self.ui.renew_slider.setValue(currentValue)
        self.module.setParameterValue("renewal_thresh", str(currentValue))
    
    def update_retrofitoptions(self, currentind):
        if currentind == 0:
            self.ui.lot_renew_check.setEnabled(0)
            self.ui.lot_decom_check.setEnabled(0)
            self.ui.street_decom_check.setEnabled(0)
            self.ui.street_renew_check.setEnabled(0)
            self.ui.neigh_renew_check.setEnabled(0)
            self.ui.neigh_decom_check.setEnabled(0)
            self.ui.prec_renew_check.setEnabled(0)
            self.ui.prec_decom_check.setEnabled(0)
            self.ui.decom_slider.setEnabled(0)
            self.ui.decom_box.setEnabled(0)
            self.ui.renew_slider.setEnabled(0)
            self.ui.renew_box.setEnabled(0)
            self.ui.radioKeep.setEnabled(0)
            self.ui.radioDecom.setEnabled(0)
        else:
            self.ui.lot_renew_check.setEnabled(1)
            self.ui.lot_decom_check.setEnabled(1)
            self.ui.street_decom_check.setEnabled(1)
            self.ui.street_renew_check.setEnabled(1)
            self.ui.neigh_renew_check.setEnabled(1)
            self.ui.neigh_decom_check.setEnabled(1)
            self.ui.prec_renew_check.setEnabled(1)
            self.ui.prec_decom_check.setEnabled(1)
            self.ui.decom_slider.setEnabled(1)
            self.ui.decom_box.setEnabled(1)
            self.ui.renew_slider.setEnabled(1)
            self.ui.renew_box.setEnabled(1)
            self.ui.radioKeep.setEnabled(1)
            self.ui.radioDecom.setEnabled(1)    
    
    ### TECHNOLOGIES TABS ###
    
    #BIOFILTRATION SYSTEMS SIGNAL-SLOT FUNCTIONS
    def openFileDialog_BF(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, "Choose Design Curve File...", os.curdir, str("Design Curves (*.dcv *.txt)"))
        if fname: 
            self.ui.BFdesigncurve_pathbox.setText(fname) 
    def BFdesign_enable(self):
        if self.ui.BFdesignUB_box.isChecked() == 1:
            self.ui.BFdesigncurve_browse.setEnabled(0)
        else:
            self.ui.BFdesigncurve_browse.setEnabled(1)

    #INFILTRATION SYSTEMS SIGNAL-SLOT FUNCTIONS
    def openFileDialog_IS(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, "Choose Design Curve File...", os.curdir, str("Design Curves (*.dcv *.txt)"))
        if fname: 
            self.ui.ISdesigncurve_pathbox.setText(fname) 
    def ISdesign_enable(self):
        if self.ui.ISdesignUB_box.isChecked() == 1:
            self.ui.ISdesigncurve_browse.setEnabled(0)
        else:
            self.ui.ISdesigncurve_browse.setEnabled(1)

    #PONDS/BASIN SYSTEM SIGNAL-SLOT FUNCTIONS
    def openFileDialog_PB(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, "Choose Design Curve File...", os.curdir, str("Design Curves (*.dcv *.txt)"))
        if fname: 
            self.ui.PBdesigncurve_pathbox.setText(fname) 
    def PBdesign_enable(self):
        if self.ui.PBdesignUB_box.isChecked() == 1:
            self.ui.PBdesigncurve_browse.setEnabled(0)
        else:
            self.ui.PBdesigncurve_browse.setEnabled(1)

    #RAINWATER TANK SIGNAL-SLOT FUNCTIONS
    def openFileDialog_RT(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, "Choose Design Curve File...", os.curdir, str("Design Curves (*.dcv *.txt)"))
        if fname: 
            self.ui.RTdesigncurve_pathbox.setText(fname) 
    def RTdesign_enable(self):
        if self.ui.RTdesignD4W_box.isChecked() == 1:
            self.ui.RTdesigncurve_browse.setEnabled(0)
        else:
            self.ui.RTdesigncurve_browse.setEnabled(1)
    
    #SURFACE WETLAND SYSTEMS SIGNAL-SLOT FUNCTIONS
    def openFileDialog_WSUR(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, "Choose Design Curve File...", os.curdir, str("Design Curves (*.dcv *.txt)"))
        if fname: 
            self.ui.WSURdesigncurve_pathbox.setText(fname) 
    def WSURdesign_enable(self):
        if self.ui.WSURdesignUB_box.isChecked() == 1:
            self.ui.WSURdesigncurve_browse.setEnabled(0)
        else:
            self.ui.WSURdesigncurve_browse.setEnabled(1)
    
    #SWALE SYSTEMS SIGNAL-SLOT FUNCTIONS
    def openFileDialog_SW(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, "Choose Design Curve File...", os.curdir, str("Design Curves (*.dcv *.txt)"))
        if fname: 
            self.ui.SWdesigncurve_pathbox.setText(fname) 
    def SWdesign_enable(self):
        if self.ui.SWdesignUB_box.isChecked() == 1:
            self.ui.SWdesigncurve_browse.setEnabled(0)
        else:
            self.ui.SWdesigncurve_browse.setEnabled(1)
    
    ### EVALUATION CRITERIA SIGNAL-SLOT FUNCTIONS
    def openFileDialog_mca(self):
        fname = QtGui.QFileDialog.getOpenFileName(self, "Choose scoring matrix...", os.curdir, str("Scoring Matrix (*.csv)"))
        if fname: 
            self.ui.mca_scoringmat_box.setText(fname) 
    def mca_scoringmat_enable(self):
        if self.ui.mca_scoringmat_check.isChecked() == 1:
            self.ui.mca_scoringmat_browse.setEnabled(0)
            self.ui.bottomlines_techN_spin.setEnabled(0)
            self.ui.bottomlines_envN_spin.setEnabled(0)
            self.ui.bottomlines_ecnN_spin.setEnabled(0)
            self.ui.bottomlines_socN_spin.setEnabled(0)
        else:
            self.ui.mca_scoringmat_browse.setEnabled(1)
            self.ui.bottomlines_techN_spin.setEnabled(1)
            self.ui.bottomlines_envN_spin.setEnabled(1)
            self.ui.bottomlines_ecnN_spin.setEnabled(1)
            self.ui.bottomlines_socN_spin.setEnabled(1)
    
    def top_score_change(self):
        if self.ui.top_score_combo.currentIndex() == 0:         #RK option
            self.ui.top_rank_spin.setEnabled(1)
            self.ui.top_CI_spin.setEnabled(0)
        if self.ui.top_score_combo.currentIndex() == 1:         #CI option
            self.ui.top_rank_spin.setEnabled(0)
            self.ui.top_CI_spin.setEnabled(1)
    
        
    #OK BUTTON PRESS FUNCTION        
    def save_values(self):
        
        ################################
        #Select Design Criteria Tab
        ################################    
        
        #-------- DESIGN RATIONALE --------------------------------------------#
        self.module.setParameterValue("ration_runoff", str(int(self.ui.ration_runoff_check.isChecked())))
        self.module.setParameterValue("ration_pollute", str(int(self.ui.ration_runoff_check.isChecked())))
        self.module.setParameterValue("ration_harvest", str(int(self.ui.ration_runoff_check.isChecked())))
        self.module.setParameterValue("runoff_pri", str(self.ui.runoff_pri_spin.value()))
        self.module.setParameterValue("pollute_pri", str(self.ui.pollute_pri_spin.value()))
        self.module.setParameterValue("harvest_pri", str(self.ui.harvest_pri_spin.value()))
        
        #-------- MANAGEMENT TARGETS ------------------------------------------#
        self.module.setParameterValue("targets_runoff", str(self.ui.targets_runoff_spin.value()))
        self.module.setParameterValue("targets_TSS", str(self.ui.targets_TSS_spin.value()))
        self.module.setParameterValue("targets_TN", str(self.ui.targets_TN_spin.value()))
        self.module.setParameterValue("targets_TP", str(self.ui.targets_TP_spin.value()))
        self.module.setParameterValue("targets_harvest", str(self.ui.targets_reuse_spin.value()))
        
        #-------- SERVICE LEVELS ----------------------------------------------#
        self.module.setParameterValue("service_swm", str(self.ui.service_swm.value()))
        self.module.setParameterValue("service_wr_private", str(self.ui.service_wr_private.value()))
        self.module.setParameterValue("service_wr_public", str(self.ui.service_wr_public.value()))
        
        self.module.setParameterValue("service_res", str(int(self.ui.service_res.isChecked())))
        self.module.setParameterValue("service_hdr", str(int(self.ui.service_hdr.isChecked())))
        self.module.setParameterValue("service_com", str(int(self.ui.service_com.isChecked())))
        self.module.setParameterValue("service_li", str(int(self.ui.service_li.isChecked())))
        self.module.setParameterValue("service_hi", str(int(self.ui.service_li.isChecked())))
        
        #-------- STRATEGY SETUP ----------------------------------------------#
        self.module.setParameterValue("strategy_lot_check", str(int(self.ui.strategy_lot_check.isChecked())))
        self.module.setParameterValue("strategy_street_check", str(int(self.ui.strategy_street_check.isChecked())))
        self.module.setParameterValue("strategy_neigh_check", str(int(self.ui.strategy_neigh_check.isChecked())))
        self.module.setParameterValue("strategy_subbas_check", str(int(self.ui.strategy_subbas_check.isChecked())))
        self.module.setParameterValue("lot_rigour", str(self.ui.strategy_lot_rigour.value()))    
        self.module.setParameterValue("street_rigour", str(self.ui.strategy_street_rigour.value()))
        self.module.setParameterValue("neigh_rigour", str(self.ui.strategy_neigh_rigour.value()))
        self.module.setParameterValue("subbas_rigour", str(self.ui.strategy_subbas_rigour.value()))
        
        self.module.setParameterValue("strategy_specific1", str(int(self.ui.strategy_specific1_check.isChecked())))
        self.module.setParameterValue("strategy_specific2", str(int(self.ui.strategy_specific2_check.isChecked())))
        self.module.setParameterValue("strategy_specific3", str(int(self.ui.strategy_specific3_check.isChecked())))
        self.module.setParameterValue("strategy_specific4", str(int(self.ui.strategy_specific4_check.isChecked())))
        self.module.setParameterValue("strategy_specific5", str(int(self.ui.strategy_specific5_check.isChecked())))
        
        #######################################
        #Retrofit Tab
        #######################################
        retrofit_scenario_matrix = ["N", "R", "F"]
        retrofit_index = self.ui.area_retrofit_combo.currentIndex()
        retrofit_scenario = retrofit_scenario_matrix[retrofit_index]
        self.module.setParameterValue("retrofit_scenario", str(retrofit_scenario))
        
        if self.ui.retrofit_renewal_check.isChecked() == 1:
            renewal_cycle_def = 1
        else:
            renewal_cycle_def = 0
        self.module.setParameterValue("renewal_cycle_def", str(renewal_cycle_def))
        
        renewal_lot_years = str(self.ui.renewal_lot_years.value())
        self.module.setParameterValue("renewal_lot_years", renewal_lot_years)
        
        renewal_lot_perc = str(self.ui.renewal_lot_spin.value())
        self.module.setParameterValue("renewal_lot_perc", renewal_lot_perc)
        
        renewal_street_years = str(self.ui.renewal_street_years.value())
        self.module.setParameterValue("renewal_street_years", renewal_street_years)
        
        renewal_neigh_years = str(self.ui.renewal_neigh_years.value())
        self.module.setParameterValue("renewal_neigh_years", renewal_neigh_years)
        
        if self.ui.retrofit_forced_street_check.isChecked() == 1:
            force_street = 1
        else:
            force_street = 0
        self.module.setParameterValue("force_street", str(force_street))
        
        if self.ui.retrofit_forced_neigh_check.isChecked() == 1:
            force_neigh = 1
        else:
            force_neigh = 0
        self.module.setParameterValue("force_neigh", str(force_neigh))
        
        if self.ui.retrofit_forced_prec_check.isChecked() == 1:
            force_prec = 1
        else:
            force_prec = 0
        self.module.setParameterValue("force_prec", str(force_prec))
        
        if self.ui.lot_renew_check.isChecked() == 1:
            lot_renew = 1
        else:
            lot_renew = 0
        self.module.setParameterValue("lot_renew", str(lot_renew))
        
        if self.ui.lot_decom_check.isChecked() == 1:
            lot_decom = 1
        else:
            lot_decom = 0
        self.module.setParameterValue("lot_decom", str(lot_decom))
        
        if self.ui.street_renew_check.isChecked() == 1:
            street_renew = 1
        else:
            street_renew = 0
        self.module.setParameterValue("street_renew", str(street_renew))
        
        if self.ui.street_decom_check.isChecked() == 1:
            street_decom = 1
        else:
            street_decom = 0
        self.module.setParameterValue("street_decom", str(street_decom))
        
        if self.ui.neigh_renew_check.isChecked() == 1:
            neigh_renew = 1
        else:
            neigh_renew = 0
        self.module.setParameterValue("neigh_renew", str(neigh_renew))
        
        if self.ui.neigh_decom_check.isChecked() == 1:
            neigh_decom = 1
        else:
            neigh_decom = 0
        self.module.setParameterValue("neigh_decom", str(neigh_decom))
        
        if self.ui.prec_renew_check.isChecked() == 1:
            prec_renew = 1
        else:
            prec_renew = 0
        self.module.setParameterValue("prec_renew", str(prec_renew))
        
        if self.ui.prec_decom_check.isChecked() == 1:
            prec_decom = 1
        else:
            prec_decom = 0
        self.module.setParameterValue("prec_decom", str(prec_decom))
        
        decom_thresh = str(self.ui.decom_slider.value())
        self.module.setParameterValue("decom_thresh", decom_thresh)
        
        renewal_thresh = str(self.ui.renew_slider.value())
        self.module.setParameterValue("renewal_thresh", renewal_thresh)
        
        if self.ui.radioKeep.isChecked() == True:
            renewal_alternative = "K"
        if self.ui.radioDecom.isChecked() == True:
            renewal_alternative = "D"
        self.module.setParameterValue("renewal_alternative", renewal_alternative)
        
        
        #######################################
        #Choose & Customize Technologies Tab
        #######################################
        
        #--------- Advanced Stormwater Harvesting Plant -----------------------#
        if self.ui.ASHPstatus_box.isChecked() == 1:
            ASHPstatus = 1
        else:
            ASHPstatus = 0
        self.module.setParameterValue("ASHPstatus", str(ASHPstatus))
        
        #--------- Aquaculture/Living Systems ---------------------------------#
        if self.ui.AQstatus_box.isChecked() == 1:
            AQstatus = 1
        else:
            AQstatus = 0
        self.module.setParameterValue("AQstatus", str(AQstatus))
        
        #--------- Aquifer Storage & Recovery ---------------------------------#
        if self.ui.ASRstatus_box.isChecked() == 1:
            ASRstatus = 1
        else:
            ASRstatus = 0
        self.module.setParameterValue("ASRstatus", str(ASRstatus))
        
        #--------- Biofiltration/Raingardens ----------------------------------#
        if self.ui.BFstatus_box.isChecked() == 1:
            BFstatus = 1
        else:
            BFstatus = 0
        self.module.setParameterValue("BFstatus", str(BFstatus))
        
        #Available Scales
        if self.ui.BFlot_check.isChecked() == 1:
            BFlot = 1
        else:
            BFlot = 0
        self.module.setParameterValue("BFlot", str(BFlot))
        
        if self.ui.BFstreet_check.isChecked() == 1:
            BFstreet = 1
        else:
            BFstreet = 0
        self.module.setParameterValue("BFstreet", str(BFstreet))
        
        if self.ui.BFneigh_check.isChecked() == 1:
            BFneigh = 1
        else:
            BFneigh = 0
        self.module.setParameterValue("BFneigh", str(BFneigh))
        
        if self.ui.BFprec_check.isChecked() == 1:
            BFprec = 1
        else:
            BFprec = 0
        self.module.setParameterValue("BFprec", str(BFprec))
        
        #Available Applications
        if self.ui.BFpollute_check.isChecked() == 1:
            BFpollute = 1
        else:
            BFpollute = 0
        self.module.setParameterValue("BFpollute", str(BFpollute))
        
        #Design Curves
        if self.ui.BFdesignUB_box.isChecked() == 1:
            BFdesignUB = 1
        else:
            BFdesignUB = 0
        self.module.setParameterValue("BFdesignUB", str(BFdesignUB))
        
        BFdescur_path = str(self.ui.BFdesigncurve_pathbox.text())
        self.module.setParameterValue("BFdescur_path", BFdescur_path)
        
        #Design Information
        
        #combo box
        BFspec_matrix = [[0,0.1,0.2,0.3,0.4],[0.2,0.4,0.6,0.8]]
        BFspec_EDDindex = self.ui.BFspecs_EDD_combo.currentIndex()
        BFspec_FDindex = self.ui.BFspecs_FD_combo.currentIndex()
        BFspec_EDD = BFspec_matrix[0][BFspec_EDDindex]
        BFspec_FD = BFspec_matrix[1][BFspec_FDindex]
        self.module.setParameterValue("BFspec_EDD", str(BFspec_EDD))
        self.module.setParameterValue("BFspec_FD", str(BFspec_FD))
        
        BFmaxsize = str(self.ui.BFmaxsize_box.text())
        self.module.setParameterValue("BFmaxsize", BFmaxsize)
        
        if self.ui.BFlined_check.isChecked() == 1:
            BFlined = 1
        else:
            BFlined = 0
        self.module.setParameterValue("BFlined", str(BFlined))
        
        #further design parameters coming soon...
        
        #--------- Green Roof -------------------------------------------------#
        if self.ui.GRstatus_box.isChecked() == 1:
            GRstatus = 1
        else:
            GRstatus = 0
        self.module.setParameterValue("GRstatus", str(GRstatus))
        
        #--------- Greywater Tank/Treatment -----------------------------------#
        if self.ui.GTstatus_box.isChecked() == 1:
            GTstatus = 1
        else:
            GTstatus = 0
        self.module.setParameterValue("GTstatus", str(GTstatus))
        
        #--------- Gross Pollutant Trap ---------------------------------------#
        if self.ui.GPTstatus_box.isChecked() == 1:
            GPTstatus = 1
        else:
            GPTstatus = 0
        self.module.setParameterValue("GPTstatus", str(GPTstatus))
        
        #--------- Infiltration System ----------------------------------------#
        if self.ui.ISstatus_box.isChecked() == 1:
            ISstatus = 1
        else:
            ISstatus = 0
        self.module.setParameterValue("ISstatus", str(ISstatus))
        
        #Available Scales
        if self.ui.ISlot_check.isChecked() == 1:
            ISlot = 1
        else:
            ISlot = 0
        self.module.setParameterValue("ISlot", str(ISlot))
        
        if self.ui.ISstreet_check.isChecked() == 1:
            ISstreet = 1
        else:
            ISstreet = 0
        self.module.setParameterValue("ISstreet", str(ISstreet))
        
        if self.ui.ISneigh_check.isChecked() == 1:
            ISneigh = 1
        else:
            ISneigh = 0
        self.module.setParameterValue("ISneigh", str(ISneigh))
        
        #Available Applications
        if self.ui.ISflow_check.isChecked() == 1:
            ISflow = 1
        else:
            ISflow = 0
        self.module.setParameterValue("ISflow", str(ISflow))
        
        if self.ui.ISpollute_check.isChecked() == 1:
            ISpollute = 1
        else:
            ISpollute = 0
        self.module.setParameterValue("ISpollute", str(ISpollute))
        
        #Design Curves
        if self.ui.ISdesignUB_box.isChecked() == 1:
            ISdesignUB = 1
        else:
            ISdesignUB = 0
        self.module.setParameterValue("ISdesignUB", str(ISdesignUB))
        
        ISdescur_path = str(self.ui.ISdesigncurve_pathbox.text())
        self.module.setParameterValue("ISdescur_path", ISdescur_path)
        
        #Design Information
        #combo box
        ISspec_matrix = [[0.1,0.2,0.3,0.4,0.5],[0.2,0.4,0.6,0.8]]
        ISspec_EDDindex = self.ui.ISspecs_EDD_combo.currentIndex()
        ISspec_FDindex = self.ui.ISspecs_FD_combo.currentIndex()
        ISspec_EDD = ISspec_matrix[0][ISspec_EDDindex]
        ISspec_FD = ISspec_matrix[1][ISspec_FDindex]
        self.module.setParameterValue("ISspec_EDD", str(ISspec_EDD))
        self.module.setParameterValue("ISspec_FD", str(ISspec_FD))
        
        self.module.setParameterValue("ISmaxsize", str(self.ui.ISmaxsize_box.text()))
        self.module.setParameterValue("ISavglife", str(self.ui.ISavglifespin.value()))
        
        #--------- Packaged Plants --------------------------------------------#
        if self.ui.PPLstatus_box.isChecked() == 1:
            PPLstatus = 1
        else:
            PPLstatus = 0
        self.module.setParameterValue("PPLstatus", str(PPLstatus))
        
        #--------- Ponds/Sedimentation Basins ---------------------------------#
        if self.ui.PBstatus_box.isChecked() == 1:
            PBstatus = 1
        else:
            PBstatus = 0
        self.module.setParameterValue("PBstatus", str(PBstatus))
        
        #Available Scales
        if self.ui.PBneigh_check.isChecked() == 1:
            PBneigh = 1
        else:
            PBneigh = 0
        self.module.setParameterValue("PBneigh", str(PBneigh))
        
        if self.ui.PBprec_check.isChecked() == 1:
            PBprec = 1
        else:
            PBprec = 0
        self.module.setParameterValue("PBprec", str(PBprec))
        
        #Available Applications
        if self.ui.PBflow_check.isChecked() == 1:
            PBflow = 1
        else:
            PBflow = 0
        self.module.setParameterValue("PBflow", str(PBflow))
        
        if self.ui.PBpollute_check.isChecked() == 1:
            PBpollute = 1
        else:
            PBpollute = 0
        self.module.setParameterValue("PBpollute", str(PBpollute))
        
        #Design Curves
        if self.ui.PBdesignUB_box.isChecked() == 1:
            PBdesignUB = 1
        else:
            PBdesignUB = 0
        self.module.setParameterValue("PBdesignUB", str(PBdesignUB))
        
        PBdescur_path = str(self.ui.PBdesigncurve_pathbox.text())
        self.module.setParameterValue("PBdescur_path", PBdescur_path)
        
        #Design Information
        #combo box
        PBspec_matrix = ["0.25", "0.50", "0.75", "1.00", "1.25"]
        PBspec_MDindex = self.ui.PBspecs_combo.currentIndex()
        PBspec_MD = PBspec_matrix[PBspec_MDindex]
        self.module.setParameterValue("PBspec_MD", str(PBspec_MD))
        print PBspec_MD
        
        PBmaxsize = str(self.ui.PBmaxsize_box.text())
        self.module.setParameterValue("PBmaxsize", PBmaxsize)
        #further design parameters coming soon...
        
        #---------- Porous/Pervious Pavements ---------------------------------#
        if self.ui.PPstatus_box.isChecked() == 1:
            PPstatus = 1
        else:
            PPstatus = 0
        self.module.setParameterValue("PPstatus", str(PPstatus))
        
        #---------- Rainwater Tank --------------------------------------------#
        if self.ui.RTstatus_box.isChecked() == 1:
            RTstatus = 1
        else:
            RTstatus = 0
        self.module.setParameterValue("RTstatus", str(RTstatus))
        
        RT_maxdepth = str(self.ui.RT_maxdepth_box.text())
        self.module.setParameterValue("RT_maxdepth", RT_maxdepth)
        RT_mindead = str(self.ui.RT_mindead_box.text())
        self.module.setParameterValue("RT_mindead", RT_mindead)
        RT_firstflush = str(self.ui.RT_firstflush_box.text())
        self.module.setParameterValue("RT_firstflush", RT_firstflush)
        
        if self.ui.RTscale_lot_box.isChecked() == 1:
            RTscale_lot = 1
        else:
            RTscale_lot = 0
        self.module.setParameterValue("RTscale_lot", str(RTscale_lot))
        
        if self.ui.RTscale_street_box.isChecked() == 1:
            RTscale_street = 1
        else:
            RTscale_street = 0
        self.module.setParameterValue("RTscale_street", str(RTscale_street))
        
        if self.ui.RTpurp_flood_box.isChecked() == 1:
            RTpurp_flood = 1
        else:
            RTpurp_flood = 0
        self.module.setParameterValue("RTpurp_flood", str(RTpurp_flood))
        
        if self.ui.RTpurp_recyc_box.isChecked() == 1:
            RTpurp_recyc = 1
        else:
            RTpurp_recyc = 0
        self.module.setParameterValue("RTpurp_recyc", str(RTpurp_recyc))
        
        if self.ui.RT_shape_circ_check.isChecked() == 1:
            RT_shape_circ = 1
        else:
            RT_shape_circ = 0
        self.module.setParameterValue("RT_shape_circ", str(RT_shape_circ))
        
        if self.ui.RT_shape_rect_check.isChecked() == 1:
            RT_shape_rect = 1
        else:
            RT_shape_rect = 0
        self.module.setParameterValue("RT_shape_rect", str(RT_shape_rect))
        
        if self.ui.RTdesignD4W_box.isChecked() == 1:
            RTdesignD4W = 1
        else:
            RTdesignD4W = 0
        self.module.setParameterValue("RTdesignD4W", str(RTdesignD4W))
        
        RTdescur_path = str(self.ui.RTdesigncurve_pathbox.text())
        self.module.setParameterValue("RTdescur_path", RTdescur_path)
        
        if self.ui.RT_sbmodel_ybs_radio.isChecked() == True:
            RT_sbmodel = "ybs"
        elif self.ui.RT_sbmodel_yas_radio.isChecked() == True:
            RT_sbmodel = "yas"
        self.module.setParameterValue("RT_sbmodel", RT_sbmodel)
        
        #---------- Sand/Peat/Gravel Filter -----------------------------------#
        if self.ui.SFstatus_box.isChecked() == 1:
            SFstatus = 1
        else:
            SFstatus = 0
        self.module.setParameterValue("SFstatus", str(SFstatus))
        
        #---------- Subsurface Irrigation System ------------------------------#
        if self.ui.IRRstatus_box.isChecked() == 1:
            IRRstatus = 1
        else:
            IRRstatus = 0
        self.module.setParameterValue("IRRstatus", str(IRRstatus))
        
        #---------- Subsurface Wetland/Reed Bed -------------------------------#
        if self.ui.WSUBstatus_box.isChecked() == 1:
            WSUBstatus = 1
        else:
            WSUBstatus = 0
        self.module.setParameterValue("WSUBstatus", str(WSUBstatus))
        
        #---------- Surface Wetland -------------------------------------------#
        if self.ui.WSURstatus_box.isChecked() == 1:
            WSURstatus = 1
        else:
            WSURstatus = 0
        self.module.setParameterValue("WSURstatus", str(WSURstatus))
        
        #Available Scales
        if self.ui.WSURneigh_check.isChecked() == 1:
            WSURneigh = 1
        else:
            WSURneigh = 0
        self.module.setParameterValue("WSURneigh", str(WSURneigh))
        
        if self.ui.WSURprec_check.isChecked() == 1:
            WSURprec = 1
        else:
            WSURprec = 0
        self.module.setParameterValue("WSURprec", str(WSURprec))
        
        #Available Applications
        if self.ui.WSURflow_check.isChecked() == 1:
            WSURflow = 1
        else:
            WSURflow = 0
        self.module.setParameterValue("WSURflow", str(WSURflow))
        
        if self.ui.WSURpollute_check.isChecked() == 1:
            WSURpollute = 1
        else:
            WSURpollute = 0
        self.module.setParameterValue("WSURpollute", str(WSURpollute))
        
        #Design Curves
        if self.ui.WSURdesignUB_box.isChecked() == 1:
            WSURdesignUB = 1
        else:
            WSURdesignUB = 0
        self.module.setParameterValue("WSURdesignUB", str(WSURdesignUB))
        
        WSURdescur_path = str(self.ui.WSURdesigncurve_pathbox.text())
        self.module.setParameterValue("WSURdescur_path", WSURdescur_path)
        
        #Design Information
        #combo box
        WSURspec_matrix = ["0.25", "0.50", "0.75", "0.25", "0.50", "0.75"]
        WSURspec_EDDindex = self.ui.WSURspecs_combo.currentIndex()
        WSURspec_EDD = WSURspec_matrix[WSURspec_EDDindex]
        self.module.setParameterValue("WSURspec_EDD", str(WSURspec_EDD))
        
        WSURmaxsize = str(self.ui.WSURmaxsize_box.text())
        self.module.setParameterValue("WSURmaxsize", WSURmaxsize)
        #further design parameters coming soon...
        
        #---------- Swales/Buffer Strips --------------------------------------#
        if self.ui.SWstatus_box.isChecked() == 1:
            SWstatus = 1
        else:
            SWstatus = 0
        self.module.setParameterValue("SWstatus", str(SWstatus))
        
        #Available Scales
        if self.ui.SWstreet_check.isChecked() == 1:
            SWstreet = 1
        else:
            SWstreet = 0
        self.module.setParameterValue("SWstreet", str(SWstreet))
        
        #Available Applications
        if self.ui.SWflow_check.isChecked() == 1:
            SWflow = 1
        else:
            SWflow = 0
        self.module.setParameterValue("SWflow", str(SWflow))
        
        if self.ui.SWpollute_check.isChecked() == 1:
            SWpollute = 1
        else:
            SWpollute = 0
        self.module.setParameterValue("SWpollute", str(SWpollute))
        
        #Design Curves
        if self.ui.SWdesignUB_box.isChecked() == 1:
            SWdesignUB = 1
        else:
            SWdesignUB = 0
        self.module.setParameterValue("SWdesignUB", str(SWdesignUB))
        
        SWdescur_path = str(self.ui.SWdesigncurve_pathbox.text())
        self.module.setParameterValue("SWdescur_path", SWdescur_path)
        
        #Design Information
        #combo box
        SWmaxsize = str(self.ui.SWmaxsize_box.text())
        self.module.setParameterValue("SWmaxsize", SWmaxsize)
        #further design parameters coming soon...
        
        #--------- Tree Pits --------------------------------------------------#
        if self.ui.TPSstatus_box.isChecked() == 1:
            TPSstatus = 1
        else:
            TPSstatus = 0
        self.module.setParameterValue("TPSstatus", str(TPSstatus))
        
        #---------- Urine-separating Toilets ----------------------------------#
        if self.ui.UTstatus_box.isChecked() == 1:
            UTstatus = 1
        else:
            UTstatus = 0
        self.module.setParameterValue("UTstatus", str(UTstatus))
        
        #---------- Wastwater Recovery/Recycling Plant ------------------------#
        if self.ui.WWRRstatus_box.isChecked() == 1:
            WWRRstatus = 1
        else:
            WWRRstatus = 0
        self.module.setParameterValue("WWRRstatus", str(WWRRstatus))
        
        #---------- Waterless/Composting Toilets ------------------------------#
        if self.ui.WTstatus_box.isChecked() == 1:
            WTstatus = 1
        else:
            WTstatus = 0
        self.module.setParameterValue("WTstatus", str(WTstatus))
        
        #---------- Water Efficient Appliances --------------------------------#
        if self.ui.WEFstatus_box.isChecked() == 1:
            WEFstatus = 1
        else:
            WEFstatus = 0
        self.module.setParameterValue("WEFstatus", str(WEFstatus))
        
        ###NOTE: NOT LINKING COMBO BOX WITH RATING SYSTEM, AS6400 the only one for now
        
        LEG_minrate = str(self.ui.LEG_minrate_spin.value())
        self.module.setParameterValue("LEG_minrate", LEG_minrate)
        
        PPP_likelihood = str(self.ui.PPP_likelihood_spin.value())
        self.module.setParameterValue("PPP_likelihood", PPP_likelihood)
        
            #COMBO BOXES
        WEF_implement_method_matrix = ["LEG", "PPP", "SEC", "D4W"]
        
        WEF_implement_index = self.ui.WEF_implement_method_combo.currentIndex()
        WEF_implement_method = WEF_implement_method_matrix[WEF_implement_index]
        self.module.setParameterValue("WEF_implement_method", WEF_implement_method)
        
        if self.ui.LEG_force_check.isChecked() == 1:
            LEG_force = 1
        else:
            LEG_force = 0
        self.module.setParameterValue("LEG_force", str(LEG_force))
        
        if self.ui.PPP_force_check.isChecked() == 1:
            PPP_force = 1
        else:
            PPP_force = 0
        self.module.setParameterValue("PPP_force", str(PPP_force))
        
        if self.ui.SEC_force_check.isChecked() == 1:
            SEC_force = 1
        else:
            SEC_force = 0
        self.module.setParameterValue("SEC_force", str(SEC_force))
        
        if self.ui.SEC_urbansim_check.isChecked() == 1:
            SEC_urbansim = 1
        else:
            SEC_urbansim = 0
        self.module.setParameterValue("SEC_urbansim", str(SEC_urbansim))
        
        if self.ui.D4W_UDMactive_check.isChecked() == 1:
            D4W_UDMactive = 1
        else:
            D4W_UDMactive = 0
        self.module.setParameterValue("D4W_UDMactive", str(D4W_UDMactive))
        
        if self.ui.D4W_STMactive_check.isChecked() == 1:
            D4W_STMactive = 1
        else:
            D4W_STMactive = 0
        self.module.setParameterValue("D4W_STMactive", str(D4W_STMactive))
        
        if self.ui.D4W_EVMactive_check.isChecked() == 1:
            D4W_EVMactive = 1
        else:
            D4W_EVMactive = 0
        self.module.setParameterValue("D4W_EVMactive", str(D4W_EVMactive))
        
        if self.ui.WEF_loc_famhouse_check.isChecked() == 1:
            WEF_loc_famhouse = 1
        else:
            WEF_loc_famhouse = 0
        self.module.setParameterValue("WEF_loc_famhouse", str(WEF_loc_famhouse))
        
        if self.ui.WEF_loc_apart_check.isChecked() == 1:
            WEF_loc_apart = 1
        else:
            WEF_loc_apart = 0
        self.module.setParameterValue("WEF_loc_apart", str(WEF_loc_apart))
        
        if self.ui.WEF_loc_nonres_check.isChecked() == 1:
            WEF_loc_nonres = 1
        else:
            WEF_loc_nonres = 0
        self.module.setParameterValue("WEF_loc_nonres", str(WEF_loc_nonres))
        
        if self.ui.WEF_radio_medflow.isChecked() == True:
            WEF_flow_method = "M"
        elif self.ui.WEF_radio_stochflow.isChecked() == True:
            WEF_flow_method = "S"
        self.module.setParameterValue("WEF_flow_method", WEF_flow_method)
        
        #--- ## --- REGIONAL INFORMATION---------------------------------------#
        regioncity_matrix = ["Adelaide", "Brisbane", "Melbourne", "Perth", "Sydney"]
        
        regioncity_index = self.ui.regioncity_combo.currentIndex()
        regioncity = regioncity_matrix[regioncity_index]
        self.module.setParameterValue("regioncity", regioncity)
        
        
        ################################
        #Select Evaluation Criteria Tab
        ################################ 
        
        #-------- Evaluation Metrics Select------------------------------------#
        if self.ui.mca_scoringmat_check.isChecked() == 1:
            scoringmatrix_default = 1
        else:
            scoringmatrix_default = 0
        self.module.setParameterValue("scoringmatrix_default", str(scoringmatrix_default))
        
        scoringmatrix_path = str(self.ui.mca_scoringmat_box.text())
        self.module.setParameterValue("scoringmatrix_path", scoringmatrix_path)
        
        #-------- Customize Evaluation Criteria--------------------------------#
        if self.ui.bottomlines_tech_check.isChecked() == 1:
            bottomlines_tech = 1
        else:
            bottomlines_tech = 0
        self.module.setParameterValue("bottomlines_tech", str(bottomlines_tech))

        if self.ui.bottomlines_env_check.isChecked() == 1:
            bottomlines_env = 1
        else:
            bottomlines_env = 0
        self.module.setParameterValue("bottomlines_env", str(bottomlines_env))

        if self.ui.bottomlines_ecn_check.isChecked() == 1:
            bottomlines_ecn = 1
        else:
            bottomlines_ecn = 0
        self.module.setParameterValue("bottomlines_ecn", str(bottomlines_ecn))
        
        if self.ui.bottomlines_soc_check.isChecked() == 1:
            bottomlines_soc = 1
        else:
            bottomlines_soc = 0
        self.module.setParameterValue("bottomlines_soc", str(bottomlines_soc))

        bottomlines_tech_n = str(self.ui.bottomlines_techN_spin.value())
        self.module.setParameterValue("bottomlines_tech_n", bottomlines_tech_n)

        bottomlines_env_n = str(self.ui.bottomlines_envN_spin.value())
        self.module.setParameterValue("bottomlines_env_n", bottomlines_env_n)

        bottomlines_ecn_n = str(self.ui.bottomlines_ecnN_spin.value())
        self.module.setParameterValue("bottomlines_ecn_n", bottomlines_ecn_n)
        
        bottomlines_soc_n = str(self.ui.bottomlines_socN_spin.value())
        self.module.setParameterValue("bottomlines_soc_n", bottomlines_soc_n)
        
        bottomlines_tech_w = str(self.ui.bottomlines_techW_spin.value())
        self.module.setParameterValue("bottomlines_tech_w", bottomlines_tech_w)

        bottomlines_env_w = str(self.ui.bottomlines_envW_spin.value())
        self.module.setParameterValue("bottomlines_env_w", bottomlines_env_w)

        bottomlines_ecn_w = str(self.ui.bottomlines_ecnW_spin.value())
        self.module.setParameterValue("bottomlines_ecn_w", bottomlines_ecn_w)
        
        bottomlines_soc_w = str(self.ui.bottomlines_socW_spin.value())
        self.module.setParameterValue("bottomlines_soc_w", bottomlines_soc_w)

        #-------- EVALUATION SCOPE & METHOD -----------------------------------#
        score_method_matrix = ["WPM", "WSM"]
        score_index = self.ui.eval_method_combo.currentIndex()
        score_method = score_method_matrix[score_index]
        self.module.setParameterValue("score_method", score_method)
    
        if self.ui.scope_stoch_check.isChecked() == 1:
            scope_stoch = 1
        else:
            scope_stoch = 0
        self.module.setParameterValue("scope_stoch", str(scope_stoch))
        
        if self.ui.radioScoreAvg.isChecked() == True:
            ingroup_scoring = "Avg"
        if self.ui.radioScoreMed.isChecked() == True:
            ingroup_scoring = "Med"
        if self.ui.radioScoreMin.isChecked() == True:
            ingroup_scoring = "Min"
        if self.ui.radioScoreMax.isChecked() == True:
            ingroup_scoring = "Max"
        self.module.setParameterValue("ingroup_scoring", ingroup_scoring)

        #-------- RANKING OF STRATEGIES ---------------------------------------#
        rank_method_matrix = ["RK", "CI"]
        rank_index = self.ui.top_score_combo.currentIndex()
        ranktype = rank_method_matrix[rank_index]
        self.module.setParameterValue("ranktype", ranktype)
        
        topranklimit = str(self.ui.top_rank_spin.value())
        self.module.setParameterValue("topranklimit", topranklimit)
        
        conf_int = str(self.ui.top_CI_spin.value())
        self.module.setParameterValue("conf_int", conf_int)