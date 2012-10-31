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
            self.createParameter("PlannedWSUD", BOOL, "")
            self.createParameter("ImplementedWSUD", BOOL, "")
            self.createParameter("BasinMap", BOOL, "")
            self.createParameter("BlockCentres", BOOL, "")
            self.BuildingBlocks = True
            self.PatchData = False
            self.FlowPaths = False
            self.PlannedWSUD = False
            self.ImplementedWSUD = False
            self.BasinMap = False
            self.BlockCentres = False
            
            #VIEWS
            self.mapattributes = View("GlobalMapAttributes", COMPONENT, READ)
            self.block = View("Block", FACE, READ)
            self.patch = View("Patch", FACE, READ)
            self.network = View("Network", EDGE, READ)
            self.blocknodes = View("BlockNodes", NODE, READ)
            
            datastream = []
            datastream.append(self.mapattributes)
            datastream.append(self.block)
            datastream.append(self.patch)
            datastream.append(self.network)
            datastream.append(self.blocknodes)
            
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
            if self.PlannedWSUD:
                print "Exporting WSUD Planned"
                self.exportPlannedWSUD()
            if self.ImplementWSUD:
                print "Exporting WSUD Implemented"
                self.exportImplementWSUD()
            if self.BasinMap:
                print "Exporting Basin Map"
                self.exportBasinMap()
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

            if map_attr.getAttribute("considerCBD").getDouble(): fielddefmatrix.append(ogr.FieldDefn("CBDdist", ogr.OFTReal))          
            if map_attr.getAttribute("considerCBD").getDouble(): fielddefmatrix.append(ogr.FieldDefn("CBDdir", ogr.OFTReal))
         
            
                #>>> FROM URBPLANBB
            
            
            
                #>>> FROM TECHPLACEMENT

            
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

                if map_attr.getAttribute("considerCBD").getDouble(): feature.SetField("CBDdist", currentAttList.getAttribute("CBDdist").getDouble())          
                if map_attr.getAttribute("considerCBD").getDouble(): feature.SetField("CBDdir", currentAttList.getAttribute("CBDdir").getDouble())
                
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
        
        def exportPlannedWSUD(self):
            return True
        
        
        def exportImplementWSUD(self):
            return True
        
        
        def exportBasinMap(self):
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