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
from PyQt4 import QtCore, QtGui
#from pyvibe import *
from pydynamind import *
from techimplementgui import Ui_TechImplement_Dialog

class activatetechimplementGUI(QtGui.QDialog):
    def __init__(self, m, parent=None):
        self.module = Module
        self.module = m
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_TechImplement_Dialog()
        self.ui.setupUi(self)
        
        #Set all default parameters contained in the module file into the GUI's fields
        
        #RULES AT DIFFERENT SCALES
        if self.module.getParameterAsString("dynamic_rule") == "B":
            self.ui.implementdynamics_combo.setCurrentIndex(0)
        elif self.module.getParameterAsString("dynamic_rule") == "P":
            self.ui.implementdynamics_combo.setCurrentIndex(1)
        
        self.ui.block_dev_threshold.setValue(float(self.module.getParameterAsString("block_based_thresh")))
        
        if self.module.getParameterAsString("bb_lot_rule") == "AMAP":
            self.ui.lot_amap_radio.setChecked(1)
        elif self.module.getParameterAsString("bb_lot_rule") == "STRICT":
            self.ui.lot_strict_radio.setChecked(1)
        
        if self.module.getParameterAsString("bb_street_zone") == "1":
            self.ui.street_forceimplement_check.setChecked(1)
        else:
            self.ui.street_forceimplement_check.setChecked(0)
        
        if self.module.getParameterAsString("bb_neigh_zone") == "1":
            self.ui.neigh_forceimplement_check.setChecked(1)
        else:
            self.ui.neigh_forceimplement_check.setChecked(0)
        
        if self.module.getParameterAsString("pb_lot_rule") == "G":
            self.ui.parcel_rule_lot.setCurrentIndex(0)
        elif self.module.getParameterAsString("pb_lot_rule") == "I":
            self.ui.parcel_rule_lot.setCurrentIndex(1)
        elif self.module.getParameterAsString("pb_lot_rule") == "D":
            self.ui.parcel_rule_lot.setCurrentIndex(2)
        
        if self.module.getParameterAsString("pb_street_rule") == "G":
            self.ui.parcel_rule_street.setCurrentIndex(0)
        elif self.module.getParameterAsString("pb_street_rule") == "I":
            self.ui.parcel_rule_street.setCurrentIndex(1)
        elif self.module.getParameterAsString("pb_street_rule") == "D":
            self.ui.parcel_rule_street.setCurrentIndex(2)
        
        if self.module.getParameterAsString("pb_neigh_rule") == "G":
            self.ui.parcel_rule_neigh.setCurrentIndex(0)
        elif self.module.getParameterAsString("pb_neigh_rule") == "I":
            self.ui.parcel_rule_neigh.setCurrentIndex(1)
        elif self.module.getParameterAsString("pb_neigh_rule") == "D":
            self.ui.parcel_rule_neigh.setCurrentIndex(2)
        
        if self.module.getParameterAsString("pb_neigh_zone_ignore") == "1":
            self.ui.parcel_rule_neigh_check.setChecked(1)
        else:
            self.ui.parcel_rule_neigh_check.setChecked(0)
        
        if self.module.getParameterAsString("prec_rule") == "G":
            self.ui.prec_impl_rule.setCurrentIndex(0)
        elif self.module.getParameterAsString("prec_rule") == "I":
            self.ui.prec_impl_rule.setCurrentIndex(1)
        elif self.module.getParameterAsString("prec_rule") == "D":
            self.ui.prec_impl_rule.setCurrentIndex(2)
        
        if self.module.getParameterAsString("prec_zone_ignore") == "1":
            self.ui.prec_impl_force_check.setChecked(1)
        else:
            self.ui.prec_impl_force_check.setChecked(0)
        
        if self.module.getParameterAsString("prec_dev_threshold") == "1":
            self.ui.prec_impl_thresh_check.setChecked(1)
            self.ui.prec_impl_thresh_spin.setEnabled(1)
        else:
            self.ui.prec_impl_thresh_check.setChecked(0)
            self.ui.prec_impl_thresh_spin.setEnabled(0)
    
        self.ui.prec_impl_thresh_spin.setValue(float(self.module.getParameterAsString("prec_dev_percent")))
        
        #DRIVERS
        if self.module.getParameterAsString("driver_people") == "1":
            self.ui.peoplepref_check.setChecked(1)
        else:
            self.ui.peoplepref_check.setChecked(0)
    
        if self.module.getParameterAsString("driver_legal") == "1":
            self.ui.legal_check.setChecked(1)
        else:
            self.ui.legal_check.setChecked(0)
        
        if self.module.getParameterAsString("driver_establish") == "1":
            self.ui.establish_check.setChecked(1)
        else:
            self.ui.establish_check.setChecked(0)
            
        QtCore.QObject.connect(self.ui.prec_impl_thresh_check, QtCore.SIGNAL("clicked()"), self.prec_threshold_enable)
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.save_values)
    
    
    def prec_threshold_enable(self):
        if self.ui.prec_impl_thresh_check.isChecked() == 1:
            self.ui.prec_impl_thresh_spin.setEnabled(1)
        else:
            self.ui.prec_impl_thresh_spin.setEnabled(0)
    
    
    def save_values(self):
        
        #RULES AT ALL SCALES
        dynamic_rule_matrix = ["B", "P"]
        dynamic_rule_index = self.ui.implementdynamics_combo.currentIndex()
        dynamic_rule = dynamic_rule_matrix[dynamic_rule_index]
        self.module.setParameterValue("dynamic_rule", dynamic_rule)
        
        block_based_thresh = str(self.ui.block_dev_threshold.value())
        self.module.setParameterValue("block_based_thresh", block_based_thresh)
        
        if self.ui.lot_amap_radio.isChecked() == 1:
            bb_lot_rule = "AMAP"
        elif self.ui.lot_strict_radio.isChecked() == 1:
            bb_lot_rule = "STRICT"
        self.module.setParameterValue("bb_lot_rule", str(bb_lot_rule))
        
        if self.ui.street_forceimplement_check.isChecked() == 1:
            bb_street_zone = 1
        else:
            bb_street_zone = 0
        self.module.setParameterValue("bb_street_zone", str(bb_street_zone))
        
        if self.ui.neigh_forceimplement_check.isChecked() == 1:
            bb_neigh_zone = 1
        else:
            bb_neigh_zone = 0
        self.module.setParameterValue("bb_neigh_zone", str(bb_neigh_zone))
        
        rules_matrix = ["G", "I", "D"]
        
        lot_rule_index = self.ui.parcel_rule_lot.currentIndex()
        street_rule_index = self.ui.parcel_rule_street.currentIndex()
        neigh_rule_index = self.ui.parcel_rule_neigh.currentIndex()
        prec_rule_index = self.ui.prec_impl_rule.currentIndex()
        
        pb_lot_rule = rules_matrix[lot_rule_index]
        pb_street_rule = rules_matrix[street_rule_index]
        pb_neigh_rule = rules_matrix[neigh_rule_index]
        prec_rule = rules_matrix[prec_rule_index]
        
        self.module.setParameterValue("pb_lot_rule", pb_lot_rule)
        self.module.setParameterValue("pb_street_rule", pb_street_rule)
        self.module.setParameterValue("pb_neigh_rule", pb_neigh_rule)
        self.module.setParameterValue("prec_rule", prec_rule)
        
        if self.ui.parcel_rule_neigh_check.isChecked() == 1:
            pb_neigh_zone_ignore = 1
        else:
            pb_neigh_zone_ignore = 0
        self.module.setParameterValue("pb_neigh_zone_ignore", str(pb_neigh_zone_ignore))
        
        if self.ui.prec_impl_force_check.isChecked() == 1:
            prec_zone_ignore = 1
        else:
            prec_zone_ignore = 0
        self.module.setParameterValue("prec_zone_ignore", str(prec_zone_ignore))
        
        if self.ui.prec_impl_thresh_check.isChecked() == 1:
            prec_dev_threshold = 1
        else:
            prec_dev_threshold = 0
        self.module.setParameterValue("prec_dev_threshold", str(prec_dev_threshold))
        
        prec_dev_percent = str(self.ui.prec_impl_thresh_spin.value())
        self.module.setParameterValue("prec_dev_percent", prec_dev_percent)
        
        #DRIVERS
        if self.ui.peoplepref_check.isChecked() == 1:
            driver_people = 1
        else:
            driver_people = 0
        self.module.setParameterValue("driver_people", str(driver_people))
        
        if self.ui.legal_check.isChecked() == 1:
            driver_legal = 1
        else:
            driver_legal = 0
        self.module.setParameterValue("driver_legal", str(driver_legal))
        
        if self.ui.establish_check.isChecked() == 1:
            driver_establish = 1
        else:
            driver_establish = 0
        self.module.setParameterValue("driver_establish", str(driver_establish))
        
        
        
        
    
