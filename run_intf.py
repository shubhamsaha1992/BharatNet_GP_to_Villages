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
dictVilToGPAll = {}


base_filename = sys.argv[1]
dir_name = os.getcwd() + '/Data/' +base_filename
full_filename = os.getcwd() + '/Data/' +base_filename+ '/dictGPSetTxPow.p'

if not os.path.exists(full_filename):
    sys.exit(full_filename + " doesn't exist. Next file trying.")

#if not os.path.exists(dir_name):
#    sys.exit(dir_name + " doesn't exist. Next file trying.")
    
base_filename = 'dictGPTxPow'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')
with open(full_filename, 'r') as dictGPTxPowFile:
    dictGPTxPow = pickle.load(dictGPTxPowFile)
    

base_filename = 'dictVilToGPAll'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')    
with open(full_filename, 'r') as dictVilToGPAllFile:
    dictVilToGPAll = pickle.load(dictVilToGPAllFile)

base_filename = 'listGPCon'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')  
with open(full_filename, 'r') as listGPConFile:
    listGPCon = pickle.load(listGPConFile)

base_filename = 'GPUniq'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')     
with open(full_filename, 'r') as GPUniqFile:
    GPUniq = pickle.load(GPUniqFile)
 
base_filename = 'VilUniq'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')    
with open(full_filename, 'r') as VilUniqFile:
    VilUniq = pickle.load(VilUniqFile)
    
ts2 = time.time()
print "Time taken to load from file", (ts2-ts1)
    

keysVilAll = list(dictVilToGPAll.keys())
valLinkOnListVilSINR = []
vallistGPCon = [] 
valdictVilCon = {}


nIter = len(VilUniq)*10
ts3 = time.time()
maxIterTrial = []
maxRewTrial = []
#for trials in range(1):
#    ts3 = time.time()
#    maxIter = 0
#    maxRew = 0
#    dictGPSetTxPow = generate_GPPower(dictGPTxPow)
#    for n in range(nIter):    
#        ts4 = time.time()
#        [dictGPSetTxPow,valdictVilCon] = calcNextVilList(dictGPSetTxPow,n,dictVilToGPAll,dictGPTxPow)
#        Rew = len(valdictVilCon)
#        if(Rew > maxRew):
#            maxRew = Rew
#            maxIter = n
#        #ts5 = time.time()
#        #print "Time taken for this iteration", (ts5-ts4)
#    maxIterTrial.append(maxIter)
#    maxRewTrial.append(maxRew)
#    ts6 = time.time()
#    print "Time taken for ", (nIter), " iterations is ", (ts6-ts3)
    
ts6 = time.time()

base_filename = 'dictGPSetTxPow'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')        
with open(full_filename, 'r') as dictGPSetTxPowFile:
    dictGPSetTxPow = pickle.load(dictGPSetTxPowFile)

base_filename = 'valdictVilCon'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')    
with open(full_filename, 'r') as valdictVilConFile:
    valdictVilCon = pickle.load(valdictVilConFile)

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

[dictGPSetTxPow,_] = localOpt(dictGPSetTxPow,dictGPTxPow,dictVilToGPAll)


[Rew,valdictVilCon,valdictGPThpt] = rewardSINR(dictGPSetTxPow,dictVilToGPAll)






labels = nx.get_node_attributes(GR_GP2Vil, 'label')
labels = list(labels.values())
pos_nodes = nx.get_node_attributes(GR_GP2Vil,'pos')
color = nx.get_node_attributes(GR_GP2Vil, 'category')
color = list(color.values())
node_labels = nx.get_edge_attributes(GR_GP2Vil,'weight')
label_pos = {k:[v[0]+0.005,v[1]+.005] for k,v in pos_nodes.iteritems()}
edges = list(valdictVilCon.items())
nx.draw_networkx_nodes(GR_GP2Vil,pos_nodes,node_size=5, node_color = color,linewidths = 0)
nx.draw_networkx_labels(GR_GP2Vil,label_pos,font_size=3)
nx.draw_networkx_edges(GR_GP2Vil, pos_nodes, edges)

    
