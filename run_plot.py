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
import pylab


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


nIter = len(VilUniq)*100
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
node_GP_all = []
node_GP_lit = []
node_Vil_lit = []
node_Vil_unlit = []
node_Vil_all = []
GR_GP2Vil = nx.Graph()
for thisGP in GPUniq :
    thisGPID = int(thisGP[0])
    locThisGP = (thisGP[1],thisGP[2])
    node_GP_all.append(thisGPID)
    if thisGPID in valdictVilCon.values():
        GR_GP2Vil.add_node(thisGPID, pos = locThisGP, label = str(thisGPID), category = 'b')
        node_GP_lit.append(thisGPID)
        countGP2Lit += 1
    else:
        GR_GP2Vil.add_node(thisGPID, pos = locThisGP, label = str(thisGPID), category = 'b')

#    else:
#        GR_GP2Vil.add_node(thisGPID, pos = locThisGP, shape = "o", label = str(thisGPID), category = 'y')

    
    #locListGP.append(locThisGP)
    countGP += 1
    
for thisVil in VilUniq :
    thisVilID = int(thisVil[0])
    locThisVil = (thisVil[1],thisVil[2])
    node_Vil_all.append(thisVilID)
    if thisVilID in valdictVilCon.keys():
        GR_GP2Vil.add_node(thisVilID, pos = locThisVil, label = str(thisVilID), category = 'g')
        node_Vil_lit.append(thisVilID)
        countVilLit += 1
    else:
        GR_GP2Vil.add_node(thisVilID, pos = locThisVil, label = str(thisVilID), category = 'r' )
        node_Vil_unlit.append(thisVilID)
    #locListVil.append(locThisVil)
    countVil += 1


labels = nx.get_node_attributes(GR_GP2Vil, 'label')
labels = list(labels.values())
pos_nodes = nx.get_node_attributes(GR_GP2Vil,'pos')
color = nx.get_node_attributes(GR_GP2Vil, 'category')
color = list(color.values())
shapes = nx.get_node_attributes(GR_GP2Vil, 'shapes')
shapes = list(shapes.values())
node_labels = nx.get_edge_attributes(GR_GP2Vil,'weight')
label_pos = {k:[v[0]+0.005,v[1]+.005] for k,v in pos_nodes.iteritems()}
edges = list(valdictVilCon.items())
nx.draw_networkx_nodes(GR_GP2Vil,pos_nodes,nodelist=node_GP_lit, node_size=5, node_color = 'b',node_shape='o', linewidths = 0)
#nx.draw_networkx_nodes(GR_GP2Vil,pos_nodes,nodelist=node_GP_all, node_size=5, node_color = 'b',node_shape='o', linewidths = 0)
#nx.draw_networkx_nodes(GR_GP2Vil,pos_nodes,nodelist=node_Vil_all, node_size=20, node_color = 'r',node_shape='+', linewidths = 0.5)
nx.draw_networkx_nodes(GR_GP2Vil,pos_nodes,nodelist=node_Vil_lit, node_size=10, node_color = 'g',node_shape='D', linewidths = 0)
nx.draw_networkx_nodes(GR_GP2Vil,pos_nodes,nodelist=node_Vil_unlit, node_size=20, node_color = 'r',node_shape='+', linewidths = 0.5)
#nx.draw_networkx_labels(GR_GP2Vil,label_pos,font_size=3)
nx.draw_networkx_edges(GR_GP2Vil, pos_nodes, edges, width = 0.5)
plt.axis('on')
plt.xlabel('Latitude')
plt.ylabel('Longitude')
plt.ylim([77.1,77.7])

plt.legend(["Lit GPs","Connected Villages","Unconnected Villages"],prop={'size':9})



base_filename = sys.argv[1]
full_filename = os.getcwd() + '/Data/' +base_filename + '/'+base_filename+'.eps'

plt.savefig(full_filename, format='eps', dpi=5000)
#plt.show()

print ("complete")


# Generate a report
full_filename = os.getcwd() + '/Data/' +base_filename +'/Report.txt'
with open(full_filename, "w") as text_file:
    text_file.write("Total number of Villages: %s \n" % countVil)
    text_file.write("Total number of Villages connected: %s \n" % countVilLit)
    text_file.write("Total number of GPs: %s \n" % countGP)
    text_file.write("Total number of GPs used: %s \n" % countGP2Lit)
    text_file.write("Time taken for %s iterations is %s"%(nIter, (ts6-ts3)))
    text_file.write("\n Convergence conditions: \n")
    for item in maxIterTrial:
        text_file.write("%s " % item)
    #minIter = min(maxIterTrial)
    #maxIter = max(maxIterTrial)
    #avgIter = (sum(maxIterTrial) / float(len(maxIterTrial)))
    #text_file.write("\n(Min,Max,Avg): (%s,%s,%s) \n"%(minIter,maxIter,avgIter))
    text_file.write("\n Convergence values (number of Villages connected): \n")
    for item in maxRewTrial:
        text_file.write("%s " % item)
        
        

base_filename = sys.argv[1]
dir_name = os.getcwd() + '/Throughput files'
full_filename = os.path.join(dir_name, base_filename + "." + 'csv')

with open(full_filename, 'rb') as f:
    reader = csv.reader(f)
    readCSV = list(reader)
    
nameDist = readCSV[1][2]
conRatio = float(countVilLit)/countVil
        
    
rowDist = [nameDist,countVil,countVilLit,countGP,countGP2Lit,conRatio]
 
with open('Maharashtra.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(rowDist)
    
    
