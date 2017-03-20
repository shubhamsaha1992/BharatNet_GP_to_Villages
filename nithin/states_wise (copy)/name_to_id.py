#!/usr/bin/env python
"""
script to rename files with dist names to dist codes
it expects the main lgd file named as main.csv in the folder
"""

import pandas as pd
import os
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("state")
args = parser.parse_args()

state_dir = args.state
dir = 'lgd'

df_list = pd.read_csv(os.path.join(state_dir, 'main.csv'), usecols=[2, 3],index_col=False, skipinitialspace=True)
df_list = df_list.drop_duplicates()
name_list = df_list.iloc[:, 0].tolist()

for file in os.listdir(state_dir+'/'+dir):
    match = process.extractOne(file.split('.')[0], name_list, scorer=fuzz.WRatio, score_cutoff=85)
    if not match:
        print (file + "no match")
        continue
    else:
        # print match[0]
        dd = df_list[df_list.iloc[:, 0] == match[0]]
        num = df_list[df_list.iloc[:, 0] == match[0]].iloc[:, 1].tolist()[0]
        print file, num
        os.rename(state_dir+'/lgd/'+str(file), state_dir+'/lgd/'+str(num)+'.csv')