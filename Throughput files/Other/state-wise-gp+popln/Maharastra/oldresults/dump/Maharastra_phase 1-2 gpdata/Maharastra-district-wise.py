from __future__ import print_function
import csv


#Read population data
reader = csv.reader(open('PAN-Maharastra-phase1.csv'))

districts = []

next(reader,None)

for row in reader:
	row[3] = row[3].strip()
	districts.append(row[3])

unique_districts = set(districts)	

#for i in districts:
#	i = open( str(i) + "_Maharastra-gpdata-phase1.csv", "w")

state_data = []

read_file = csv.reader(open('PAN-Maharastra-phase1.csv'))
next(read_file,None)
for row in read_file:
	state_data.append(row)


for district in unique_districts:
	file = open( str(district) + "_Maharastra-gpdata-phase1.csv", "w")
	for row in state_data:

		if district == row[3]:
			file.write(", ".join(row))
			file.write("\n")	
			#print district, row
			#file_name = str(district) + "_Maharastra-gpdata-phase1.csv"
			#print("hi there", file = )	
	#file_district = open( district + "_Maharastra-gpdata-phase1.csv", "w")
		
	#file_district.close()
#
'''
for district in unique_districts:
	for row in reader:
		if district == row[3]:
			file_district.write(row)

'''