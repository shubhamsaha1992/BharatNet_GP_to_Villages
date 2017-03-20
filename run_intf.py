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

#readCSV = sample(readCSV,50)
nSamples = 50
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
GPThptVal = 100
maxThptCol = np.ones((len(GPUniq),1)) * GPThptVal
GPUniq = np.append(GPUniq,maxThptCol,axis = 1)


VilID = np.array(VilID)
b = np.ascontiguousarray(VilID).view(np.dtype((np.void, VilID.dtype.itemsize * VilID.shape[1])))
_, idx = np.unique(b, return_index=True)
VilUniq = VilID[idx]
GR_GP2Vil = nx.Graph()

countGP = 0
countVil = 0
#locListGP = []
#locListVil = []

for thisGP in GPUniq :
    thisGPID = int(thisGP[0])
    locThisGP = (thisGP[1],thisGP[2])
    GR_GP2Vil.add_node(thisGPID, pos = locThisGP, label = str(thisGPID), category = 'g')
    #locListGP.append(locThisGP)
    countGP += 1
    

for thisVil in VilUniq :
    thisVil[0] = thisVil[0] + 1000
    thisVilID = int(thisVil[0])
    locThisVil = (thisVil[1],thisVil[2])
    GR_GP2Vil.add_node(thisVilID, pos = locThisVil, label = str(thisVilID), category = 'r')
    #locListVil.append(locThisVil)
    countVil += 1


ts2 = time.time()
print "\n Time taken for preprocessing : ", (ts2-ts1), "\n"

#allDist = []
maxCountLinks = 0

dictVilToGPAll = {}

#dummyCountVil = 1
for thisVil in VilUniq :
    thisVilID = int(thisVil[0])
    thisVilLoc = (thisVil[1],thisVil[2])
    thisVilReqThpt = thisVil[3]
    dictVilToGPAll[thisVilID] = [[thisVilLoc, thisVilReqThpt]]
    thisVilToGPList = {}
    #thisVilNoise = -200
    #dummyCountGP = 0
    for thisGP in GPUniq :
	thisGPID = int(thisGP[0])
	thisGPLoc = (thisGP[1],thisGP[2])
	thisDist = vincenty(thisGPLoc, thisVilLoc).km
	thisLinkObtThpt = 0
	thisLinkSig = -200
	if(thisDist < 5):
	    thisLinkResult =  rf_get([thisGPLoc,thisVilLoc],[10,15],[3,6,9,12],thisVilReqThpt)
	    thisLinkObtThpt = thisLinkResult[0][0]
	    thisLinkSig = thisLinkResult[0][2] + NN_5_8
	if(thisLinkObtThpt > thisVilReqThpt):
	    #thisVilNoise = addIntf(thisVilNoise,thisLinkSig)
	    thisVilToGPList[thisGPID] = thisLinkSig
    if len(thisVilToGPList) > 0:
	#print thisVilToGPList
	dictVilToGPAll[thisVilID].append(thisVilToGPList)
    else:
	del dictVilToGPAll[thisVilID]
    #dictVilToGPAll[thisVilID][0].append(thisVilNoise)
	    #dummyCountGP = dummyCountGP + 1
    #if(dummyCountGP > 0):
	#dummyCountVil = dummyCountVil * dummyCountGP
	#print dummyCountVil
	    
	    
#print dummyCountVil
#print dictVilToGPAll

ts3 = time.time()
print "\n Time taken for shortlisting GPs", (ts3-ts2), "\n"
keysVilAll = list(dictVilToGPAll.keys())
V_n = keysVilAll

valLinkOnListVilSINR = []
vallistGPCon = []
valdictVilCon = {}
for n in range(1000):
    
    ts4 = time.time()
    [V_n,valdictVilCon] = calcNextVilList(V_n,n,dictVilToGPAll,valLinkOnListVilSINR,vallistGPCon,valdictVilCon)
    
#print len(valdictVilCon.keys())
#edges = GR_GP2Vil.edges()
    
[Rew_V_n,valdictVilCon,valdictGPThpt] = rewardSINR(V_n,dictVilToGPAll,valLinkOnListVilSINR,vallistGPCon,valdictVilCon)    
print valdictGPThpt

labels = nx.get_node_attributes(GR_GP2Vil, 'label')
labels = list(labels.values())
pos = nx.get_node_attributes(GR_GP2Vil,'pos')
color = nx.get_node_attributes(GR_GP2Vil, 'category')
color = list(color.values())
nx.draw_networkx_nodes(GR_GP2Vil,pos,node_size=20, node_color = color,linewidths = 0)
nx.draw_networkx_labels(GR_GP2Vil,pos,font_size=5)

edges = list(valdictVilCon.items())
#labels = nx.get_edge_attributes(GR_GP2Vil,'weight')
nx.draw_networkx_edges(GR_GP2Vil, pos, edges)
#nx.draw_networkx_edge_labels(GR_GP2Vil, pos, edge_labels = labels)
plt.axis('off')
plt.savefig("weighted_graph.pdf", dpi = 2000) # save as png
plt.show()
    
