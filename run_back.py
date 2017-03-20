from copy import copy 
import csv
import math
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np
import pandas as pd
from scipy.signal import argrelextrema
from snap import *
from random import shuffle
from geopy.distance import vincenty
from Path_Loss import *
from pse_2 import *


with open('Akkalkuwa_Part_GP2Village.csv', 'rb') as f:
    reader = csv.reader(f)
    readCSV = list(reader)
    
    
GPName = []
GPID = []
VilName = []
VilID =[]

    
for row in readCSV:
	thisGP = row[4]+'_'+row[5]
	GPName.append(thisGP)
	thisVil = row[9]+'_'+row[10] 
	VilName.append(thisVil)
    
GPconv = pd.Series(GPName).astype('category')
GPID = GPconv.cat.codes
GPID[0] = 'GP_ID'

Vilconv = pd.Series(VilName).astype('category')
VilID = Vilconv.cat.codes + 1000
VilID[0] = 'Village_ID'
readCSV = np.insert(readCSV,4,GPID,axis=1)
readCSV = np.insert(readCSV,10,VilID,axis=1)
GPID = readCSV[1:,(4,5,6,7)]
GPID = np.array(GPID)
GPName = np.reshape(np.array(GPName[1:]),(len(GPName[1:]),1))
GPID = np.append(GPID,GPName,axis = 1)
#GPID = [[float(y) for y in x] for x in GPID[:,:-2]]
VilID = readCSV[1:,(10,11,12,8)]
VilID = np.array(VilID)
VilName = np.reshape(np.array(VilName[1:]),(len(VilName[1:]),1))
VilID = np.append(VilID,VilName,axis = 1)
#VilID = [map(float,x) for x in VilID[:,:-2]]

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
locListGP = []
locListVil = []

for thisGP in GPUniq :
	thisGPID = int(thisGP[0])
	locThisGP = (thisGP[1],thisGP[2])
	GR_GP2Vil.add_node(thisGPID, pos = locThisGP, category = 'g')
	locListGP.append(locThisGP)
	countGP = countGP + 1
	
print "countGP", countGP
	

for thisVil in VilUniq :
	thisVil[0] = int(thisVil[0]) + 1000
	thisVilID = int(thisVil[0])
	locThisVil = (thisVil[1],thisVil[2])
	GR_GP2Vil.add_node(thisVilID, pos = locThisVil, category = 'r')
	locListVil.append(locThisVil)
	countVil += 1

allDist = []
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
	print GPUniq
	print "new run"
	GPUniq[:,3] = maxThptCol[:,0]	
	#print GPUniq	
	for thisVil in VilUniq :
		thisVilID = int(thisVil[0])
		thisVilLoc = (thisVil[1],thisVil[2])
		reqThpt = thisVil[3]
		print "\n \n new Vil ", thisVil[0], "\w throughput", reqThpt
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
				latlongPair = [thisGPLoc,thisVilLoc]
				latlongPair= [map(float,x) for x in latlongPair]
				linkResult =  rf_get(latlongPair,[10,15],[3,6,9,12])
				obtThpt = linkResult[0][0]
				obtSNR = linkResult[0][2]
				thisGPThpt = thisGP[3]
				if(obtThpt > reqThpt):
					print "Link feasible \w ", thisGPID, "(thisGPThpt,GPwMinThpt,minGPThpt)" , thisGPThpt,GPwMinThpt[0],minGPThpt
					if(thisGPThpt < minGPThpt):
						print "Selecting ",thisGP[0]
						minGPThpt = thisGPThpt
						GPwMinThpt = copy(thisGP)
						GPwMinThpt_pt = []
						GPwMinThpt_pt = thisGP
					thisVilThpt = reqThpt
				else:
					print "Link infeasible, obt (thpt,SNR) = ", obtThpt,obtSNR 
		if thisVilThpt > 0 :
			if GPwMinThpt[3] > thisVilThpt:
				print thisVil[0], " served by ", GPwMinThpt[0]
				GPwMinThpt[3] -= thisVilThpt
				GPwMinThpt_pt[3] -= thisVilThpt
				minGPThpt = GPwMinThpt[3] 
				countLinks += 1
				print "count links" , countLinks
				print "GPwMinThpt",GPwMinThpt
				GR_GP2Vil.add_edge(GPwMinThpt[0], thisVilID)
				
		if countLinks > maxCountLinks:
			maxCountLinks = countLinks
			print "max count links" , maxCountLinks
	# Please remove the extra last column
	print GPUniq[:,(0,-2)]


		

print countGP, countVil	, maxCountLinks	

pos = nx.get_node_attributes(GR_GP2Vil,'pos')
color = nx.get_node_attributes(GR_GP2Vil, 'category')
color = list(color.values())
nx.draw_networkx_nodes(GR_GP2Vil,pos,node_size=10, node_color = color,linewidths = 0)
edges = GR_GP2Vil.edges()
labels = nx.get_edge_attributes(GR_GP2Vil,'weight')
nx.draw_networkx_edges(GR_GP2Vil, pos, edges)
#nx.draw_networkx_edge_labels(GR_GP2Vil, pos, edge_labels = labels)
plt.axis('off')
plt.savefig("weighted_graph.png", dpi = 1000) # save as png
plt.show()
myfile = open('Mapping.csv', "wb")
wr = csv.writer(myfile)
wr.writerows(readCSV)
