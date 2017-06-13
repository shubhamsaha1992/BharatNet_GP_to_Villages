# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 23:48:43 2017

@author: shubham
"""

from copy import copy 
import csv
import cPickle as pickle
import json
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
#from snap import *
import time
from random import shuffle,sample,randint
from geopy.distance import vincenty
from Path_Loss import *
from func_5GHz import *
import re
import sys

ts1 = time.time()

base_filename = sys.argv[1]
dir_name = os.getcwd() + '/Throughput files'
full_filename = os.path.join(dir_name, base_filename + "." + 'csv')
#full_filename = os.path.join(dir_name, base_filename)

with open(full_filename, 'rb') as f:
    reader = csv.reader(f)
    readCSV = list(reader)
    
for row in readCSV:
#	thisGP = row[4]+'_'+row[5]
#	GPName.append(thisGP)
	thisVil = row[9]+'_'+row[10] 
	VilName.append(thisVil)
    
    
base_filename = sys.argv[1]
dir_name = os.getcwd() + '/Throughput files/Maharashtra_input'
full_filename = os.path.join(dir_name, base_filename + "." + 'csv')
#full_filename = os.path.join(dir_name, base_filename)

with open(full_filename, 'rb') as f:
    reader = csv.reader(f)
    readCSV_GP = list(reader)
    
for row in readCSV_GP:
      thisGPCode = row[11]
	thisGP = row[8]+'_'+row[9]
	GPName.append(thisGP)
#	thisVil = row[9]+'_'+row[10] 
#	VilName.append(thisVil)
    
    
    
GPName = []
GPID = []
VilName = []
VilID =[]

#readCSV = sample(readCSV,50)
#nSamples = 50
#begin = randint(1,(len(readCSV) - nSamples - 1))
#begin = 25
#end = begin + nSamples
#readCSV = readCSV[begin:end]

GPconv = pd.Series(GPName).astype('category')
GPID = GPconv.cat.codes
Vilconv = pd.Series(VilName).astype('category')
VilID = Vilconv.cat.codes + 1000
readCSV_GP = np.insert(readCSV_GP,8,GPID,axis=1)
readCSV = np.insert(readCSV,10,VilID,axis=1)
GPID = readCSV_GP[1:,(8,9,10)]
GPID = [[float(y) for y in x] for x in GPID]
VilID = readCSV[1:,(10,11,12,8)]
VilID = [map(float,x) for x in VilID]

GPID = np.array(GPID)
b = np.ascontiguousarray(GPID).view(np.dtype((np.void, GPID.dtype.itemsize * GPID.shape[1])))
_, idx = np.unique(b, return_index=True)
GPUniq = GPID[idx]

VilID = np.array(VilID)
b = np.ascontiguousarray(VilID).view(np.dtype((np.void, VilID.dtype.itemsize * VilID.shape[1])))
_, idx = np.unique(b, return_index=True)
VilUniq = VilID[idx]

countGP = 0
countVil = 0
#locListGP = []
#locListVil = []



for thisVil in VilUniq :
    thisVil[0] = thisVil[0] + len(readCSV)
    #locListVil.append(locThisVil)


ts2 = time.time()
print "\n Time taken for preprocessing : ", (ts2-ts1), "\n"

#allDist = []
maxCountLinks = 0

dictVilToGPAll = {}
listGPCon = []
listVilCon = []
dictVilCon = []
dictGPTxPow = {}
#dummyCountVil = 1
for thisVil in VilUniq :
    thisVilID = int(thisVil[0])
    thisVilLoc = (thisVil[1],thisVil[2])
    thisVilReqThpt = thisVil[3]
    print (thisVilReqThpt)
    dictthisVilToGPSig = {}
    listthisVilGPCon = []
    #thisVilNoise = -200
    #dummyCountGP = 0
    for thisGP in GPUniq :
        thisGPID = int(thisGP[0])
        thisGPLoc = (thisGP[1],thisGP[2])
        thisDist = vincenty(thisGPLoc, thisVilLoc).km
        thisLinkObtThpt = 0
        thisLinkSig = -200
        if(thisDist < 5):
            thisLinkResult =  rf_get(base_filename,[thisGPLoc,thisVilLoc],[10,15],[3,6,9,12],thisVilReqThpt)
            thisLinkObtThpt = thisLinkResult[0][0]
            thisLinkSig = thisLinkResult[0][2] + NN_5_8
            thisLinkTxPow = thisLinkResult[0][1]
            if(thisLinkObtThpt > thisVilReqThpt):
                dictthisVilToGPSig[thisGPID] = [thisLinkSig,thisLinkTxPow]
                dictVilToGPAll[thisVilID] = [thisVilLoc, thisVilReqThpt]
            	#dictVilToGPAll[thisVilID].append(dictthisVilToGPSig)
            	listVilCon.append(thisVilID)
            	listthisVilGPCon.append(thisGPID)
                if thisGPID not in listGPCon:
                      listGPCon.append(thisGPID)
                      dictGPTxPow[thisGPID] = []
                dictGPTxPow[thisGPID].append(thisLinkTxPow)
    if(thisVilID in dictVilToGPAll.keys()):
        dictVilToGPAll[thisVilID].append(dictthisVilToGPSig)
        
ts3 = time.time()
print "\n Time taken for shortlisting GPs", (ts3-ts2), "\n"

base_foldername = base_filename

dir_name = os.getcwd() + '/Data/' + base_foldername +'/'

if not os.path.exists(dir_name):
    os.makedirs(dir_name)

base_filename = 'dictGPTxPow'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')
with open(full_filename, 'w') as dictGPTxPowFile:
    pickle.dump(dictGPTxPow, dictGPTxPowFile)

base_filename = 'dictVilToGPAll'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')    
with open(full_filename, 'w') as dictVilToGPAllFile:
    pickle.dump(dictVilToGPAll, dictVilToGPAllFile)

base_filename = 'listGPCon'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')  
with open(full_filename, 'w') as listGPConFile:
    pickle.dump(listGPCon, listGPConFile)

base_filename = 'GPUniq'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')     
with open(full_filename, 'w') as GPUniqFile:
    pickle.dump(GPUniq, GPUniqFile)
 
base_filename = 'VilUniq'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')    
with open(full_filename, 'w') as VilUniqFile:
    pickle.dump(VilUniq, VilUniqFile)

