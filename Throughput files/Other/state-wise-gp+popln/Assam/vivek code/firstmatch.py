
import csv


def match1(arg1, arg2):
#Read population data
	#reader = csv.reader(open('dist_555.csv'))
	reader = csv.reader(open(arg1))
	d = {}
	for row in reader:
		row[9] = row[9].strip()
		d[ ( row[9].strip()).lower() ] = { 'TOT_P': row[5], 'panch_code': row[8] }
		
	#print d 
	  
	#Read GP data
	#reader = csv.reader(open('555.csv'))
	reader = csv.reader(open(arg2))
	next(reader,None)
	gp_names = []
	gp_codes = []
	for row in reader:
		row[6] = row[6].strip()
		row[7] = row[7].strip()
		gp_names.append(row[6].lower()) 
		gp_codes.append(row[7].lower())


	#primary match of Gp data with population data and print population for matched GPs

	file = open("555_first_match.csv", "w")
	for i in range(len(gp_names)):
		if d.get(gp_names[i]) != None:
			#print gp_codes[i]+','+ gp_names[i] + ','+ ','.join(d[gp_names[i]]['household'])
			#print gp_codes[i].strip(),",",gp_names[i].strip(),",",d[gp_names[i]]['household'] +",",d[gp_names[i]]['population']
			
			GP_Code = d[gp_names[i]]['panch_code'].strip()
			#total_population = 0
			total_household = 0
			for key, value in d.items():
				if value['panch_code'] == GP_Code :
					#print key,value['GP_CODES'],value['household'],value['population']
					#print "--------------" 
					#total_population += int(value['population']) 
					total_household += int(value['TOT_P'])

			file.write(gp_names[i])
			file.write(",")
			file.write(str(total_household))
			file.write("\n")		
			#print gp_names[i],",",total_household
			#print find_key(d, d[gp_names[i]]['GP_CODES'])
			
			#file.write("%s %s \n"  ( gp_name, ', '.join(d.get(gp_name)) ) ) 
			#print int(d[gp_names[i]]['household']) + int (d[gp_names[i]]['household'])
	file.close()

	#print unmatched GPs to a file
	f = open("GPs_unmatched_op.txt", "w")
	for i in range(len(gp_names)):
		if d.get(gp_names[i]) == None:
		 	f.write(gp_codes[i])
		 	f.write(',')
		 	f.write(gp_names[i])
		 	f.write("\n")
	f.close()
	
	return '555_first_match.csv', 'GPs_unmatched_op.txt'
#print "matched GPs", count
#print "population data",len(d)

