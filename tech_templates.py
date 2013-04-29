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
import random as rand
import numpy as np

### EXTERNAL FUNCTIONS THAT CAN MANIPULATE THE CLASSES OF THIS MODULE ###
def CalculateMCATechScores(strategyobject, areaEIA, bracketwidth, techarray, tech, env, ecn, soc):
    """Calculates the individual multicriteria scores for the given strategy object
    and saves it into its attributes, takes the techarray and four other vectors
    containing MCA scores as input.
    """
    
    techs = strategyobject.getTechnologies()
    servicebin = strategyobject.getBlockBin()
    totService = strategyobject.getTotalBasinContribution(areaEIA)
    totImpServed = strategyobject.getService()
    if totService > 1:
        print "THERE IS AN ISSUE HERE!!!"
    
    penaltyfactor = 1.0-float(abs(totService - servicebin)/bracketwidth)
    
    mca_tech = 0        #Initialize trackers
    mca_env = 0
    mca_ecn = 0
    mca_soc = 0
    
    for i in techs:
        if i == 0:
            continue
        lotcount = float(strategyobject.getQuantity(i.getLandUse()))
        
        #Score = (individual Tech score) x (imp served by tech / imp served by strategy) X number of techs implemented
        mca_tech += sum(tech[techarray.index(i.getType())]) * i.getService()/areaEIA * lotcount
        mca_env += sum(env[techarray.index(i.getType())]) * i.getService()/areaEIA * lotcount
        mca_ecn += sum(ecn[techarray.index(i.getType())]) * i.getService()/areaEIA * lotcount
        mca_soc += sum(soc[techarray.index(i.getType())]) * i.getService()/areaEIA * lotcount
        
    strategyobject.setMCAscore("tec", mca_tech*penaltyfactor)
    strategyobject.setMCAscore("env", mca_env*penaltyfactor)
    strategyobject.setMCAscore("ecn", mca_ecn*penaltyfactor)
    strategyobject.setMCAscore("soc", mca_soc*penaltyfactor)
    return True

def CalculateMCAStratScore(strategyobject, weightings):
    """Calculates the final MCA score of the strategy for the given strategy object
    and input weightings for the four criteria [tech, env, ecn, soc]. Saves the final
    score into the object's attributes
    """
    #Normalize the weightings
    weightings = rescaleList(weightings, 'normalize')
    
    #Calculate final score and set it
    mca_total = 0
    mca_total += strategyobject.getMCAscore("tec") * weightings[0]
    mca_total += strategyobject.getMCAscore("env") * weightings[1]
    mca_total += strategyobject.getMCAscore("ecn") * weightings[2]
    mca_total += strategyobject.getMCAscore("soc") * weightings[3]
    strategyobject.setTotalMCAscore(mca_total)
    return True

def rescaleList(list, method):
    """Simple rescaling of a single-dimensional array based on the either the number of entries
    (method='length') or the sum of its values (method='normalize')."""
    if method == 'length':
        for i in range(len(list)):
            list[i] = list[i]/float(len(list))
    elif method == 'normalize':
        for i in range(len(list)):
            list[i] = list[i]/sum(list)
    return list

def createDataBaseString(blockstrategy):
    """Prepare's the blockstrategy object's properties into a string that can be inserted
    into the database table corresponding to top-inblock strategies
    """
    dbstring = ""
    dbstring += str(blockstrategy.getLocation())+","+str(blockstrategy.getBlockBin())+","
    #grab all technologies
    techlist = blockstrategy.getTechnologies()
    for i in techlist:
        if i == 0:
            dbstring += "'0',0,0,"
        else:
            dbstring += "'"+str(i.getType())+"',"+str(blockstrategy.getQuantity(i.getLandUse()))+","+str(i.getService())+","
            
    dbstring += str(blockstrategy.getService())+","+str(blockstrategy.getMCAscore("tec"))+","+str(blockstrategy.getMCAscore("env"))+","
    dbstring += str(blockstrategy.getMCAscore("ecn"))+","+str(blockstrategy.getMCAscore("soc"))+","+str(blockstrategy.getTotalMCAscore())
    #print dbstring
    return dbstring

def writeReportFile(basinstrategyobject, filename):
    """Writes an output CSV file of the basin strategy object passed to the function
    and saves it to the file with the given <filename>.csv. The file can be opened in
    Excel for convenient viewing"""

    return True

def reportStrategy(strategyobject):
    """Prints details of the strategy into the console window for quick viewing, use
    this function for debugging"""
    
    return True

def addBlockStrategyToBasin(blockstrategy, basinstrategy):
    """Adds an In-Block Strategy Object to the basin strategy object, used to build
    up the basin strategy"""
    
    return True

