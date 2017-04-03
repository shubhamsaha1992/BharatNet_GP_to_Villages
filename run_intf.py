from copy import copy 
import csv
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



keysVilAll = list(dictVilToGPAll.keys())
V_n = keysVilAll
dictGPSetTxPow = generate_GPPower(listGPCon,dictGPTxPow)
valLinkOnListVilSINR = []
vallistGPCon = [] 
valdictVilCon = {}
for n in range(1000):
    
    ts4 = time.time()
    [V_n,valdictVilCon] = calcNextVilList(V_n,dictGPSetTxPow,n,dictVilToGPAll,valLinkOnListVilSINR,listGPCon,vallistGPCon,valdictVilCon,dictGPTxPow)
#print len(valdictVilCon.keys())
#edges = GR_GP2Vil.edges()
    
[Rew_V_n,valdictVilCon,valdictGPThpt] = rewardSINR(V_n,dictGPSetTxPow,dictVilToGPAll,valLinkOnListVilSINR,vallistGPCon,valdictVilCon)    
print valdictGPThpt

for thisGP in GPUniq :
    thisGPID = int(thisGP[0])
    locThisGP = (thisGP[1],thisGP[2])
    if thisGPID in valdictVilCon.values():
	GR_GP2Vil.add_node(thisGPID, pos = locThisGP, label = str(thisGPID), category = 'b')
    #locListGP.append(locThisGP)
    countGP += 1

for thisVil in VilUniq :
    thisVilID = int(thisVil[0])
    locThisVil = (thisVil[1],thisVil[2])
    if thisVilID in valdictVilCon.keys():
	GR_GP2Vil.add_node(thisVilID, pos = locThisVil, label = str(thisVilID), category = 'g')
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
plt.savefig("weighted_graph.pdf", dpi = 5000) # save as png
plt.show()


# Generate a report
with open("Report.txt", "w") as text_file:
    text_file.write("Total number of Villages: %s" % countVil)
    text_file.write("Total number of Villages connected: %s" % Rew_V_n)
    text_file.write("Total number of GPs: %s" % countGP)
    text_file.write("Total number of GPs used: %s" % len(vallistGPCon))
    
