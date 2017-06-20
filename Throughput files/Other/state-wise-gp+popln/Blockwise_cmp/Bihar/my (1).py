import csv
import os

f1 = csv.reader(open('Bihar.csv'))

f2 = csv.reader(open('Bihar_blk.csv'))
next(f1)
next(f2)

ls_bihar=[row[5] for row in f1]
ls_blk=[row[5] for row in f2]

new_phase=dict()



for i in ls_bihar:
	f=0
	if i in ls_blk:
		new_phase.update({int(i):"1"})
	else:
		new_phase.update({int(i):"2"})
phases = list()
f3 = csv.reader(open('Bihar.csv'))
next(f3,None)
for row in f3:
	row[11] = new_phase[int(row[5])]
	phases.append(row)
f  = open('Bihar_block.csv','w')
f.write(','.join(['State Name','State Code','District Name','District_Code','Block_Name','Block_Code','GP Name','GP Code','Latitude','Longitude','Location OF GP','Phase']))
f.write('\n')
for row in phases:
	f.write(','.join(row))
	f.write('\n')









		