def addSubbasinTechToBasin(subbasintech, basinstrategy):
    """Adds a large regional system to the basin strategy, used to build up the 
    basin strategy"""
    
    return True

def getInBlockStrategy(basinstrategy, currentID):
    """Retrieves the In-Block Strategy from a basin strategy object at the location
    with currentID. If none is available, it returns zero"""
    
    return True

def getSubbasinTech(basinstrategy, currentID):
    """Searches the basin strategy for a regional system in Block with ID currentID
    if none is available, returns zero instead"""

    return True


### CLASSES IN THIS MODULE ###

class WaterTech(object):
    def __init__(self, type, size, scale, service, areafactor, landuse, blockID):
        """Technology type = initials of the tech e.g. BF = biofilter
                type = system type  in terms of abbreviation
                size = surface area/volume/specification number depending on system type
                scale = a letter signifiying scale of application, L-lot, S-street, N-neighbourhood, R-regional (sub-basin)
                service = impervious area served by the system (in sqm) or population or an amount of public space
                areafactor = a factor for multiplying the system footprint to get planning-allocated area
                landuse = the type of land use the system was designed for
        """
        self.__type = type
        self.__size = size
        self.__scale = scale
        self.__service = float(service)
        self.__areafactor = areafactor
        self.__landuse = landuse
        self.__designincrement = 1.0
        self.__blockID = blockID

        #Assign some descriptive variables to the object
        if self.__type in ['BF', 'IS']:
            self.hasFilter = True
        else:
            self.hasFilter = False
        if self.__type in ['WSUR', 'PB', 'RT', 'GW']:
            self.hasStorage = True
        else:
            self.hasStorage = False
        if self.__type in ['RT', 'GW', 'PPL']:
            self.isGreyTech = True
            self.isGreenTech = False
        else:
            self.isGreyTech = False
            self.isGreenTech = True
    
    def setDesignIncrement(self, increment):
        self.__designincrement = increment
    
    def getDesignIncrement(self):
        return self.__designincrement
    
    def getType(self):
        return self.__type
    
    def getAreaFactor(self):
        return self.__areafactor
    
    def getSize(self):
        return self.__size
    
    def getScale(self):
        return self.__scale
    
    def getService(self):
        return self.__service
    
    def getContributionToBasin(self, basinMeasure):
        if basinMeasure == 0:
            contribution = 0
        else:
            contribution = self.__area_service / basinMeasure
        return contribution
    
    def getLandUse(self):
        return self.__landuse
    
    def getLocation(self):
        return self.__blockID
    

class BlockStrategy(object):
    def __init__(self, combo, totalserviceabsolute, allotments, currentID, bin):
        self.__lotRES_tech = combo[0]
        self.__lotHDR_tech = combo[1]
        self.__lotLI_tech = combo[2]
        self.__lotHI_tech = combo[3]
        self.__lotCOM_tech = combo[4]
        self.__street_tech = combo[5]
        self.__neigh_tech = combo[6]
        self.__service = totalserviceabsolute   #e.g. total imp served, total pop served
        self.__location = currentID
        self.__blockbin = bin
        
        self.__allotments = allotments  #a list of lotcounts [RES Lots, HDR Lots, LI estates, HI estates, COM estates]
        self.lucmatrix = ["RES", "HDR", "LI", "HI", "COM", "Street", "Neigh"]
        self.__MCA_scores = [0,0,0,0]
        self.__MCA_totscore = 0
        self.criteriamatrix = ["tec", "env", "ecn", "soc"]
    
    def getBlockBin(self):
        return self.__blockbin
    
    def getQuantity(self, luc):
        if luc not in self.lucmatrix:
            return 1
        else:
            return self.__allotments[self.lucmatrix.index(luc)]
    
    def setMCAscore(self, criteria, score):
        self.__MCA_scores[self.criteriamatrix.index(criteria)] = score
    
    def getMCAscore(self, criteria):
        return self.__MCA_scores[self.criteriamatrix.index(criteria)]
    
    def setTotalMCAscore(self, score):
        self.__MCA_totscore = score
    
    def getTotalMCAscore(self):
        return self.__MCA_totscore
    
    def getTechnologies(self):
        return [self.__lotRES_tech, self.__lotHDR_tech, self.__lotLI_tech, self.__lotHI_tech, self.__lotCOM_tech, self.__street_tech, self.__neigh_tech]
        
    def getService(self):
        return self.__service
    
    def getLocation(self):
        return self.__location
    
    def getTotalBasinContribution(self, basinAimp):
        return self.__service/basinAimp
    
    
