import csv

#Read population data
reader1 = csv.reader(open('499-first-match.csv'))
reader2 = csv.reader(open('499_best-match.csv'))
reader3 = csv.reader(open('499.csv'))
next(reader3,None)


total_gps = {}

for i in reader1:
	total_gps [ (i[0].strip().lower()) ] = (i[1])

for i in reader2:
	total_gps [i[0].strip().lower()] = (i[1])


#print total_gps
#State Name	State Code	District Name	District_Code	Block_Name	Block_Code	GP Name	GP Code	Latitude	Longitude	 Location OF GP	Phase	throughput


file = open("499-final-popln.csv", "w")
header = "State Name,State Code,District Name,District_Code,Block_Name,Block_Code,GP Name,GP Code,Latitude,Longitude, Location OF GP,Phase,population"
file.write(header)
file.write("\n")
for i in reader3:
	i[6] = i[6].strip().lower()
	if i[6] in total_gps.keys():
		#print total_gps[i[6]]
		file.write(','.join(i))
		file.write(',')
		file.write(total_gps[i[6]])
		file.write("\n")
		#print ', '.join(i) , total_gps[i[6]]
		#print "\n"	
file.close()		