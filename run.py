from copy import copy 
import csv
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from snap import *
from random import shuffle,sample,randint
from geopy.distance import vincenty
from Path_Loss import *
from func_5GHz import *


with open('Akkalkuwa_GP2Village.csv', 'rb') as f:
    reader = csv.reader(f)
    readCSV = list(reader)
    
    
GPName = []
GPID = []
VilName = []
VilID =[]
nSamples = 50

#readCSV = sample(readCSV,50)
begin = randint(1,(len(readCSV) - nSamples - 1))
#begin = 1
end = begin + nSamples
readCSV = readCSV[begin:end]
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
	countGP = countGP + 1
	

for thisVil in VilUniq :
	thisVil[0] = thisVil[0] + 1000
	thisVilID = int(thisVil[0])
	locThisVil = (thisVil[1],thisVil[2])
	GR_GP2Vil.add_node(thisVilID, pos = locThisVil, label = str(thisVilID), category = 'r')
	#locListVil.append(locThisVil)
	countVil += 1

labels = nx.get_node_attributes(GR_GP2Vil, 'label')
labels = list(labels.values())
pos = nx.get_node_attributes(GR_GP2Vil,'pos')
color = nx.get_node_attributes(GR_GP2Vil, 'category')
color = list(color.values())
nx.draw_networkx_nodes(GR_GP2Vil,pos,node_size=20, node_color = color,linewidths = 0)
nx.draw_networkx_labels(GR_GP2Vil,pos,font_size=10)

#allDist = []
maxCountLinks = 0

#for row in readCSV[1:]:
	#thisGP = int(float(row[4]))
	#thisVil = int(float	(row[10]))
	#thisGPLoc = (float(row[5]), float(row[6]))
	#thisVilLoc = (float(row[11]), float(row[12]))	
	#thisDist = vincenty(thisGPLoc, thisVilLoc).km
	#allDist.append(thisDist)
	#linkResult =  rf_get( [thisGPLoc,thisVilLoc],[10,15],[3,6,9,12])
	#if(linkResult[0][0] > 0):
		#countLinks += 1
#print VilUniq
for i in range(0,1):
	countLinks = 0
	#shuffle(VilUniq)
	#shuffle(GPUniq)
	print "new run"
	GPUniq[:,3] = maxThptCol[:,0]	
	#print GPUniq	
	for thisVil in VilUniq :
		thisVilID = int(thisVil[0])
		thisVilLoc = (thisVil[1],thisVil[2])
		reqThpt = thisVil[3]
		thisVilIntf = 0
		thisVilSig = 0
		print "\n \n new Vil ", thisVil[0], "\w req. throughput", reqThpt
		#maxThpt = 0
		thisVilThpt = 0
		minGPThpt = GPUniq[0][3] # 100 Mbps
		GPwMinThpt = copy(GPUniq[0])
		GPwMinThpt_pt = []
		GPwMinThpt_pt = GPUniq[0]	
		for thisGP in GPUniq :
			thisGPID = int(thisGP[0])
			thisGPLoc = (thisGP[1],thisGP[2])
			thisDist = vincenty(thisGPLoc, thisVilLoc).km
			obtThpt = 0
			#print "new GP" ,thisGP[0]
			if(minGPThpt < reqThpt):
				GPwMinThpt = copy(thisGP) #copy
				GPwMinThpt_pt = []
				GPwMinThpt_pt = thisGP #pointer
				minGPThpt = GPwMinThpt[3]
				print "Limit exceeded, GPwMin switched to ",  GPwMinThpt[0], "minGPThpt", minGPThpt ," < ", reqThpt 
			if(thisDist < 5):
				print "GP within 5km"
				linkResult =  rf_get([thisGPLoc,thisVilLoc],[10,15],[3,6,9,12],reqThpt)
				obtThpt = linkResult[0][0]
				obtSNR = linkResult[0][2]
				thisGPThpt = thisGP[3]
				if(obtThpt > reqThpt):
					print "Link feasible \w ", thisGPID, "(thisGPThpt,GPwMinThpt,minGPThpt,SNR)" , thisGPThpt,GPwMinThpt[0],minGPThpt,obtSNR
					if(thisGPThpt < minGPThpt):
						print "Selecting ",thisGP[0]
						minGPThpt = thisGPThpt
						GPwMinThpt = copy(thisGP)
						GPwMinThpt_pt = []
						GPwMinThpt_pt = thisGP
					thisVilThpt = reqThpt
				else:
					print "Link infeasible \w, ", thisGPID, " obt (thpt,SNR) = ", obtThpt,obtSNR 
		if thisVilThpt > 0 :
			if GPwMinThpt[3] > thisVilThpt:
				print thisVil, " served by ", GPwMinThpt[0]
				GPwMinThpt[3] -= thisVilThpt
				GPwMinThpt_pt[3] -= thisVilThpt
				minGPThpt = GPwMinThpt[3] 
				countLinks += 1
				print "count links" , countLinks
				print "GPwMinThpt" , GPwMinThpt
				GR_GP2Vil.add_edge(GPwMinThpt[0], thisVilID)
				
		if countLinks > maxCountLinks:
			maxCountLinks = countLinks
			print "max count links" , maxCountLinks
	print GPUniq[:,(0,-1)]

