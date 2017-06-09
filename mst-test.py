try:
	import simplejson
except:
	import json as simplejson

import pickle
import numpy as np
import random
import math
import os
import sys
import time
from sets import Set
from random import randrange
from csv2npy import read_csv_fields
from adj_maker import make_adjacency
from pse_2 import rf_get
from pse_2 import get_elevation_profile
from feas_mkr import make_feas
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import minimum_spanning_tree
#from directions import fetch_direction
from maps_blk import road_dist_block,road_dist_block_file
from sptgraph import spt,print_mst_links,build_Tcsr,fibre_saved_if_wireless,handle_no_road_cases
from sptgraph import prun_leaf_wps,get_te_route_length,make_rooted_tree,remove_nodes_from_tree
from pse_2 import latlongdist
from copy import copy, deepcopy
from directions import get_waypoints,update_block_waypoint
from wireless_connectivity import get_towers_list,make_phase1_connection,make_tower_connection,get_phase1_list

########################################



## '21' ---phase-1  [initial]
## '2' ---phase-1  [initial]
## '9' ---tower    [initial]
##----------------------------------
## '3' ---children of '2'
## '4' ---children of '3',state,dist   ---not used
## '5' ---New fibre --New ministers
## '6' ---children of '5' 
## '8' ---phase-2 GP within 300 mtr of tower  
## '10'---
## '11'---children of '10'   ---not used
## '12'---New ONT proposed because of throughput requirement  
## '13'---children of '12'
## '14'---children of '13'   not used
## '15'---Block HQ

########################################

##distance criteria for adjacency matrix
TOWER_CONNECTION_LIMIT = 4
P1_CONNECTION_LIMIT = 3
REF_DIST = 7						##km for adjacency matrix
htListT = [10,15,20,30,40]      ##Available heights of transmitting Towers
htListR = [3,6,9,15,20]            ##Available heights of receiving Towers

########################################
upper_limit = 100000
NUM_ZERO_HOP=0
NUMT_ZERO_HOP=0
NUM_FIRST_HOP=0
MAX_ROUTE_LENGTH = 50000
GUARD_DISTANCE = 30000
BETA = 0.5

KEY = 'AIzaSyDlk6P3ZkMelE9SVYGQmunFDTC5Y4ZD37c'




# near_limit = 300
# rear_limit = 2000
########################################
def get_block_hq(dijkstralist,bhqsindx):
	bhq_to_nodes = []

	for bhqidxes in bhqsindx:
		#spt(dijkstralist,bhqidxes)
		bhq_to_nodes_dist = spt(dijkstralist,bhqidxes)
		print "total fibre in block",bhq_to_nodes_dist
		# sys.exit()
		bhq_to_nodes.append(bhq_to_nodes_dist)
		print "bhq_to_nodes",bhq_to_nodes.index(min(bhq_to_nodes))

	#print "Final bhq ",(bhq_to_nodes.index(min(bhq_to_nodes)))
	#return bhq[(bhq_to_nodes.index(min(bhq_to_nodes)))]		
	return (bhq_to_nodes.index(min(bhq_to_nodes)))



def do_something(input_file):
	dist_onts = list()
	dist_conctd_to_ph1_gps = list()
	dist_conctd_to_tower_gps = list()
	dist_problem_case_gps = list()
	dist_satellite_gps = list()

	tot_conctd_to_towers = 0 
	tot_conctd_to_ph1 = 0
	tot_onts = 0
	tot_problem_cases = 0
	tot_satel_recmdns = 0
	tot_olts = 0
	tot_ph2_gps = 0

	dist_olts = 0
	if not os.path.exists('tower'):
		os.makedirs('tower')
	f1 = open('tower/tower_'+str(input_file)+'.csv','w')
	f1.write('GP Name,GP seq,GP lat,GP long,GP status,GP tower height' +  '\n')
	f1.close()
	f1 = open('tower/tower_'+str(input_file)+'.csv','a+')

	if not os.path.exists('stats.csv'): 
		f2 = open('stats.csv','w')
		f2.write('District Code,Phase 1, Phase 2,Rural Exchanges, Towers, Conn. to P1,Conn. to towers \n')
		f2.close()
		f2 = open('stats.csv','a+')
	else:    
		f2 = open('stats.csv','a+')
		next(f2,None)
		for row in f2:
			print (int(row.split(",")[0]),int(input_file))
			if (int(row.split(",")[0]) == int(input_file)):
				print ("district code already processed:",input_file)
				f2.close()
				#sys.exit()
				return

	if not os.path.exists('data_error.csv'): 
		f9 = open('data_error.csv','w')
		f9.write('District Code,GP Code, GP Name, GP Lat, GP_Lon,Status\n')
		f9.close()
	#else:    
	f9 = open('data_error.csv','a+')
	

	if not os.path.exists('fibre_all'):
		os.makedirs('fibre_all')
	f3=open('fibre_all/fibre_'+str(input_file)+'.csv','w')
	f3.write('Block Code,fibre length,max. route length,No. of OLTs\n')
	f3.close()
	f3=open('fibre_all/fibre_'+str(input_file)+'.csv','a+')

	if not os.path.exists('sat'):
		os.makedirs('sat')
	f4=open('sat/sat_'+str(input_file)+'.csv','w')
	f4.write('Block Code,Sat. GP code, Sat. GP Name,Latitude, Longitude, population\n')
	f4.close()
	f4=open('sat/sat_'+str(input_file)+'.csv','a+')

	if not os.path.exists('fibre_all'):
		os.makedirs('fibre_all')
	f5=open('fibre_all/mst_'+str(input_file)+'.csv','w')
	f5.write('Block Code,FROM GP lat,FROM GP long,TO GP Lat , TO GP Long,link length(km)\n')
	f5.close()
	f5=open('fibre_all/mst_'+str(input_file)+'.csv','a+')


	if not os.path.exists('fibre'):
		os.makedirs('fibre')
	f6=open('fibre/fibre_'+str(input_file)+'.csv','w')
	f6.write('Block Code,fibre length,max. route length,Length reduction,No. of OLTs\n')
	f6.close()
	f6=open('fibre/fibre_'+str(input_file)+'.csv','a+')

	f7=open('fibre/mst_link'+str(input_file)+'.csv','w')
	f7.write('Block Code,From_gp_name,FROM GP lat,FROM GP long,To_gp_name,TO GP Lat , TO GP Long,link length(km)\n')
	f7.close()
	f7=open('fibre/mst_link'+str(input_file)+'.csv','a+')


	f8=open('fibre_all/unconnected_'+str(input_file)+'.csv','w')
	f8.write('GP Name,GP Code,Block Code,GP lat,GP long,Population,Status\n')
	f8.close()
	f8=open('fibre_all/unconnected_'+str(input_file)+'.csv','a+')



	if not os.path.exists('olt_connect'):
		os.makedirs('olt_connect')
	


	if not os.path.exists('output'):
		os.makedirs('output')
	f = open('output/output_'+str(input_file)+'.csv','w')
	f.write('FROM GP Name,FROM GP seq, FROM Block_code, FROM GP lat,FROM GP long,FROM GP status,FROM GP tower height,LINK throughput,TO GP Name,TO GP seq, TO Block Code,TO GP lat,TO GP long,TO GP status,TO GP tower height' +  '\n')
	f.close()
	f = open('output/output_'+str(input_file)+'.csv' ,'a+')
	#####################################
	##thane_GP_data.csv gives the following informations
	# ['State_Code','District_Code','Block_Code','GP_Code', 'Latitude', 'Longitude','Phase','throughput']
	filename = read_csv_fields(str(input_file),['State Code','District_Code','Block_Code','GP Name','GP Code', 'Latitude', 'Longitude','Phase','population'])
	
	#####################################

	# # #create adjacency matrix
	fname = make_adjacency(REF_DIST,filename,input_file) #############################
	# # ######################################

	
	all_data = np.load('adjmat/AD_mat_' +str(input_file)+ '_'+str(REF_DIST)+'.npy')


	States_list = all_data[1]     #Sate names ???It is giving district code
	GP_lists = all_data[2]        #GP codes
	GP_Names = all_data[9]
	Phase_lists = all_data[3]     #Phase of Bharatnet project
	DistMats = all_data[4]        #distance matrix for each district
	District_code = all_data[5]   #unique code for all districts
	Block_code = all_data[8]
	LatLong = all_data[6]         #lat and long of GPs
	reqTP_mat = all_data[7][0]    #throughput required for each GP It is a list
	# print "required throughput",reqTP_mat
	Block_code=Block_code[0]
	state = np.unique(States_list[0])
	# print "Districts ",District_code[0]
	dist = np.unique(District_code[0])
	state=str(int(state[0]))
	dist= str(int(dist[0]))
	#####################################

	ffname = make_feas(REF_DIST,htListT,htListR,state,dist,input_file) ######################################

	feas = np.load('feasmat/Feas_mat_'+str(input_file)+'_'+str(REF_DIST)+'.npy')
	feasibility_mat_raw = feas[0]
	throughPut_mat = feas[1]
	transHeight_mat = feas[2]
	receivHeight_mat = feas[3]
	adjMats = [feas[4]] ##this feasibility is according to throughput

	NODE, NODE = np.shape(adjMats[0])
	for i in range(0,NODE):
		for j in range(0,NODE):
			if(adjMats[0][i][j]==1 and i!=j):
				print "adj",i,j,adjMats[0][i][j]
				print "thr",throughPut_mat[i][j]
				print "txh",transHeight_mat[i][j]
				print "rcx",receivHeight_mat[i][j]
	########################################################
	tower_height = [0 for k in range(NODE)]
	availableTP_mat = [0 for i in range(NODE)]

	########################################################


	#print Phase_lists[0]
	blocks = []
	blocks=np.unique(Block_code)
	#print "blocksssss",blocks

	#......................................................................
	##In this adjacency matrix first remove "TO" connections to phase-1 GPs
	##then remove any interconnection between phase-1 GPs
	#......................................................................

	alc=0
	for j in range(NODE):                                                                     ##for each node in that district

		if(Phase_lists[0][j] == 9 or Phase_lists[0][j] == 8 or Phase_lists[0][j] == 21 or Phase_lists[0][j] == 15):       ##if some node belongs to tower                    
			alc+=1
			adjMats[0][:,j] = 0                                                               ##cut all the incoming connections for that
			
			for k in range(NODE):                                                             ##for that node
				
				if(adjMats[0][j][k] == 1):                                                    ##if there is any adjacent nodes
					
					if(Phase_lists[0][k] == 9 or Phase_lists[0][k] == 8 or Phase_lists[0][k] == 21 or Phase_lists[0][k] == 15):   ##if it belongs to tower

						adjMats[0][j][k] = 0                                                  ## cut outgoing connection which go to that node
	#print "Phasssesssss2=---\n",len(Phase_lists[0])
	#print "Phasssesssss2=---\n",Phase_lists
