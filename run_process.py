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


with open('/home/shubham/TVWS/BharatNet_GP_to_Villages/Data/512/dictGPSetTxPow.p', 'w') as dictGPSetTxPowFile:
    pickle.dump(dictGPSetTxPow, dictGPSetTxPowFile)
    
with open('/home/shubham/TVWS/BharatNet_GP_to_Villages/Data/512/valdictVilCon.p', 'w') as valdictVilConFile:
    pickle.dump(valdictVilCon, valdictVilConFile)
    