countGPreq = 0
for thisGP in GPUniq:
	if(thisGP[-1] < 100):
		countGPreq += 1

for thisVil in VilUniq :
	thisVilID = int(thisVil[0])
	print "\n \n Village", thisVilID , " \n \n"
	thisVilLoc = (thisVil[1],thisVil[2])
	thisVilIntf = -200
	thisVilSig = -200
	thisVilSNR = -200
	thisVilSINR = -200
	for thisGP in GPUniq :
		thisGPID = int(thisGP[0])
		thisGPLoc = (thisGP[1],thisGP[2])
		thisDist = vincenty(thisGPLoc, thisVilLoc).km
		thisGPThpt = thisGP[-1]
		if(thisDist<5) &(thisGPThpt<100):
			linkResult = rf_get([thisGPLoc,thisVilLoc],[10,15],[3,6,9,12],reqThpt)
			obtSNR = linkResult[0][2]
			print "SNR from ", thisGPID, " to ", thisVilID, "is ", obtSNR 
			thisVilIntf = addIntf(thisVilIntf,(obtSNR + NN_5_8)) 
			if obtSNR > thisVilSNR :
				thisVilSNR = obtSNR
			print "(Sig,Intf,SNR,SINR) of ", thisVilID, "is", (thisVilSig,thisVilIntf,thisVilSNR,thisVilSINR)
		#print "(Sig,Intf,SNR,SINR) of ", thisVilID, "is", (thisVilSig,thisVilIntf,thisVilSNR,thisVilSINR)
	print "SINR calculated"
	thisVilSig = thisVilSNR + NN_5_8
	thisVilIntf = subIntf(thisVilIntf,thisVilSig)
	thisVilSINR = SINR(thisVilSig,thisVilIntf)
	print "(Sig,Intf,SNR,SINR) of ", thisVilID, "is", (thisVilSig,thisVilIntf,thisVilSNR,thisVilSINR)
	
print "countGP",countGP,"countVil",countVil,"maxCountLinks",maxCountLinks,"countGPreq",countGPreq


edges = GR_GP2Vil.edges()
#labels = nx.get_edge_attributes(GR_GP2Vil,'weight')
nx.draw_networkx_edges(GR_GP2Vil, pos, edges)
#nx.draw_networkx_edge_labels(GR_GP2Vil, pos, edge_labels = labels)
plt.axis('off')
plt.savefig("weighted_graph.png", dpi = 1000) # save as png
plt.show()
myfile = open('Mapping.csv', "wb")
wr = csv.writer(myfile)
wr.writerows(readCSV)