#class BlockStrategy(object):
#    #Class for Water Management Strategy, which consists of lot, street, neighbourhood scales
#    #options that can be added to it using the WSUD class
#    def __init__(self, degrees, combo, allotments, totalimp):
#        #Strategy Class must hold a list of WSUD systems, each WSUD with its representative scale
#        #of application.
#        #       degrees = lot, street, neighbourhood degrees (0, 0, 0) proportions
#        #       combo = three WSUD objects one for each scale   [lot, street, neighbourhood]
#        #       allotments = total number of houses
#        #       totalimp = total imperviousness of the site being assessed
        
#        #degrees or service + combinations
#        self.__stratdegs = degrees
#        self.__stratlist = combo
        
#        #SERVICE LEVEL OF IMPERVIOUS AREA
#        self.__allotments = allotments
#        self.__totalimp = totalimp
        
#        self.__lot_servimp = 0          #holds total lot area serviced
#        self.__street_servimp = 0       #holds total street imp area serviced
#        self.__neigh_servimp = 0        #holds total neighbourhood imp area serviced
#        self.__tot_servimp = 0          #holds the total area of imp area serviced
#        self.__prop_totimpserv = 0      #holds the % of imp area serviced
        
#        #MCA SCORES
#        self.__mcaenv_score = 0
#        self.__mcatech_score = 0
#        self.__mcasoc_score = 0
#        self.__mcaecn_score = 0
#        self.__mcatot_score = 0
        
#        #print "Details"
#        #print self.__stratdegs
#        #print allotments
    
#    def checkTechnologies(self):
#        #Checks the technologies in the combinations matrix and calculates areas served
#        #Also corrects for 0 technologies
#        #LOT SCALE - get the area served
#        if self.__stratlist[0] == 0 or self.__stratdegs[0] == 0:
#            self.__lot_servimp = 0
#        else:
#            self.__lot_servimp = float(self.__stratdegs[0]) * float(self.__allotments) * float(self.__stratlist[0].getAreaServed())
#            #serviced area = (degree) x (# allotments) x (area served per allotment)
            
#        #print self.__lot_servimp
        
#        #STREET SCALE - get the area served
#        if self.__stratlist[1] == 0 or self.__stratdegs[1] == 0:
#            self.__street_servimp = 0
#        else:
#            self.__street_servimp = float(self.__stratlist[1].getAreaServed())
#            #serviced area = (degree) x (# allotments) x (area served per allotment)
        
#        #print self.__street_servimp 
        
#        #NEIGHBOURHOOD SCALE - get the area served
#        if self.__stratlist[2] == 0 or self.__stratdegs[2] == 0:
#            self.__neigh_servimp = 0
#        else:
#            self.__neigh_servimp = float(self.__stratlist[2].getAreaServed())
#            #serviced area = (degree) x (# allotments) x (area served per allotment)
    
#        #print self.__neigh_servimp
    
#        #Get total served and proportion served
#        self.__tot_servimp = float(self.__lot_servimp + self.__street_servimp + self.__neigh_servimp)
        
#        #Calculate service level
#        if self.__totalimp == 0:
#            self.__prop_totimpserv = 0
#        else:
#            self.__prop_totimpserv = np.round(float(self.__tot_servimp/self.__totalimp),4)
        
#        return True
        
#    #UPDATE AND GET COUNT OF TECHNOLOGIES IN STRATEGY
#    def reportStrategy(self):
#        outputstring = "Combo: ("
#        for i in self.__stratdegs:
#            outputstring += str(i)+","
#        outputstring += ") "
#        for i in self.__stratlist:
#            if i == 0:
#                outputstring += "0,"
#            else:
#                outputstring += str(i.getType())+","
#        return outputstring
    
#    def writeReportCombo(self):
#        outputstring = ""
#        for i in self.__stratdegs:
#            outputstring += str(i)+","
#        return outputstring
    
#    def writeReportSystems(self):
#        outputstring = ""
#        for i in self.__stratlist:
#            if i == 0:
#                outputstring += "0,0,0,0,"
#            else:
#                outputstring += str(i.getType())+","+str(i.getScale())+","+str(i.getSize())+","+str(i.getAreaServed())+","
#        return outputstring
    
#    def writeReportScores(self):
#        outputstring = ""
#        sub_scores = self.getMCAsubscores()
#        for i in sub_scores:
#            outputstring += str(i)+","
#        outputstring += str(self.getMCAtotscore())+","
#        return outputstring
    
#    def getSystemList(self):
#        return self.__stratlist
    
#    def getSystemDegs(self):
#        return self.__stratdegs
    
#    def getLotImplementation(self):
#        return self.__stratdegs[0]*100
    