###Give satellite suggestion for GPs which do not have any incoming or outgoing feasible connections
	# satr=0
 #    for j in range(NODE):
 #    	if(Phase_lists[0][j] == 2):
 #    		if(sum(adjMats[0][j,:])<=1 and sum(adjMats[0][:,j])<=1):
 #    		# if(sum(adjMats[0][j,:])<=1):
 #    			m=min(i for i in DistMats[0][:,j] if i>0)
 #    			# print "minimum",m
 #    			if(m>2000):
	#     			x=np.where(adjMats[0][j,:]==1)
	#     			f4.write(str(Block_code[j])+','+str(GP_lists[0][j])+','+str(GP_Names[0][j])+ ',' +str(LatLong[j][0]) + ',' +str(LatLong[j][1])+','+str(reqTP_mat[j])+'\n')
	#     			satr+=1 
				# print "outgoing connections from ",GP_lists[0][j], "are ",sum(adjMats[0][j,:]),"to",  GP_lists[0][x[0]],"TP",reqTP_mat[j]

	###Connet unconnected GP to nearest tower or connected GP
	


	def connect(gp,status,blk_code):
		for m in range(NODE):  
		   ##for all nodes
			if (Phase_lists[0][m] == status):    ##check for phase 1 or towers    
				# degree3 = [0 for i in range(NODE)]
				# dist3 = [upper_limit for i in range(NODE)]                           
				if adjMats[0][m][gp] == 1:                       ##If any other node is adjacent to child of Status 3 node
					#print "phase ",Phase_lists[0][m]
					Phase_lists[0][gp] = status+1            ##GP is connected wirelessly from tower 

					#print "connected ",GP_Names[0][m], "to", GP_Names[0][gp]
					#print "connect with wireless",LatLong[m],LatLong[gp], reqTP_mat[gp],m,gp, Phase_lists[0][gp]
					#print "Transmission height", transHeight_mat[m][gp]
					f.write(str(GP_Names[0][m]) + ',' +str(GP_lists[0][m]) + ','+str(Block_code[m])+',' +str(LatLong[m][0]) + ',' +str(LatLong[m][1]) + ',' +str(Phase_lists[0][m]) + ',' + str(transHeight_mat[m][gp])+','+str(throughPut_mat[m][gp]) +','+str(GP_Names[0][gp]) + ',' +str(GP_lists[0][gp]) + ',' +str(blk_code)+','+str(LatLong[gp][0]) + ',' +str(LatLong[gp][1]) + ',' +str(Phase_lists[0][gp]) + ','+ str(receivHeight_mat[m][gp]) +',' +'\n' )
					# f.write(str(GP_Names[0][gp])+ ',' +str(GP_lists[0][m]) + ',' +str(LatLong[m][0]) + ',' +str(LatLong[m][1]) + ',' +str(Phase_lists[0][m]) + ',' + str(transHeight_mat[m][index3])+','+str(throughPut_mat[m][index3]) +','+str(GP_Names[0][index3]) + ',' +str(GP_lists[0][index3]) + ',' +str(LatLong[index3][0]) + ',' +str(LatLong[index3][1]) + ',' +str(Phase_lists[0][index3]) + ','+ str(receivHeight_mat[m][index3]) +',' +'\n' )
					if tower_height[m] < transHeight_mat[m][gp]:
						tower_height[m] = transHeight_mat[m][gp]

					if tower_height[gp] < receivHeight_mat[m][gp]:
						tower_height[gp] = receivHeight_mat[m][gp]

					adjMats[0][:,gp] = 0                  ##cut all the incoming connections
					return 1
			
		return 0    

	ctt = 0

	block_idx=[]
	block_phase={}
	for j in blocks:
		blocks1={}
		for i in range(NODE):
			if int(Block_code[i])==j:
				blocks1.update({i:int(Phase_lists[0][i])}) #i is id as per district rows
		block_phase.update({j:blocks1})
		blocks1=[]

	##DistMats is distance matrix for all towers and GP's of the district
	DistMats=DistMats[0]
	##We create a distance matrix for fibre GP's & Block HQ of each block
	# block_dist_mat =[0 for k in range(len(blocks))]
	block_dist_mat={}
	block_adj_mat={}
	Block_MST=[]
	road_dr_array=[]
	LatLong_fibre=[0 for k in range(len(blocks))]

	##cut block distance matrix for fibre GPP's from distance matrix for whole district
	for j in blocks: 
		if int(j) in [1117,1122]:
			continue
		# block_dist_mat[j]=DistMats[:,block_phase[j].keys()][block_phase[j].keys(),:]
		print "Processing block ============",j
		f10 = open('olt_connect/olt_connections_'+str(int(j))+'.csv','w')
		f10.write('Block Code,OLT Code,OLT Name,OLT Lat,OLT Lon,GP Name,GP Code,GP Lat,GP Lon,Route Length(km)\n')
		f10.close()
		f10 = open('olt_connect/olt_connections_'+str(int(j))+'.csv','a+')

		if not os.path.exists('waypoints'):
			os.makedirs('waypoints')
		
		if not os.path.exists('waypoints/waypoints_'+str(int(j))+'.csv'):
			fw=open('waypoints/waypoints_'+str(int(j))+'.csv','w')
			fw.write('Waypoint Code,Waypoint lat,Waypoint long\n')
			fw.close()
		fw=open('waypoints/waypoints_'+str(int(j))+'.csv','a+')

		
		temp_list = [x for x in block_phase[j].keys()]
		gps_in_the_block = sorted(temp_list, key=int)
		# gives sorted list of district wuse id's for gps in the block
		block_waypoints_list = list()
		status2 = []
		brk=0
		#print block_phase[j].items()
		#for key,value in block_phase[j].items():
		for key in gps_in_the_block:
			value = block_phase[j][key]
			if (value == 21):
				brk=1
				continue
			elif(value == 2 or value == 15):
				status2.append(key) #key = district wise id for GP
		if(brk):
			continue
		##Extract distance and adjacency matrix for that block GP's
		# block_dist_mat.update({j:DistMats[:,status2][status2,:]})
		blkx_distx={}
		#####Block index to district index mapping
		for k in range(len(status2)):
			blkx_distx.update({k:status2[k]})

		# bhqs=[x for x,y in block_phase[j].items() if int(y) ==15]
		# bhqs = sorted(bhqs, key=int)

		# print "BHQs == ",bhqs
		
		# #Compute total number of phase 2 gps in the district
		# tot_ph2_gps += len(gps_in_the_block) - len(bhqs)

		# bhqsindx=[]
		# for indx in bhqs:
		# 	bhqsindx.append([x for x,y in blkx_distx.items() if int(y) ==indx][0])
		# print "bhqsindx",bhqsindx,blkx_distx

		# bhqsindx = sorted(bhqsindx, key=int)
		# bhq = bhqsindx[0]
		# if (j == 3564):
		# 	bhq = 1
		# bhq_id = 'gp,'+str(bhq)
		# print "UP bhq------------",bhq,status2[bhq],LatLong[status2[bhq]],LatLong[status2[bhq]],str(GP_Names[0][status2[bhq]]),str(GP_lists[0][status2[bhq]])
		
		
		# print "Number of GPs::::",len(status2)
		# road_d=[]
		# for l in range(len(status2)):
		# 	road_dr=[]
		# 	for m in range(len(status2)):
		# 		if(l>=m):
		# 			road_dr.append(0.0)
		# 		else:
		# 			try:
		# 				wp_list,dis=get_waypoints(LatLong[status2[l]],LatLong[status2[m]],state,dist,j,KEY)
		# 			except IOError, e:
		# 				if e.errno == 101 or e.errno == 'socket error' or e.errno == -3 or e.errno == 2:
		# 					print "Network Error"
		# 					time.sleep(1)
		# 					wp_list,dis=get_waypoints(LatLong[status2[l]],LatLong[status2[m]],state,dist,j,KEY)
		# 				else:
		# 					raise
		# 			wp_list_tmp = [u for u in wp_list if u != LatLong[status2[l]] and u != LatLong[status2[m]]]  
		# 			block_waypoints_list = update_block_waypoint(block_waypoints_list,wp_list_tmp)
		# 			if dis == 0.1: #same coordinates 
		# 				print "Possible???", l,m,LatLong[status2[l]],LatLong[status2[m]],str(GP_Names[0][status2[m]]),str(GP_lists[0][status2[m]])
		# 				f9.write(str(dist)+","+str(GP_lists[0][status2[m]])+","+str(GP_Names[0][status2[m]])+","+str(LatLong[status2[m]][0])+","+str(LatLong[status2[m]][1])+",Duplicate LatLong\n")
		# 				f9.write(str(dist)+","+str(GP_lists[0][status2[l]])+","+str(GP_Names[0][status2[l]])+","+str(LatLong[status2[l]][0])+","+str(LatLong[status2[l]][1])+",Duplicate LatLong\n")
		# 			road_dr.append(dis)
		# 			#print "Getting inter GP distances: Processing out of ",	LatLong[status2[l]],LatLong[status2[m]],dis
					
		# 	#sys.exit()
		# 	road_d.append(road_dr) 
			#road_d is a list of list road_d[x][y] = road distance between gp's x and y if x < y and 0 otherwise

			#sys.exit()

		###############################
		# Get Waypoints for the block #
		###############################
		# road_d_min = {}
		# processed_nodes = [bhq]
		# #block_waypoints_list = list() #list of block waypoints  
		# for l in range(len(status2)): #Initialization Loop
		# 	if l > bhq:
		# 		road_d_min.update({str(l)+','+','.join([str(x) for x in LatLong[status2[bhq]]]) : road_d[bhq][l]})
		# 	elif l < bhq:
		# 		road_d_min.update({str(l)+','+','.join([str(x) for x in LatLong[status2[bhq]]]) : road_d[l][bhq]})

		# while len(road_d_min) > 0:
		# 	print "Number of GP's still to be processed::",len(road_d_min)
		# 	min_curr_road_d = 10000000000000
		# 	for x,y in road_d_min.items(): #Find GP with the min distance from the set of points chosen already
		# 		if y < min_curr_road_d:
		# 			min_curr_road_d = y
		# 			min_curr_road_d_key = x
		# 	print "ROAD D MIN::::",min_curr_road_d_key,road_d_min[min_curr_road_d_key]
		# 	del road_d_min[min_curr_road_d_key]

		# 	if min_curr_road_d >= 1000000: #If road data not found then nothing can be done. Sorry!!
		# 		continue

		# 	x_list = min_curr_road_d_key.split(',')
		# 	x_latlong = [float(x_list[1]),float(x_list[2])] #latlong of waypoint with the curr min distance

		# 	try:
		# 		#print "distance not there in file"
		# 		waypoints_list,d = get_waypoints(x_latlong,LatLong[status2[int(x_list[0])]],state,dist,j,KEY) 
		# 	except IOError, e:
		# 		if e.errno == 101 or e.errno == 'socket error' or e.errno == -3 or e.errno == 2:
		# 			print "Network Error"
		# 			time.sleep(1)
		# 			waypoints_list,d = get_waypoints(x_latlong,LatLong[status2[int(x_list[0])]],state,dist,j,KEY) 
		# 		else:
		# 			raise
		# 	wp_list_tmp = [u for u in waypoints_list if u != LatLong[status2[int(x_list[0])]]]
		# 	block_waypoints_list = update_block_waypoint(block_waypoints_list,wp_list_tmp)



			# print "Waypoints List:::",waypoints_list
			
			
		# 	for x,y in road_d_min.items():
		# 		rd_min = y
		# 		gp_latlong = LatLong[status2[int(x.split(',')[0])]] # Waypoint order does not matter
				
		# 		for l in waypoints_list:
		# 			try:
		# 				#print "distance not there in file"
		# 				wp_temp,rd = get_waypoints(gp_latlong,l,state,dist,j,KEY)
		# 			except IOError, e:
		# 				if e.errno == 101 or e.errno == 'socket error' or e.errno == -3 or e.errno == 2:
		# 					print "Network Error"
		# 					time.sleep(1)
		# 					wp_temp,rd = get_waypoints(gp_latlong,l,state,dist,j,KEY)
		# 				else:
		# 					raise 
		# 			wp_list_tmp = [u for u in waypoints_list if u != gp_latlong]
		# 			block_waypoints_list = update_block_waypoint(block_waypoints_list,wp_list_tmp)

					
		# 			#rd = road_dist_block(gp_latlong,l,state,dist,j,KEY)
		# 			if rd < rd_min:
		# 				rd_min = rd
		# 				rd_min_latlong = l
	
		# 		if rd_min < y:
		# 			del road_d_min[x]
		# 			road_d_min.update({x.split(',')[0]+','+','.join([str(u) for u in rd_min_latlong]):rd_min})
		
		# block_waypoints_list = [u for u in block_waypoints_list if u not in [LatLong[status2[v]] for v in range(len(status2))]]
			
		############################################
		# Finished Getting Waypoints for the block #
		############################################

		#print "All waypoints in the block",block_waypoints_list,[LatLong[status2[v]] for v in range(len(status2))]
		#sys.exit()

		##################################
		# Start Making the Spanning Tree #
		##################################

		## Make the underlyting graph with gps and wps ##
		original_graph = dict()
		#key = node and value = [ [node,road_dist] ]
		#Creating nodes in the graph
		for l in range(len(status2)):
			original_graph.update({'gp,'+str(l):[]})
		tower_connect_dict = dict()
		#key = tower id, value = list of gps connected to the tower

		phase1_connect_dict = dict()	

		# for l in range(len(block_waypoints_list)):
		# 	original_graph.update({'wp,'+str(l):[]})
		towers_list = get_towers_list(Phase_lists[0],NODE)
		phase1_list = get_phase1_list(Phase_lists[0],NODE)
		for z in towers_list:
			tower_connect_dict.update({z:[]})
		for z in phase1_list:
			phase1_connect_dict.update({z:[]})
		connect_flag = 'TOWER'
		print "no of gps in original graph",len(original_graph)
		

		while  True:
			if connect_flag == 'TOWER':
				link = make_tower_connection(None,original_graph.keys(),towers_list,adjMats[0],reqTP_mat,status2)
			else:
				link = make_phase1_connection(None,original_graph.keys(),phase1_list,adjMats[0],reqTP_mat,status2)
			
			if link == {}:
					if connect_flag == 'TOWER':
						connect_flag = "PHASE1"
						continue
					else:
						break
			else:
				# print "gp connected wirelessly"
				# print "link",link

				leaf_gp_index = int(link.keys()[0].split(',')[1])
				leaf_gp_id = link.keys()[0]
				min_arial_dist = 100000000000000
				for x in link[leaf_gp_id]:
					arial_dist = latlongdist(LatLong[status2[leaf_gp_index]],LatLong[x])
					if arial_dist < min_arial_dist:
						min_arial_dist = arial_dist
						min_dist_node = x

				if connect_flag == 'TOWER':
					print "GP Connected to Tower::",min_dist_node,leaf_gp_id
					tower_connect_dict[min_dist_node].append(leaf_gp_id) #connection added to the chosen tower
					if len(tower_connect_dict[min_dist_node]) >= TOWER_CONNECTION_LIMIT:
						towers_list = [u for u in towers_list if u != min_dist_node] #Remove tower if it has max connections
				else:
					print "GP Connected to Phase1::",min_dist_node,leaf_gp_id
					phase1_connect_dict[min_dist_node].append(leaf_gp_id) #connection added to the chosen tower
					if len(phase1_connect_dict[min_dist_node]) >= P1_CONNECTION_LIMIT:
						phase1_list = [u for u in phase1_list if u != min_dist_node] #Remove tower if it has max connections
					
				#remaining_original_graph. = [u for u in problem_cases if u != leaf_gp_id]
				del original_graph[link.keys()[0]]
		connect_flag = 'TOWER'

		print "tower connections",tower_connect_dict
		print "ph1 connections",phase1_connect_dict
		print "no of gps in new graph",len(original_graph)

		for x,y in tower_connect_dict.items():
			for gp in y:
				gp_id = int(gp.split(',')[1])	
				if tower_height[x] < transHeight_mat[x][[status2[gp_id]]]:
					tower_height[x] = transHeight_mat[x][[status2[gp_id]]]

		block_tot_conctd_to_towers = 0
		
		for x,y in tower_connect_dict.items():
			print "tower",x
			block_tot_conctd_to_towers += len(y)
			# x_id = x.split(',')[1]
			print "\n\n\n\ntower details",GP_Names[0][x],GP_lists[0][x]
			if len(y) > 0:	
				for gp in y:
					gp_id = int(gp.split(',')[1])
					# f.write(str(GP_Names[0][[x]]) + ',' +str(GP_lists[0][[x]]) + ','+str(j)+',' +str(LatLong[x][0]) + ',' +str(LatLong[x][1]) + ',' +str(Phase_lists[0][x]) + ',' + str(transHeight_mat[x][status2[gp_id]])+','+str(throughPut_mat[x][status2[gp_id]]) +','+str(GP_Names[0][status2[gp_id]]) + ',' +str(GP_lists[0][status2[gp_id]]) + ',' +str(j)+','+str(LatLong[status2[gp_id]][0]) + ',' +str(LatLong[status2[gp_id]][1]) + ',' +str(Phase_lists[0][status2[gp_id]]) + ','+ str(receivHeight_mat[x][status2[gp_id]]) +',' +'\n' )
					f.write(str(GP_Names[0][x]) + ',' +str(GP_lists[0][x]) + ','+str(j)+',' +str(LatLong[x][0]) + ',' +str(LatLong[x][1]) + ',' +str(Phase_lists[0][x]) + ',' + str(tower_height[x][0])+','+str(throughPut_mat[x][status2[gp_id]]) +','+str(GP_Names[0][status2[gp_id]]) + ',' +str(GP_lists[0][status2[gp_id]]) + ',' +str(j)+','+str(LatLong[status2[gp_id]][0]) + ',' + str(LatLong[status2[gp_id]][1]) + ',' +str(Phase_lists[0][status2[gp_id]]) + ','+ str(receivHeight_mat[x][status2[gp_id]]) +',' +'\n' )


		for x,y in phase1_connect_dict.items():
			for gp in y:
				gp_id = int(gp.split(',')[1])	
				if tower_height[x] < transHeight_mat[x][[status2[gp_id]]]:
					tower_height[x] = transHeight_mat[x][[status2[gp_id]]]


		block_tot_conctd_to_ph1=0
		for x,y in phase1_connect_dict.items():
			block_tot_conctd_to_ph1 += len(y)
			# x_id = x.split(',')[1]
			if len(y) > 0:
				for gp in y:
					gp_id = int(gp.split(',')[1])
					# f.write(str(GP_Names[0][x]) + ',' +str(GP_lists[0][x]) + ','+str(j)+',' +str(LatLong[x][0]) + ',' +str(LatLong[x][1]) + ',' +str(Phase_lists[0][status2[x]]) + ',' + str(transHeight_mat[m][x])+','+str(throughPut_mat[m][gp_id]) +','+str(GP_Names[0][gp_id]) + ',' +str(GP_lists[0][gp_id]) + ',' +str(j)+','+str(LatLong[gp_id][0]) + ',' +str(LatLong[gp_id][1]) + ',' +str(Phase_lists[0][gp_id]) + ','+ str(receivHeight_mat[m][gp_id]) +',' +'\n' )
					f.write(str(GP_Names[0][x]) + ',' +str(GP_lists[0][x]) + ','+str(j)+',' +str(LatLong[x][0]) + ',' +str(LatLong[x][1]) + ',' +str(Phase_lists[0][x]) + ',' + str(tower_height[x][0])+','+str(throughPut_mat[x][status2[gp_id]]) +','+str(GP_Names[0][status2[gp_id]]) + ',' +str(GP_lists[0][status2[gp_id]]) + ',' +str(j)+','+str(LatLong[status2[gp_id]][0]) + ',' + str(LatLong[status2[gp_id]][1]) + ',' +str(Phase_lists[0][status2[gp_id]]) + ','+ str(receivHeight_mat[x][status2[gp_id]]) +','+'\n' )

		# print "len of original graph",len(original_graph)
		# while  True:
		# 	if connect_flag == 'TOWER':
		# 		link = make_tower_connection(None,original_graph.keys(),towers_list,adjMats[0],reqTP_mat,status2)
		# 		# print "link",link
		# 	else:
		# 		link = make_phase1_connection(None,original_graph.keys(),phase1_list,adjMats[0],reqTP_mat,status2)
			
		# 	if link == {}:
		# 			if connect_flag == 'TOWER':
		# 				connect_flag = "PHASE1"
		# 				continue
		# 			else:
		# 				break
		# 	else:
		# 		print "link",link
		# 		del original_graph[link.keys()[0]]
		# 		print "new original graph",len(original_graph.keys())
				
		
		# print "running for wireless"				
		# sys.exit()				



