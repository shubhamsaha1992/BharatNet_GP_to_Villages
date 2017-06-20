
import csv

#Read population data
reader = csv.reader(open('state_26.csv'))
next(reader,None)
dists = {}
#for i in range(20,34):
#	states[str(i)] = []

for row in reader:
	if row[1] in dists.keys():
		dists[row[1]].append(row)
	else:
		dists[row[1]] = []
		dists[row[1]].append(row)
header = "STATE,DISTRICT,SUBDISTT,T_VILLCODE,NAME,TOT_P,blk_code,blk_name,panch_code,panch_name"
for key in dists.keys():
	with open('dist_{}.csv'.format(key),'w') as f:
		f.write(header)
		f.write("\n")
		for li in dists[key]:
			for col in li:
				f.write(col)
				f.write(",")
			f.write('\n')





#print states.keys()


#for item in states.items():


#for row in reader



#unique_state_dist = set(state_dist)


#for row in unique_state_dist:
#	print row
	#file_name = "f" + " _" + str(row)

	#row[6] = row[6].strip()

	
	#if row[0] == ""	
