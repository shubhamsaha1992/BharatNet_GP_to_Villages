import csv

def lcs(a, b):
    lengths = [[0 for j in range(len(b)+1)] for i in range(len(a)+1)]
    # row 0 and column 0 are initialized to 0 already
    for i, x in enumerate(a):
        for j, y in enumerate(b):
            if x == y:
                lengths[i+1][j+1] = lengths[i][j] + 1
            else:
                lengths[i+1][j+1] = max(lengths[i+1][j], lengths[i][j+1])
    # read the substring out from the matrix
    result = ""
    x, y = len(a), len(b)
    while x != 0 and y != 0:
        if lengths[x][y] == lengths[x-1][y]:
            x -= 1
        elif lengths[x][y] == lengths[x][y-1]:
            y -= 1
        else:
            assert a[x-1] == b[y-1]
            result = a[x-1] + result
            x -= 1
            y -= 1
    return result



reader = csv.reader(open('dist_499.csv'))
d = {}
for row in reader:
	row[9] = row[9].strip()
	d[ ( row[9].strip()).lower() ] = { 'TOT_P': row[5], 'panch_code': row[8] }


reader = csv.reader(open('GPs_unmatched_op.txt'))
gp_names_unmatched = []
#gp_codes_unmatched = []
for row in reader:
	#gp_codes_unmatched.append(row[0])
	gp_names_unmatched.append(row[1].lower())
	#print row[0]

#keys_in_d = []
#keys_in_d = d.keys()

#for key in d.keys(): 
#	print key 


#matched_string_list = []
f = open("499_best-match.csv", "w")
		
for i in range(len(gp_names_unmatched)):
#	print row 
	max_match = 0
	matched_string = None
	for key in d.keys():
		#print (row,key)
		set_value = lcs (gp_names_unmatched[i].lower(),key)  
		#print str
		if len(set_value) > max_match:
			#print ( len(set_value), key)
			max_match = len(set_value)
			matched_string = key
	if d.get(matched_string) != None:
		GP_Code = d[matched_string]['TOT_P'].strip()
		#total_population = 0
		total_household = 0
		for key, value in d.items():
			if value['TOT_P'] == GP_Code :
				#print key,value['GP_CODES'],value['household'],value['population']
				#print "--------------" 
				#total_population += int(value['population']) 
				total_household += int(value['TOT_P'])
				#print value['GP_CODES'],value['NO_HH']
		f.write(gp_names_unmatched[i])
		f.write(",")
		f.write(str(total_household))
		f.write("\n")
		
		#print gp_names_unmatched[i],",",total_household
		#print gp_codes_unmatched[i]+','+gp_names_unmatched[i] +','+ ', '.join(d.get(matched_string))		
	#print(matched_string,row)	
	#matched_string_list.append(matched_string)	
f.close()
'''

for line in matched_string_list:
	print line
		
		str = lcs(row.lower(),key)
		if len(str) > max_match:
			print len (str)
			print("\n")
			max_match = len(str)
			matched_string = str
			print matched_string




'''