# 		for l in range(len(status2)):
# 			l_key = 'gp,'+str(l)
			
# 			for m in range(l+1,len(status2)):
# 				m_key = 'gp,'+str(m)
# 				#d_chk = road_dist_block_file(LatLong[status2[l]],LatLong[status2[m]],state,dist,j)
# 				d_chk = road_dist_block(LatLong[status2[l]],LatLong[status2[m]],state,dist,j)
# 				if d_chk > 0:
# 					original_graph[l_key].append([m_key,d_chk])
# 					original_graph[m_key].append([l_key,d_chk])
# 			print "Done making gp to gp adjacency for",GP_Names[0][status2[l]]
			
# 			for m in range(len(block_waypoints_list)):
# 				m_key = 'wp,'+str(m)
# 				d_chk = road_dist_block_file(LatLong[status2[l]],block_waypoints_list[m],state,dist,j)
# 				if d_chk > 0:
# 					original_graph[l_key].append([m_key,d_chk])
# 					original_graph[m_key].append([l_key,d_chk])
# 			print "Done making gp to wp adjacency!!!",GP_Names[0][status2[l]]

# 		for l in range(len(block_waypoints_list)):
# 			l_key = 'wp,'+str(l)
			
# 			for m in range(l+1,len(block_waypoints_list)):
# 				m_key = 'wp,'+str(m)
# 				d_chk = road_dist_block_file(block_waypoints_list[l],block_waypoints_list[m],state,dist,j)
# 				if d_chk > 0:
# 					original_graph[l_key].append([m_key,d_chk])
# 					original_graph[m_key].append([l_key,d_chk])	
# 		print "Done making wp to wp adjacency!!!"		