#    def getAllotments(self):
#        return self.__allotments
    
#    ################################################
#    ##    Functions for Service Levels            ##
#    ################################################
#    def getTotalImpServed(self):
#        return self.__prop_totimpserv
    
#    def getTotalAImpServed(self):
#        return float(self.__tot_servimp)
    
#    def getTotalBasinContribution(self, basin_Aimp):
#        if basin_Aimp == 0:
#            contribution = 0
#        else:
#            contribution = self.__tot_servimp/basin_Aimp
#        return contribution
    
    
#    ################################################
#    ##    MCA Functions for Strategy              ##
#    ################################################
#    def calcTechScores(self, mca_techindex, mca_matrixtech, mca_matrixenv, mca_matrixecn, mca_matrixsoc, t2s):
#        if self.__tot_servimp == 0:
#            sew_weights = [0, 0, 0]
#        else:
#            sew_weights = [self.__lot_servimp/self.__totalimp , self.__street_servimp/self.__totalimp, self.__neigh_servimp/self.__totalimp]
#        #print "Sew_Weights"
#        #print sew_weights
        
#        tech_techscores = []
#        tech_envscores = []
#        tech_ecnscores = []
#        tech_socscores = []
        
#        #get individual tech scores
#        for tech in self.__stratlist:
#            if tech == 0:                       #if the tech score is zero, then use the BAU type (business as usual)
#                row_num = 1
#            else:
#                row_num = mca_techindex.index(tech.getType())   #otherwise get the index row number
#            if mca_matrixtech == 0 or len(mca_matrixtech) == 0:             #if there are no tech score matrices
#                tech_techscores = [0]
#            else:
#                tech_techscores.append(sum(mca_matrixtech[row_num])/len(mca_matrixtech[row_num]))    #total score for that technology
#            if mca_matrixenv == 0 or len(mca_matrixenv) == 0:
#                tech_envscores = [0]
#            else:
#                tech_envscores.append(sum(mca_matrixenv[row_num])/len(mca_matrixenv[row_num]))
#            if mca_matrixecn == 0 or len(mca_matrixecn) == 0:
#                tech_ecnscores = [0]
#            else:
#                tech_ecnscores.append(sum(mca_matrixecn[row_num])/len(mca_matrixecn[row_num]))
#            if mca_matrixsoc == 0 or len(mca_matrixsoc) == 0:
#                tech_socscores = [0]
#            else:
#                tech_socscores.append(sum(mca_matrixsoc[row_num])/len(mca_matrixsoc[row_num]))
        
#        final_techscore = 0
#        final_envscore = 0
#        final_ecnscore = 0
#        final_socscore = 0
        
#        if t2s == 'EqW':                                #Equal Weighting - simply sum the three different scores
#            final_techscore = sum(tech_techscores)
#            final_envscore = sum(tech_envscores)
#            final_ecnscore = sum(tech_ecnscores)
#            final_socscore = sum(tech_socscores)
#        elif t2s == 'SeW':                              #Service-based weighting - need to do area proportions and sum accordingly
#            for scl in range(len(sew_weights)):                 #loop over [lot-weight, street-weight, neigh-weight]
#                if sum(tech_techscores) == 0:                   #tech_techscores = [lot_score, street_score, neigh_score] tallied earlier
#                    final_techscore = 0                         #add to final scores of each criteri the sub-scores weighted for each SEW-weight
#                else:
#                    final_techscore += tech_techscores[scl]*sew_weights[scl]
#                if sum(tech_envscores) == 0:
#                    final_envscore = 0
#                else:
#                    final_envscore += tech_envscores[scl]*sew_weights[scl] 
#                if sum(tech_ecnscores) == 0:
#                    final_ecnscore = 0
#                else:
#                    final_ecnscore += tech_ecnscores[scl]*sew_weights[scl]
#                if sum(tech_socscores) == 0:
#                    final_socscore = 0
#                else:
#                    final_socscore += tech_socscores[scl]*sew_weights[scl]
        
#        self.__mcatech_score = final_techscore  #Set final scores
#        self.__mcaenv_score = final_envscore
#        self.__mcaecn_score = final_ecnscore
#        self.__mcasoc_score = final_socscore
#        return True
                       
#    def calcStratScoreSingle(self, method, stoch, techW, envW, ecnW, socW):
#        totW = 0
#        for i in [techW, envW, ecnW, socW]:          #IF ONE OF THE CRITERIA ISN'T FEATURED, 
#            if i == 0:                                  #NEED TO ACCOUNT FOR THIS WHEN NORMALIZING WEIGHTINGS
#                pass
#            else:
#                totW += i               #normalize the weightings
#        if totW == 0:
#            techWfinal = 0.25
#            envWfinal = 0.25
#            ecnWfinal = 0.25
#            socWfinal = 0.25
#        else:
#            techWfinal = techW/totW
#            envWfinal = envW/totW
#            ecnWfinal = ecnW/totW
#            socWfinal = socW/totW
        
