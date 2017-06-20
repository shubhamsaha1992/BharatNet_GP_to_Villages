# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 18:44:01 2017

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

GPName = []
GPID = []
VilName = []
VilID =[]


base_filename = sys.argv[1]
dir_name = os.getcwd() + '/Throughput files/Pipeline'
full_filename = os.path.join(dir_name, base_filename + "." + 'csv')
#full_filename = os.path.join(dir_name, base_filename)

print "Running count for ", base_filename

with open(full_filename, 'rb') as f:
    reader = csv.reader(f)
    readCSV_Vil = list(reader)
    
for row in readCSV_Vil:
	thisVil = row[13]+'_'+row[14] 
	VilName.append(thisVil)
    
    
base_filename = sys.argv[1] + '_1'
dir_name = os.getcwd() + '/Throughput files/1'
full_filename = os.path.join(dir_name, base_filename + "." + 'csv')
#full_filename = os.path.join(dir_name, base_filename)

base_filename = sys.argv[1]

with open(full_filename, 'rb') as f:
    reader = csv.reader(f)
    readCSV_GP = list(reader)
    
GPName = []

for row_GP in readCSV_GP:
    thisGPCode = row_GP[11]
    if thisGPCode not in ['2','21']:
        readCSV_GP.remove(row_GP)
      
for row_GP in readCSV_GP:
    thisGPCode = row_GP[11]
    if thisGPCode in ['2','21']:
        thisGP = row_GP[7]+'_'+row_GP[8]
        GPName.append(thisGP)
        

GPconv = pd.Series(GPName).astype('category')
GPID = GPconv.cat.codes
Vilconv = pd.Series(VilName).astype('category')
VilID = Vilconv.cat.codes + 1000
readCSV_GP = np.insert(readCSV_GP,8,GPID,axis=1)
readCSV_Vil = np.insert(readCSV_Vil,13,VilID,axis=1)
GPID = readCSV_GP[1:,(8,9,10)]
GPID_new = []
for x in GPID:
    try:
        GPID_new.append([float(y) for y in x]) 
    except ValueError:
        pass
GPID = GPID_new
VilID = readCSV_Vil[1:,(13,14,15,18)]
VilID = [map(float,x) for x in VilID]


GPID = np.array(GPID)
b = np.ascontiguousarray(GPID).view(np.dtype((np.void, GPID.dtype.itemsize * GPID.shape[1])))
_, idx = np.unique(b, return_index=True)
GPUniq = GPID[idx]

VilID = np.array(VilID)
b = np.ascontiguousarray(VilID).view(np.dtype((np.void, VilID.dtype.itemsize * VilID.shape[1])))
_, idx = np.unique(b, return_index=True)
VilUniq = VilID[idx]

countGP = len(GPUniq)
countVil = len(VilUniq)
#locListGP = []
#locListVil = []



for thisVil in VilUniq :
    thisVil[0] = thisVil[0] + len(readCSV_GP)
    #locListVil.append(locThisVil)


ts2 = time.time()
print "\n Time taken for preprocessing : ", (ts2-ts1), "\n"

nameDist = readCSV_Vil[1][2]
numDist = readCSV_Vil[1][3]

rowDist = [nameDist,numDist,countVil,countGP,float(countVil)/countGP]
print rowDist

 
with open('Maharashtra_Count.csv', 'a') as f:
    writer = csv.writer(f)
    writer.writerow(rowDist)