# 		print "original graph ------",len(original_graph)		

# 		no_neighbor_nodes = []
# 		for x,y in original_graph.items():
# 			if y == []:
# 				print "Node is not connected to anything::::", x
# 				no_neighbor_nodes.append(x)

# 		#sys.exit()

		
# 		## Building the Tree from the graph ##	

# 		tree_with_wps = dict()
# 		# key = node and value = parent id, link lenght, [children], route length from bhq
# 		#node_status = dict() #whether nodes are in or out of the current tree
		
# 		for x in original_graph.keys():
# 			init_tree_value_list = [None,0,[],0]
# 			if x == 'gp,'+str(bhq):
# 				y = 'in'
# 			else:
# 				y = 'out'
# 			init_tree_value_list.append(y)
# 			init_tree_value_list.append(0)
# 			tree_with_wps.update({x:init_tree_value_list})

# 		# print "Tree with wps:::", tree_with_wps

# 		last_added = 'gp,'+str(bhq)
# 		# print "Tree initial values::", tree_with_wps,last_added
# 		not_yet_connected = [x for x in tree_with_wps.keys() if tree_with_wps[x][4] == 'out']

# 		# print "Not yet connected 1:::",not_yet_connected

# 		#while (len(not_yet_connected) > 0):
# 		while (len(not_yet_connected) > len(no_neighbor_nodes)):
# 			#last_added_adj_list = original_graph[last_added]
# 			#print "LAST ADDED====",last_added,not_yet_connected
# 			for x in original_graph[last_added]: 
# 				#print "Last added x==== ",x #original_graph[last_added]

