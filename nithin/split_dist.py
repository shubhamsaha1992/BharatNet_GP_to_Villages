#!/usr/bin/env python
"""
script to split state files to district wise files with dist code as filename
"""
import pandas as pd
import os

folder = 'UP'
in_file = 'UP.csv'

print (os.path.join( folder,in_file) )

lgd_df = pd.read_csv(os.path.join( folder,in_file) , index_col=False, skipinitialspace=True)

dists = lgd_df.iloc[:, 3].unique()
for dist in dists:
   lgd_df[lgd_df.iloc[:, 3] == dist].to_csv(os.path.join(folder, str(dist)+'.csv'))