#        if stoch == 1:       #introduce distortion in terms of the weightings   #INCLUDE STOCHASTIC NOISE? 
#            distort = [rand.random(),rand.random(), rand.random(), rand.random()]
#        else:
#            distort = [0,0,0,0]
        
#        #DEPENDING ON METHOD, TALLY WILL BE DIFFERENT! FOR NOW USE WEIGHTED SUM METHOD!    
#        tech = self.__mcatech_score * (techWfinal + distort[0])
#        env = self.__mcaenv_score * (envWfinal + distort[1])
#        ecn = self.__mcaecn_score * (ecnWfinal + distort[2])
#        soc = self.__mcasoc_score * (socWfinal + distort[3])
        
#        final_score = tech + env + ecn + soc
        
#        self.__mcatot_score = final_score
#        return True 
    
#    def calcStratScorePareto(self, method, techP, envP, ecnP, socP):
#        #Performs the Pareto Exploratory Evaluation i.e. multiple alternative criteria
#        #weightings applied with the current individual scores to determine the sensitivity
#        #of the scores to variable weightings.
        
        
#        #get combinations for Pareto
#        techW = [0]              #if increment = 4, then techW = [0, 2.5, 5, 7.5, 10] weighting
#        envW = [0]
#        ecnW = [0]
#        socW = [0]
        
#        for i in range(int(techP)):
#            techW.append((i+1)*10/techP)        #1st: 1*10/4 = 2.5, 2nd: 2*10/4 = 5...
#        for i in range(int(envP)):
#            envW.append((i+1)*10/envP)
#        for i in range(int(ecnP)):
#            ecnW.append((i+1)*10/ecnP)
#        for i in range(int(socP)):
#            socW.append((i+1)*10/socP)
        
#        combos = []
#        for i in techW:
#            for j in envW:
#                for k in ecnW:
#                    for l in socW:
#                        combos.append([i, j, k, l])
        
#        score_sensitivity_matrix = []
#        #loop across each combo
#        for cc in combos:
#            #cc = current combo e.g. [4, 4, 6, 8]
#            totW = 0
#            for i in cc:          #IF ONE OF THE CRITERIA ISN'T FEATURED, 
#                if i == 0:                                  #NEED TO ACCOUNT FOR THIS WHEN NORMALIZING WEIGHTINGS
#                    pass
#                else:
#                    totW += i               #normalize the weightings
#            if totW == 0:
#                techWfinal = 0.25
#                envWfinal = 0.25
#                ecnWfinal = 0.25
#                socWfinal = 0.25
#            else:
#                techWfinal = cc[0]/totW
#                envWfinal = cc[1]/totW
#                ecnWfinal = cc[2]/totW
#                socWfinal = cc[3]/totW
#            #NO STOCHASTICS IN PARETO MODE
        
#            #DEPENDING ON METHOD, TALLY WILL BE DIFFERENT! FOR NOW USE WEIGHTED SUM METHOD!    
#            tech = self.__mcatech_score * (techWfinal)
#            env = self.__mcaenv_score * (envWfinal)
#            ecn = self.__mcaecn_score * (ecnWfinal)
#            soc = self.__mcasoc_score * (socWfinal)
            
#            final_combo_score = tech + env + ecn + soc
#            score_sensitivity_matrix.append([cc, final_combo_score])
        
#        self.__mcatot_score = score_sensitivity_matrix
        
#        return True 

#    def getMCAsubscores(self):
#        return [self.__mcatech_score, self.__mcaenv_score, self.__mcaecn_score, self.__mcasoc_score]
    
#    def getMCAtotscore(self):
#        return self.__mcatot_score
    
#    def reportMCAscores(self):
#        return [self.__mcatech_score, self.__mcaenv_score, self.__mcaecn_score, self.__mcasoc_score, self.__mcatot_score]

################################################## END OF BlockStrategy CLASS ###########################################################