# 				x_id = x[0]
# 				x_dist_from_last_added = x[1]


# 				#if tree_with_wps[x_id][4] == 'in':
# 				if x_id not in not_yet_connected:
# 					#print "The Neighbours are connected",tree_with_wps[x_id]
# 					continue
# 				else:
# 					#print "Processing Node === ",tree_with_wps[x_id]
# 					if tree_with_wps[x_id][0] == None:
# 						tree_with_wps[x_id][0] = last_added
# 						tree_with_wps[x_id][1] = x[1]
# 						tree_with_wps[x_id][3] = tree_with_wps[last_added][3] + x[1]
# 						tree_with_wps[x_id][5] = tree_with_wps[x_id][1] + BETA*tree_with_wps[x_id][3]
# 					else:
# 						if tree_with_wps[x_id][5] > x[1] + BETA*(tree_with_wps[last_added][3]+x[1]):
# 							tree_with_wps[x_id][1] = x[1]
# 							tree_with_wps[x_id][0] = last_added
# 							tree_with_wps[x_id][3] = tree_with_wps[last_added][3] + x[1]
# 							tree_with_wps[x_id][5] = tree_with_wps[x_id][1] + BETA*tree_with_wps[x_id][3]

# 			min_length = 10000000000000000
# 			min_length_id = not_yet_connected[0] 
# 			for x in [y for y in not_yet_connected if tree_with_wps[y][0] != None]:
# 				if tree_with_wps[x][5] < min_length: #for MST 
# 					min_length = tree_with_wps[x][5]
# 					min_length_id = x

# 			if min_length == 10000000000000000: # No more nodes can be connected to the tree
# 				print "Not yet conncted == ", not_yet_connected
# 				break
# 				#sys.exit()

# 			#print "Chosen Node for addition to tree == ",min_length_id,min_length,tree_with_wps[min_length_id]
# 			tree_with_wps[min_length_id][4] = 'in'
# 			tree_with_wps[tree_with_wps[min_length_id][0]][2].append(min_length_id)

# 			last_added = min_length_id
# 			not_yet_connected = [x for x in tree_with_wps.keys() if tree_with_wps[x][4] == 'out']

# 		print "Not yet connected:::",len(not_yet_connected),not_yet_connected,no_neighbor_nodes

# 		for y in [u for u in tree_with_wps.keys() if tree_with_wps[u][4] == 'out']:
# 			del tree_with_wps[y]

		


# 		# print "B4 HANDLE NO ROAD DATA === ", tree_with_wps

# 		tree_with_wps,sattelite_reco_list = handle_no_road_cases(tree_with_wps,LatLong,block_waypoints_list,status2,state,dist) 
# 		#Handles no road data cases
# 		# print "B4 HANDLE NO ROAD DATA === ", tree_with_wps,sattelite_reco_list

# 		tree_with_wps = prun_leaf_wps(tree_with_wps) #Removes leaf wp's

# 		#remove te's and wp's from satellite recommendations
# 		sattelite_reco_list = [u for u in sattelite_reco_list if u.split(',')[0] == 'gp' and Phase_lists[0][status2[int(u.split(',')[1])]]!=15]			

# 		print "Satellite Recommendations:::",sattelite_reco_list
# 		# print "Tree with wps::::", tree_with_wps
		
# 		############################################################
# 		# Get Route length along tree from each Telephone Exchange # 
# 		############################################################

# 		te_route_length_dict = dict()
# 		# key is TE node ID and value is dict containing {node_id:route_legth}

# 		for x in bhqs: 
# 			te_id = 'gp,'+str(status2.index(x))
# 			if te_id in tree_with_wps.keys():
# 				# print "TREE WITH WPS====",tree_with_wps
# 				te_route_length_dict.update({te_id:get_te_route_length(tree_with_wps,te_id)})

# 		###############################################################################
# 		# Find Problem cases, nodes with distance > MAX_ROUTE_LENGTH from chosen BHQs #
# 		###############################################################################

# 		#min_route_length = [10000000000 for x in range(len(tree_dist[0]))]
		
		
# 		# bhq_id = 'gp,'+str(bhq)
# 		# for x in tree_with_wps.keys():
# 		# 	olt_assigned_dict.update({x:bhq_id}) #initially every point is connected to bhq
		 
# 		problem_cases = [x for x,y in tree_with_wps.items() if y[3] > MAX_ROUTE_LENGTH and y[3] < 1000000]

		
		
# 		# for x in problem_cases:
# 		# 	problem_case_gps.append(x, block_phase[j][status2[(int(x.split(',')[1]))]])
# 		# print "prob case gps " 
# 		#sys.exit() #Prasanna

# 		all_olts = [bhq_id] 
# 		resolvable_cases_dict = dict()
# 		#key = bhq id and value = list of problem cases that can be resolved by the gp

# 		if len(problem_cases) > 0: #If problem cases exist
# 			while True:
# 				for x in bhqs: #Process for all TEs
#  					if x in all_olts: #If already chosen as OLT location do nothing
# 						continue
# 					x_id = 'gp,'+str(status2.index(x))
# 					resolvable_cases_dict.update({x_id:[]})

# 					resolvable_cases_dict[x_id] = [y for y in problem_cases if te_route_length_dict[x_id][y] < MAX_ROUTE_LENGTH]

# 				most_resolved = 0

# 				for x in resolvable_cases_dict.keys():
# 					if len(resolvable_cases_dict[x]) > most_resolved:
# 						most_resolved = len(resolvable_cases_dict[x])
# 						most_resolving_te = x 

# 				if most_resolved == 0:
# 					break
# 				else:
# 					all_olts.append(most_resolving_te)
# 					problem_cases = [y for y in problem_cases if y not in resolvable_cases_dict[most_resolving_te]]

# 		# Problem cases should not contain wp's and te's
# 		problem_cases = [u for u in problem_cases if u.split(',')[0] == 'gp' and Phase_lists[0][status2[int(u.split(',')[1])]]!=15]			
# 		# print "Chosen OLTs =", all_olts
# 		print "Remaining Problem cases = ", problem_cases 
# 		#Remove problem cases from tree

# 		tree_with_wps = remove_nodes_from_tree(tree_with_wps,problem_cases)

# 		##########################################################################
# 		# Assign nodes to the chosen OLT locations based on the closest distance #
# 		##########################################################################

# 		olt_assigned_dict = dict()
# 		#key = node_id and value = id of olt location to which it will connect

# 		for x in all_olts:
# 			olt_assigned_dict.update({x:[]})

# 		for y in tree_with_wps.keys():
# 			min_tree_dist = 10000000

# 			for x in all_olts:
# 				if te_route_length_dict[x][y] < min_tree_dist:
# 					min_tree_dist = te_route_length_dict[x][y]
# 					min_tree_dist_olt = x

# 			olt_assigned_dict[min_tree_dist_olt].append([y,"{:0.2f}".format(min_tree_dist)])

# 		#print "OLT assigned :::: ", olt_assigned_dict #olts as key and its nodes as children 

# 		####### Construct rooted trees corresponding to diffent OLTs ########

# 		olt_trees_with_wps = dict()
		
# 		if len(all_olts) == 1:
# 			olt_trees_with_wps.update({bhq_id: tree_with_wps})
# 		else:
# 			for x in all_olts:
# 				olt_tree = {x:[None,0,[],0]}
# 				parent = tree_with_wps[x][0]
# 				nodes_to_be_checked = [y for y in tree_with_wps[x][2]]
# 				if parent == None:
# 					olt_trees_with_wps.update({x:make_rooted_tree(x,tree_with_wps,olt_assigned_dict[x],olt_tree,nodes_to_be_checked)})
# 				else:
# 					nodes_to_be_checked.append(parent)
# 					olt_trees_with_wps.update({x:make_rooted_tree(x,tree_with_wps,olt_assigned_dict[x],olt_tree,nodes_to_be_checked)})


# 					#prasanna
# 				#print "OLT TREE== ",x,olt_trees_with_wps[x]

# 				for y in [z[0] for z in olt_assigned_dict[x]]:
# 					if y not in olt_trees_with_wps[x].keys():
# 						print "Node not in tree::::::::::::::::::",x,y
# 						sys.exit()

# 		#sys.exit()
				

# 		fibre_all_len = 0
# 		fibre_all_max_route_length = 0

# 		for z in olt_trees_with_wps.keys():

