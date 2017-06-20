from __future__ import print_function
import csv


#Read population data
reader = csv.reader(open('karna_final.csv'))

districts = []

next(reader,None)

for row in reader:
	row[3] = row[3].strip()
	districts.append(row[3])

unique_districts = set(districts)

f = open('district_codes.csv','w')

for code in unique_districts:
	f.write(code)
	f.write("\n")
	

#for i in districts:
#	i = open( str(i) + "_Maharastra-gpdata-phase1.csv", "w")

state_data = []

read_file = csv.reader(open('karna_final.csv'))
next(read_file,None)

for row in read_file:
	state_data.append(row)


for district in unique_districts:
	file = open( str(district) + ".csv", "w")
	header = "State Name,State Code,District Name,District_Code,Block_Name,Block_Code,GP Name,GP Code,Latitude,Longitude, Location OF GP,Phase"
	file.write(header)
	file.write("\n")
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