###THIS ONE IS USED IN OLD CODE!!!
class BasinManagementStrategy(object):
    def __init__(self, strategyID, basinID, basinblockIDs, partakeIDs, cumu_Aimp):
        #basinblockIDs - all IDs inside the basin
        #partakeIDs - all blocks that can hold precinct techs
        #cumu_Aimp - total impervious area of basin
        
        #Details about the basin's blocks
        self.__basinID = basinID
        self.__strategyID = strategyID
        self.__blocks = len(basinblockIDs)
        self.__basinblockIDs = basinblockIDs
        self.__precpartakeIDs = partakeIDs
        
        self.__degreesarray = []                #will hold the chosen degrees - prec_alt_chosen, block_alt_chosen (length of basinblockIDs)
        self.__subbasinarray = []               #holds info on the subbasins (length of precpartakeIDs)
        self.__blockarray = []                  #holds all objects for block strategies (length of basinblockIDs)
        self.__precarray = []                   #holds all objects for precinct strategies (length of precpartakeIDs)
        for i in basinblockIDs:
            self.__blockarray.append([])        #ID position determined by basinblockIDs.index(ID)
            self.__degreesarray.append([0,0])   #two elements... [ID][0] = blockstrategy's degree, [ID][1] = precinct strategy's degree
        for i in partakeIDs:
            self.__precarray.append([])         #ID position determined by partakeIDs.index(ID)
            self.__subbasinarray.append([])
        
        self.__basinAimp = cumu_Aimp
        self.__propImpserved = 0                #
        self.__total_imp_served = 0             #
        
        #MCA SCORES
        self.__mcaenv_score = 0
        self.__mcatech_score = 0
        self.__mcasoc_score = 0
        self.__mcaecn_score = 0
        self.__mcatot_score = 0
        
    #METHODS FOR ADDING SYSTEMS TO THE OVERALL STRATEGY - NEED TO SPECIFY THE LOCATION (i.e. BLOCK ID) with every system
    def addSubBasinInfo(self, currentID, upstreamIDs, subbasinIDs, totalAimp_subbasin):
        i = self.__precpartakeIDs.index(currentID)    #i = short for INDEX
        self.__subbasinarray[i].append(currentID)
        self.__subbasinarray[i].append(upstreamIDs)
        self.__subbasinarray[i].append(subbasinIDs)
        self.__subbasinarray[i].append(totalAimp_subbasin)
        return True
        
    def addPrecTechnology(self, currentID, deg, chosen_object):
        i = self.__precpartakeIDs.index(currentID)    #i = short for INDEX
        j = self.__basinblockIDs.index(currentID)     #j = index in other array
        self.__precarray[i].append(chosen_object)
        self.__degreesarray[i][1] = deg
        return True
    
    def addBlockStrategy(self, currentID, deg, chosen_stratobject):
        i = self.__basinblockIDs.index(currentID)
        self.__blockarray[i].append(chosen_stratobject)
        self.__degreesarray[i][0] = deg
        return True
    
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #                                                                                             #
    #METHODS TO UPDATE AND RETRIEVE IMPERVIOUS SURFACE AND POPULATION SERVICE LEVELS OF STRATEGY  #
    # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # # #                                                                                            
    def updateBasinService(self):
        self.__total_imp_served = float(0.0)
        for i in self.__precarray:
            if len(i) == 0:
                continue
            self.__total_imp_served += float(i[0].getAreaServed())
        for i in self.__blockarray:
            if len(i) == 0:
                continue
            self.__total_imp_served += float(i[0].getTotalAImpServed())
        self.__propImpserved = self.__total_imp_served/self.__basinAimp * 100
        return [self.__total_imp_served, self.__propImpserved]
    
    def getPropImpServed(self):
        return self.__propImpserved             #returns imperviousness serviced
    
    def getTotalImpServed(self):
        return self.__total_imp_served          #returns impervious area served
    
    def getBasinBlockIDs(self):
        return self.__basinblockIDs
    
    def getInBlockStrategy(self, currentID):
        strat = self.__blockarray[self.__basinblockIDs.index(currentID)]
        if len(strat) == 0:
            strat = None
        else:
            strat = strat[0]
        return strat
    
    def getOutBlockStrategy(self, currentID):
        if currentID in self.__precpartakeIDs:
            strat = self.__precarray[self.__precpartakeIDs.index(currentID)]
            if len(strat) == 0:
                strat = None
            else:
                strat = strat[0]
        else:
            strat = None
        return strat
    
    def getOutBlockStrategyDeg(self, currentID):
        if currentID in self.__precpartakeIDs:
            strat = self.__precarray[self.__precpartakeIDs.index(currentID)]
            if len(strat) == 0:
                degofstrat = None
            else:
                degofstrat = self.__degreesarray[self.__precpartakeIDs.index(currentID)][1]
        else:
            degofstrat = None
        return degofstrat
        
    def reportBasinStrategy(self):
        print "-----------------------------------------"
        print "Basin ID", self.__basinID
        print "-----------------------------------------"
        print "Total Blocks in basin: ", self.__blocks
        print "Total Impervious Area: ", self.__basinAimp/10000, " ha"
        print "Block IDs"
        print self.__basinblockIDs
        print "Blocks that can fit a precinct-scale system:"
        print self.__precpartakeIDs 
        print ""
        print "Chosen Objects for precinct"
        print self.__precarray
        print "Chosen Objects for in-block"
        print self.__blockarray
        return True
    
    def writeReportFile(self):
        f = open("UB_BasinStrategy No "+str(self.__basinID)+"-"+str(self.__strategyID)+".csv", 'w')
        f.write("UrbanBEATS Basin Strategy File for Strategy No. "+str(self.__strategyID)+"\n\n")
        f.write("Basin ID:,"+str(self.__basinID)+"\n")
        f.write("Total Service:,"+str(self.getPropImpServed())+"%\n")
        f.write("Blocks within basin:,"+str(len(self.__basinblockIDs))+"\n")
        f.write("Blocks containing precinct-scale opportunities:,"+str(len(self.__precpartakeIDs))+"\n\n")
        f.write("Tech Score, Env Score, Ecn Score, Soc Score, Total Score\n")
        scorestring = ""
        for i in self.getMCAsubscores():
            scorestring += str(i)+","
        scorestring += str(self.getMCAtotscore())+","
        f.write(scorestring+"\n\n")
        
        f.write("Block ID, Lot System, Size, Service, Houses [%], Allotments, Street System, Size, Service, Neigh System, Size, Service, Prec System, Size, Service,\n")
        
        for i in range(len(self.__basinblockIDs)):
            #get strategy list
            outputstring1 = ""
            if len(self.__blockarray[i]) == 0:
                outputstring1 = "0,0,0,0,0,0,0,0,0,0,0,"
            else:
                stratlist = self.__blockarray[i][0].getSystemList()
                for j in range(len(stratlist)):
                    if stratlist[j] == 0:
                        outputstring1 += "0,0,0,"
                    else:
                        outputstring1 += str(stratlist[j].getType())+","+str(stratlist[j].getSize())+","+str(stratlist[j].getBasinContribution(self.__basinAimp))+","
                    if j == 0 and stratlist[j] != 0:
                        outputstring1 += str(self.__blockarray[i][0].getLotImplementation())+","+str(self.__blockarray[i][0].getAllotments())+","
                    elif j == 0 and stratlist[j] == 0:
                        outputstring1 += "0,0,"
            
            #get precinct-scale stuff
            outputstring2 = ""
            if self.__basinblockIDs[i] in self.__precpartakeIDs:                   #if the ID is also a precinct ID check if there's a tech
                ix = self.__precpartakeIDs.index(self.__basinblockIDs[i])          #get index to reference
                if len(self.__precarray[ix]) == 0:                                   #check if there's a tech object or not
                    outputstring2 = "0,0,0,"
                else:
                    outputstring2 = str(self.__precarray[ix][0].getType())+","+str(self.__precarray[ix][0].getSize())+","+str(self.__precarray[ix][0].getBasinContribution(self.__basinAimp))+","
            else:
                outputstring2 = "0,0,0,"
            #combine option strings
            f.write(str(self.__basinblockIDs[i])+","+outputstring1+outputstring2+"\n")
        f.close()
        return True
    
    # # # # # # # # # # # # # # # # # # #
    # MCA FUNCTIONS FOR BASIN STRATEGY  #
    # # # # # # # # # # # # # # # # # # #
    def calcTechScores(self, mca_techindex, mca_matrixtech, mca_matrixenv, mca_matrixecn, mca_matrixsoc):
        basin_precscores = []        #matrix holds the precince scores for all techs at prec scale
        #get individual tech scores
        for i in self.__precarray:
            if len(i) == 0:                       #if the tech score is zero, then use the BAU type (business as usual)
                continue
            tech = i[0]
            row_num = mca_techindex.index(tech.getType())   #otherwise get the index row number
            contribution = i[0].getBasinContribution(self.__basinAimp)
            
            tech_techscores = []
            tech_envscores = []
            tech_ecnscores = []
            tech_socscores = []
            
            if mca_matrixtech == 0 or len(mca_matrixtech) == 0:             #if there are no tech score matrices
                tech_techscores = [0]
            else:
                tech_techscores.append(sum(mca_matrixtech[row_num])/len(mca_matrixtech[row_num]))    #total score for that technology
            if mca_matrixenv == 0 or len(mca_matrixenv) == 0:
                tech_envscores = [0]
            else:
                tech_envscores.append(sum(mca_matrixenv[row_num])/len(mca_matrixenv[row_num]))
            if mca_matrixecn == 0 or len(mca_matrixecn) == 0:
                tech_ecnscores = [0]
            else:
                tech_ecnscores.append(sum(mca_matrixecn[row_num])/len(mca_matrixecn[row_num]))
            if mca_matrixsoc == 0 or len(mca_matrixsoc) == 0:
                tech_socscores = [0]
            else:
                tech_socscores.append(sum(mca_matrixsoc[row_num])/len(mca_matrixsoc[row_num]))
        
            final_techscore = sum(tech_techscores)
            final_envscore = sum(tech_envscores)
            final_ecnscore = sum(tech_ecnscores)
            final_socscore = sum(tech_socscores)
            
            basin_precscores.append([[final_techscore, final_envscore, final_ecnscore, final_socscore],contribution])
        
        print "Basin Precinct Tech Scores"
        print basin_precscores
        
        basin_blockscores = []  #matrix holds the block scores
        #get all block scores
        for i in self.__blockarray:
            if len(i) == 0:
                continue
            subscores = i[0].getMCAsubscores()
            contribution = i[0].getTotalBasinContribution(self.__basinAimp)
            basin_blockscores.append([subscores, contribution])
        
        print "Basin Block Scores"
        print basin_blockscores
        
        #Tally up prec sub-scores and add to existing score variable
        for i in range(len(basin_precscores)):
            self.__mcatech_score += basin_precscores[i][0][0]* basin_precscores[i][1]
            self.__mcaenv_score += basin_precscores[i][0][1]* basin_precscores[i][1]
            self.__mcaecn_score += basin_precscores[i][0][2]* basin_precscores[i][1]
            self.__mcasoc_score += basin_precscores[i][0][3]* basin_precscores[i][1]
        
        print "Subscores for precinct"
        print [self.__mcatech_score, self.__mcaenv_score, self.__mcaecn_score, self.__mcasoc_score]
        
        #Tally up block sub-scores add to existing scores
        for i in range(len(basin_blockscores)):
            self.__mcatech_score += basin_blockscores[i][0][0] * basin_blockscores[i][1]
            self.__mcaenv_score += basin_blockscores[i][0][1] * basin_blockscores[i][1]
            self.__mcaecn_score += basin_blockscores[i][0][2] * basin_blockscores[i][1]
            self.__mcasoc_score += basin_blockscores[i][0][3] * basin_blockscores[i][1]
        
        print "Subscores for precinct + Block"
        print [self.__mcatech_score, self.__mcaenv_score, self.__mcaecn_score, self.__mcasoc_score]
        
        return True
    
    def calcStratScoreSingle(self, method, stoch, techW, envW, ecnW, socW):
        totW = 0
        for i in [techW, envW, ecnW, socW]:          #IF ONE OF THE CRITERIA ISN'T FEATURED, 
            if i == 0:                                  #NEED TO ACCOUNT FOR THIS WHEN NORMALIZING WEIGHTINGS
                pass
            else:
                totW += i               #normalize the weightings
        if totW == 0:
            techWfinal = 0.25
            envWfinal = 0.25
            ecnWfinal = 0.25
            socWfinal = 0.25
        else:
            techWfinal = techW/totW
            envWfinal = envW/totW
            ecnWfinal = ecnW/totW
            socWfinal = socW/totW
        
        if stoch == 1:       #introduce distortion in terms of the weightings   #INCLUDE STOCHASTIC NOISE? 
            distort = [rand.random(),rand.random(), rand.random(), rand.random()]
        else:
            distort = [0,0,0,0]
        
        #DEPENDING ON METHOD, TALLY WILL BE DIFFERENT! FOR NOW USE WEIGHTED SUM METHOD!    
        tech = self.__mcatech_score * (techWfinal + distort[0])
        env = self.__mcaenv_score * (envWfinal + distort[1])
        ecn = self.__mcaecn_score * (ecnWfinal + distort[2])
        soc = self.__mcasoc_score * (socWfinal + distort[3])
        
        final_score = tech + env + ecn + soc
        self.__mcatot_score = final_score
        print "FINAL SCORE FOR WEIGHTINGS: ", [techWfinal, envWfinal, ecnWfinal, socWfinal], " IS: ", final_score
        
        return True
    
    
    def calcStratScorePareto(self, method, techP, envP, ecnP, socP):
        pass
        return True
    
    def getMCAsubscores(self):
        return [self.__mcatech_score, self.__mcaenv_score, self.__mcaecn_score, self.__mcasoc_score]
    
    def getMCAtotscore(self):
        return self.__mcatot_score
    
    def reportMCAscores(self):
        return [self.__mcatech_score, self.__mcaenv_score, self.__mcaecn_score, self.__mcasoc_score, self.__mcatot_score]
    