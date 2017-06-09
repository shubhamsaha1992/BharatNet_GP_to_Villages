# -*- coding: utf-8 -*-
"""
Created on Mon Apr  3 23:48:43 2017

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

base_filename = sys.argv[1]
dir_name = os.getcwd() + '/Throughput files'
full_filename = os.path.join(dir_name, base_filename + "." + 'csv')
#full_filename = os.path.join(dir_name, base_filename)



with open(full_filename, 'rb') as f:
    reader = csv.reader(f)
    readCSV = list(reader)
    
    
GPName = []
GPID = []
VilName = []
VilID =[]

#readCSV = sample(readCSV,50)
#nSamples = 50
#begin = randint(1,(len(readCSV) - nSamples - 1))
#begin = 25
#end = begin + nSamples
#readCSV = readCSV[begin:end]
for row in readCSV:
	thisGP = row[7]
	GPName.append(thisGP)


GPconv = pd.Series(GPName).astype('category')
GPID = GPconv.cat.codes
GPID = np.array(GPID)
GPUniq = np.unique(GPID)

print len(GPUniq)
