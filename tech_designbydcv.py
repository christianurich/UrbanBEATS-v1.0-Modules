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

import numpy as np

def retrieveDesign(pathname, systemtype, ksat, targets):
    #Step 1: Read DCV file
    dcv = readDCVFile(pathname, systemtype)
    #print "Designing for : ", ksat
    #Step 2: Get Brackets
    k0, k1, lowbrack, upbrack = bracketDCVFile(dcv, ksat)
    
    #Step 3: Get both sets of areas
    areaslower = findTargetSize(lowbrack, targets)
    areasupper = findTargetSize(upbrack, targets)
    
    #Step 4: Get final design area
    finalarea = getFinalSizeRequirement(k0, k1, areaslower, areasupper, ksat)
    
    return finalarea


def readDCVFile(pathfname, systemtype):
    f = open(pathfname, 'r')
    designcurve = []
    for lines in f:
        designcurve.append(lines.split(','))          
    f.close()    
    finaldcv = [[],[],[],[],[],[],[]]
    for i in range(len(designcurve)):
        if i == 0:
            #print designcurve[i]
            continue
        for j in range(len(designcurve[i])):
            finaldcv[j].append(float(designcurve[i][j]))
    return finaldcv

def bracketDCVFile(array, ksat):
    #function to retrieve the arrays from the DCV file from which design can be undertaken
    #   array = dcv array
    #   ksat = exfiltration rate for which to find the bracket
    #   match = indicates whether it's an close match (0) or a double bracket (1)
    #           if exact, function returns one array, if double bracket, function returns two arrays

    #Step 1: obtain unique kvalue
    kuniques = []
    for i in array[1]:
        if i in kuniques:
            continue
        kuniques.append(i)
    #print kuniques    
    
    #Step 2a: check if ksat falls within the k-values of the dcv, if not, only work with one bracket
    kmin = min(array[1])
    #print "Kmin ", kmin
    kmax = max(array[1])
    if ksat <= kmin or ksat >= kmax:
        #print "Warning, ksat is not within bounds of dcv file, using single value"
        if ksat <= kmin:
            klow = kmin
            kup = kmin
        else:
            klow = kmax
            kup = kmax
    else:
        #Step 2b: if there are two brackets because ksat falls within range of kmin, kmax, find the values
        klow = kmin    #initialize lower and upper k brackets
        kup = klow
        for i in range(len(kuniques)):
            if kup > ksat:
                continue
            klow = kuniques[i]
            kup = kuniques[i+1]
        #print klow, kup
    
    #Step 3: Retrieve brackets        
    lowerbracket = [[],[],[],[],[],[],[]]
    upperbracket = [[],[],[],[],[],[],[]]

    if klow == kup:     #one bracket
        index = array[1].index(klow)
        while array[1][index] == klow:
            for i in range(7):
                lowerbracket[i].append(array[i][index])
                upperbracket[i].append(array[i][index])                
            index += 1
        #print lowerbracket
        #print upperbracket
    
    if klow != kup: #two brackets
        index = array[1].index(klow)
        while array[1][index] == klow:
            for i in range(7):
                lowerbracket[i].append(array[i][index])
            index += 1
        index = array[1].index(kup)
        while array[1][index] == kup:
            for i in range(7):
                upperbracket[i].append(array[i][index])
            if index == len(array[1])-1:    #if kup is the last bracket in the file, need to terminate while loop in a different way
                break
            else:
                index += 1
        #print lowerbracket
        #print upperbracket
    
    return klow, kup, lowerbracket, upperbracket
    
def findTargetSize(bracket, targetvalues):
    #retrieves the required system size for given targetvalues
    Apercent = []   #holds five values: Q, TSS, TP, TN, GP 
    #loop through the five different targets    
    for i in range(len(targetvalues)):
        #find the value in the bracket
        targetmax = max(bracket[i+2])   #offset the index by 2
        #print targetmax        
        target = targetvalues[i]
        #print target
        if target > targetmax:      #if required target exceeds that of max, cannot design
            #print ".dcv designs cannot meet current target"
            Apercent.append(np.inf)
            continue
        lower = 0                   #initialize lower and upper variables
        upper = min(bracket[i+2])
        for j in range(len(bracket[i+2])):
            if target <= upper:
                continue
            lower = upper
            upper = bracket[i+2][j]
        #grab indices for Asystem in bracket[0]
        if lower == 0:       #but if the lower bound is zero, which isn't in the .dcv, go straight to interpolation
            Apercent.append(linearInterpolate(lower, upper, 0, bracket[0][0], target))
            continue
        mindex = bracket[i+2].index(lower)
        maxdex = mindex + 1
        Apercent.append(linearInterpolate(lower, upper, bracket[0][mindex], bracket[0][maxdex], target))
    #final Apercent has sizes for [Qreduction, TSSreduction, TPreduction, TNreduction, GPreduction]
    return Apercent

def getFinalSizeRequirement(klow, kup, minsizes, maxsizes, ksat):        
    #retrieves the final system size required based on two sets of sizes for the lower and upper kbracket
    if klow == kup:       #if there was only one bracket, no interpolation needed
        #print max(minsizes) #min and max sizes are identical        
        return max(minsizes)    #the maximum size among the brackets
        
    Apercent = []   #initialize possible areas
    for i in range(len(minsizes)):
        if minsizes[i] == np.inf or maxsizes[i] == np.inf:
            Apercent.append(np.inf)
        else:
            Apercent.append(linearInterpolate(klow, kup, minsizes[i], maxsizes[i], ksat))
    #print Apercent
    Afinal = max(Apercent)
    #print "Final Ap: "+str(Afinal)
    return float(Afinal)/100

def linearInterpolate(x0, x1, y0, y1, x):
    y = y0+(x - x0)*((y1 - y0)/(x1 - x0))    
    return y