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

ts1 = time.time()

dictGPTxPow = {}
    
with open('/home/shubham/TVWS/BharatNet_GP_to_Villages/Data/512/dictGPTxPow.p', 'r') as dictGPTxPowFile:
    dictGPTxPow = pickle.load(dictGPTxPowFile)
    
dictVilToGPAll = {}

with open('/home/shubham/TVWS/BharatNet_GP_to_Villages/Data/512/dictVilToGPAll.p', 'r') as dictVilToGPAllFile:
    dictVilToGPAll = pickle.load(dictVilToGPAllFile)
#print dictVilToGPAll

with open('/home/shubham/TVWS/BharatNet_GP_to_Villages/Data/512/listGPCon.p', 'r') as listGPConFile:
    listGPCon = pickle.load(listGPConFile)
    
with open('/home/shubham/TVWS/BharatNet_GP_to_Villages/Data/512/GPUniq.p', 'r') as GPUniqFile:
    GPUniq = pickle.load(GPUniqFile)
    
with open('/home/shubham/TVWS/BharatNet_GP_to_Villages/Data/512/VilUniq.p', 'r') as VilUniqFile:
    VilUniq = pickle.load(VilUniqFile)
    
ts2 = time.time()
print "Time taken to load from file", (ts2-ts1)
    

keysVilAll = list(dictVilToGPAll.keys())
valLinkOnListVilSINR = []
vallistGPCon = [] 
valdictVilCon = {}
nIter = len(VilUniq)*1000

maxIterTrial = []
for trials in range(1):
    ts3 = time.time()
    maxIter = 0
    maxRew = 0
    dictGPSetTxPow = generate_GPPower(dictGPTxPow)
    for n in range(nIter):    
        ts4 = time.time()
        [dictGPSetTxPow,valdictVilCon] = calcNextVilList(dictGPSetTxPow,n,dictVilToGPAll,listGPCon,dictGPTxPow)
        Rew = len(valdictVilCon)
        if(Rew > maxRew):
            maxRew = Rew
            maxIter = n
        #ts5 = time.time()
        #print "Time taken for this iteration", (ts5-ts4)
    maxIterTrial.append(maxIter)
    ts6 = time.time()
    print "Time taken for ", (nIter), " iterations is ", (ts6-ts3)


[Rew,valdictVilCon,valdictGPThpt] = rewardSINR(dictGPSetTxPow,dictVilToGPAll)
#print valdictGPThpt
    
countGP = 0
countVil = 0
countGP2Lit = 0
countVilLit = 0

GR_GP2Vil = nx.Graph()
for thisGP in GPUniq :
    thisGPID = int(thisGP[0])
    locThisGP = (thisGP[1],thisGP[2])
    if thisGPID in valdictVilCon.values():
        GR_GP2Vil.add_node(thisGPID, pos = locThisGP, label = str(thisGPID), category = 'b')
        countGP2Lit += 1
    #locListGP.append(locThisGP)
    countGP += 1
    
for thisVil in VilUniq :
    thisVilID = int(thisVil[0])
    locThisVil = (thisVil[1],thisVil[2])
    if thisVilID in valdictVilCon.keys():
        GR_GP2Vil.add_node(thisVilID, pos = locThisVil, label = str(thisVilID), category = 'g')
        countVilLit += 1
    else:
	GR_GP2Vil.add_node(thisVilID, pos = locThisVil, label = str(thisVilID), category = 'r')
    #locListVil.append(locThisVil)
    countVil += 1



labels = nx.get_node_attributes(GR_GP2Vil, 'label')
labels = list(labels.values())
pos_nodes = nx.get_node_attributes(GR_GP2Vil,'pos')
color = nx.get_node_attributes(GR_GP2Vil, 'category')
color = list(color.values())
nx.draw_networkx_nodes(GR_GP2Vil,pos_nodes,node_size=5, node_color = color,linewidths = 0)
pos_labels = {k:[v[0],v[1]+.004] for k,v in pos_nodes.iteritems()}
nx.draw_networkx_labels(GR_GP2Vil,pos_labels,font_size=3)
edges = list(valdictVilCon.items())
#labels = nx.get_edge_attributes(GR_GP2Vil,'weight')
nx.draw_networkx_edges(GR_GP2Vil, pos_nodes, edges)
#nx.draw_networkx_edge_labels(GR_GP2Vil, pos, edge_labels = labels)
plt.axis('off')
plt.savefig("/home/shubham/TVWS/BharatNet_GP_to_Villages/Data/512/weighted_graph.pdf", dpi = 5000) # save as png
plt.show()


# Generate a report
with open("/home/shubham/TVWS/BharatNet_GP_to_Villages/Data/512/Report.txt", "w") as text_file:
    text_file.write("Time taken for %s iterations is %s \n" % (countVil,(ts6-ts3)))
    text_file.write("Total number of Villages: %s \n" % countVil)
    text_file.write("Total number of Villages connected: %s \n" % countVilLit)
    text_file.write("Total number of GPs: %s \n" % countGP)
    text_file.write("Total number of GPs used: %s \n" % countGP2Lit)
    text_file.write("Convergence conditions: \n")
    for item in maxIterTrial:
        text_file.write("%s " % item)
    
