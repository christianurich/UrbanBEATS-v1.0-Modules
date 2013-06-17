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
from urbplanbbgui import Ui_BuildingBlockDialog

class activateurbplanbbGUI(QtGui.QDialog):
    def __init__(self, m, parent=None):
        self.module = Module
        self.module = m
        QtGui.QDialog.__init__(self, parent)
        self.ui = Ui_BuildingBlockDialog()
        self.ui.setupUi(self)
        
        #Assign Default Values & Connect Signal/Slots
        
        ##########################
        #General Rules Tab
        ##########################
        #--> General City Structure
        if self.module.getParameterAsString("cityarchetype") == "MC":
            self.ui.citymono_radio.setChecked(1)
        elif self.module.getParameterAsString("cityarchetype") == "PC":
            self.ui.citypoly_radio.setChecked(1)
        
        self.ui.citysprawl_spin.setValue(float(self.module.getParameterAsString("citysprawl")))
        self.ui.mun_localmap_check.setChecked(bool(self.module.getParameterAsString("locality_mun_trans")))
        
        #--> Decision Variables for Block Dynamics
        if self.module.getParameterAsString("lucredev") == "1":
            self.ui.lucredevelop_check.setChecked(1)
            self.ui.lucredevelop_spin.setEnabled(1)
        else:
            self.ui.lucredevelop_check.setChecked(0)
            self.ui.lucredevelop_spin.setEnabled(0)
            
        if self.module.getParameterAsString("popredev") == "1":
            self.ui.popredevelop_check.setChecked(1)
            self.ui.popredevelop_spin.setEnabled(1)
        else:
            self.ui.popredevelop_check.setChecked(0)
            self.ui.popredevelop_spin.setEnabled(0)
            
        if self.module.getParameterAsString("noredev") == "1":
            self.ui.noredevelop_check.setChecked(1)
            self.ui.lucredevelop_check.setEnabled(0)
            self.ui.lucredevelop_spin.setEnabled(0)
            self.ui.popredevelop_check.setEnabled(0)
            self.ui.popredevelop_spin.setEnabled(0)
        else:
            self.ui.noredevelop_check.setChecked(0)
            self.ui.lucredevelop_check.setEnabled(1)
            if self.ui.lucredevelop_check.isChecked() == 1:
                self.ui.lucredevelop_spin.setEnabled(1)
            else:
                self.ui.lucredevelop_spin.setEnabled(0)
            
            self.ui.popredevelop_check.setEnabled(1)
            if self.ui.popredevelop_check.isChecked() == 1:
                self.ui.popredevelop_spin.setEnabled(1)
            else:
                self.ui.popredevelop_spin.setEnabled(0)
            
        self.ui.lucredevelop_spin.setValue(int(self.module.getParameterAsString("lucredev_thresh")))
        self.ui.popredevelop_spin.setValue(int(self.module.getParameterAsString("popredev_thresh")))
        
        QtCore.QObject.connect(self.ui.lucredevelop_check, QtCore.SIGNAL("clicked()"), self.enableReDevThresh)
        QtCore.QObject.connect(self.ui.popredevelop_check, QtCore.SIGNAL("clicked()"), self.enableReDevThresh)
        QtCore.QObject.connect(self.ui.noredevelop_check, QtCore.SIGNAL("clicked()"), self.enableReDevThresh)
        
        ##########################
        #Residential Tab
        ##########################
        self.ui.occup_avg_box.setText(self.module.getParameterAsString("occup_avg"))
        self.ui.occup_max_box.setText(self.module.getParameterAsString("occup_max"))
        self.ui.person_space_box.setText(self.module.getParameterAsString("person_space"))
        self.ui.extra_comm_area_box.setText(self.module.getParameterAsString("extra_comm_area"))
        self.ui.setback_f_min_box.setText(self.module.getParameterAsString("setback_f_min"))
        self.ui.setback_f_max_box.setText(self.module.getParameterAsString("setback_f_max"))
        self.ui.setback_s_min_box.setText(self.module.getParameterAsString("setback_s_min"))
        self.ui.setback_s_max_box.setText(self.module.getParameterAsString("setback_s_max"))
        self.ui.fsetbackmed_check.setChecked(bool(int(self.module.getParameterAsString("setback_f_med"))))
        self.ui.ssetbackmed_check.setChecked(bool(int(self.module.getParameterAsString("setback_s_med"))))
        self.ui.carports_max_box.setText(self.module.getParameterAsString("carports_max"))
        self.ui.garage_incl_box.setChecked(bool(int(self.module.getParameterAsString("garage_incl"))))
        self.ui.w_driveway_min_box.setText(self.module.getParameterAsString("w_driveway_min"))
        self.ui.patio_area_max_box.setText(self.module.getParameterAsString("patio_area_max"))
        self.ui.patio_covered_box.setChecked(bool(int(self.module.getParameterAsString("patio_covered"))))
        self.ui.house_floors.setValue(int(self.module.getParameterAsString("floor_num_max")))
        self.ui.occup_flat_avg_box.setText(self.module.getParameterAsString("occup_flat_avg"))
        self.ui.indoor_com_spin.setValue(int(self.module.getParameterAsString("commspace_indoor")))
        self.ui.flat_area_max_box.setText(self.module.getParameterAsString("flat_area_max"))
        self.ui.outdoor_com_spin.setValue(int(self.module.getParameterAsString("commspace_outdoor")))
        self.ui.setback_HDR_avg_box.setText(self.module.getParameterAsString("setback_HDR_avg"))
        self.ui.aptbldg_floors.setValue(int(self.module.getParameterAsString("floor_num_HDRmax")))
        
        if self.module.getParameterAsString("parking_HDR") == "On":
            self.ui.parking_on.setChecked(1)
        elif self.module.getParameterAsString("parking_HDR") == "Off":
            self.ui.parking_off.setChecked(1)
        elif self.module.getParameterAsString("parking_HDR") == "Var":
            self.ui.parking_vary.setChecked(1)
        elif self.module.getParameterAsString("parking_HDR") == "NA":
            self.ui.parking_none.setChecked(1)
            
        self.ui.OSR_parks_include.setChecked(bool(int(self.module.getParameterAsString("park_OSR"))))
        
        if self.module.getParameterAsString("roof_connected") == "Direct":
            self.ui.roof_connected_radiodirect.setChecked(1)
        elif self.module.getParameterAsString("roof_connected") == "Disconnect":
            self.ui.roof_connected_radiodisc.setChecked(1)
        elif self.module.getParameterAsString("roof_connected") == "Vary":
            self.ui.roof_connected_radiovary.setChecked(1)
        
        self.ui.avg_imp_dced_spin.setValue(int(self.module.getParameterAsString("imperv_prop_dced")))
        
        ##########################
        #Non-Residential Tab
        ##########################
        #--> Employment Details
        if self.module.getParameterAsString("employment_mode") == "I":
            self.ui.jobs_direct_radio.setChecked(1)
            self.ui.jobs_define_stack.setCurrentIndex(0)
        elif self.module.getParameterAsString("employment_mode") == "D":
            self.ui.jobs_dist_radio.setChecked(1)
            self.ui.jobs_define_stack.setCurrentIndex(1)
        elif self.module.getParameterAsString("employment_mode") == "S":
            self.ui.jobs_total_radio.setChecked(1)
            self.ui.jobs_define_stack.setCurrentIndex(2)
        
        self.ui.dist_ind_spin.setValue(int(self.module.getParameterAsString("ind_edist")))
        self.ui.dist_com_spin.setValue(int(self.module.getParameterAsString("com_edist")))
        self.ui.dist_orc_spin.setValue(int(self.module.getParameterAsString("orc_edist")))
        self.ui.totjobs_box.setText(self.module.getParameterAsString("employment_total"))
        
        QtCore.QObject.connect(self.ui.jobs_direct_radio, QtCore.SIGNAL("clicked()"), self.employment_pagechange)
        QtCore.QObject.connect(self.ui.jobs_dist_radio, QtCore.SIGNAL("clicked()"), self.employment_pagechange)
        QtCore.QObject.connect(self.ui.jobs_total_radio, QtCore.SIGNAL("clicked()"), self.employment_pagechange)
        
        #-->Land Subdivision & Site Layout
        self.ui.ind_subd_min.setText(self.module.getParameterAsString("ind_subd_min"))
        self.ui.ind_subd_max.setText(self.module.getParameterAsString("ind_subd_max"))
        self.ui.com_subd_min.setText(self.module.getParameterAsString("com_subd_min"))
        self.ui.com_subd_max.setText(self.module.getParameterAsString("com_subd_max"))
        
        self.ui.nres_setback_box.setText(self.module.getParameterAsString("nres_minfsetback"))
        self.ui.nres_setback_auto.setChecked(bool(int(self.module.getParameterAsString("nres_setback_auto"))))
        self.ui.nres_maxfloors_spin.setValue(int(self.module.getParameterAsString("nres_maxfloors")))
        
        if self.module.getParameterAsString("nres_setback_auto") == "1":
            self.ui.nres_setback_auto.setChecked(1)
            self.ui.nres_setback_box.setEnabled(0)
        else:
            self.ui.nres_setback_auto.setChecked(0)
            self.ui.nres_setback_box.setEnabled(1)
        
        QtCore.QObject.connect(self.ui.nres_setback_auto, QtCore.SIGNAL("clicked()"), self.nres_minfsetback_check)
        
        if self.module.getParameterAsString("nres_nolimit_floors") == "1":
            self.ui.nres_maxfloors_nolimit.setChecked(1)
            self.ui.nres_maxfloors_spin.setEnabled(0)
        else:
            self.ui.nres_maxfloors_nolimit.setChecked(0)
            self.ui.nres_maxfloors_spin.setEnabled(1)
        
        QtCore.QObject.connect(self.ui.nres_maxfloors_nolimit, QtCore.SIGNAL("clicked()"), self.nres_floors_check)
        
        self.ui.plotratio_ind_box.setText(str(float(self.module.getParameterAsString("maxplotratio_ind"))/100))
        self.ui.plotratio_ind_slider.setValue(int(self.module.getParameterAsString("maxplotratio_ind")))
        QtCore.QObject.connect(self.ui.plotratio_ind_slider, QtCore.SIGNAL("valueChanged(int)"), self.plotratio_ind_update)
        
        self.ui.plotratio_com_box.setText(str(float(self.module.getParameterAsString("maxplotratio_com"))/100))
        self.ui.plotratio_com_slider.setValue(int(self.module.getParameterAsString("maxplotratio_com")))
        QtCore.QObject.connect(self.ui.plotratio_com_slider, QtCore.SIGNAL("valueChanged(int)"), self.plotratio_com_update)
        
        #--> Car Parking and Loading Bay
        self.ui.carpark_dimW_box.setText(self.module.getParameterAsString("carpark_Wmin"))
        self.ui.carpark_dimD_box.setText(self.module.getParameterAsString("carpark_Dmin"))
        self.ui.carpark_imp_spin.setValue(int(self.module.getParameterAsString("carpark_imp")))
        self.ui.carpark_ind_box.setText(self.module.getParameterAsString("carpark_ind"))
        self.ui.carpark_com_box.setText(self.module.getParameterAsString("carpark_com"))
        self.ui.loadingbay_box.setText(self.module.getParameterAsString("loadingbay_A"))
       
        #--> Landscaping & Drainage
        self.ui.lscape_hsbalance_slide.setValue(int(self.module.getParameterAsString("lscape_hsbalance")))
        self.ui.lscape_impdced_spin.setValue(int(self.module.getParameterAsString("lscape_impdced")))
        
        #--> Municipal Facilities
        if self.module.getParameterAsString("mun_explicit") == "1":
            self.ui.civ_consider_check.setChecked(1)
            self.ui.edu_school_box.setEnabled(1)
            self.ui.edu_uni_box.setEnabled(1)
            self.ui.edu_lib_box.setEnabled(1)
            self.ui.civ_hospital_box.setEnabled(1)
            self.ui.civ_clinic_box.setEnabled(1)
            self.ui.civ_police_box.setEnabled(1)
            self.ui.civ_fire_box.setEnabled(1)
            self.ui.civ_jail_box.setEnabled(1)
            self.ui.civ_religion_box.setEnabled(1)
            self.ui.civ_leisure_box.setEnabled(1)
            self.ui.civ_museum_box.setEnabled(1)
            self.ui.civ_zoo_box.setEnabled(1)
            self.ui.civ_sports_box.setEnabled(1)
            self.ui.civ_race_box.setEnabled(1)
            self.ui.civ_dead_box.setEnabled(1)
        else:
            self.ui.civ_consider_check.setChecked(0)
            self.ui.edu_school_box.setEnabled(0)
            self.ui.edu_uni_box.setEnabled(0)
            self.ui.edu_lib_box.setEnabled(0)
            self.ui.civ_hospital_box.setEnabled(0)
            self.ui.civ_clinic_box.setEnabled(0)
            self.ui.civ_police_box.setEnabled(0)
            self.ui.civ_fire_box.setEnabled(0)
            self.ui.civ_jail_box.setEnabled(0)
            self.ui.civ_religion_box.setEnabled(0)
            self.ui.civ_leisure_box.setEnabled(0)
            self.ui.civ_museum_box.setEnabled(0)
            self.ui.civ_zoo_box.setEnabled(0)
            self.ui.civ_sports_box.setEnabled(0)
            self.ui.civ_race_box.setEnabled(0)
            self.ui.civ_dead_box.setEnabled(0)
        QtCore.QObject.connect(self.ui.civ_consider_check, QtCore.SIGNAL("clicked()"), self.mun_on_off_enable)
                
        self.ui.edu_school_box.setChecked(bool(int(self.module.getParameterAsString("edu_school"))))
        self.ui.edu_uni_box.setChecked(bool(int(self.module.getParameterAsString("edu_uni"))))
        self.ui.edu_lib_box.setChecked(bool(int(self.module.getParameterAsString("edu_lib"))))
        self.ui.civ_hospital_box.setChecked(bool(int(self.module.getParameterAsString("civ_hospital"))))
        self.ui.civ_clinic_box.setChecked(bool(int(self.module.getParameterAsString("civ_clinic"))))
        self.ui.civ_police_box.setChecked(bool(int(self.module.getParameterAsString("civ_police"))))
        self.ui.civ_fire_box.setChecked(bool(int(self.module.getParameterAsString("civ_fire"))))
        self.ui.civ_jail_box.setChecked(bool(int(self.module.getParameterAsString("civ_jail"))))
        self.ui.civ_religion_box.setChecked(bool(int(self.module.getParameterAsString("civ_worship"))))
        self.ui.civ_leisure_box.setChecked(bool(int(self.module.getParameterAsString("civ_leisure"))))
        self.ui.civ_museum_box.setChecked(bool(int(self.module.getParameterAsString("civ_museum"))))
        self.ui.civ_zoo_box.setChecked(bool(int(self.module.getParameterAsString("civ_zoo"))))
        self.ui.civ_sports_box.setChecked(bool(int(self.module.getParameterAsString("civ_stadium"))))
        self.ui.civ_race_box.setChecked(bool(int(self.module.getParameterAsString("civ_racing"))))
        self.ui.civ_dead_box.setChecked(bool(int(self.module.getParameterAsString("civ_cemetery"))))
        
        ##########################
        #Transport Tab
        ##########################        
        #--> Frontage & Pedestrian Information
        self.ui.w_resfootpath_min_box.setText(self.module.getParameterAsString("res_fpwmin"))
        self.ui.w_resfootpath_max_box.setText(self.module.getParameterAsString("res_fpwmax"))
        self.ui.w_resnaturestrip_min_box.setText(self.module.getParameterAsString("res_nswmin"))
        self.ui.w_resnaturestrip_max_box.setText(self.module.getParameterAsString("res_nswmax"))
        self.ui.w_resfootpath_med_check.setChecked(bool(int(self.module.getParameterAsString("res_fpmed"))))
        self.ui.w_resnaturestrip_med_check.setChecked(bool(int(self.module.getParameterAsString("res_nsmed"))))

        self.ui.w_comfootpath_min_box.setText(self.module.getParameterAsString("nres_fpwmin"))
        self.ui.w_comfootpath_max_box.setText(self.module.getParameterAsString("nres_fpwmax"))
        self.ui.w_comnaturestrip_min_box.setText(self.module.getParameterAsString("nres_nswmin"))
        self.ui.w_comnaturestrip_max_box.setText(self.module.getParameterAsString("nres_nswmax"))
        self.ui.w_comfootpath_med_check.setChecked(bool(int(self.module.getParameterAsString("nres_fpmed"))))
        self.ui.w_comnaturestrip_med_check.setChecked(bool(int(self.module.getParameterAsString("nres_nsmed"))))

        self.ui.w_collectlane_min_box.setText(self.module.getParameterAsString("lane_wmin"))
        self.ui.w_collectlane_max_box.setText(self.module.getParameterAsString("lane_wmax"))
        self.ui.collect_crossfall_box.setText(self.module.getParameterAsString("lane_crossfall"))
        self.ui.w_collectlane_med_check.setChecked(bool(int(self.module.getParameterAsString("lane_wmed"))))
        
        self.ui.w_arterial_min_box.setText(self.module.getParameterAsString("hwy_wlanemin"))
        self.ui.w_arterial_max_box.setText(self.module.getParameterAsString("hwy_wlanemax"))
        self.ui.w_arterialmed_minbox.setText(self.module.getParameterAsString("hwy_wmedianmin"))
        self.ui.w_arterialmed_maxbox.setText(self.module.getParameterAsString("hwy_wmedianmax"))
        self.ui.w_arterialsh_minbox.setText(self.module.getParameterAsString("hwy_wbufmin"))
        self.ui.w_arterialsh_maxbox.setText(self.module.getParameterAsString("hwy_wbufmax"))
        self.ui.w_arterial_med_check.setChecked(bool(int(self.module.getParameterAsString("hwy_lanemed"))))
        self.ui.w_arterialmed_med_check.setChecked(bool(int(self.module.getParameterAsString("hwy_medmed"))))
        self.ui.w_arterialsh_med_check.setChecked(bool(int(self.module.getParameterAsString("hwy_bufmed"))))
        self.ui.arterial_crossfall_box.setText(self.module.getParameterAsString("hwy_crossfall"))
        self.ui.w_arterialmed_nodev_check.setChecked(bool(int(self.module.getParameterAsString("hwy_restrict"))))
        self.ui.highway_buffer_check.setChecked(bool(int(self.module.getParameterAsString("hwy_buffer"))))

        #--> Other Transport
        if self.module.getParameterAsString("considerTRFacilities") == "1":
            self.ui.trans_on_off_check.setChecked(1)
            self.ui.trans_airport_box.setEnabled(1)
            self.ui.trans_seaport_box.setEnabled(1)
            self.ui.trans_busdepot_box.setEnabled(1)
            self.ui.trans_rail_box.setEnabled(1)
        else:
            self.ui.trans_on_off_check.setChecked(0)
            self.ui.trans_airport_box.setEnabled(0)
            self.ui.trans_seaport_box.setEnabled(0)
            self.ui.trans_busdepot_box.setEnabled(0)
            self.ui.trans_rail_box.setEnabled(0)
        QtCore.QObject.connect(self.ui.trans_on_off_check, QtCore.SIGNAL("clicked()"), self.trans_on_off_enable)
        
        self.ui.trans_airport_box.setChecked(bool(int(self.module.getParameterAsString("trans_airport"))))
        self.ui.trans_seaport_box.setChecked(bool(int(self.module.getParameterAsString("trans_seaport"))))
        self.ui.trans_busdepot_box.setChecked(bool(int(self.module.getParameterAsString("trans_busdepot"))))
        self.ui.trans_rail_box.setChecked(bool(int(self.module.getParameterAsString("trans_railterminal"))))
        
        ##########################
        #Open Space Tab
        ##########################
        #--> Parks, Squares and Gardens
        self.ui.pg_ggratio_slide.setValue(int(self.module.getParameterAsString("pg_greengrey_ratio")))
        self.ui.pg_ggratio_box.setText(self.module.getParameterAsString("pg_greengrey_ratio"))
        QtCore.QObject.connect(self.ui.pg_ggratio_slide, QtCore.SIGNAL("valueChanged(int)"), self.ggratio_update)
        #CONNECT GREYGREEN SLIDER TO TEXTBOX
        
        if self.module.getParameterAsString("pgsq_distribution") == "C":
            self.ui.pg_dist_mix_radio.setChecked(1)
        elif self.module.getParameterAsString("pgsq_distribution") == "S":
            self.ui.pg_dist_sep_radio.setChecked(1)
        
        self.ui.pg_usable_spin.setValue(int(self.module.getParameterAsString("pg_unused_space")))
        self.ui.pg_usable_prohibit.setChecked(bool(int(self.module.getParameterAsString("pg_restrict"))))
        
        #--> Reserves & Floodways
        if self.module.getParameterAsString("ref_usable") == "1":
            self.ui.ref_usable_check.setChecked(1)
            self.ui.ref_usable_spin.setEnabled(1)
        else:
            self.ui.ref_usable_check.setChecked(0)
            self.ui.ref_usable_spin.setEnabled(0)
        
        self.ui.ref_usable_spin.setValue(int(self.module.getParameterAsString("ref_usable_percent")))
        
        QtCore.QObject.connect(self.ui.ref_usable_check, QtCore.SIGNAL("clicked()"), self.ref_usable_update)
        
        self.ui.ref_limit_check.setChecked(bool(int(self.module.getParameterAsString("ref_limit_stormwater"))))
        
        #--> Services & Utilities
        svu_water = self.module.getParameterAsString("svu_water")
        svu_nonwater = 100 - int(svu_water)
        self.ui.svu_wat_box.setText(str(svu_water))
        self.ui.svu_nonwat_box.setText(str(svu_nonwater))
        
        self.ui.svu_slider.setValue(int(svu_water))
        QtCore.QObject.connect(self.ui.svu_slider, QtCore.SIGNAL("valueChanged(int)"), self.svu_slider_update)
        
        if self.module.getParameterAsString("svu4supply") == "1":
            self.ui.svu_supply_check.setChecked(1)
            self.ui.svu_supply_spin.setEnabled(1)
        else:
            self.ui.svu_supply_check.setChecked(0)
            self.ui.svu_supply_spin.setEnabled(0)
            
        if self.module.getParameterAsString("svu4waste") == "1":
            self.ui.svu_waste_check.setChecked(1)
            self.ui.svu_waste_spin.setEnabled(1)
        else:
            self.ui.svu_waste_check.setChecked(0)
            self.ui.svu_waste_spin.setEnabled(0)
        
        if self.module.getParameterAsString("svu4storm") == "1":
            self.ui.svu_storm_check.setChecked(1)
            self.ui.svu_storm_spin.setEnabled(1)
        else:
            self.ui.svu_storm_check.setChecked(0)
            self.ui.svu_storm_spin.setEnabled(0)
        
        self.ui.svu_supply_spin.setValue(int(self.module.getParameterAsString("svu4supply_prop")))
        self.ui.svu_waste_spin.setValue(int(self.module.getParameterAsString("svu4waste_prop")))
        self.ui.svu_storm_spin.setValue(int(self.module.getParameterAsString("svu4storm_prop")))
        
        QtCore.QObject.connect(self.ui.svu_supply_check, QtCore.SIGNAL("clicked()"), self.svu_supply_update)
        QtCore.QObject.connect(self.ui.svu_waste_check, QtCore.SIGNAL("clicked()"), self.svu_waste_update)
        QtCore.QObject.connect(self.ui.svu_storm_check, QtCore.SIGNAL("clicked()"), self.svu_storm_update)
        
        ##########################
        #Others Tab
        ##########################
        #--> Unclassified Land
        if self.module.getParameterAsString("unc_merge") == "1":
            self.ui.unc_merge_check.setChecked(1)
            self.ui.unc_merge2ref_check.setEnabled(1)
            self.ui.unc_merge2pg_check.setEnabled(1)
            self.ui.unc_merge2trans_check.setEnabled(1)
            self.ui.unc_merge2ref_spin.setEnabled(1)
            self.ui.unc_merge2pg_spin.setEnabled(1)
            self.ui.unc_merge2trans_spin.setEnabled(1)
        else:
            self.ui.unc_merge_check.setChecked(0)
            self.ui.unc_merge2ref_check.setEnabled(0)
            self.ui.unc_merge2pg_check.setEnabled(0)
            self.ui.unc_merge2trans_check.setEnabled(0)
            self.ui.unc_merge2ref_spin.setEnabled(0)
            self.ui.unc_merge2pg_spin.setEnabled(0)
            self.ui.unc_merge2trans_spin.setEnabled(0)
        QtCore.QObject.connect(self.ui.unc_merge_check, QtCore.SIGNAL("clicked()"), self.unc_merge_enable)
        
        if self.module.getParameterAsString("unc_pgmerge") == "1":
            self.ui.unc_merge2pg_check.setChecked(1)
        else:
            self.ui.unc_merge2pg_check.setChecked(0)
            self.ui.unc_merge2pg_spin.setEnabled(0)
        QtCore.QObject.connect(self.ui.unc_merge2pg_check, QtCore.SIGNAL("clicked()"), self.unc_merge2pg_enable)
        
        if self.module.getParameterAsString("unc_refmerge") == "1":
            self.ui.unc_merge2ref_check.setChecked(1)
        else:
            self.ui.unc_merge2ref_check.setChecked(0)
            self.ui.unc_merge2ref_spin.setEnabled(0)
        QtCore.QObject.connect(self.ui.unc_merge2ref_check, QtCore.SIGNAL("clicked()"), self.unc_merge2ref_enable)
        
        if self.module.getParameterAsString("unc_rdmerge") == "1":
            self.ui.unc_merge2trans_check.setChecked(1)
        else:
            self.ui.unc_merge2trans_check.setChecked(0)
            self.ui.unc_merge2trans_spin.setEnabled(0)
        QtCore.QObject.connect(self.ui.unc_merge2trans_check, QtCore.SIGNAL("clicked()"), self.unc_merge2trans_enable)
        
        self.ui.unc_merge2ref_spin.setValue(float(self.module.getParameterAsString("unc_refmerge_w")))
        self.ui.unc_merge2pg_spin.setValue(float(self.module.getParameterAsString("unc_pgmerge_w")))
        self.ui.unc_merge2trans_spin.setValue(float(self.module.getParameterAsString("unc_rdmerge_w")))
        
        if self.module.getParameterAsString("unc_custom") == "1":
            self.ui.unc_custom_check.setChecked(1)
            self.ui.unc_areathresh_spin.setEnabled(1)
            self.ui.unc_customimp_spin.setEnabled(1)
            self.ui.unc_customirrigate_check.setEnabled(1)
        else:
            self.ui.unc_custom_check.setChecked(0)
            self.ui.unc_areathresh_spin.setEnabled(0)
            self.ui.unc_customimp_spin.setEnabled(0)
            self.ui.unc_customirrigate_check.setEnabled(0)
        QtCore.QObject.connect(self.ui.unc_custom_check, QtCore.SIGNAL("clicked()"), self.unc_custom_check_enable)
        
        self.ui.unc_areathresh_spin.setValue(float(self.module.getParameterAsString("unc_customthresh")))
        self.ui.unc_customimp_spin.setValue(float(self.module.getParameterAsString("unc_customimp")))
        
        if self.module.getParameterAsString("unc_landirrigate") == "1":
            self.ui.unc_customirrigate_check.setChecked(1)
        else:
            self.ui.unc_customirrigate_check.setChecked(0)
        
        #--> Undeveloped
        if self.module.getParameterAsString("und_state") == "M":
            self.ui.und_statemanual_radio.setChecked(1)
            self.ui.und_statemanual_combo.setEnabled(1)
        elif self.module.getParameterAsString("und_state") == "A":
            self.ui.und_stateauto_radio.setChecked(1)
            self.ui.und_statemanual_combo.setEnabled(0)
        
        self.undev_matrix = ["GF", "BF", "AG"]
        undev_type = self.module.getParameterAsString("und_type_manual")
        undevindex = self.undev_matrix.index(undev_type)
        self.ui.und_statemanual_combo.setCurrentIndex(int(undevindex))
        
        QtCore.QObject.connect(self.ui.und_statemanual_radio, QtCore.SIGNAL("clicked()"), self.und_typeEnable)
        QtCore.QObject.connect(self.ui.und_stateauto_radio, QtCore.SIGNAL("clicked()"), self.und_typeEnable)
        
        self.ui.und_allowdev_check.setChecked(bool(int(self.module.getParameterAsString("und_allowdev"))))
        
        #CONNECT DETAILS WITH THE OK BUTTON SO THAT GUI UPDATES MODULE
        QtCore.QObject.connect(self.ui.buttonBox, QtCore.SIGNAL("accepted()"), self.save_values)
        
        
    ###############################
    #   Update functions          #
    ###############################
    
    #--> GENERAL TAB
    def enableReDevThresh(self):
        if self.ui.lucredevelop_check.isChecked() == 1:
            self.ui.lucredevelop_spin.setEnabled(1)
        else:
            self.ui.lucredevelop_spin.setEnabled(0)
        
        if self.ui.popredevelop_check.isChecked() == 1:
            self.ui.popredevelop_spin.setEnabled(1)
        else:
            self.ui.popredevelop_spin.setEnabled(0)
        
        if self.ui.noredevelop_check.isChecked() == 1:
            self.ui.lucredevelop_check.setEnabled(0)
            self.ui.lucredevelop_spin.setEnabled(0)
            self.ui.popredevelop_check.setEnabled(0)
            self.ui.popredevelop_spin.setEnabled(0)
        else:
            self.ui.lucredevelop_check.setEnabled(1)
            if self.ui.lucredevelop_check.isChecked() == 1:
                self.ui.lucredevelop_spin.setEnabled(1)
            else:
                self.ui.lucredevelop_spin.setEnabled(0)
            
            self.ui.popredevelop_check.setEnabled(1)
            if self.ui.popredevelop_check.isChecked() == 1:
                self.ui.popredevelop_spin.setEnabled(1)
            else:
                self.ui.popredevelop_spin.setEnabled(0)
            
    #--> NON-RESIDENTIAL TAB
    def employment_pagechange(self):
        if self.ui.jobs_direct_radio.isChecked() == 1:
            self.ui.jobs_define_stack.setCurrentIndex(0)
        elif self.ui.jobs_dist_radio.isChecked() == 1:
            self.ui.jobs_define_stack.setCurrentIndex(1)
        elif self.ui.jobs_total_radio.isChecked() == 1:
            self.ui.jobs_define_stack.setCurrentIndex(2)
    
    def nres_minfsetback_check(self):
        if self.ui.nres_setback_auto.isChecked() == 1:
            self.ui.nres_setback_box.setEnabled(0)
        else:
            self.ui.nres_setback_box.setEnabled(1)
    
    def nres_floors_check(self):
        if self.ui.nres_maxfloors_nolimit.isChecked() == 1:
            self.ui.nres_maxfloors_spin.setEnabled(0)
        else:
            self.ui.nres_maxfloors_spin.setEnabled(1)
    
    def plotratio_ind_update(self, currentValue):
        self.ui.plotratio_ind_box.setText(str(float(currentValue)/100))
    
    def plotratio_com_update(self, currentValue):
        self.ui.plotratio_com_box.setText(str(float(currentValue)/100))
    
    def mun_on_off_enable(self):
        if self.ui.civ_consider_check.isChecked() == 1:
            self.ui.edu_school_box.setEnabled(1)
            self.ui.edu_uni_box.setEnabled(1)
            self.ui.edu_lib_box.setEnabled(1)
            self.ui.civ_hospital_box.setEnabled(1)
            self.ui.civ_clinic_box.setEnabled(1)
            self.ui.civ_police_box.setEnabled(1)
            self.ui.civ_fire_box.setEnabled(1)
            self.ui.civ_jail_box.setEnabled(1)
            self.ui.civ_religion_box.setEnabled(1)
            self.ui.civ_leisure_box.setEnabled(1)
            self.ui.civ_museum_box.setEnabled(1)
            self.ui.civ_zoo_box.setEnabled(1)
            self.ui.civ_sports_box.setEnabled(1)
            self.ui.civ_race_box.setEnabled(1)
            self.ui.civ_dead_box.setEnabled(1)
        else:
            self.ui.edu_school_box.setEnabled(0)
            self.ui.edu_uni_box.setEnabled(0)
            self.ui.edu_lib_box.setEnabled(0)
            self.ui.civ_hospital_box.setEnabled(0)
            self.ui.civ_clinic_box.setEnabled(0)
            self.ui.civ_police_box.setEnabled(0)
            self.ui.civ_fire_box.setEnabled(0)
            self.ui.civ_jail_box.setEnabled(0)
            self.ui.civ_religion_box.setEnabled(0)
            self.ui.civ_leisure_box.setEnabled(0)
            self.ui.civ_museum_box.setEnabled(0)
            self.ui.civ_zoo_box.setEnabled(0)
            self.ui.civ_sports_box.setEnabled(0)
            self.ui.civ_race_box.setEnabled(0)
            self.ui.civ_dead_box.setEnabled(0)
    
    #--> TRANSPORT TAB
    def trans_on_off_enable(self):
        if self.ui.trans_on_off_check.isChecked() == 1:
            self.ui.trans_airport_box.setEnabled(1)
            self.ui.trans_seaport_box.setEnabled(1)
            self.ui.trans_busdepot_box.setEnabled(1)
            self.ui.trans_rail_box.setEnabled(1)
        else:
            self.ui.trans_airport_box.setEnabled(0)
            self.ui.trans_seaport_box.setEnabled(0)
            self.ui.trans_busdepot_box.setEnabled(0)
            self.ui.trans_rail_box.setEnabled(0)
        
    #--> OPEN SPACE TAB
    def ggratio_update(self, currentValue):
        self.ui.pg_ggratio_box.setText(str(currentValue))

    def ref_usable_update(self):
        if self.ui.ref_usable_check.isChecked() == 1:
            self.ui.ref_usable_spin.setEnabled(1)
        else:
            self.ui.ref_usable_spin.setEnabled(0)

    def svu_slider_update(self, currentValue):
        self.ui.svu_wat_box.setText(str(currentValue))
        self.ui.svu_nonwat_box.setText(str(100-currentValue))
        
    def svu_supply_update(self):
        if self.ui.svu_supply_check.isChecked() == 1:
            self.ui.svu_supply_spin.setEnabled(1)
        else:
            self.ui.svu_supply_spin.setEnabled(0)
    
    def svu_waste_update(self):
        if self.ui.svu_waste_check.isChecked() == 1:
            self.ui.svu_waste_spin.setEnabled(1)
        else:
            self.ui.svu_waste_spin.setEnabled(0)
    
    def svu_storm_update(self):
        if self.ui.svu_storm_check.isChecked() == 1:
            self.ui.svu_storm_spin.setEnabled(1)
        else:
            self.ui.svu_storm_spin.setEnabled(0)        

    #--> OTHERS TAB
    def unc_merge_enable(self):
        if self.ui.unc_merge_check.isChecked() == 1:
            self.ui.unc_merge2ref_check.setEnabled(1)
            self.ui.unc_merge2pg_check.setEnabled(1)
            self.ui.unc_merge2trans_check.setEnabled(1)
            self.unc_merge2ref_enable()
            self.unc_merge2pg_enable()
            self.unc_merge2trans_enable()
        else:
            self.ui.unc_merge2ref_check.setEnabled(0)
            self.ui.unc_merge2pg_check.setEnabled(0)
            self.ui.unc_merge2trans_check.setEnabled(0)
            self.ui.unc_merge2ref_spin.setEnabled(0)
            self.ui.unc_merge2pg_spin.setEnabled(0)
            self.ui.unc_merge2trans_spin.setEnabled(0)
        
    def unc_merge2ref_enable(self):
        if self.ui.unc_merge2ref_check.isChecked() == 1:
            self.ui.unc_merge2ref_spin.setEnabled(1)
        else:
            self.ui.unc_merge2ref_spin.setEnabled(0)
        
    def unc_merge2pg_enable(self):
        if self.ui.unc_merge2pg_check.isChecked() == 1:
            self.ui.unc_merge2pg_spin.setEnabled(1)
        else:
            self.ui.unc_merge2pg_spin.setEnabled(0)
        
    def unc_merge2trans_enable(self):
        if self.ui.unc_merge2trans_check.isChecked() == 1:
            self.ui.unc_merge2trans_spin.setEnabled(1)
        else:
            self.ui.unc_merge2trans_spin.setEnabled(0)
    
    def unc_custom_check_enable(self):
        if self.ui.unc_custom_check.isChecked() == 1:
            self.ui.unc_areathresh_spin.setEnabled(1)
            self.ui.unc_customimp_spin.setEnabled(1)
            self.ui.unc_customirrigate_check.setEnabled(1)
        else:
            self.ui.unc_areathresh_spin.setEnabled(0)
            self.ui.unc_customimp_spin.setEnabled(0)
            self.ui.unc_customirrigate_check.setEnabled(0) 
    
    def und_typeEnable(self):
        if self.ui.und_statemanual_radio.isChecked() == 1:
            self.ui.und_statemanual_combo.setEnabled(1)
        else:
            self.ui.und_statemanual_combo.setEnabled(0)
        
    #################################
    # OK Button/Cancel Button Click # 
    #################################     
      
    def save_values(self):
        ffp_matrix = ["PO", "NP", "RW", "SW", "GW"]
        ##########################
        #General Rules Tab
        ##########################
        #-->General City Structure
        if self.ui.citymono_radio.isChecked() == 1:
            self.module.setParameterValue("cityarchetype", "MC")
        elif self.ui.citypoly_radio.isChecked() == 1:
            self.module.setParameterValue("cityarchetype", "PC")
        
        self.module.setParameterValue("citysprawl", str(self.ui.citysprawl_spin.value()))
        if self.ui.mun_localmap_check.isChecked() == 1:
            locality_mun_trans = 1
        else:
            locality_mun_trans = 0
        self.module.setParameterValue("locality_mun_trans", str(locality_mun_trans))
        
        #building block dynamics parameters
        self.module.setParameterValue("lucredev", str(int(self.ui.lucredevelop_check.isChecked())))
        self.module.setParameterValue("popredev", str(int(self.ui.popredevelop_check.isChecked())))
        self.module.setParameterValue("lucredev_thresh", str(self.ui.lucredevelop_spin.value()))
        self.module.setParameterValue("popredev_thresh", str(self.ui.popredevelop_spin.value()))
        self.module.setParameterValue("noredev", str(int(self.ui.noredevelop_check.isChecked())))
            
        ##########################
        #Residential Tab
        ##########################
        self.module.setParameterValue("occup_avg", str(self.ui.occup_avg_box.text()))
        self.module.setParameterValue("occup_max", str(self.ui.occup_max_box.text()))
        self.module.setParameterValue("person_space", str(self.ui.person_space_box.text()))
        self.module.setParameterValue("extra_comm_area", str(self.ui.extra_comm_area_box.text()))
        self.module.setParameterValue("setback_f_min", str(self.ui.setback_f_min_box.text()))
        self.module.setParameterValue("setback_f_max", str(self.ui.setback_f_max_box.text()))
        self.module.setParameterValue("setback_s_min", str(self.ui.setback_s_min_box.text()))
        self.module.setParameterValue("setback_s_max", str(self.ui.setback_s_max_box.text()))
        self.module.setParameterValue("setback_f_med", str(int(self.ui.fsetbackmed_check.isChecked())))
        self.module.setParameterValue("setback_s_med", str(int(self.ui.ssetbackmed_check.isChecked())))
        self.module.setParameterValue("carports_max", str(self.ui.carports_max_box.text()))
        self.module.setParameterValue("garage_incl", str(int(self.ui.garage_incl_box.isChecked())))
        self.module.setParameterValue("w_driveway_min", str(self.ui.w_driveway_min_box.text()))
        self.module.setParameterValue("patio_area_max", str(self.ui.patio_area_max_box.text()))
        self.module.setParameterValue("patio_covered", str(int(self.ui.patio_covered_box.isChecked())))
        self.module.setParameterValue("floor_num_max", str(self.ui.house_floors.value()))
        self.module.setParameterValue("occup_flat_avg", str(self.ui.occup_flat_avg_box.text()))
        self.module.setParameterValue("commspace_indoor", str(self.ui.indoor_com_spin.value()))
        self.module.setParameterValue("flat_area_max", str(self.ui.flat_area_max_box.text()))
        self.module.setParameterValue("commspace_outdoor", str(self.ui.outdoor_com_spin.value()))
        self.module.setParameterValue("setback_HDR_avg", str(self.ui.setback_HDR_avg_box.text()))
        self.module.setParameterValue("floor_num_HDRmax", str(self.ui.aptbldg_floors.value()))

        if self.ui.parking_on.isChecked() == 1:
            self.module.setParameterValue("parking_HDR", "On")
        elif self.ui.parking_off.isChecked() == 1:
            self.module.setParameterValue("parking_HDR", "Off")
        elif self.ui.parking_vary.isChecked() == 1:
            self.module.setParameterValue("parking_HDR", "Var")
        elif self.ui.parking_none.isChecked() == 1:
            self.module.setParameterValue("parking_HDR", "NA")
        
        self.module.setParameterValue("park_OSR", str(int(self.ui.OSR_parks_include.isChecked())))

        if self.ui.roof_connected_radiodirect.isChecked() == True:
            self.module.setParameterValue("roof_connected", "Direct")
        if self.ui.roof_connected_radiodisc.isChecked() == True:
            self.module.setParameterValue("roof_connected", "Disconnect")
        if self.ui.roof_connected_radiovary.isChecked() == True:
            self.module.setParameterValue("roof_connected", "Vary")
        
        self.module.setParameterValue("imperv_prop_dced", str(int(self.ui.avg_imp_dced_spin.value())))
        
        ##########################
        #Non-Residential Tab
        ##########################
        #--> Employment Details
        if self.ui.jobs_direct_radio.isChecked() == True:
            self.module.setParameterValue("employment_mode", "I")
        if self.ui.jobs_dist_radio.isChecked() == True:
            self.module.setParameterValue("employment_mode", "D")
        if self.ui.jobs_total_radio.isChecked() == True:
            self.module.setParameterValue("employment_mode", "S")
        
        self.module.setParameterValue("ind_edist", str(self.ui.dist_ind_spin.value()))
        self.module.setParameterValue("com_edist", str(self.ui.dist_com_spin.value()))
        self.module.setParameterValue("orc_edist", str(self.ui.dist_orc_spin.value()))
        self.module.setParameterValue("employment_total", str(self.ui.totjobs_box.text()))
        
        #--> Land Subdivision & Site Layout
        self.module.setParameterValue("ind_subd_min", str(self.ui.ind_subd_min.text()))
        self.module.setParameterValue("ind_subd_max", str(self.ui.ind_subd_max.text()))
        self.module.setParameterValue("com_subd_min", str(self.ui.com_subd_min.text()))
        self.module.setParameterValue("com_subd_max", str(self.ui.com_subd_max.text()))
        
        self.module.setParameterValue("nres_minfsetback", str(self.ui.nres_setback_box.text()))
        self.module.setParameterValue("nres_maxfloors", str(self.ui.nres_maxfloors_spin.value()))
        self.module.setParameterValue("nres_setback_auto", str(int(self.ui.nres_setback_auto.isChecked())))
        self.module.setParameterValue("nres_nolimit_floors", str(int(self.ui.nres_maxfloors_nolimit.isChecked())))
        
        self.module.setParameterValue("maxplotratio_ind", str(self.ui.plotratio_ind_slider.value()))
        self.module.setParameterValue("maxplotratio_com", str(self.ui.plotratio_com_slider.value()))
        
        #--> Car Parking and Loading Bay
        self.module.setParameterValue("carpark_Wmin", str(self.ui.carpark_dimW_box.text()))
        self.module.setParameterValue("carpark_Dmin", str(self.ui.carpark_dimD_box.text()))
        self.module.setParameterValue("carpark_imp", str(self.ui.carpark_imp_spin.value()))
        self.module.setParameterValue("carpark_ind", str(self.ui.carpark_ind_box.text()))
        self.module.setParameterValue("carpark_com", str(self.ui.carpark_com_box.text()))
        self.module.setParameterValue("loadingbay_A", str(self.ui.loadingbay_box.text()))
        
        #--> Landscaping & Drainage
        lscape_hsbalance = str(self.ui.lscape_hsbalance_slide.value())
        self.module.setParameterValue("lscape_hsbalance", lscape_hsbalance)
        
        lscape_impdced = str(self.ui.lscape_impdced_spin.value())
        self.module.setParameterValue("lscape_impdced", lscape_impdced)

        #--> Municipal Facilities
        self.module.setParameterValue("mun_explicit", str(int(self.ui.civ_consider_check.isChecked())))
        self.module.setParameterValue("edu_school", str(int(self.ui.edu_school_box.isChecked())))
        self.module.setParameterValue("edu_uni", str(int(self.ui.edu_uni_box.isChecked())))
        self.module.setParameterValue("edu_lib", str(int(self.ui.edu_lib_box.isChecked())))
        self.module.setParameterValue("civ_hospital", str(int(self.ui.civ_hospital_box.isChecked())))
        self.module.setParameterValue("civ_clinic", str(int(self.ui.civ_clinic_box.isChecked())))
        self.module.setParameterValue("civ_police", str(int(self.ui.civ_police_box.isChecked())))
        self.module.setParameterValue("civ_fire", str(int(self.ui.civ_fire_box.isChecked())))
        self.module.setParameterValue("civ_jail", str(int(self.ui.civ_jail_box.isChecked())))
        self.module.setParameterValue("civ_worship", str(int(self.ui.civ_religion_box.isChecked())))
        self.module.setParameterValue("civ_leisure", str(int(self.ui.civ_leisure_box.isChecked())))
        self.module.setParameterValue("civ_museum", str(int(self.ui.civ_museum_box.isChecked())))
        self.module.setParameterValue("civ_zoo", str(int(self.ui.civ_zoo_box.isChecked())))
        self.module.setParameterValue("civ_stadium", str(int(self.ui.civ_sports_box.isChecked())))
        self.module.setParameterValue("civ_racing", str(int(self.ui.civ_race_box.isChecked())))
        self.module.setParameterValue("civ_cemetery", str(int(self.ui.civ_dead_box.isChecked())))
        
        ##########################
        #Transport Tab
        ##########################
        #--> Frontage & Pedestrian Information
        self.module.setParameterValue("res_fpwmin", str(self.ui.w_resfootpath_min_box.text()))
        self.module.setParameterValue("res_fpwmax", str(self.ui.w_resfootpath_max_box.text()))
        self.module.setParameterValue("res_fpmed", str(int(self.ui.w_resfootpath_med_check.isChecked())))
        self.module.setParameterValue("res_nswmin", str(self.ui.w_resnaturestrip_min_box.text()))
        self.module.setParameterValue("res_nswmax", str(self.ui.w_resnaturestrip_max_box.text()))
        self.module.setParameterValue("res_nsmed", str(int(self.ui.w_resnaturestrip_med_check.isChecked())))
        
        self.module.setParameterValue("nres_fpwmin", str(self.ui.w_comfootpath_min_box.text()))
        self.module.setParameterValue("nres_fpwmax", str(self.ui.w_comfootpath_max_box.text()))
        self.module.setParameterValue("nres_fpmed", str(int(self.ui.w_comfootpath_med_check.isChecked())))
        self.module.setParameterValue("nres_nswmin", str(self.ui.w_comnaturestrip_min_box.text()))
        self.module.setParameterValue("nres_nswmax", str(self.ui.w_comnaturestrip_max_box.text()))
        self.module.setParameterValue("nres_nsmed", str(int(self.ui.w_comnaturestrip_med_check.isChecked())))
        
        self.module.setParameterValue("lane_wmin", str(self.ui.w_collectlane_min_box.text()))
        self.module.setParameterValue("lane_wmax", str(self.ui.w_collectlane_max_box.text()))
        self.module.setParameterValue("lane_wmed", str(int(self.ui.w_collectlane_med_check.isChecked())))
        self.module.setParameterValue("lane_crossfall", str(self.ui.collect_crossfall_box.text()))
        
        self.module.setParameterValue("hwy_wlanemin", str(self.ui.w_arterial_min_box.text()))
        self.module.setParameterValue("hwy_wlanemax", str(self.ui.w_arterial_max_box.text()))
        self.module.setParameterValue("hwy_lanemed", str(int(self.ui.w_arterial_med_check.isChecked())))
        self.module.setParameterValue("hwy_wmedianmin", str(self.ui.w_arterialmed_minbox.text()))
        self.module.setParameterValue("hwy_wmedianmax", str(self.ui.w_arterialmed_maxbox.text()))
        self.module.setParameterValue("hwy_medmed", str(int(self.ui.w_arterialmed_med_check.isChecked())))
        self.module.setParameterValue("hwy_wbufmin", str(self.ui.w_arterialsh_minbox.text()))
        self.module.setParameterValue("hwy_wbufmax", str(self.ui.w_arterialsh_maxbox.text()))
        self.module.setParameterValue("hwy_bufmed", str(int(self.ui.w_arterialsh_med_check.isChecked())))
        self.module.setParameterValue("hwy_crossfall", str(self.ui.arterial_crossfall_box.text()))
        self.module.setParameterValue("hwy_restrict", str(int(self.ui.w_arterialmed_nodev_check.isChecked())))
        self.module.setParameterValue("hwy_buffer", str(int(self.ui.highway_buffer_check.isChecked())))
        
        #--> Other Transportation
        self.module.setParameterValue("considerTRFacilities", str(int(self.ui.trans_on_off_check.isChecked())))
        self.module.setParameterValue("trans_airport", str(int(self.ui.trans_airport_box.isChecked())))
        self.module.setParameterValue("trans_seaport", str(int(self.ui.trans_seaport_box.isChecked())))
        self.module.setParameterValue("trans_busdepot", str(int(self.ui.trans_busdepot_box.isChecked())))
        self.module.setParameterValue("trans_railterminal", str(int(self.ui.trans_rail_box.isChecked())))
        
        ##########################
        #Open Space Tab
        ##########################
        #--> Parks, Squares & Gardens
        self.module.setParameterValue("pg_greengrey_ratio", str(self.ui.pg_ggratio_slide.value()))
        if self.ui.pg_dist_mix_radio.isChecked() == 1:
            self.module.setParameterValue("pgsq_distribution", "C")
        if self.ui.pg_dist_sep_radio.isChecked() == 1:
            self.module.setParameterValue("pgsq_distribution", "S")
        
        self.module.setParameterValue("pg_unused_space", str(self.ui.pg_usable_spin.value()))
        self.module.setParameterValue("pg_restrict", str(int(self.ui.pg_usable_prohibit.isChecked())))
        
        #--> Reserves & Floodways
        self.module.setParameterValue("ref_usable", str(int(self.ui.ref_usable_check.isChecked())))
        self.module.setParameterValue("ref_usable_percent", str(self.ui.ref_usable_spin.value()))
        self.module.setParameterValue("ref_limit_stormwater", str(int(self.ui.ref_limit_check.isChecked())))
        
        #--> Services & Utilities
        self.module.setParameterValue("svu_water", str(self.ui.svu_wat_box.text()))
        self.module.setParameterValue("svu4supply", str(int(self.ui.svu_supply_check.isChecked())))
        self.module.setParameterValue("svu4waste", str(int(self.ui.svu_waste_check.isChecked())))
        self.module.setParameterValue("svu4storm", str(int(self.ui.svu_storm_check.isChecked())))
        self.module.setParameterValue("svu4supply_prop", str(self.ui.svu_supply_spin.value()))
        self.module.setParameterValue("svu4waste_prop", str(self.ui.svu_waste_spin.value()))
        self.module.setParameterValue("svu4storm_prop", str(self.ui.svu_storm_spin.value()))
        
        ##########################
        #Others Tab
        ##########################
        #--> Unclassified
        self.module.setParameterValue("unc_merge", str(int(self.ui.unc_merge_check.isChecked())))
        self.module.setParameterValue("unc_refmerge", str(int(self.ui.unc_merge2ref_check.isChecked())))
        self.module.setParameterValue("unc_pgmerge", str(int(self.ui.unc_merge2pg_check.isChecked())))
        self.module.setParameterValue("unc_rdmerge", str(int(self.ui.unc_merge2trans_check.isChecked())))
        self.module.setParameterValue("unc_pgmerge_w", str(self.ui.unc_merge2pg_spin.value()))
        self.module.setParameterValue("unc_refmerge_w", str(self.ui.unc_merge2ref_spin.value()))
        self.module.setParameterValue("unc_rdmerge_w", str(self.ui.unc_merge2trans_spin.value()))
        self.module.setParameterValue("unc_custom", str(int(self.ui.unc_custom_check.isChecked())))
        self.module.setParameterValue("unc_customthresh", str(self.ui.unc_areathresh_spin.value()))
        self.module.setParameterValue("unc_customimp", str(self.ui.unc_customimp_spin.value()))
        self.module.setParameterValue("unc_landirrigate", str(int(self.ui.unc_customirrigate_check.isChecked())))
        
        #--> Undeveloped
        if self.ui.und_statemanual_radio.isChecked() == True:
            und_state = "M"
        if self.ui.und_stateauto_radio.isChecked() == True:
            und_state = "A"
        self.module.setParameterValue("und_state", und_state)
        
        undev_type = self.undev_matrix[self.ui.und_statemanual_combo.currentIndex()]
        self.module.setParameterValue("und_type_manual", undev_type)
        
        self.module.setParameterValue("und_allowdev", str(int(self.ui.und_allowdev_check.isChecked())))
        
        #----------------END OF SAVE VALUES------------------------------------#