# 			olt_trees_with_wps[z] = prun_leaf_wps(olt_trees_with_wps[z]) #Removes leaf wp's
# 			mst_link_list = list()
# 			#mst_link_dict = print_mst_links('gp,'+str(bhq),tree_with_wps,mst_link_dict)

# 			tot_mst_links = 0
# 			for x in olt_trees_with_wps[z].keys():
# 				if olt_trees_with_wps[z][x][2] != []:
# 					tot_mst_links += len(tree_with_wps[x][2])
# 					if fibre_all_max_route_length < olt_trees_with_wps[z][x][3]:
# 						fibre_all_max_route_length = olt_trees_with_wps[z][x][3]
# 					for y in olt_trees_with_wps[z][x][2]:
# 						fibre_all_len += int(olt_trees_with_wps[z][y][1])
# 						mst_link_list.append([x,y])
# 				#Add in olt_connections, where olt is z and node connected to it is x

			

# 			# print "mst_link_list::::::",len(mst_link_list),tot_mst_links,mst_link_list

# 			## Print MST links in the file ##
# 			for x in mst_link_list:
# 				x_from = x[0].split(',')[0]
# 				x_to = x[1].split(',')[0]
# 				gp_from_name = ' '
# 				gp_to_name = ' ' 
				
# 				if x_from == 'wp':
# 					from_latlong =  block_waypoints_list[int(x[0].split(',')[1])]
				
# 				elif x_from == 'gp':
# 					from_latlong = LatLong[status2[(int(x[0].split(',')[1]))]]
# 					gp_from_name = GP_Names[0][status2[(int(x[0].split(',')[1]))]]
				
# 				if x_to == 'wp':
# 					to_latlong =  block_waypoints_list[int(x[1].split(',')[1])]
				
# 				elif x_to == 'gp':
# 					#print "Debug gp name printing problem:::",x
# 					to_latlong = LatLong[status2[int(x[1].split(',')[1])]]
# 					gp_to_name = GP_Names[0][status2[(int(x[1].split(',')[1]))]]

# 				#print str(j),gp_from_name,str(from_latlong[0]),str(from_latlong[1]),gp_to_name,str(to_latlong[0]),str(to_latlong[1]),tree_with_wps[x[1]][1]
		
					
# 				f5.write(str(j)+ ", " + gp_from_name +',' + str(from_latlong[0]) + ", "+ str(from_latlong[1]) + "," + gp_to_name + ',' + str(to_latlong[0]) + "," +str(to_latlong[1]) +',' + str(float(tree_with_wps[x[1]][1]/1000.0)) + '\n' )
# 		f3.write(str(j)+','+str(fibre_all_len/1000)+'km,'+ str(fibre_all_max_route_length/1000) + ','+ str(len(all_olts)) +'\n')
		
# 		# print "olt tree with wps",olt_trees_with_wps		
# 		tree_with_wireless = deepcopy(olt_trees_with_wps)
# 		# print "olt tree with wireless",tree_with_wireless

# 		tower_connect_dict = dict()
# 		#key = tower id, value = list of gps connected to the tower

# 		phase1_connect_dict = dict()
# 		#key = phase1_gp_id, value = list of gps connected to the tower

# 		towers_list = get_towers_list(Phase_lists[0],NODE)
# 		phase1_list = get_phase1_list(Phase_lists[0],NODE)

# 		print "Tower List = ", towers_list

# 		for z in towers_list:
# 			tower_connect_dict.update({z:[]})
# 		for z in phase1_list:
# 			phase1_connect_dict.update({z:[]})


# 		connect_flag = 'TOWER'
# 		print "\n\n\n\n\nLEN OF OLT, block code",len(olt_trees_with_wps.keys()),j

# 		problem_cases += [u for u in not_yet_connected if u.split(',')[0] == 'gp']

# 		while  True:
# 			if connect_flag == 'TOWER':
# 				link = make_tower_connection(None,problem_cases,towers_list,adjMats[0],reqTP_mat,status2)
# 			else:
# 				link = make_phase1_connection(None,problem_cases,phase1_list,adjMats[0],reqTP_mat,status2)
			
# 			if link == {}:
# 					if connect_flag == 'TOWER':
# 						connect_flag = "PHASE1"
# 						continue
# 					else:
# 						break
# 			else:
# 				leaf_gp_index = int(link.keys()[0].split(',')[1])
# 				leaf_gp_id = link.keys()[0]
# 				min_arial_dist = 100000000000000
# 				for x in link[leaf_gp_id]:
# 					arial_dist = latlongdist(LatLong[status2[leaf_gp_index]],LatLong[x])
# 					if arial_dist < min_arial_dist:
# 						min_arial_dist = arial_dist
# 						min_dist_node = x

# 				if connect_flag == 'TOWER':
# 					print "Problem case Connected to Tower::",min_dist_node,leaf_gp_id
# 					tower_connect_dict[min_dist_node].append(leaf_gp_id) #connection added to the chosen tower
# 					if len(tower_connect_dict[min_dist_node]) >= TOWER_CONNECTION_LIMIT:
# 						towers_list = [u for u in towers_list if u != min_dist_node] #Remove tower if it has max connections
# 				else:
# 					print "Problem Case Connected to Phase1::",min_dist_node,leaf_gp_id
# 					phase1_connect_dict[min_dist_node].append(leaf_gp_id) #connection added to the chosen tower
# 					if len(phase1_connect_dict[min_dist_node]) >= P1_CONNECTION_LIMIT:
# 						phase1_list = [u for u in phase1_list if u != min_dist_node] #Remove tower if it has max connections
					
# 				problem_cases = [u for u in problem_cases if u != leaf_gp_id]

# 		connect_flag = 'TOWER'


# 		while  True:
# 			if connect_flag == 'TOWER':
# 				link = make_tower_connection(None,sattelite_reco_list,towers_list,adjMats[0],reqTP_mat,status2)
# 			else:
# 				link = make_phase1_connection(None,sattelite_reco_list,phase1_list,adjMats[0],reqTP_mat,status2)
			
# 			if link == {}:
# 					if connect_flag == 'TOWER':
# 						connect_flag = "PHASE1"
# 						continue
# 					else:
# 						break
# 			else:
# 				leaf_gp_index = int(link.keys()[0].split(',')[1])
# 				leaf_gp_id = link.keys()[0]
# 				min_arial_dist = 100000000000000
# 				for x in link[leaf_gp_id]:
# 					arial_dist = latlongdist(LatLong[status2[leaf_gp_index]],LatLong[x])
# 					if arial_dist < min_arial_dist:
# 						min_arial_dist = arial_dist
# 						min_dist_node = x

# 				if connect_flag == 'TOWER':
# 					print "Satellite Case Connected to Tower::",min_dist_node,leaf_gp_id
# 					tower_connect_dict[min_dist_node].append(leaf_gp_id) #connection added to the chosen tower
# 					if len(tower_connect_dict[min_dist_node]) >= TOWER_CONNECTION_LIMIT:
# 						towers_list = [u for u in towers_list if u != min_dist_node] #Remove tower if it has max connections
# 				else:
# 					print "Satellite Case Connected to Phase1::",min_dist_node,leaf_gp_id
# 					phase1_connect_dict[min_dist_node].append(leaf_gp_id) #connection added to the chosen tower
# 					if len(phase1_connect_dict[min_dist_node]) >= P1_CONNECTION_LIMIT:
# 						phase1_list = [u for u in phase1_list if u != min_dist_node] #Remove tower if it has max connections
					
# 				sattelite_reco_list = [u for u in sattelite_reco_list if u != leaf_gp_id]

# 		connect_flag = 'TOWER'

# 		gp_list_in_tree = list()

# 		for z in tree_with_wireless.keys():

# 			# print "tree before wireless",len(olt_assigned_dict[z])
# 			while True:

# 				curr_leaf_nodes = [x for x in tree_with_wireless[z].keys() if tree_with_wireless[z][x][2]==[] and float(reqTP_mat[int(x.split(',')[1])]) <= 6250.0]
# 				curr_leaf_nodes = [x for x in curr_leaf_nodes if Phase_lists[0][status2[int(x.split(',')[1])]] != 15]

# 				if connect_flag == 'TOWER':
# 					link = make_tower_connection(tree_with_wireless[z],curr_leaf_nodes,towers_list,adjMats[0],reqTP_mat,status2,'TREE')
# 				else:
# 					link = make_phase1_connection(tree_with_wireless[z],curr_leaf_nodes,phase1_list,adjMats[0],reqTP_mat,status2,'TREE')
				
