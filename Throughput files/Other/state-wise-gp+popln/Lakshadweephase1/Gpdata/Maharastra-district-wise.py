from __future__ import print_function
import csv
import os

#Read population data
reader = csv.reader(open('Lakshadweep.csv'))

districts = []

next(reader,None)

for row in reader:
	row[3] = row[3].strip()
	districts.append(row[3])

unique_districts = set(districts)	

#for i in districts:
#	i = open( str(i) + "_Maharastra-gpdata-phase1.csv","w")

state_data = []

read_file = csv.reader(open('Lakshadweep.csv'))
next(read_file,None)

for row in read_file:
	state_data.append(row)


for district in unique_districts:
	file = open( str(district) + ".csv","w")
	header = "State Name,State Code,District Name,District_Code,Block_Name,Block_Code,GP Name,GP Code,Latitude,Longitude,Location OF GP,Phase"
	file.write(header)
	file.write("\n")
	phase = '21' 
	for row in state_data:
		if row[11] == '1': 
			row[11] = '21'
		
		if district == row[3]:
			if row[11].strip() == '2':
				phase = '2'
			file.write(",".join(row))
			file.write("\n")
	if phase == '21':		
		os.rename(  str(district) + ".csv",str(district) + "_phase1_.csv")		
			#print district,row
			#file_name = str(district) + "_Maharastra-gpdata-phase1.csv"
			#print("hi there",file = )	
	#file_district = open( district + "_Maharastra-gpdata-phase1.csv","w")
	'''
	read = csv.reader(open(str(district) + '.csv'))
	phase = '1'
	next(read,None)
	for row in read:
		for r in row
			r 
		row = row.rstrip()
		if row[11] == '2':
			phase = '2'
	if phase == '1':
		os.rename(str(district) + ".csv",str(district) + "_phase1_.csv")		

# files = os.listdir('.')

# for fi in files:
# 	if '.csv' in fi:
# 		print (fi) 
	#file_district.close()
#

for district in unique_districts:
	for row in reader:
		if district == row[3]:
			file_district.write(row)

'''