# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 18:47:17 2017

@author: shubham
"""

import os
import sys

def process(filename):
    filename = os.path.splitext(filename)[0]
    run_cmd = "python run_count.py " + filename
    os.system(run_cmd)
    
 

try:
    os.remove('Maharashtra_Count.csv')
except OSError:
    pass

dir_name = os.getcwd() + '/Throughput files/Pipeline'
#base_filename = sys.argv[1]
#process(base_filename)

for f in os.listdir(dir_name):
    try:
        process(f)
    except IOError:
        pass
    