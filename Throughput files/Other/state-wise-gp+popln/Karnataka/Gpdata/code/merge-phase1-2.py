import csv
reader1 = csv.reader(open('PAN-Maharastra-phase1.csv'))
reader2 = csv.reader(open('PAN-Maharastra-phase2.csv'))

#reader = csv.reader(open('PAN-Maharastra-phase1.csv'))
combined_districts = []

next(reader1,None)
next(reader2,None)

for row in reader1:
	
	combined_districts.append(row)

for row in reader2:
	
	combined_districts.append(row)

#unique_districts = set(districts)
#print len(unique_districts)	
districts = []
for row in combined_districts:
	districts.append( row[3].strip() ) 

unique_districts = set(districts)
#	print len(unique_districts)


header = "State Name,State Code,District Name,District_Code,Block_Name,Block_Code,GP Name,GP Code,Latitude,Longitude, Location OF GP,Phase"

for district in unique_districts:
	file = open( str(district) + "_Maharastra-gpdata.csv", "w")	
	file.write(header)
	file.write("\n")
	for row in combined_districts:

		if district == row[3]:
			file.write(", ".join(row))
			file.write("\n")
