from copy import copy 
import csv
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from snap import *
import time
from random import shuffle,sample,randint
from geopy.distance import vincenty
from Path_Loss import *
from func_5GHz import *

ts1 = time.time()

with open('497.csv', 'rb') as f:
    reader = csv.reader(f)
    readCSV = list(reader)
    
    
GPName = []
GPID = []
VilName = []
VilID =[]

nSamples = 20
begin = randint(1,(len(readCSV) - nSamples - 1))
begin = 25
end = begin + nSamples
#readCSV = readCSV[begin:end]
for row in readCSV:
	thisGP = row[4]+'_'+row[5]
	GPName.append(thisGP)
	thisVil = row[9]+'_'+row[10] 
	VilName.append(thisVil)
    
GPconv = pd.Series(GPName).astype('category')
GPID = GPconv.cat.codes
Vilconv = pd.Series(VilName).astype('category')
VilID = Vilconv.cat.codes + 1000
readCSV = np.insert(readCSV,4,GPID,axis=1)
readCSV = np.insert(readCSV,10,VilID,axis=1)
GPID = readCSV[1:,(4,5,6)]
GPID = [[float(y) for y in x] for x in GPID]
VilID = readCSV[1:,(10,11,12,8)]
VilID = [map(float,x) for x in VilID]

GPID = np.array(GPID)
b = np.ascontiguousarray(GPID).view(np.dtype((np.void, GPID.dtype.itemsize * GPID.shape[1])))
_, idx = np.unique(b, return_index=True)
GPUniq = GPID[idx]
maxThptCol = np.ones((len(GPUniq),1)) * GPThptVal
GPUniq = np.append(GPUniq,maxThptCol,axis = 1)


VilID = np.array(VilID)
b = np.ascontiguousarray(VilID).view(np.dtype((np.void, VilID.dtype.itemsize * VilID.shape[1])))
_, idx = np.unique(b, return_index=True)
VilUniq = VilID[idx]

for thisVil in VilUniq :
    thisVil[0] = thisVil[0] + 1000


ts2 = time.time()
print "\n Time taken for preprocessing : ", (ts2-ts1), "\n"

maxCountLinks = 0

dictVilToGPAll = {}

for thisVil in VilUniq :
    thisVilID = int(thisVil[0])
    thisVilLoc = (thisVil[1],thisVil[2])
    thisVilReqThpt = thisVil[3]
    #dictVilToGPAll[thisVilID] = [[thisVilLoc, thisVilReqThpt]]
    thisVilToGPList = {}
    for thisGP in GPUniq :
	thisGPID = int(thisGP[0])
	thisGPLoc = (thisGP[1],thisGP[2])
	thisDist = vincenty(thisGPLoc, thisVilLoc).km
	thisVilToGPList[thisGPID] = thisDist
    dictVilToGPAll[thisVilID] = thisVilToGPList
    
with open('DistMatrix.csv', 'wb') as csv_file:
    writer = csv.writer(csv_file)
    for key, value in dictVilToGPAll.items():
       writer.writerow([key, value])

	#if(thisDist < 5):
	    #thisLinkResult =  rf_get([thisGPLoc,thisVilLoc],[10,15],[3,6,9,12],thisVilReqThpt)
	    #thisLinkObtThpt = thisLinkResult[0][0]
	    #thisLinkSig = thisLinkResult[0][2] + NN_5_8
	#if(thisLinkObtThpt > thisVilReqThpt):
	    ##thisVilNoise = addIntf(thisVilNoise,thisLinkSig)
	    #thisVilToGPList[thisGPID] = thisLinkSig
    #if len(thisVilToGPList) > 0:
	##print thisVilToGPList
	#dictVilToGPAll[thisVilID].append(thisVilToGPList)
    #else:
	#del dictVilToGPAll[thisVilID]
