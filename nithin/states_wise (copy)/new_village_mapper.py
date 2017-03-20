"""
python script to map villages and find distance
first search villages within a distance threshould and then match name fuzzy
"""

from __future__ import print_function

import pandas
import os, sys
import IPython
from adj_maker import latlongdist
from fuzzywuzzy import process
from fuzzywuzzy import fuzz
import time

input_files = './cleaned_files'
lgd_files = './LGD'
villages_dir = './'
output_dir = './output_files'
completed = []


def debug():
    IPython.embed()
    exit()


village_df = pandas.read_csv( os.path.join(villages_dir,'Village_list.csv'), usecols=[0,1,3], index_col=False, skipinitialspace=True)
villages_names = [x.lower() for x in village_df.iloc[:,2].tolist()]
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

    print (file)
    if file in os.listdir(output_dir):
        print ('skipping...')
        continue

    # block, gp, lat , long
    input_df = pandas.read_csv(os.path.join(input_files,file), usecols=[4,6,8,9], index_col=False, skipinitialspace=True)
    # blk, village, gp
    lgd_df = pandas.read_csv(os.path.join(lgd_files,file), usecols=[1, 2, 3], index_col=False, skipinitialspace=True)
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
        gp_pos = input_df[(input_df.iloc[:, 0] == blk_search) & (input_df.iloc[:, 1] == gp_search)]  # get pos of gp
        gp_pos = (float(gp_pos.iloc[0, 2]), float(gp_pos.iloc[0, 3]))

        # find villages near this gp
        def df_sorting_helper(index):
            distance_threshold = 20
            return latlongdist(gp_pos, [float(village_df.iloc[index, 0]),
                                        float(village_df.iloc[index, 1])]) >= distance_threshold


        start = time.clock()
        possible_matches = filter(df_sorting_helper, xrange(len(villages_names)))

        if len(possible_matches) == 0:
            village_notmatched.add(village)
            village_stats[1] += 1
            continue

        # find village matching name
        final_match = process.extractOne(village.lower(), possible_matches, processor=fuzzy_df_helper,
                                                scorer=wrap_ratio, score_cutoff=85)
        # debug()
        print (time.clock() - start)

        if len(final_match) == 0:
            village_notmatched.add(village)
            village_stats[1] += 1
            continue

        final_match = final_match[0]
        min_dist = latlongdist(gp_pos, [float(village_df.iloc[final_match, 0]), float(village_df.iloc[final_match, 1])])
        village_stats[0] += 1
        final_df = final_df.append({"Block Name": blk, "GP Name": gp, "GP_lat": gp_pos[0], "GP_long": gp_pos[1],
        "Village Name": village, "Village_lat": village_df.iloc[final_match, 0],
        "Village_long": village_df.iloc[final_match, 1], "Distance": min_dist/1000}, ignore_index=True)

    final_df.to_csv(os.path.join(output_dir, file), encoding='utf-8')
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