# 				if link == {}:
# 						if connect_flag == 'TOWER':
# 							connect_flag = "PHASE1"
# 							continue
# 						else:
# 							break
# 				else:
# 					leaf_gp_index = int(link.keys()[0].split(',')[1])
# 					leaf_gp_id = link.keys()[0]
# 					min_arial_dist = 100000000000000
# 					for x in link[leaf_gp_id]:
# 						# print "X = ",x 
# 						# print LatLong[status2[x]]
# 						arial_dist = latlongdist(LatLong[status2[leaf_gp_index]],LatLong[x])
# 						if arial_dist < min_arial_dist:
# 							min_arial_dist = arial_dist
# 							min_dist_node = x

# 					if connect_flag == 'TOWER':
# 						tower_connect_dict[min_dist_node].append(leaf_gp_id) #connection added to the chosen tower
# 						if len(tower_connect_dict[min_dist_node]) >= TOWER_CONNECTION_LIMIT:
# 							towers_list = [u for u in towers_list if u != min_dist_node] #Remove tower if it has max connections
# 					else:
# 						phase1_connect_dict[min_dist_node].append(leaf_gp_id) #connection added to the chosen tower
# 						if len(phase1_connect_dict[min_dist_node]) >= P1_CONNECTION_LIMIT:
# 							phase1_list = [u for u in phase1_list if u != min_dist_node] #Remove tower if it has max connections
						
# 					leaf_gp_parent = tree_with_wireless[z][leaf_gp_id][0]
# 					tree_with_wireless[z][leaf_gp_parent][2] = [u for u in tree_with_wireless[z][leaf_gp_parent][2] if u != leaf_gp_id] 
# 					del tree_with_wireless[z][leaf_gp_id]
# 					tree_with_wireless[z] = prun_leaf_wps(tree_with_wireless[z])
			

# 			############### stats #############		
			

# 			# for key,values in tower_connect_dict.items():	#connected to towers	
# 			# 	print "tower",key,len(values),values
# 			# 	conctd_to_towers += len(values)
# 			# 	for x in values:
# 			# 			conctd_to_tower_gps.append([x, block_phase[j][status2[(int(x.split(',')[1]))]]])
# 			# print "\n\n\nconctd to towers ", conctd_to_tower_gps		
# 			# conctd_to_towers = len([ x for x in conctd_to_tower_gps if x[1]!=15 ] )
# 			# # print "\n\n\nno of ph1 gps concted to ph1",len([ x for x in conctd_to_ph1_gps if x[1]!=15 ])
# 			# print "\n\n\nno of gps concted to tower", conctd_to_towers

			

# 			# for key,values in phase1_connect_dict.items():  #connected to ph1
# 			# 	if len(values) > 0:		
# 			# 		print "phse1", key,len(values),values
# 			# 		for x in values:
# 			# 			conctd_to_ph1_gps.append([x, block_phase[j][status2[(int(x.split(',')[1]))]]])
# 			# 		# conctd_to_ph1_gps = [ x, block_phase[j][status2[(int(x[1].split(',')[1]))]] for x in values  if x==x ]  
# 			# print "\n\n\nconctd tp phase1 ", conctd_to_ph1_gps		
# 			# conctd_to_ph1 = len([ x for x in conctd_to_ph1_gps if x[1]!=15 ] )
# 			# # print "\n\n\nno of ph1 gps concted to ph1",len([ x for x in conctd_to_ph1_gps if x[1]!=15 ])
# 			# print "\n\n\nno of phase1 concted gps", conctd_to_ph1


# 			# No_of_Prb_cases = len([ x for x in problem_cases if x[1]!=15 or x[0]!= 'wp'] )
# 			No_of_Prb_cases = len(problem_cases)
# 			print "Prob case gps,No of prob cases",problem_cases,No_of_Prb_cases



# 			############ stats ####################	

# 			gp_list_olt_connctns = [x for x in tree_with_wireless[z].keys() if x.split(',')[0] == 'gp' and Phase_lists[0][status2[int(x.split(',')[1])]] != 15]				
# 			gp_list_in_tree += [x for x in tree_with_wireless[z].keys() if x.split(',')[0] == 'gp' and Phase_lists[0][status2[int(x.split(',')[1])]] != 15]
			

# 			z_id = int(z.split(',')[1])
# 			for gp in gp_list_olt_connctns:
# 				gp_id = int(gp.split(',')[1])
# 				f10.write(str(j)+","+str(GP_lists[0][status2[z_id]])+','+str(GP_Names[0][status2[z_id]])+","+str(LatLong[status2[z_id]][0])+","+str(LatLong[status2[z_id]][1])+','+str(GP_lists[0][status2[gp_id]])+","+str(GP_Names[0][status2[gp_id]])+","+str(LatLong[status2[gp_id]][0])+","+str(LatLong[status2[gp_id]][1])+','+str((tree_with_wireless[z][gp][3])/1000)+'\n')

		
# 		fibre_len = 0
# 		max_route_length = 0

# 		for z in tree_with_wireless.keys():
# 			mst_link_list = list()
# 			for x in tree_with_wireless[z].keys():
# 				if max_route_length < tree_with_wireless[z][x][3]:
# 					max_route_length = tree_with_wireless[z][x][3]
# 				if tree_with_wireless[z][x][2] != []:
# 					for y in tree_with_wireless[z][x][2]:
# 						mst_link_list.append([x,y])
# 						fibre_len += int(tree_with_wireless[z][y][1])
				
			
# 			for x in mst_link_list:
# 				x_from = x[0].split(',')[0]
# 				x_to = x[1].split(',')[0]
# 				gp_from_name = ' '
# 				gp_to_name = ' ' 
				
# 				if x_from == 'wp':
# 					from_latlong =  block_waypoints_list[int(x[0].split(',')[1])]
				
# 				elif x_from == 'gp':
# 					from_latlong = LatLong[status2[(int(x[0].split(',')[1]))]]
# 					gp_from_name = GP_Names[0][status2[(int(x[0].split(',')[1]))]]
				
# 				if x_to == 'wp':
# 					to_latlong =  block_waypoints_list[int(x[1].split(',')[1])]
				
# 				elif x_to == 'gp':
# 					to_latlong = LatLong[status2[int(x[1].split(',')[1])]]
# 					gp_to_name = GP_Names[0][status2[(int(x[1].split(',')[1]))]]
				
					


# 				f7.write(str(j)+ ", " + gp_from_name +',' + str(from_latlong[0]) + ", "+ str(from_latlong[1]) + "," + gp_to_name + ',' + str(to_latlong[0]) + "," +str(to_latlong[1]) +',' + str("{:0.2f}".format(float(tree_with_wireless[z][x[1]][1]/1000.0))) + '\n' )
# 		# print "fibre len ",(fibre_len)/1000		
# 		f6.write(str(j)+','+str(fibre_len/1000)+'km,'+ str(max_route_length/1000)+'km,'+str((fibre_all_len - fibre_len)/1000)+'km,'+str(len(all_olts))+'\n')	

# 		for z in tower_connect_dict.keys():
# 			if len(tower_connect_dict[z]) > 0:
# 				from_latlong = LatLong[z]
# 				for x in tower_connect_dict[z]:
# 					x_id = int(x.split(',')[1])
# 					to_latlong = LatLong[status2[x_id]]
# 					gp_to_name = GP_Names[0][status2[x_id]]
# 					# f7.write(str(j)+ ", " + gp_from_name +',' + str(from_latlong[0]) + ", "+ str(from_latlong[1]) + "," + gp_to_name + ',' + str(to_latlong[0]) + "," +str(to_latlong[1]) +',' + str(latlongdist(from_latlong,to_latlong)) + '\n' )	

# 		# dist_satellite_gps += sattelite_reco_list
# 		for s in sattelite_reco_list:
# 			s_id = int(s.split(',')[1])
# 			f4.write(str(j)+','+str(GP_lists[0][status2[s_id]])+','+str(GP_Names[0][status2[s_id]])+ ',' +str(LatLong[status2[s_id]][0]) + ',' +str(LatLong[status2[s_id]][1])+','+str(reqTP_mat[status2[s_id]])+'\n')
		
# 		for p in problem_cases:
# 			p_id = int(p.split(',')[1])
# 			f8.write(str(GP_Names[0][status2[p_id]])+','+str(GP_lists[0][status2[p_id]])+','+str(j)+','+str(LatLong[status2[p_id]][0])+','+str(LatLong[status2[p_id]][1])+','+str(reqTP_mat[status2[p_id]])+',Too far from bhqs\n')
# 		# dist_problem_case_gps += problem_cases	

