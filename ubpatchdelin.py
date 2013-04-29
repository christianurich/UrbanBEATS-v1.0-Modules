# -*- coding: utf-8 -*-
"""
@file
@author  Peter M Bach <peterbach@gmail.com>
@version 1.0
@section LICENSE

This file is part of UrbanBEATS (www.urbanbeatsmodel.com)
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

def landscapePatchDelineation(landuse, elevation, soil):
    #Performs patch analysis and returns a full dictionary of the patches found, their properties
    #and all points contained therein to allow them to be drawn.
    #Inputs:
    #   - landuse: a square matrix of the landscape's land use classification
    #   - elevation: a matrix of the landscape's elevation (georeferenced to the land use map)
    #   - soil: a matrix of the landscape's soil (georeferenced to the land use map)
    #   - nhd: the neighbourhood to use in the cellular automata
    
    patchdict = {}      #Holds the collection of patches labelled according to their IDs
    
    #Test Condition for delineation:
    x = len(landuse)
    y = x
    richness = 0
    landusetypes = []
    landusecount = 0
    for i in range(x):
        for j in range(y):
            if landuse[i][j] == -9999:
                continue
            landusecount += 1
            if landuse[i][j] in landusetypes:
                pass
            else:
                landusetypes.append(landuse[i][j])
                richness += 1
    if richness == 0:
        return patchdict
    elif richness == 1:
        #average out the elevation and soil
        elev_sum = 0
        elev_n = 0
        soil_sum = 0
        soil_n = 0
        for i in range(x):
            for j in range(y):
                if elevation[i][j] != -9999:
                    elev_sum += elevation[i][j]
                    elev_n += 1
                if soil[i][j] != -9999:
                    soil_sum += soil[i][j]
                    soil_n += 1
        if elev_n == 0:
            patchelev = -9999
        else:
            patchelev = elev_sum/elev_n
        
        if soil_n == 0:
            patchsoil = -9999
        else:
            patchsoil = soil_sum/soil_n
        patchdict["PatchID1"] = [landusecount, landusetypes[0],patchelev, patchsoil, [[0,0],[1,0],[1,1],[0,1]]]
        return patchdict
    
    #else, do patch delineation, continue
    patchIDcounter = 0
    finished_sign = 0
    
    #Generate Status Matrix
    statusmatrix = createZerosMatrix(x, y)
    
    landpatchfreq = [0,0,0,0,0,0,0,0,0,0,0,0,0]
    
    while finished_sign == 0:
        point_found = 0
        
        #Step 1: Find the start position and note the coordinate
        xpos, ypos = findNextStart(statusmatrix)        #returns positions in matrix if point found, otherwise -1
        patchface = [[xpos, ypos], [xpos+1, ypos], [xpos+1, ypos+1], [xpos, ypos+1]]
        
        #Check whether finished going through status matrix
        if xpos == -1:
            finished_sign = 1
            break
        
        #Step 2: Conduct Cellular Automata from irow, jcol
        statusmatrix[xpos][ypos] = 1    #mark out this position on the status matrix
        currentCALU = landuse[xpos][ypos]       #will need this later, so define this now.
        
        camatrix, patcharea = patchCellularAutomata(x,y,xpos, ypos, statusmatrix, landuse, currentCALU)   #Run the CA Algo
        
        #Update status matrix with new data from CAMatrix and process the patch data in CAMatrix
        patchIDcounter += 1     #Increment by one because we definitely have a new patch
        for iCA in range(len(statusmatrix[0])):
            for jCA in range(len(statusmatrix[0])):
                if statusmatrix[iCA][jCA] == 1:
                    continue
                else:
                    statusmatrix[iCA][jCA] = camatrix[iCA][jCA]
        
        #Grab elevation and soil data
        elevation_tally = 0             #reset the tally
        elev_patch_counter = 0          #counts the number of cells
        soil_tally = 0                      #reset tally
        soil_patch_counter = 0          #counts the number of valid soil cells
        
        #---- CODE NOT USED DUE TO LARGE COMPUTATIONAL REQUIREMENTS IN URBANBEATS ---
        #patchedges = []
        #---- CODE NOT USED DUE TO LARGE COMPUTATIONAL REQUIREMENTS IN URBANBEATS ---
        
        for iCA in range(len(camatrix[0])):
            for jCA in range(len(camatrix[0])):
                if camatrix[iCA][jCA] == 0:
                    continue
                if elevation[iCA][jCA] != -9999:
                    elevation_tally += elevation[iCA][jCA]
                    elev_patch_counter += 1
                if soil[iCA][jCA] != -9999:
                    soil_tally += soil[iCA][jCA]
                    soil_patch_counter += 1
                
                #---- CODE NOT USED DUE TO LARGE COMPUTATIONAL REQUIREMENTS IN URBANBEATS ---
                #patchedges.append([[iCA, jCA],[iCA+1, jCA]])
                #patchedges.append([[iCA, jCA],[iCA, jCA+1]])
                #patchedges.append([[iCA+1, jCA], [iCA+1, jCA+1]])
                #patchedges.append([[iCA, jCA+1], [iCA+1, jCA+1]])
                #---- CODE NOT USED DUE TO LARGE COMPUTATIONAL REQUIREMENTS IN URBANBEATS ---
                
        #---- CODE NOT USED DUE TO LARGE COMPUTATIONAL REQUIREMENTS IN URBANBEATS ---
        #The following code runs through the entire patch's edges and returns the points
        #that make up the outer edges of the patch, allowing you to draw the rectilinear polygon
        #outeredges = []
        #while len(patchedges) > 0:
        #    currentedge = patchedges[0]            
        #    patchedges.remove(currentedge)
        #    if currentedge in patchedges:
        #        for j in range(len(patchedges)):
        #            try:
        #                patchedges.remove(currentedge)
        #            except ValueError as e:
        #                pass
        #    else:
        #        outeredges.append(currentedge)
        #        print outeredges
        # 
        #outeredges.sort()
        #sortededges = []
        #sortededges.append(outeredges[0])
        #outeredges.remove(sortededges[0])
        #while len(outeredges) > 0:
        #    currentedge = sortededges[len(sortededges)-1]   #max
        #    for edge in outeredges:
        #        print edge
        #        print edge[0]                
        #        if currentedge[1] in edge or currentedge[0] in edge:
        #            sortededges.append(edge)
        #            outeredges.remove(edge)
        #
        #finalpoints = []
        #for i in range(len(sortededges)):
        #    if i < len(sortededges)-1:            
        #        nexti = i+1
        #    else:
        #        nexti = 0
        #    if sortededges[i][0] not in sortededges[nexti]:
        #        finalpoints.append(sortededges[i][0])
        #    else:
        #        finalpoints.append(sortededges[i][1])
        #---- CODE NOT USED DUE TO LARGE COMPUTATIONAL REQUIREMENTS IN URBANBEATS ---
        
        if elev_patch_counter == 0:
            patchelev = -9999        
        else:
            patchelev = elevation_tally/elev_patch_counter
        if soil_patch_counter == 0:
            patchsoil = -9999
        else:
            patchsoil = soil_tally/soil_patch_counter
        
        patchdict["PatchID"+str(patchIDcounter)] = [patcharea, currentCALU, patchelev, patchsoil, patchface]
        #Next iteration
    
    #END OF WHILE LOOP
    del camatrix
    del statusmatrix
    return patchdict

def createZerosMatrix(x, y):
    zerosmatrix = []
    for i in range(x):
        zerosmatrix.append([])
        for j in range(y):
            zerosmatrix[i].append(0)
    return zerosmatrix

def findNextStart(statusmatrix):
    point_found = 0    
    for iCA in range(len(statusmatrix[0])):
        for jCA in range(len(statusmatrix[0])):
            if point_found == 1:
                break
            if statusmatrix[iCA][jCA] == 0:
                point_found = 1
                irow = iCA
                jcol = jCA
                #print "Next starting point: ", iCA,",", jCA
                return irow, jcol
            else:
                point_found = 0
    if point_found == 0:
        return -1, -1

def patchCellularAutomata(x, y, xpos, ypos, statusmatrix, landuse, currentCALU):
    #print "CurrentLUC:", currentCALU
    camatrix = createZerosMatrix(x, y)     #Create the cellular automata matrix
    camatrix[xpos][ypos] = 1               #mark the first cell in CAmatrix for CA algorithm
    patch_area_previous = 0
    patch_area_current = -9999  #Initialize
    
    while patch_area_current != patch_area_previous:
        patch_area_previous = patch_area_current
        camatrix_new = camatrix
        for iCA in range(len(camatrix[0])):
            for jCA in range(len(camatrix[0])):
                #check if current cell's value is identical to currentCALU
                if statusmatrix[iCA][jCA] == 1:         #If the cell's already been considered, skip
                    continue
                if landuse[iCA][jCA] != currentCALU:    #If the cell's land use is not the same as current, skip
                    continue
                
                #Get Cell's Neighbourhood
                if jCA == 0:
                    dx = [0,1]                  #if we have first column then only forward
                elif jCA == (len(camatrix[0])-1):
                    dx = [-1,0]             #if we have last column then only backward
                else:
                    dx = [-1,0,1]           #otherwise allow both

                if iCA == 0:
                    dy = [0,1]                  #if we have top row, only move down
                elif iCA == (len(camatrix[0])-1):
                    dy = [-1,0]             #if we have bottom row, only move up
                else:
                    dy = [-1,0,1]           #otherwise allow both

                #Transfer Function - obtain the total sum of neighbours
                total_neighbour_sum = 0
                for a in dy:
                    for b in dx:
                        total_neighbour_sum += camatrix[iCA+a][jCA+b]
                
                #Determine if the cell belongs to the patch or not
                if total_neighbour_sum >= 1:
                    camatrix_new[iCA][jCA] = 1
                else:
                    camatrix_new[iCA][jCA] = 0
                
        camatrix = camatrix_new         #Transfer old camatrix into new one
        patch_area_current = 0          #Initialize the current patch area
        for i in range(len(camatrix[0])):       #Calculate the current patch area
            patch_area_current += sum(camatrix[i])
    
    return camatrix, patch_area_current
    

