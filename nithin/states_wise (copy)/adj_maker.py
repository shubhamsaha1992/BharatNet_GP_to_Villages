from __future__ import print_function
import itertools
import sys
import csv
import math
import numpy as np
import os

## SETTINGS are defined here
##distance for adjacency matrix (5-10kms)
REF_DIST = 5

##Indexes in latlongRAW.npy
GP_CODE_IDX = 4
GPN_IDX = 3
LAT_IDX = 5
LONG_IDX = 6
BLK_IDX = 2
DC_IDX = 1
PHASE_IDX = 7
ST_IDX=0
TP_IDX =8

##calculates distance between two given points
def latlongdist(L1, L2):
    #print type(L1),L1 
    L1_rad = np.radians(np.array(L1))
    L2_rad = np.radians(np.array(L2))

    dlat = L1_rad[0]-L2_rad[0]
    dlon = L1_rad[1]-L2_rad[1]


    
    a = (np.sin(dlat/2.0)**2)+(np.cos(L1_rad[0])*np.cos(L2_rad[0])*np.sin(dlon/2.0)**2)
    c = 2*math.atan2(np.sqrt(a), np.sqrt(1-a))
    return c*6371000

##Prepares adjacency matrix 
def make_adjacency(REF_DIST,filename,input_file):
    
    # LOAD states data from pickle
    all_data = np.load('latlongraw/latlongRAW_'+str(input_file)+'.npy')
    states_data = all_data[0]
    states_list = all_data[1]
    # print ("")

    # Variables to hold results
    finalStates=[] 
    finalAdj=[]
    finalGPs=[] 
    finalPHASEs=[]
    finalDist=[]
    finalDC=[]
    finalBlocks=[]
    finalLatLong=[]
    finalTPreq=[]
    finalGPNames=[]

    # Calculation of adjacency matrix
    k = 0
    print('The number of districts :{}'.format(len(states_data)))
    #exit()
    for mat in states_data:
        # VISUAL que
        # print (mat[0,1])
        # exit()
        print ('{} Processing district_code:{} of {}\r\nNumber of GPs : {}\r\n\r\n'.format( k, mat[0,DC_IDX], mat[0,ST_IDX], mat.shape[0]) )
        
        rows, cols =mat.shape         
        print (rows,cols)
        # TEMPORARY variables
        adjMat = np.zeros((rows,rows),dtype=int)
        distMat = np.zeros((rows,rows),dtype=int)
        GPs = []
        PHASEs = []
        DCs = []
        Block = []
        TPreq =[]
        GPNames = []
        # latlong 2 distance converion
        for i in range(rows):
            latlong_i = []
            latlong_i.append(float(mat[i,LAT_IDX]))
            latlong_i.append(float(mat[i,LONG_IDX]))
            
            ## Also keep saving the GP Codes
            GPs.append(mat[i,GP_CODE_IDX])
            PHASEs.append(int(mat[i,PHASE_IDX]))
            DCs.append(mat[i,DC_IDX])
            Block.append(int(mat[i,BLK_IDX]))
            TPreq.append(mat[i,TP_IDX])
            GPNames.append(mat[i,GPN_IDX])
            finalLatLong.append(latlong_i)
            for j in range(i,rows):
                latlong_j = []

                # NON-Diagonal elements
                if not i==j:
                    
                    latlong_j.append(float(mat[j,LAT_IDX]))
                    latlong_j.append(float(mat[j,LONG_IDX]))

                    #print ('LL1 : {}, LL2 :{}'.format(latlong_i, latlong_j)) 
                    d = latlongdist(latlong_i, latlong_j)
                    #print('The distance is : {} km'.format(d))
                    distMat[i,j] = int(d)
                    distMat[j,i] = int(d)

                    if (d > REF_DIST*1000):
                        adjMat[i,j]=0
                        adjMat[j,i]=0
                       
                    else:
                         adjMat[i,j]=1
                         adjMat[j,i]=1
                # Diagonal elements kept 1 in adjMAT and distance matrix 0   
                else:   
                    adjMat[i,i]=1
                    distMat[i,i]=0
            if rows>1:
                print ('Completed: {:.2f}% '.format((i*(rows-i) +(i*(i+1)/2.0) )/((rows*(rows-1))/2.0)*100),end='\r')
            sys.stdout.flush
            
        
        finalDC.append(DCs)
        finalDist.append(distMat)
        finalPHASEs.append(PHASEs)
        finalGPs.append(GPs)
        finalAdj.append(adjMat)
        finalStates.append(states_list[0])
        finalTPreq.append(TPreq)
        finalBlocks.append(Block)
        finalGPNames.append(GPNames)
        
        # print (finalPHASEs)
        # for i in range(rows):
        #     if(finalPHASEs[0][i]==9):
        #         for j in range(rows):
        #             if(i!=j and finalPHASEs[0][j]==2):          ##if its not a diagonal element and rx is phase 2 element
        #                 if(distMat[i,j] < 300.0):
        #                     adjMat[i,j] = 0
        #                     adjMat[j,i] = 0
        #                     finalPHASEs[0][j]=8
        #                     print ("status 8 matrix")
        print (finalPHASEs)
        # New addition to ensure no two phase 2 GPs connect with each other                
        for i in range(rows):
            if (finalPHASEs[0][i]==15):
                adjMat[i,:]=0
                adjMat[:,i]=0
            elif (finalPHASEs[0][i]==2):
                for j in range(rows):
                    if (finalPHASEs[0][j]==2):
                        adjMat[i,j] = 0
                        adjMat[j,i] = 0

                # print ("making row and column 0 in adj mat for", GPNames[0][i])


        if len(adjMat) == len(GPs):
            print ('{} data len {}'.format(mat[0,DC_IDX],len(adjMat)))
        #finalDist.append[distmat]
        #finalredDist.append[reddistmat]
        k=k+1
    # print('Final size of Adjacency matrix : {}'.format(finalAdj))
    if not os.path.exists('adjmat'):
        os.makedirs('adjmat')
    name = 'adjmat/AD_mat_{}_{}'.format(input_file,REF_DIST)
    np.save(name, np.array([finalAdj, finalStates, finalGPs, finalPHASEs, finalDist, finalDC,finalLatLong,finalTPreq,finalBlocks,finalGPNames]))
    return name




if __name__ == '__main__':
    #print latlongdist([38.8985, -77.0378],[38.8971, -77.0439])a
    make_adjacency(REF_DIST,'latlongRAW.npy',6)
