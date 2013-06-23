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
from osgeo import ogr, osr
import os
from pydynamind import *
from pydmtoolbox import *

class ExportToGISShapeFile(Module):
    """A Custom Export Module for UrbanBEATS Maps that exports the required
    maps selected by the user to shapefiles
    
    @ingroup UrbanBEATS
    @author Peter M Bach
    """
    
    def __init__(self):
        Module.__init__(self)
        
        #PARAMETER LIST
        self.createParameter("FileName", STRING, "")
        self.createParameter("Directory", STRING, "")
        self.createParameter("Projection", STRING, "")
        self.createParameter("OffsetX", DOUBLE, "")
        self.createParameter("OffsetY", DOUBLE, "")
        self.FileName = ""
        self.Directory = "C:/"
        self.Projection = "+proj=utm +zone=55 +south +ellps=WGS84 +datum=WGS84 +units=m +no_defs +towgs84=0,0,0"
        self.OffsetX = 313420.7405
        self.OffsetY = 5807211.478
        
        #Maps to export
        self.createParameter("BuildingBlocks", BOOL, "")
        self.createParameter("PatchData", BOOL, "")
        self.createParameter("FlowPaths", BOOL, "")
        self.createParameter("Localities", BOOL, "")
        self.createParameter("PlannedWSUD", BOOL, "")
        self.createParameter("ImplementedWSUD", BOOL, "")
        self.createParameter("BlockCentres", BOOL, "")
        self.BuildingBlocks = True
        self.PatchData = False
        self.FlowPaths = False
        self.Localities = False
        self.PlannedWSUD = False
        self.ImplementedWSUD = False
        self.BlockCentres = False
        
        #VIEWS
        self.mapattributes = View("GlobalMapAttributes", COMPONENT, READ)            
        self.block = View("Block", FACE, READ)
        self.patch = View("Patch", FACE, READ)
        self.network = View("Network", EDGE, READ)
        self.blocklocality = View("BlockLocality", NODE, READ)
        self.blocknodes = View("BlockNodes", NODE, READ)
        self.wsudAttr = View("WsudAttr", COMPONENT, READ)
        
        datastream = []
        datastream.append(self.mapattributes)
        datastream.append(self.block)
        datastream.append(self.patch)
        datastream.append(self.network)
        datastream.append(self.blocklocality)
        datastream.append(self.blocknodes)
        datastream.append(self.wsudAttr)
        
        self.addData("City", datastream)
        
    def run(self):
        os.chdir(self.Directory)
        if self.BuildingBlocks:
            print "Exporting Blocks"
            self.exportBuildingBlocks()
        if self.PatchData:
            print "Exporting Patch Data"
            self.exportPatchData()
        if self.FlowPaths:
            print "Exporting Flow Paths"
            self.exportFlowPaths()
        if self.Localities:
            print "Exporting Block Localities"
            self.exportBlockLocalities()
        if self.PlannedWSUD:
            print "Exporting WSUD Planned"
            self.exportPlannedWSUD()
        if self.ImplementWSUD:
            print "Exporting WSUD Implemented"
            self.exportImplementWSUD()
        if self.BlockCentres:
            print "Exporting Block Centres"
            self.exportBlockCentre()
        
        
    def exportBuildingBlocks(self):
        city = self.getData("City")
        
        strvec = city.getUUIDsOfComponentsInView(self.mapattributes)
        map_attr = city.getComponent(strvec[0])		#blockcityin.getAttributes("MapAttributes")   #Get map attributes
        
        spatialRef = osr.SpatialReference()                #Define Spatial Reference
        spatialRef.ImportFromProj4(self.Projection)
        
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(str(self.FileName+"_Blocks.shp")): os.remove(self.FileName+"_Blocks.shp")
        shapefile = driver.CreateDataSource(self.FileName+"_Blocks.shp")
        
        layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbPolygon)
        layerDefinition = layer.GetLayerDefn()
        
        #DEFINE ATTRIBUTES
        fielddefmatrix = []
            #>>> FROM DELINBLOCKS
        fielddefmatrix.append(ogr.FieldDefn("BlockID", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("BasinID", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("LocateX", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LocateY", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("CentreX", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("CentreY", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("OriginX", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("OriginY", ogr.OFTReal))             
        fielddefmatrix.append(ogr.FieldDefn("Status", ogr.OFTInteger))         
        fielddefmatrix.append(ogr.FieldDefn("Active", ogr.OFTReal))            
        fielddefmatrix.append(ogr.FieldDefn("Nhd_N", ogr.OFTInteger))          
        fielddefmatrix.append(ogr.FieldDefn("Nhd_S", ogr.OFTInteger))          
        fielddefmatrix.append(ogr.FieldDefn("Nhd_W", ogr.OFTInteger))          
        fielddefmatrix.append(ogr.FieldDefn("Nhd_E", ogr.OFTInteger))          
        fielddefmatrix.append(ogr.FieldDefn("Nhd_NE", ogr.OFTInteger))         
        fielddefmatrix.append(ogr.FieldDefn("Nhd_NW", ogr.OFTInteger))         
        fielddefmatrix.append(ogr.FieldDefn("Nhd_SE", ogr.OFTInteger))         
        fielddefmatrix.append(ogr.FieldDefn("Nhd_SW", ogr.OFTInteger))         
        fielddefmatrix.append(ogr.FieldDefn("Soil_k", ogr.OFTReal))            
        fielddefmatrix.append(ogr.FieldDefn("AvgElev", ogr.OFTReal))           
        fielddefmatrix.append(ogr.FieldDefn("pLU_RES", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_COM", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_ORC", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_LI", ogr.OFTReal)) 
        fielddefmatrix.append(ogr.FieldDefn("pLU_HI", ogr.OFTReal)) 
        fielddefmatrix.append(ogr.FieldDefn("pLU_CIV", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_SVU", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_RD", ogr.OFTReal)) 
        fielddefmatrix.append(ogr.FieldDefn("pLU_TR", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_PG", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_REF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_UND", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("pLU_NA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Pop", ogr.OFTReal))
        
        if map_attr.getAttribute("include_employment").getDouble(): fielddefmatrix.append(ogr.FieldDefn("Employ", ogr.OFTReal)) 
        if map_attr.getAttribute("include_groundwater").getDouble(): fielddefmatrix.append(ogr.FieldDefn("GWDepth", ogr.OFTReal))
        if map_attr.getAttribute("include_soc_par1").getDouble(): fielddefmatrix.append(ogr.FieldDefn("SocPar1", ogr.OFTReal))
        if map_attr.getAttribute("include_soc_par2").getDouble(): fielddefmatrix.append(ogr.FieldDefn("SocPar2", ogr.OFTReal))
        if map_attr.getAttribute("include_plan_map").getDouble(): fielddefmatrix.append(ogr.FieldDefn("PM_RES", ogr.OFTReal))
        if map_attr.getAttribute("include_plan_map").getDouble(): fielddefmatrix.append(ogr.FieldDefn("PM_COM", ogr.OFTReal))
        if map_attr.getAttribute("include_plan_map").getDouble(): fielddefmatrix.append(ogr.FieldDefn("PM_LI", ogr.OFTReal))
        if map_attr.getAttribute("include_plan_map").getDouble(): fielddefmatrix.append(ogr.FieldDefn("PM_HI", ogr.OFTReal))
        if map_attr.getAttribute("include_rivers").getDouble(): fielddefmatrix.append(ogr.FieldDefn("HasRiv", ogr.OFTReal))
        if map_attr.getAttribute("include_lakes").getDouble(): fielddefmatrix.append(ogr.FieldDefn("HasLake", ogr.OFTReal))
        if map_attr.getAttribute("include_lakes").getDouble(): fielddefmatrix.append(ogr.FieldDefn("LakeAr", ogr.OFTReal))
        if map_attr.getAttribute("include_local_map").getDouble(): fielddefmatrix.append(ogr.FieldDefn("HasLoc", ogr.OFTReal))
        if map_attr.getAttribute("include_local_map").getDouble(): fielddefmatrix.append(ogr.FieldDefn("NFacil", ogr.OFTReal))
        if map_attr.getAttribute("patchdelin").getDouble(): fielddefmatrix.append(ogr.FieldDefn("Patches", ogr.OFTInteger))                                          
        if map_attr.getAttribute("spatialmetrics").getDouble(): fielddefmatrix.append(ogr.FieldDefn("Rich", ogr.OFTReal))            
        if map_attr.getAttribute("spatialmetrics").getDouble(): fielddefmatrix.append(ogr.FieldDefn("ShDIV", ogr.OFTReal))           
        if map_attr.getAttribute("spatialmetrics").getDouble(): fielddefmatrix.append(ogr.FieldDefn("ShDOM", ogr.OFTReal))           
        if map_attr.getAttribute("spatialmetrics").getDouble(): fielddefmatrix.append(ogr.FieldDefn("ShEVEN", ogr.OFTReal))          
        
        fielddefmatrix.append(ogr.FieldDefn("downID", ogr.OFTReal))          
        fielddefmatrix.append(ogr.FieldDefn("maxdZ", ogr.OFTReal))           
        fielddefmatrix.append(ogr.FieldDefn("slope", ogr.OFTReal))           
        fielddefmatrix.append(ogr.FieldDefn("drainID", ogr.OFTReal))         
        fielddefmatrix.append(ogr.FieldDefn("h_pond", ogr.OFTReal))          
        fielddefmatrix.append(ogr.FieldDefn("Outlet", ogr.OFTInteger))          

        if map_attr.getAttribute("considerCBD").getDouble(): fielddefmatrix.append(ogr.FieldDefn("CBDdist", ogr.OFTReal))          
        if map_attr.getAttribute("considerCBD").getDouble(): fielddefmatrix.append(ogr.FieldDefn("CBDdir", ogr.OFTReal))         
        
            #>>> FROM URBPLANBB
        fielddefmatrix.append(ogr.FieldDefn("MiscAtot", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("UndType", ogr.OFTString))
        fielddefmatrix.append(ogr.FieldDefn("UND_av", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("OpenSpace", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("AGardens", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ASquare", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("PG_av", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("REF_av", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ANonW_Utils", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("SVU_avWS", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("SVU_avWW", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("SVU_avSW", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("SVU_avOTH", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("RoadTIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ParkBuffer", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("RD_av", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("RDMedW", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("DemPublicI", ogr.OFTReal))
        
        fielddefmatrix.append(ogr.FieldDefn("HouseOccup", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avSt_RES", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("WResNstrip", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResAllots", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResDWpLot", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResHouses", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResLotArea", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResRoof", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_RES", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResHFloors", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResLotTIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResLotEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResGarden", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ResRoofCon", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDRFlats", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDRRoofA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDROccup", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDR_TIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDR_EIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDRFloors", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("av_HDRes", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDRGarden", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HDRCarPark", ogr.OFTReal))
        
        fielddefmatrix.append(ogr.FieldDefn("LIjobs", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIestates", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avSt_LI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAfront", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAfrEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAestate", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeBldg", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIFloors", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeLoad", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeCPark", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_LI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeLgrey", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("LIAeTIA", ogr.OFTReal))
        
        fielddefmatrix.append(ogr.FieldDefn("HIjobs", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIestates", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avSt_HI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAfront", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAfrEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAestate", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeBldg", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIFloors", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeLoad", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeCPark", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_HI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeLgrey", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("HIAeTIA", ogr.OFTReal))
        
        fielddefmatrix.append(ogr.FieldDefn("COMjobs", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMestates", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avSt_COM", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAfront", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAfrEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAestate", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeBldg", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMFloors", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeLoad", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeCPark", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_COM", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeLgrey", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("COMAeTIA", ogr.OFTReal))
        
        fielddefmatrix.append(ogr.FieldDefn("ORCjobs", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCestates", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avSt_ORC", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAfront", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAfrEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAestate", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeBldg", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCFloors", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeLoad", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeCPark", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("avLt_ORC", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeLgrey", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeEIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ORCAeTIA", ogr.OFTReal))
        
        fielddefmatrix.append(ogr.FieldDefn("Blk_TIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_EIA", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_EIF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_TIF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_RoofsA", ogr.OFTReal))
        
            #>>> FROM TECHPLACEMENT
        fielddefmatrix.append(ogr.FieldDefn("wd_Rating", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_RES_K", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_RES_S", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_RES_T", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_RES_L", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_RES_IN", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_RES_OUT", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_HDR_K", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_HDR_S", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_HDR_T", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_HDR_L", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_HDR_IN", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_HDR_OUT", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_PrivIN", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_PrivOUT", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_LI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_HI", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_COM", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_ORC", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_Nres_IN", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Apub_irr", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("wd_PubOUT", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_WD", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Blk_WD_OUT", ogr.OFTReal))
        
        #Create the fields
        for field in fielddefmatrix:
            layer.CreateField(field)
            layer.GetLayerDefn()
        
        #Get Blocks View
        uuids = city.getUUIDsOfComponentsInView(self.block)
        for i in range(len(uuids)):
            currentAttList = city.getFace(uuids[i])
        
            #Draw Geometry
            line = ogr.Geometry(ogr.wkbPolygon)
            ring = ogr.Geometry(ogr.wkbLinearRing)
            nl = TBVectorData.getNodeListFromFace(city, currentAttList)
            for point in nl:
                ring.AddPoint(point.getX()+self.OffsetX, point.getY()+self.OffsetY)
            line.AddGeometry(ring)
            
            feature = ogr.Feature(layerDefinition)
            feature.SetGeometry(line)
            feature.SetFID(0)
            
            #Add Attributes
            feature.SetField("BlockID", int(currentAttList.getAttribute("BlockID").getDouble()))
            feature.SetField("BasinID", int(currentAttList.getAttribute("BasinID").getDouble()))
            feature.SetField("LocateX", currentAttList.getAttribute("LocateX").getDouble())
            feature.SetField("LocateY", currentAttList.getAttribute("LocateY").getDouble())
            feature.SetField("CentreX", currentAttList.getAttribute("CentreX").getDouble())
            feature.SetField("CentreY", currentAttList.getAttribute("CentreY").getDouble())
            feature.SetField("OriginX", currentAttList.getAttribute("OriginX").getDouble())
            feature.SetField("OriginY", currentAttList.getAttribute("OriginY").getDouble())            
            feature.SetField("Status", int(currentAttList.getAttribute("Status").getDouble()))         
            feature.SetField("Active", currentAttList.getAttribute("Active").getDouble())            
            feature.SetField("Nhd_N", int(currentAttList.getAttribute("Nhd_N").getDouble()))          
            feature.SetField("Nhd_S", int(currentAttList.getAttribute("Nhd_S").getDouble()))          
            feature.SetField("Nhd_W", int(currentAttList.getAttribute("Nhd_W").getDouble()))          
            feature.SetField("Nhd_E", int(currentAttList.getAttribute("Nhd_E").getDouble()))          
            feature.SetField("Nhd_NE", int(currentAttList.getAttribute("Nhd_NE").getDouble()))         
            feature.SetField("Nhd_NW", int(currentAttList.getAttribute("Nhd_NW").getDouble()))         
            feature.SetField("Nhd_SE", int(currentAttList.getAttribute("Nhd_SE").getDouble()))         
            feature.SetField("Nhd_SW", int(currentAttList.getAttribute("Nhd_SW").getDouble()))         
            feature.SetField("Soil_k", currentAttList.getAttribute("Soil_k").getDouble())            
            feature.SetField("AvgElev", currentAttList.getAttribute("AvgElev").getDouble())           
            feature.SetField("pLU_RES", currentAttList.getAttribute("pLU_RES").getDouble())
            feature.SetField("pLU_COM", currentAttList.getAttribute("pLU_COM").getDouble())
            feature.SetField("pLU_ORC", currentAttList.getAttribute("pLU_ORC").getDouble())
            feature.SetField("pLU_LI", currentAttList.getAttribute("pLU_LI").getDouble()) 
            feature.SetField("pLU_HI", currentAttList.getAttribute("pLU_HI").getDouble()) 
            feature.SetField("pLU_CIV", currentAttList.getAttribute("pLU_CIV").getDouble())
            feature.SetField("pLU_SVU", currentAttList.getAttribute("pLU_SVU").getDouble())
            feature.SetField("pLU_RD", currentAttList.getAttribute("pLU_RD").getDouble()) 
            feature.SetField("pLU_TR", currentAttList.getAttribute("pLU_TR").getDouble())
            feature.SetField("pLU_PG", currentAttList.getAttribute("pLU_PG").getDouble())
            feature.SetField("pLU_REF", currentAttList.getAttribute("pLU_REF").getDouble())
            feature.SetField("pLU_UND", currentAttList.getAttribute("pLU_UND").getDouble())
            feature.SetField("pLU_NA", currentAttList.getAttribute("pLU_NA").getDouble())
            feature.SetField("Pop", currentAttList.getAttribute("Pop").getDouble())           
            
            if map_attr.getAttribute("include_employment").getDouble(): feature.SetField("Employ", currentAttList.getAttribute("Employ").getDouble()) 
            if map_attr.getAttribute("include_groundwater").getDouble(): feature.SetField("GWDepth", currentAttList.getAttribute("GWDepth").getDouble())
            if map_attr.getAttribute("include_soc_par1").getDouble(): feature.SetField("SocPar1", currentAttList.getAttribute("SocPar1").getDouble())
            if map_attr.getAttribute("include_soc_par2").getDouble(): feature.SetField("SocPar2", currentAttList.getAttribute("SocPar2").getDouble())
            if map_attr.getAttribute("include_plan_map").getDouble(): feature.SetField("PM_RES", currentAttList.getAttribute("PM_RES").getDouble())
            if map_attr.getAttribute("include_plan_map").getDouble(): feature.SetField("PM_COM", currentAttList.getAttribute("PM_COM").getDouble())
            if map_attr.getAttribute("include_plan_map").getDouble(): feature.SetField("PM_LI", currentAttList.getAttribute("PM_LI").getDouble())
            if map_attr.getAttribute("include_plan_map").getDouble(): feature.SetField("PM_HI", currentAttList.getAttribute("PM_HI").getDouble())
            if map_attr.getAttribute("include_rivers").getDouble(): feature.SetField("HasRiv", currentAttList.getAttribute("HasRiv").getDouble())
            if map_attr.getAttribute("include_lakes").getDouble(): feature.SetField("HasLake", currentAttList.getAttribute("HasLake").getDouble())
            if map_attr.getAttribute("include_lakes").getDouble(): feature.SetField("LakeAr", currentAttList.getAttribute("LakeAr").getDouble())
            if map_attr.getAttribute("include_local_map").getDouble(): feature.SetField("HasLoc", currentAttList.getAttribute("HasLoc").getDouble())
            if map_attr.getAttribute("include_local_map").getDouble(): feature.SetField("NFacil", currentAttList.getAttribute("NFacil").getDouble())
            if map_attr.getAttribute("patchdelin").getDouble(): feature.SetField("Patches", currentAttList.getAttribute("Patches").getDouble())
            if map_attr.getAttribute("spatialmetrics").getDouble(): feature.SetField("Rich", currentAttList.getAttribute("Rich").getDouble())            
            if map_attr.getAttribute("spatialmetrics").getDouble(): feature.SetField("ShDIV", currentAttList.getAttribute("ShDIV").getDouble())           
            if map_attr.getAttribute("spatialmetrics").getDouble(): feature.SetField("ShDOM", currentAttList.getAttribute("ShDOM").getDouble())          
            if map_attr.getAttribute("spatialmetrics").getDouble(): feature.SetField("ShEVEN", currentAttList.getAttribute("ShEVEN").getDouble())          
            
            feature.SetField("downID", currentAttList.getAttribute("downID").getDouble())          
            feature.SetField("maxdZ", currentAttList.getAttribute("maxdZ").getDouble())           
            feature.SetField("slope", currentAttList.getAttribute("slope").getDouble())           
            feature.SetField("drainID", currentAttList.getAttribute("drainID").getDouble())         
            feature.SetField("h_pond", currentAttList.getAttribute("h_pond").getDouble())          
            feature.SetField("Outlet", int(currentAttList.getAttribute("Outlet").getDouble()))

            if map_attr.getAttribute("considerCBD").getDouble(): feature.SetField("CBDdist", currentAttList.getAttribute("CBDdist").getDouble())          
            if map_attr.getAttribute("considerCBD").getDouble(): feature.SetField("CBDdir", currentAttList.getAttribute("CBDdir").getDouble())
            
            #From Urbplanbb
            feature.SetField("MiscAtot", currentAttList.getAttribute("MiscAtot").getDouble())
            feature.SetField("UndType", currentAttList.getAttribute("UndType").getString())
            feature.SetField("UND_av", currentAttList.getAttribute("UND_av").getDouble())
            feature.SetField("OpenSpace", currentAttList.getAttribute("OpenSpace").getDouble())
            feature.SetField("AGardens", currentAttList.getAttribute("AGardens").getDouble())
            feature.SetField("ASquare", currentAttList.getAttribute("ASquare").getDouble())
            feature.SetField("PG_av", currentAttList.getAttribute("PG_av").getDouble())
            feature.SetField("REF_av", currentAttList.getAttribute("REF_av").getDouble())
            feature.SetField("ANonW_Utils", currentAttList.getAttribute("ANonW_Utils").getDouble())
            feature.SetField("SVU_avWS", currentAttList.getAttribute("SVU_avWS").getDouble())
            feature.SetField("SVU_avWW", currentAttList.getAttribute("SVU_avWW").getDouble())
            feature.SetField("SVU_avSW", currentAttList.getAttribute("SVU_avSW").getDouble())
            feature.SetField("SVU_avOTH", currentAttList.getAttribute("SVU_avOTH").getDouble())
            feature.SetField("RoadTIA", currentAttList.getAttribute("RoadTIA").getDouble())
            feature.SetField("ParkBuffer", currentAttList.getAttribute("ParkBuffer").getDouble())
            feature.SetField("RD_av", currentAttList.getAttribute("RD_av").getDouble())
            feature.SetField("RDMedW", currentAttList.getAttribute("RDMedW").getDouble())
            
            feature.SetField("HouseOccup", currentAttList.getAttribute("HouseOccup").getDouble())
            feature.SetField("avSt_RES", currentAttList.getAttribute("avSt_RES").getDouble())
            feature.SetField("WResNstrip", currentAttList.getAttribute("WResNstrip").getDouble())
            feature.SetField("ResAllots", currentAttList.getAttribute("ResAllots").getDouble())
            feature.SetField("ResDWpLot", currentAttList.getAttribute("ResDWpLot").getDouble())
            feature.SetField("ResHouses", currentAttList.getAttribute("ResHouses").getDouble())
            feature.SetField("ResLotArea", currentAttList.getAttribute("ResLotArea").getDouble())
            feature.SetField("ResRoof", currentAttList.getAttribute("ResRoof").getDouble())
            feature.SetField("avLt_RES", currentAttList.getAttribute("avLt_RES").getDouble())
            feature.SetField("ResHFloors", currentAttList.getAttribute("ResHFloors").getDouble())
            feature.SetField("ResLotTIA", currentAttList.getAttribute("ResLotTIA").getDouble())
            feature.SetField("ResLotEIA", currentAttList.getAttribute("ResLotEIA").getDouble())
            feature.SetField("ResGarden", currentAttList.getAttribute("ResGarden").getDouble())
            feature.SetField("ResRoofCon", currentAttList.getAttribute("ResRoofCon").getDouble())
            feature.SetField("HDRFlats", currentAttList.getAttribute("HDRFlats").getDouble())
            feature.SetField("HDRRoofA", currentAttList.getAttribute("HDRRoofA").getDouble())
            feature.SetField("HDROccup", currentAttList.getAttribute("HDROccup").getDouble())
            feature.SetField("HDR_TIA", currentAttList.getAttribute("HDR_TIA").getDouble())
            feature.SetField("HDR_EIA", currentAttList.getAttribute("HDR_EIA").getDouble())
            feature.SetField("HDRFloors", currentAttList.getAttribute("HDRFloors").getDouble())
            feature.SetField("av_HDRes", currentAttList.getAttribute("av_HDRes").getDouble())
            feature.SetField("HDRGarden", currentAttList.getAttribute("HDRGarden").getDouble())
            feature.SetField("HDRCarPark", currentAttList.getAttribute("HDRCarPark").getDouble())
            
            feature.SetField("LIjobs", currentAttList.getAttribute("LIjobs").getDouble())
            feature.SetField("LIestates", currentAttList.getAttribute("LIestates").getDouble())
            feature.SetField("avSt_LI", currentAttList.getAttribute("avSt_LI").getDouble())
            feature.SetField("LIAfront", currentAttList.getAttribute("LIAfront").getDouble())
            feature.SetField("LIAfrEIA", currentAttList.getAttribute("LIAfrEIA").getDouble())
            feature.SetField("LIAestate", currentAttList.getAttribute("LIAestate").getDouble())
            feature.SetField("LIAeBldg", currentAttList.getAttribute("LIAeBldg").getDouble())
            feature.SetField("LIFloors", currentAttList.getAttribute("LIFloors").getDouble())
            feature.SetField("LIAeLoad", currentAttList.getAttribute("LIAeLoad").getDouble())
            feature.SetField("LIAeCPark", currentAttList.getAttribute("LIAeCPark").getDouble())
            feature.SetField("avLt_LI", currentAttList.getAttribute("avLt_LI").getDouble())
            feature.SetField("LIAeLgrey", currentAttList.getAttribute("LIAeLgrey").getDouble())
            feature.SetField("LIAeEIA", currentAttList.getAttribute("LIAeEIA").getDouble())
            feature.SetField("LIAeTIA", currentAttList.getAttribute("LIAeTIA").getDouble())
            
            feature.SetField("HIjobs", currentAttList.getAttribute("HIjobs").getDouble())
            feature.SetField("HIestates", currentAttList.getAttribute("HIestates").getDouble())
            feature.SetField("avSt_HI", currentAttList.getAttribute("avSt_HI").getDouble())
            feature.SetField("HIAfront", currentAttList.getAttribute("HIAfront").getDouble())
            feature.SetField("HIAfrEIA", currentAttList.getAttribute("HIAfrEIA").getDouble())
            feature.SetField("HIAestate", currentAttList.getAttribute("HIAestate").getDouble())
            feature.SetField("HIAeBldg", currentAttList.getAttribute("HIAeBldg").getDouble())
            feature.SetField("HIFloors", currentAttList.getAttribute("HIFloors").getDouble())
            feature.SetField("HIAeLoad", currentAttList.getAttribute("HIAeLoad").getDouble())
            feature.SetField("HIAeCPark", currentAttList.getAttribute("HIAeCPark").getDouble())
            feature.SetField("avLt_HI", currentAttList.getAttribute("avLt_HI").getDouble())
            feature.SetField("HIAeLgrey", currentAttList.getAttribute("HIAeLgrey").getDouble())
            feature.SetField("HIAeEIA", currentAttList.getAttribute("HIAeEIA").getDouble())
            feature.SetField("HIAeTIA", currentAttList.getAttribute("HIAeTIA").getDouble())
            
            feature.SetField("COMjobs", currentAttList.getAttribute("COMjobs").getDouble())
            feature.SetField("COMestates", currentAttList.getAttribute("COMestates").getDouble())
            feature.SetField("avSt_COM", currentAttList.getAttribute("avSt_COM").getDouble())
            feature.SetField("COMAfront", currentAttList.getAttribute("COMAfront").getDouble())
            feature.SetField("COMAfrEIA", currentAttList.getAttribute("COMAfrEIA").getDouble())
            feature.SetField("COMAestate", currentAttList.getAttribute("COMAestate").getDouble())
            feature.SetField("COMAeBldg", currentAttList.getAttribute("COMAeBldg").getDouble())
            feature.SetField("COMFloors", currentAttList.getAttribute("COMFloors").getDouble())
            feature.SetField("COMAeLoad", currentAttList.getAttribute("COMAeLoad").getDouble())
            feature.SetField("COMAeCPark", currentAttList.getAttribute("COMAeCPark").getDouble())
            feature.SetField("avLt_COM", currentAttList.getAttribute("avLt_COM").getDouble())
            feature.SetField("COMAeLgrey", currentAttList.getAttribute("COMAeLgrey").getDouble())
            feature.SetField("COMAeEIA", currentAttList.getAttribute("COMAeEIA").getDouble())
            feature.SetField("COMAeTIA", currentAttList.getAttribute("COMAeTIA").getDouble())
            
            feature.SetField("ORCjobs", currentAttList.getAttribute("ORCjobs").getDouble())
            feature.SetField("ORCestates", currentAttList.getAttribute("ORCestates").getDouble())
            feature.SetField("avSt_ORC", currentAttList.getAttribute("avSt_ORC").getDouble())
            feature.SetField("ORCAfront", currentAttList.getAttribute("ORCAfront").getDouble())
            feature.SetField("ORCAfrEIA", currentAttList.getAttribute("ORCAfrEIA").getDouble())
            feature.SetField("ORCAestate", currentAttList.getAttribute("ORCAestate").getDouble())
            feature.SetField("ORCAeBldg", currentAttList.getAttribute("ORCAeBldg").getDouble())
            feature.SetField("ORCFloors", currentAttList.getAttribute("ORCFloors").getDouble())
            feature.SetField("ORCAeLoad", currentAttList.getAttribute("ORCAeLoad").getDouble())
            feature.SetField("ORCAeCPark", currentAttList.getAttribute("ORCAeCPark").getDouble())
            feature.SetField("avLt_ORC", currentAttList.getAttribute("avLt_ORC").getDouble())
            feature.SetField("ORCAeLgrey", currentAttList.getAttribute("ORCAeLgrey").getDouble())
            feature.SetField("ORCAeEIA", currentAttList.getAttribute("ORCAeEIA").getDouble())
            feature.SetField("ORCAeTIA", currentAttList.getAttribute("ORCAeTIA").getDouble())
            
            feature.SetField("Blk_TIA", currentAttList.getAttribute("Blk_TIA").getDouble())
            feature.SetField("Blk_EIA", currentAttList.getAttribute("Blk_EIA").getDouble())
            feature.SetField("Blk_EIF", currentAttList.getAttribute("Blk_EIF").getDouble())
            feature.SetField("Blk_TIF", currentAttList.getAttribute("Blk_TIF").getDouble())
            feature.SetField("Blk_RoofsA", currentAttList.getAttribute("Blk_RoofsA").getDouble())
            
            feature.SetField("wd_Rating", currentAttList.getAttribute("wd_Rating").getDouble())
            feature.SetField("wd_RES_K", currentAttList.getAttribute("wd_RES_K").getDouble())
            feature.SetField("wd_RES_S", currentAttList.getAttribute("wd_RES_S").getDouble())
            feature.SetField("wd_RES_T", currentAttList.getAttribute("wd_RES_T").getDouble())
            feature.SetField("wd_RES_L", currentAttList.getAttribute("wd_RES_L").getDouble())
            feature.SetField("wd_RES_IN", currentAttList.getAttribute("wd_RES_IN").getDouble())
            feature.SetField("wd_RES_OUT", currentAttList.getAttribute("wd_RES_OUT").getDouble())
            feature.SetField("wd_HDR_K", currentAttList.getAttribute("wd_HDR_K").getDouble())
            feature.SetField("wd_HDR_S", currentAttList.getAttribute("wd_HDR_S").getDouble())
            feature.SetField("wd_HDR_T", currentAttList.getAttribute("wd_HDR_T").getDouble())
            feature.SetField("wd_HDR_L", currentAttList.getAttribute("wd_HDR_L").getDouble())
            feature.SetField("wd_HDR_IN", currentAttList.getAttribute("wd_HDR_IN").getDouble())
            feature.SetField("wd_HDR_OUT", currentAttList.getAttribute("wd_HDR_OUT").getDouble())
            feature.SetField("wd_PrivIN", currentAttList.getAttribute("wd_PrivIN").getDouble())
            feature.SetField("wd_PrivOUT", currentAttList.getAttribute("wd_PrivOUT").getDouble())
            feature.SetField("wd_LI", currentAttList.getAttribute("wd_LI").getDouble())
            feature.SetField("wd_HI", currentAttList.getAttribute("wd_HI").getDouble())
            feature.SetField("wd_COM", currentAttList.getAttribute("wd_COM").getDouble())
            feature.SetField("wd_ORC", currentAttList.getAttribute("wd_ORC").getDouble())
            feature.SetField("wd_Nres_IN", currentAttList.getAttribute("wd_Nres_IN").getDouble())
            feature.SetField("Apub_irr", currentAttList.getAttribute("Apub_irr").getDouble())
            feature.SetField("wd_PubOUT", currentAttList.getAttribute("wd_PubOUT").getDouble())
            feature.SetField("Blk_WD", currentAttList.getAttribute("Blk_WD").getDouble())
            feature.SetField("Blk_WD_OUT", currentAttList.getAttribute("Blk_WD_OUT").getDouble())
            
            layer.CreateFeature(feature)
        
        shapefile.Destroy()
        return True
    
    def exportPatchData(self):
        city = self.getData("City")
        
        strvec = city.getUUIDsOfComponentsInView(self.mapattributes)
        map_attr = city.getComponent(strvec[0])		#blockcityin.getAttributes("MapAttributes")   #Get map attributes
        if map_attr.getAttribute("patchdelin") == 0:
            return True
        
        spatialRef = osr.SpatialReference()                #Define Spatial Reference
        spatialRef.ImportFromProj4(self.Projection)
        
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(str(self.FileName+"_Patches.shp")): os.remove(self.FileName+"_Patches.shp")
        shapefile = driver.CreateDataSource(self.FileName+"_Patches.shp")
        
        layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbPolygon)
        layerDefinition = layer.GetLayerDefn()
        
        #DEFINE ATTRIBUTES
        fielddefmatrix = []
        fielddefmatrix.append(ogr.FieldDefn("LandUse", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("Area", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("AvgElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("SoilK", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("BlockID", ogr.OFTInteger))
        
        #Create the fields
        for field in fielddefmatrix:
            layer.CreateField(field)
            layer.GetLayerDefn()
        
        #Get Blocks View
        uuids = city.getUUIDsOfComponentsInView(self.patch)
        for i in range(len(uuids)):
            currentAttList = city.getFace(uuids[i])
        
            #Draw Geometry
            line = ogr.Geometry(ogr.wkbPolygon)
            ring = ogr.Geometry(ogr.wkbLinearRing)
            nl = TBVectorData.getNodeListFromFace(city, currentAttList)
            for point in nl:
                ring.AddPoint(point.getX()+self.OffsetX, point.getY()+self.OffsetY)
            line.AddGeometry(ring)
            
            feature = ogr.Feature(layerDefinition)
            feature.SetGeometry(line)
            feature.SetFID(0)
            
            #Add Attributes
            feature.SetField("LandUse", int(currentAttList.getAttribute("LandUse").getDouble()))
            feature.SetField("Area", currentAttList.getAttribute("Area").getDouble())
            feature.SetField("AvgElev", currentAttList.getAttribute("AvgElev").getDouble())
            feature.SetField("SoilK", currentAttList.getAttribute("SoilK").getDouble())
            feature.SetField("BlockID", int(currentAttList.getAttribute("BlockID").getDouble()))
        
            layer.CreateFeature(feature)
        
        shapefile.Destroy()
        return True
    
    def exportFlowPaths(self):
        city = self.getData("City")
        
        spatialRef = osr.SpatialReference()                #Define Spatial Reference
        spatialRef.ImportFromProj4(self.Projection)
        
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(str(self.FileName+"_Network.shp")): os.remove(self.FileName+"_Network.shp")
        shapefile = driver.CreateDataSource(self.FileName+"_Network.shp")
        
        layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbLineString)
        layerDefinition = layer.GetLayerDefn()
        
        #DEFINE ATTRIBUTES
        fielddefmatrix = []
        fielddefmatrix.append(ogr.FieldDefn("BlockID", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("DownID", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("Z_up", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Z_down", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("max_Zdrop", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Type", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("avg_slope", ogr.OFTReal))
        
        #Create the fields
        for field in fielddefmatrix:
            layer.CreateField(field)
            layer.GetLayerDefn()
        
        #Get Blocks View
        uuids = city.getUUIDsOfComponentsInView(self.network)
        for i in range(len(uuids)):
            currentAttList = city.getEdge(uuids[i])
        
            #Draw Geometry
            line = ogr.Geometry(ogr.wkbLineString)
            p1 = city.getNode(currentAttList.getStartpointName())
            p2 = city.getNode(currentAttList.getEndpointName())
            
            line.AddPoint(p1.getX() + self.OffsetX, p1.getY() + self.OffsetY)
            line.AddPoint(p2.getX() + self.OffsetX, p2.getY() + self.OffsetY)
            
            feature = ogr.Feature(layerDefinition)
            feature.SetGeometry(line)
            feature.SetFID(0)
            
            #Add Attributes
            feature.SetField("BlockID", int(currentAttList.getAttribute("BlockID").getDouble()))
            feature.SetField("DownID", int(currentAttList.getAttribute("DownID").getDouble()))
            feature.SetField("Z_up", currentAttList.getAttribute("Z_up").getDouble())
            feature.SetField("Z_down", currentAttList.getAttribute("Z_down").getDouble())
            feature.SetField("max_Zdrop", currentAttList.getAttribute("max_Zdrop").getDouble())
            feature.SetField("Type", int(currentAttList.getAttribute("Type").getDouble()))
            feature.SetField("avg_slope", currentAttList.getAttribute("avg_slope").getDouble())
        
            layer.CreateFeature(feature)
        
        shapefile.Destroy()
        return True
    
    def exportBlockLocalities(self):
        city = self.getData("City")
        
        spatialRef = osr.SpatialReference()                #Define Spatial Reference
        spatialRef.ImportFromProj4(self.Projection)
        
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(str(self.FileName+"_Localities.shp")): os.remove(self.FileName+"_Localities.shp")
        shapefile = driver.CreateDataSource(self.FileName+"_Localities.shp")
        
        layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbPoint)
        layerDefinition = layer.GetLayerDefn()
        
        #DEFINE ATTRIBUTES
        fielddefmatrix = []
        fielddefmatrix.append(ogr.FieldDefn("BlockID", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("Type", ogr.OFTString))
        fielddefmatrix.append(ogr.FieldDefn("Area", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("TIF", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("ARoof", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("AvgWD", ogr.OFTReal))
        
        
        #Create the fields
        for field in fielddefmatrix:
            layer.CreateField(field)
            layer.GetLayerDefn()
        
        #Get Blocks View
        uuids = city.getUUIDsOfComponentsInView(self.blocklocality)
        for i in range(len(uuids)):
            currentAttList = city.getNode(uuids[i])
        
            #Draw Geometry
            point = ogr.Geometry(ogr.wkbPoint)
            point.SetPoint(0, currentAttList.getX() + self.OffsetX, currentAttList.getY() + self.OffsetY)
            
            feature = ogr.Feature(layerDefinition)
            feature.SetGeometry(point)
            feature.SetFID(0)
            
            #Add Attributes
            feature.SetField("BlockID", int(currentAttList.getAttribute("BlockID").getDouble()))
            feature.SetField("Type", currentAttList.getAttribute("Type").getString())
            feature.SetField("Area", currentAttList.getAttribute("Area").getDouble())
            feature.SetField("Area", currentAttList.getAttribute("TIF").getDouble())
            feature.SetField("Area", currentAttList.getAttribute("ARoof").getDouble())
            feature.SetField("Area", currentAttList.getAttribute("AvgWD").getDouble())
            layer.CreateFeature(feature)
        
        shapefile.Destroy()
        return True
    
    def exportPlannedWSUD(self):
        city = self.getData("City")
        strvec = city.getUUIDsOfComponentsInView(self.mapattributes)
        map_attr = city.getComponent(strvec[0])
        
        strategies = map_attr.getAttribute("OutputStrats").getDouble()
        
        uuids = city.getUUIDsOfComponentsInView(self.wsudAttr)

        for i in range(int(strategies)):
            stratID = i+1
            spatialRef = osr.SpatialReference()
            spatialRef.ImportFromProj4(self.Projection)
            
            driver = ogr.GetDriverByName('ESRI Shapefile')
            
            if os.path.exists(str(self.FileName+"_PlannedWSUD"+str(stratID)+".shp")): os.remove(self.FileName+"_PlannedWSUD"+str(stratID)+".shp")
            shapefile = driver.CreateDataSource(self.FileName+"_PlannedWSUD"+str(stratID)+".shp")
        
            layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbPoint)
            layerDefinition = layer.GetLayerDefn()
            
            #DEFINE ATTRIBUTES
            fielddefmatrix = []
            fielddefmatrix.append(ogr.FieldDefn("StrategyID", ogr.OFTInteger))
            fielddefmatrix.append(ogr.FieldDefn("BasinID", ogr.OFTInteger))
            fielddefmatrix.append(ogr.FieldDefn("Location", ogr.OFTInteger))
            fielddefmatrix.append(ogr.FieldDefn("Scale", ogr.OFTString))
            fielddefmatrix.append(ogr.FieldDefn("Type", ogr.OFTString))
            fielddefmatrix.append(ogr.FieldDefn("Qty", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("GoalQty", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("SysArea", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("Status", ogr.OFTInteger))
            fielddefmatrix.append(ogr.FieldDefn("Year", ogr.OFTInteger))
            fielddefmatrix.append(ogr.FieldDefn("EAFact", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("ImpT", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("CurImpT", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("Upgrades", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("WDepth", ogr.OFTReal))
            fielddefmatrix.append(ogr.FieldDefn("FDepth", ogr.OFTReal))
            
            for field in fielddefmatrix:
                layer.CreateField(field)
                layer.GetLayerDefn()
            
            for uuid in uuids:
                currentAttList = city.getComponent(uuid)
                if int(currentAttList.getAttribute("StrategyID").getDouble()) != int(stratID):
                    continue
                #print currentAttList.getAttribute("StrategyID").getDouble()
                #print currentAttList.getAttribute("posX").getDouble(), currentAttList.getAttribute("posY").getDouble()
                #Draw Geometry
                point = ogr.Geometry(ogr.wkbPoint)
                point.SetPoint(0, currentAttList.getAttribute("posX").getDouble()+self.OffsetX, currentAttList.getAttribute("posY").getDouble()+self.OffsetY)
                
                feature = ogr.Feature(layerDefinition)
                feature.SetGeometry(point)
                feature.SetFID(0)
                
                #Add Attributes
                feature.SetField("StrategyID", int(currentAttList.getAttribute("StrategyID").getDouble()))
                feature.SetField("BasinID", int(currentAttList.getAttribute("BasinID").getDouble()))
                feature.SetField("Location", int(currentAttList.getAttribute("Location").getDouble()))
                feature.SetField("Scale", currentAttList.getAttribute("Scale").getString())
                feature.SetField("Type", currentAttList.getAttribute("Type").getString())
                feature.SetField("Qty", int(currentAttList.getAttribute("Qty").getDouble()))
                feature.SetField("GoalQty", int(currentAttList.getAttribute("GoalQty").getDouble()))
                feature.SetField("SysArea", currentAttList.getAttribute("SysArea").getDouble())
                feature.SetField("Status", int(currentAttList.getAttribute("Status").getDouble()))
                feature.SetField("Year", int(currentAttList.getAttribute("Year").getDouble()))
                feature.SetField("EAFact", currentAttList.getAttribute("EAFact").getDouble())
                feature.SetField("ImpT", currentAttList.getAttribute("ImpT").getDouble())
                feature.SetField("CurImpT", currentAttList.getAttribute("CurImpT").getDouble())
                feature.SetField("Upgrades", currentAttList.getAttribute("Upgrades").getDouble())
                feature.SetField("WDepth", currentAttList.getAttribute("WDepth").getDouble())
                feature.SetField("FDepth", currentAttList.getAttribute("FDepth").getDouble())
                layer.CreateFeature(feature)
            
            shapefile.Destroy()
        return True
    
    def exportImplementWSUD(self):
        return True
    
    def exportBlockCentre(self):
        city = self.getData("City")
        
        spatialRef = osr.SpatialReference()                #Define Spatial Reference
        spatialRef.ImportFromProj4(self.Projection)
        
        driver = ogr.GetDriverByName('ESRI Shapefile')
        if os.path.exists(str(self.FileName+"_CentrePoints.shp")): os.remove(self.FileName+"_CentrePoints.shp")
        shapefile = driver.CreateDataSource(self.FileName+"_CentrePoints.shp")
        
        layer = shapefile.CreateLayer('layer1', spatialRef, ogr.wkbPoint)
        layerDefinition = layer.GetLayerDefn()
        
        #DEFINE ATTRIBUTES
        fielddefmatrix = []
        fielddefmatrix.append(ogr.FieldDefn("BlockID", ogr.OFTInteger))
        fielddefmatrix.append(ogr.FieldDefn("AvgElev", ogr.OFTReal))
        fielddefmatrix.append(ogr.FieldDefn("Type", ogr.OFTString))
        
        #Create the fields
        for field in fielddefmatrix:
            layer.CreateField(field)
            layer.GetLayerDefn()
        
        #Get Blocks View
        uuids = city.getUUIDsOfComponentsInView(self.blocknodes)
        for i in range(len(uuids)):
            currentAttList = city.getNode(uuids[i])
        
            #Draw Geometry
            point = ogr.Geometry(ogr.wkbPoint)
            point.SetPoint(0, currentAttList.getX() + self.OffsetX, currentAttList.getY() + self.OffsetY)
            
            feature = ogr.Feature(layerDefinition)
            feature.SetGeometry(point)
            feature.SetFID(0)
            
            #Add Attributes
            feature.SetField("BlockID", int(currentAttList.getAttribute("BlockID").getDouble()))
            feature.SetField("AvgElev", currentAttList.getAttribute("AvgElev").getDouble())
            feature.SetField("Type", currentAttList.getAttribute("Type").getString())
            layer.CreateFeature(feature)
        
        shapefile.Destroy()
        return True