# 		# f.write(str(GP_Names[0][m]) + ',' +str(GP_lists[0][m]) + ','+str(Block_code[m])+',' +str(LatLong[m][0]) + ',' +str(LatLong[m][1]) + ',' +str(Phase_lists[0][status2[gp_id]]) + ',' + str(transHeight_mat[m][gp])+','+str(throughPut_mat[m][gp]) +','+str(GP_Names[0][gp]) + ',' +str(GP_lists[0][gp]) + ',' +str(blk_code)+','+str(LatLong[gp][0]) + ',' +str(LatLong[gp][1]) + ',' +str(Phase_lists[0][gp]) + ','+ str(receivHeight_mat[m][gp]) +',' +'\n' )

# 		tot_onts += len(gp_list_in_tree)

# 		tot_olts += len(all_olts)
		
# 		tot_satel_recmdns += len(sattelite_reco_list) #prasanna
		
		for x,y in tower_connect_dict.items():
			for gp in y:
				gp_id = int(gp.split(',')[1])	
				if tower_height[x] < transHeight_mat[x][[status2[gp_id]]]:
					tower_height[x] = transHeight_mat[x][[status2[gp_id]]]

		block_tot_conctd_to_towers = 0
		for x,y in tower_connect_dict.items():
			print "tower",x
			block_tot_conctd_to_towers += len(y)
			# x_id = x.split(',')[1]
			print "\n\n\n\ntower details",GP_Names[0][x],GP_lists[0][x]
			if len(y) > 0:	
				for gp in y:
					gp_id = int(gp.split(',')[1])
# 					# f.write(str(GP_Names[0][[x]]) + ',' +str(GP_lists[0][[x]]) + ','+str(j)+',' +str(LatLong[x][0]) + ',' +str(LatLong[x][1]) + ',' +str(Phase_lists[0][x]) + ',' + str(transHeight_mat[x][status2[gp_id]])+','+str(throughPut_mat[x][status2[gp_id]]) +','+str(GP_Names[0][status2[gp_id]]) + ',' +str(GP_lists[0][status2[gp_id]]) + ',' +str(j)+','+str(LatLong[status2[gp_id]][0]) + ',' +str(LatLong[status2[gp_id]][1]) + ',' +str(Phase_lists[0][status2[gp_id]]) + ','+ str(receivHeight_mat[x][status2[gp_id]]) +',' +'\n' )
# 					f.write(str(GP_Names[0][x]) + ',' +str(GP_lists[0][x]) + ','+str(j)+',' +str(LatLong[x][0]) + ',' +str(LatLong[x][1]) + ',' +str(Phase_lists[0][x]) + ',' + str(tower_height[x][0])+','+str(throughPut_mat[x][status2[gp_id]]) +','+str(GP_Names[0][status2[gp_id]]) + ',' +str(GP_lists[0][status2[gp_id]]) + ',' +str(j)+','+str(LatLong[status2[gp_id]][0]) + ',' + str(LatLong[status2[gp_id]][1]) + ',' +str(Phase_lists[0][status2[gp_id]]) + ','+ str(receivHeight_mat[x][status2[gp_id]]) +',' +'\n' )


		for x,y in phase1_connect_dict.items():
			for gp in y:
				gp_id = int(gp.split(',')[1])	
				if tower_height[x] < transHeight_mat[x][[status2[gp_id]]]:
					tower_height[x] = transHeight_mat[x][[status2[gp_id]]]


		block_tot_conctd_to_ph1=0
		for x,y in phase1_connect_dict.items():
			block_tot_conctd_to_ph1 += len(y)
			# x_id = x.split(',')[1]
			if len(y) > 0:
				for gp in y:
					gp_id = int(gp.split(',')[1])
# 					# f.write(str(GP_Names[0][x]) + ',' +str(GP_lists[0][x]) + ','+str(j)+',' +str(LatLong[x][0]) + ',' +str(LatLong[x][1]) + ',' +str(Phase_lists[0][status2[x]]) + ',' + str(transHeight_mat[m][x])+','+str(throughPut_mat[m][gp_id]) +','+str(GP_Names[0][gp_id]) + ',' +str(GP_lists[0][gp_id]) + ',' +str(j)+','+str(LatLong[gp_id][0]) + ',' +str(LatLong[gp_id][1]) + ',' +str(Phase_lists[0][gp_id]) + ','+ str(receivHeight_mat[m][gp_id]) +',' +'\n' )
# 					f.write(str(GP_Names[0][x]) + ',' +str(GP_lists[0][x]) + ','+str(j)+',' +str(LatLong[x][0]) + ',' +str(LatLong[x][1]) + ',' +str(Phase_lists[0][x]) + ',' + str(tower_height[x][0])+','+str(throughPut_mat[x][status2[gp_id]]) +','+str(GP_Names[0][status2[gp_id]]) + ',' +str(GP_lists[0][status2[gp_id]]) + ',' +str(j)+','+str(LatLong[status2[gp_id]][0]) + ',' + str(LatLong[status2[gp_id]][1]) + ',' +str(Phase_lists[0][status2[gp_id]]) + ','+ str(receivHeight_mat[x][status2[gp_id]]) +','+'\n' )
		tot_conctd_to_towers += block_tot_conctd_to_towers
		tot_conctd_to_ph1 += block_tot_conctd_to_ph1
# 		tot_problem_cases += len(problem_cases)

# 		#print "Total GP's "

# 		#########################################
# 		# Stats for debugging 
# 		########################################

# 		block_tot_ph2_gps = len([u for u in block_phase[j].keys() if block_phase[j][u] == 2])
# 		block_tot_problem_cases = len(problem_cases)
# 		block_tot_satel_recmdns = len(sattelite_reco_list)
# 		check_tot = 0
# 		check_tot += block_tot_satel_recmdns+block_tot_conctd_to_ph1+block_tot_conctd_to_towers+block_tot_problem_cases
# 		check_tot += len(gp_list_in_tree)

# 		if check_tot != block_tot_ph2_gps:
# 			print "Big Problem... Debug this Block::",j
# 			print "Phase 2 Gps = ",block_tot_ph2_gps,[u for u in block_phase[j].keys() if block_phase[j][u] == 2]
# 			print "Problem Cases = ", block_tot_problem_cases,problem_cases
# 			print "Satellite Reco = ",block_tot_satel_recmdns,sattelite_reco_list
# 			print "GPs in tree = ",len(gp_list_in_tree),gp_list_in_tree
# 			print "GPs connected to Towers = ",block_tot_conctd_to_towers
			
# 			block_tot_conctd_to_towers_list = list()
# 			for x,y in tower_connect_dict.items():
# 				block_tot_conctd_to_towers_list += y
# 			print block_tot_conctd_to_towers_list

# # 			print "GPs connected to Phase 1 = ",block_tot_conctd_to_ph1
# 			block_tot_conctd_to_ph1_list=list()
# 			for x,y in phase1_connect_dict.items():
# 				block_tot_conctd_to_ph1_list += y
# 			print block_tot_conctd_to_ph1_list
# 			tot_conctd_to_towers += block_tot_conctd_to_towers
# 			tot_conctd_to_ph1 += block_tot_conctd_to_ph1
# 			sys.exit()



# 	print "Total Number of Phase 2 GPs", tot_ph2_gps

	tot_ph1_gps = len([x for x in range(len(Phase_lists[0])) if int(Phase_lists[0][x]) == 21])
	tot_rural_exgs = len([x for x in range(len(Phase_lists[0])) if int(Phase_lists[0][x]) == 15])
	tot_towers = len([x for x in range(len(Phase_lists[0])) if int(Phase_lists[0][x]) == 9])
	tot_ph2_gps = len([x for x in range(len(Phase_lists[0])) if int(Phase_lists[0][x]) == 2])


	

	
	
	f2.write(str(input_file)+','+str(tot_ph1_gps)+','+str(tot_ph2_gps)+','+str(tot_rural_exgs)+','+str(tot_towers)+','+str(tot_conctd_to_ph1)+','+str(tot_conctd_to_towers)+'\n')



# # 	print ("Closing everything!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
# # 	#closeall()
	
# 	# print dist_olts
# 	# sys.exit()



for file in os.listdir("input"):
	if file.endswith(".csv"):
		do_something(file.split(".")[0])
	#sys.exit()

print "Congratulations IITB Team for the AWESOME results!!!!"

# do_something(245)

# print "Towers ",t
# print "Unconnected GPs ",ug
# print "connected to phase 1 status 22--- ",p1c
# print "close to tower   --status 8",ct
# print "Throughput req. more than 150mbps status 12----",tp
# print "connected to 12--status 13 -s",c12
# print "connected to tower i.e 10-s",cont
# print "new fibre provided i.e. status 5-s",nfibre
# print "connected to new fibre i.e status  6 -s",conf



# degreeGp = np.sum(adjMats[0], axis = 1)
# sumAllElementsAdjMat = np.sum(degreeGp)
# print degreeGp[np.argmax(degreeGp)]
# print sumAllElementsAdjMat
  
