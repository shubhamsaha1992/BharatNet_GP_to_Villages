# -*- coding: utf-8 -*-
"""
Created on Wed Apr 19 05:11:26 2017

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
import sys

ts1 = time.time()

dictGPTxPow = {}
dictVilToGPAll = {}

base_filename = sys.argv[1]
dir_name = os.getcwd() + '/Data/' +base_filename

if not os.path.exists(dir_name):
    sys.exit(dir_name + " doesn't exist. Next file trying.")
    

#full_filename = os.getcwd() + '/Data/' +base_filename+ '/dictGPSetTxPow.p'
#if os.path.exists(full_filename):
#    sys.exit(full_filename + " already exist. Next file trying.")
    
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

maxIterTrial = []
maxRewTrial = []
for trials in range(1):
    ts3 = time.time()
    maxIter = 0
    maxRew = 0
    dictGPSetTxPow = generate_GPPower(dictGPTxPow)
    for n in range(nIter):    
        ts4 = time.time()
        [dictGPSetTxPow,valdictVilCon] = calcNextVilList(dictGPSetTxPow,n,dictVilToGPAll,dictGPTxPow)
        Rew = len(valdictVilCon)
        if(Rew > maxRew):
            maxRew = Rew
            maxIter = n
        #ts5 = time.time()
        #print "Time taken for this iteration", (ts5-ts4)
    maxIterTrial.append(maxIter)
    maxRewTrial.append(maxRew)
    ts6 = time.time()
    print "Time taken for ", (nIter), " iterations is ", (ts6-ts3)

base_filename = 'dictGPSetTxPow'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')     
with open(full_filename, 'w') as dictGPSetTxPowFile:
    pickle.dump(dictGPSetTxPow, dictGPSetTxPowFile)
    
 
base_filename = 'valdictVilCon'
full_filename = os.path.join(dir_name, base_filename + "." + 'p')    
with open(full_filename, 'w') as valdictVilConFile:
    pickle.dump(valdictVilCon, valdictVilConFile)




    