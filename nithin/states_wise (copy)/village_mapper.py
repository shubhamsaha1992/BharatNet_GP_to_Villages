#!/usr/bin/env python
"""
python script to map villages and find distance
first search villages name by fizzy and select one within a distance threshould
"""

from __future__ import print_function

import pandas
import os, sys
import IPython
from adj_maker import latlongdist
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import time
import argparse

parser = argparse.ArgumentParser()
parser.add_argument("state")
args = parser.parse_args()

state_dir = args.state

input_files = state_dir + '/input'
lgd_files = state_dir + '/lgd'
villages_dir = state_dir
output_dir = state_dir + '/mapped'
completed = []


def debug():
    IPython.embed()
    exit()


village_df = pandas.read_csv( os.path.join(villages_dir, 'village_list.csv'), usecols=[1, 2, 3], index_col=False, skipinitialspace=True)
villages_names = [str(x).lower() for x in village_df.iloc[:, 0].tolist()]
villages_names_dict = dict()
for name in villages_names:
    name = name.lower()
    try:
        villages_names_dict[name[0]].append(name)
    except KeyError:
        villages_names_dict[name[0]] = [name]

village_notmatched = set()
blk_notmatched = set()
gp_notmatched = set()
village_stats = [0, 0] # matched, notmatched
blk_stats = [0, 0]
gp_stats = [0, 0]
null_data = 0


def fuzzy_df_helper(elem):
    if type(elem) == int:
        # return village_df.iloc[elem, 2]
        return villages_names[elem]
    else:
        return elem


def wrap_ratio(str1, str2):
    score = []
    for str in str2.split():
        score.append(fuzz.ratio(str1, str))
    return sorted(score, reverse=True)[0]


def print_stats(f):
    print('village_notmatched', village_notmatched, file=f)
    print('blk_notmatched', blk_notmatched, file=f)
    print('gp_notmatched', gp_notmatched, file=f)
    print('village_stats', village_stats, file=f)
    print('blk_stats', blk_stats, file=f)
    print('gp_stats', gp_stats, file=f)
    print('null_data', null_data, file=f)


All_Files = os.listdir(input_files)
for file in All_Files:

    if not os.path.exists(os.path.join(lgd_files, file)):
        print ('file lgd not found, ' + file)
        continue

    print (file)
    if file in os.listdir(output_dir):
        print ('skipping...')
        continue

    # block, gp, lat , long
    input_df = pandas.read_csv(os.path.join(input_files, file), usecols=[5, 7, 9, 10], index_col=False, skipinitialspace=True)
    # blk, village, gp
    lgd_df = pandas.read_csv(os.path.join(lgd_files, file), usecols=[2, 3, 4], index_col=False, skipinitialspace=True)
    final_df = pandas.DataFrame()

    # loop through all th villages
    for row in lgd_df.itertuples():
        blk = row[1]
        gp = row[3]
        village = row[2]

        if blk != blk or gp != gp or village != village:
            null_data += 0
            continue

        # find GP position
        blk_search = process.extractOne(blk, input_df.iloc[:, 0].unique().tolist())  # find matching block
        if blk_search[1] < 80:
            blk_notmatched.add(blk)
            blk_stats[1] += 1
            continue
        blk_search = blk_search[0]
        gp_searchs = input_df[input_df.iloc[:, 0] == blk_search].iloc[:, 1].tolist()  # slice the gp's on matched blk
        gp_search = process.extractOne(gp, gp_searchs)  # find best match gp from slice
        if fuzz.WRatio(gp, gp_search[0]) < 80:
            gp_notmatched.add(gp)
            gp_stats[1] += 1
            continue
        gp_search = gp_search[0]
        gp_pos = input_df[ (input_df.iloc[:, 0] == blk_search) & (input_df.iloc[:, 1] == gp_search)]  # get pos of gp

        # find village position
        # start = time.clock()
        possible_matches = process.extractBests(village.lower(), xrange(len(villages_names)), processor=fuzzy_df_helper,
                                                scorer=wrap_ratio, limit=25, score_cutoff=55)
        # debug()
        # print time.clock() - start
        possible_matches = [x[0] for x in possible_matches]
        if len(possible_matches) == 0:
            village_notmatched.add(village)
            village_stats[1] += 1
            continue

        def df_sorting_helper(index):
            return latlongdist([float(gp_pos.iloc[0, 2]), float(gp_pos.iloc[0, 3])],
                               [float(village_df.iloc[index, 1]), float(village_df.iloc[index, 2])])

        distance_sorted = sorted(possible_matches, key=df_sorting_helper, reverse=True)
        min_distance = df_sorting_helper(distance_sorted[0])
        # if min_distance > 10000:
            # village_notmatched.add(village)
            # village_stats[1] += 1
            # continue

        village_stats[0] += 1
        final_df = final_df.append({"Block Name": blk, "GP Name": gp, "GP_lat": gp_pos.iloc[0, 2], "GP_long": gp_pos.iloc[0, 3],
        "Village Name": village, "Village_lat": village_df.iloc[distance_sorted[0], 0],
        "Village_long": village_df.iloc[distance_sorted[0], 1], "Distance": min_distance/1000}, ignore_index=True)

    final_df.to_csv(os.path.join(output_dir, file))
    print_stats(sys.stdout)

    f = open(os.path.join(output_dir, file+'stats.txt'), 'w')
    print_stats(f)
    f.close()

    village_notmatched = set()
    blk_notmatched = set()
    gp_notmatched = set()
    village_stats = [0, 0]  # matched, notmatched
    blk_stats = [0, 0]
    gp_stats = [0, 0]
    null_data = 0


# 81.431843 , 24.250417
# 3.51
