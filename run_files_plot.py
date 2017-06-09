# -*- coding: utf-8 -*-
"""
Created on Tue Jun  6 15:49:35 2017

@author: shubham
"""
import os

def process(filename):
    filename = os.path.splitext(filename)[0]
    run_cmd = "python run_plot.py " + filename
    os.system(run_cmd)
 


dir_name = os.getcwd() + '/Throughput files'
for f in os.listdir(dir_name):
    process(f)