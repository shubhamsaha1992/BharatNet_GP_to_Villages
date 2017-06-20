from firstmatch import match1
from bestmatch import match2
from merge import combine

import os
# def output():
# 	file_1,file_2 = match1('xyz.csv', 'abc.csv')
# 	file_3 = match2(file_2)
# 	output_file = combine(file_1,file_3)

if __name__ == '__main__':
	# f  = open('district_codes.csv', 'r')
	# district_codes = []
	# for code in f :
	# 	district_codes.append(code.strip())

	## Open files in ? dir
	## Open files in GP dir
	##	 	if exists open POPULATION file corresponding to the district codezz

	Gpath='/home/uesr/Project/state-wise-gp+popln/Rajasthan/Gpdata/'
	Ppath='/home/uesr/Project/state-wise-gp+popln/Rajasthan/popln/'
	#Gpath = '../Gpdata/'
	#Ppath = '../popln'
	gpfiles = os.listdir(Gpath)
	#gpfiles = os.listdir('/home/uesr/Project/Karnataka/Gpdata/')
	listofGP = []
	for gfile in gpfiles:
		#print gfile
		if '.csv' in gfile:
			if len(gfile)==7:
				listofGP.append(gfile.split('.')[0])
	#print listofGP
	#exit()
	#Gpath='/home/uesr/Project/Karnataka/Gpdata/'
	#Ppath='/home/uesr/Project/Karnataka/popln/'
	#poplnfiles = os.listdir(Ppath)
	
	poplnfiles = os.listdir('/home/uesr/Project/state-wise-gp+popln/Rajasthan/popln/')
	for pfile in poplnfiles:
		#print pfile
		if 'dist' in pfile:
			fn = pfile.split('.')[0][-3:]

			if fn in listofGP:
				print fn 
				res_A, res_B = match1(Ppath+pfile, Gpath+fn+'.csv')

				res_C = match2(Ppath+pfile, res_B)

				res_D = combine(res_A, res_C, Gpath+fn+'.csv')

			





	