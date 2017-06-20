
import c

#Read population da
reader = csv.reader(open('state_01.csv'
next(reader,Non
dists = 
#for i in range(20,34
#	states[str(i)] = 

for row in reade
	if row[1] in dists.keys(
		dists[row[1]].append(ro
	els
		dists[row[1]] = 
		dists[row[1]].append(ro
header = "STATE,DISTRICT,SUBDISTT,T_VILLCODE,NAME,TOT_P,blk_code,blk_name,panch_code,panch_nam
for key in dists.keys(
	with open('dist_{}.csv'.format(key),'w') as 
		f.write(heade
		f.write("\n
		for li in dists[key
			for col in l
				f.write(co
				f.write(",
			f.write('\n





#print states.keys


#for item in states.items(


#for row in read



#unique_state_dist = set(state_dis


#for row in unique_state_dis
#	print r
	#file_name = "f" + " _" + str(ro

	#row[6] = row[6].strip


	#if row[0] == "
