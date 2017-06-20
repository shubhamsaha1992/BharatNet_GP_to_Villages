# -*- coding: utf-8 -*-
"""
Created on Wed Jun 14 18:24:25 2017

@author: shubham
"""

import glob, os

def rename(dir, pattern, titlePattern):
    for pathAndFilename in glob.iglob(os.path.join(dir, pattern)):
        title, ext = os.path.splitext(os.path.basename(pathAndFilename))
        #os.rename(pathAndFilename,os.path.join(dir, titlePattern % title + ext))
        os.rename(pathAndFilename,pathAndFilename.replace('phase1_.','1'))


rename(r'/home/shubham/TVWS/BharatNet_GP_to_Villages/Throughput files/GP/Renaming', r'*.csv', r'%s_1')
