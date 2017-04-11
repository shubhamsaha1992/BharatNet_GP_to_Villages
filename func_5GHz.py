from __future__ import division
import random
import math
import os
import numpy as np
import matplotlib.pyplot as plt
# import simplejson
try:
	import simplejson
except:
	import json as simplejson
import urllib
import time
from goapi import sign_url
import hashlib
import hmac
import base64
from copy import copy
import sys
import urlparse


__author__= 'infonet'
__date__  = '25May2016'



MIN_ANT_HEIGHT = 3          #Minimum antenna height  ---not used now
INCR_ANT_HEIGHT = 2         ##Increment in antenna height  ----not used now
FADE_MARGIN_REQ = 5        ##required fade margin for every link

txPower_2_6= 24
Gt_2_6= 25              #Transmitter gain for 5.8 Ghz
Gr_2_6= 25              #Receiver gain for 5.8 Ghz
NN_2_6= -100            ##Noise for 2.6Ghz
Gt_5_8= 25              #Transmitter gain for 5.8 Ghz
Gr_5_8= 25              #Receiver gain for 5.8 Ghz
NN_5_8= -100            ##Noise for 2.6Ghz
htListT = [10,20,30,40]      ##Available height of Towers
htListR = [3,6,9,15]      ##Available height of Towers
TPactual=0.7            ##Ratio of actual throughput to theoritical throughput for 5.8Ghz 
GPThptVal = 100


ELEVATION_BASE_URL = 'https://maps.google.com/maps/api/elevation/json'





def getElevation(path, latlong_list, state="Maharashtra", dist="Nandurbar", samples="512",sensor="false", **elvtn_args):
	'''
		path contains a '|' seperated lat long eg
			lat0, long0 | lat1, long1
	'''
	print "fetching at", time.time()
	secret = 'psWqzr5Q3Nj0hMjD5SETEzs2ebs='
	client='gme-iitmumbai'
	elvtn_args.update({
				'client':client,
				'path': path,
				'samples': samples,
				'sensor': sensor,
				# 'key': key
				})
	
	url = ELEVATION_BASE_URL + '?' + urllib.urlencode(elvtn_args)
	signedurl=sign_url(url, secret)
	response = simplejson.load(urllib.urlopen(signedurl))	
	# f= simplejson.load(urllib.urlopen(signedurl))
	####print signedurl,"signed url"	
	# #print (response)


	# Create a dictionary for each results[] object
	elevationArray = []

	for resultset in response['results']:
		elevationArray.append(int(resultset['elevation']))
		# #print (elevationArray)
	path = path
	linkele = path, elevationArray
	
	#Append fetched data in a file eleFile
	if(elevationArray):
		if not os.path.exists('elefile'):
	 		os.makedirs('elefile')
	 	with open('elefile/eleFile_'+str(state)+'_'+str(dist), 'a+') as fo:
	 		lstr = ''
	 		for ht in elevationArray:
	 			lstr += str(ht)
	 			lstr += ','
	 		fo.write('{},{},{},{},{}\n'.format(latlong_list[0], latlong_list[1], latlong_list[2], latlong_list[3], lstr))
	
	return elevationArray



def get_elevation_profile(latlongPair,state='Maharashtra',dist='Nandurbar'):
	'''
		RETURNS a list of two elements
		First element is status. 
			If status is true, Second element will return elevation profile.
	'''
	print "called at", time.time()
	if(os.path.exists('elefile/eleFile_'+str(state)+'_'+str(dist))):
		with open('elefile/eleFile_'+str(state)+'_'+str(dist), 'r+') as foo:
			lines = foo.readlines()

		for li in lines:
			if not li:
				#print "hi"
				continue
			tokens = li.split(',')
			if ((np.isclose(latlongPair[0],float(tokens[0]))) \
			and (np.isclose(latlongPair[1],float(tokens[1]))) \
			and (np.isclose(latlongPair[2],float(tokens[2]))) \
			and (np.isclose(latlongPair[3],float(tokens[3])))):
				elevationProfile = map(lambda x: int(x,10), tokens[4:-1])
				##print 'elevation was found in file'
				return elevationProfile
			elif ((np.isclose(latlongPair[0],float(tokens[2]))) \
			and (np.isclose(latlongPair[1],float(tokens[3]))) \
			and (np.isclose(latlongPair[2],float(tokens[0]))) \
			and (np.isclose(latlongPair[3],float(tokens[1])))):
				elevationProfile = map(lambda x: int(x,10), tokens[4:-1])
				elevationProfile=elevationProfile[::-1]
				##print 'elevation profile reversed'
				# #print "reverse",latlongPair, elevationProfile
				return elevationProfile
	latlong_query_str = '{},{} | {},{}'.format(latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3])
	##print 'elevation will be fetched now',latlongPair
	#return getElevation(latlong_query_str,[latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3]],state,dist)
	try:
		return getElevation(latlong_query_str,[latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3]],state,dist)
	except IOError, e:
		if e.errno == 101 or e.errno == 'socket error' or e.errno == -3 or e.errno == -2 or e.errno == 1:
			#print "Network Error"
			time.sleep(1)
					#return get_distance(orig_coord,dest_coord,state,dist) 
			return get_elevation_profile(latlongPair,state,dist)
			#return getElevation(latlong_query_str,[latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3]],state,dist)         
		else:
			raise             



def latlongdist(L1, L2):
	'''
	Returns distance(in meters) between L1 (lat, long) and L2 (lat, long)

	'''
	L1_rad = np.radians(np.array(L1))
	L2_rad = np.radians(np.array(L2))

	dlat = L1_rad[0]-L2_rad[0]
	dlon = L1_rad[1]-L2_rad[1]

	a = (np.sin(dlat/2.0)**2)+(np.cos(L1_rad[0])*np.cos(L2_rad[0])*np.sin(dlon/2.0)**2)
	c = 2*math.atan2(np.sqrt(a), np.sqrt(1-a))
	return c*6371000

def latlongdist_Lateral(L1, L2, ht_diff):
	'''
	Returns distance(in meters) between L1 (lat, long) and L2 (lat, long)

	'''
	L1_rad = np.radians(np.array(L1))
	L2_rad = np.radians(np.array(L2))

	dlat = L1_rad[0]-L2_rad[0]
	dlon = L1_rad[1]-L2_rad[1]

	a = (np.sin(dlat/2.0)**2)+(np.cos(L1_rad[0])*np.cos(L2_rad[0])*np.sin(dlon/2.0)**2)
	c = 2*math.atan2(np.sqrt(a), np.sqrt(1-a))
	c = c*6371000   ## Now the data is in meters
	r = math.sqrt(c**2 + ht_diff**2) 
	return r



def createFirstFresnel( posTX, posRX, htTX, htRX, lenEP, freq, NNN):
	'''
	Returns the fresnel zone
	'''
	x_t = posTX
	x_r = posRX
	h_t = htTX
	h_r = htRX
	##print 'Inside create Fresnel :posTX :', posTX, 'posRX : ', posRX
	##print('htTX :{},  htRX:{}, len:{}, freq:{}'.format(h_t, h_r, lenEP, freq)) ;
	c_x = (x_t + x_r)/2
	c_y = (h_t + h_r)/2
															## distance ?
	dist = math.sqrt((x_t - x_r)**2 + (h_t - h_r)**2)/1000
															## Transformed distance?
	ra = 0.6*8.657*math.sqrt(dist/freq)                     ## Units of frequency?
	
	ax = (dist/2)*1000
	ba = ra
	div = (h_r - h_t)/lenEP
	x = [i for i in range(lenEP)]
	y = [ htTX + div*i for i in range(lenEP)]
	
	delta_x = c_x 
	delta_y = c_y
	if(x_r - x_t) == 0:
		x_r=x_t+1
	theta = math.atan((h_r - h_t)/(x_r - x_t))
	rTheta = [[math.cos(theta), -math.sin(theta)],[math.sin(theta), math.cos(theta)]]
  
	
	fresnelZone = [[0 for i in xrange(lenEP)], [0 for i in xrange(lenEP)]]
	for i in xrange(lenEP):
		xx = i*NNN
		fresnelZone[0][i] = xx
		if ((xx - c_x)/ax)**2 < 1:
			fresnelZone[1][i]  = c_y - ba * math.sqrt( 1 - ((xx - c_x)/ax)**2 )
		else:
			fresnelZone[1][i]  = c_y - ba * math.sqrt( (((xx - c_x)/ax)**2) -1 )
	
	alias = np.array(fresnelZone)
   
	##print('Before subtraction: {} {}'.format(alias, type(delta_x)))
	alias[0,:] = alias[0,:]-delta_x
	alias[1,:] = alias[1,:]-delta_y
	
	##print('After subtraction: {}'.format(alias))
	
	
	
	alias = np.dot(rTheta, alias)
	
	alias[0,:] = alias[0,:]+delta_x
	alias[1,:] = alias[1,:]+delta_y
	
	
	##print  fresnelZone[1,:]
	#plt.plot(x,y, 'r')
	#plt.plot(alias[1,:], 'g')
	#plt.plot(alias, 'v')

	#plt.show()
	#plt.close()
	return alias[1,:]


def freePathLoss(dist, freq):
	'''
	Returns freePathLoss when given distance and frequency.
	'''
	#return ((4*math.pi*dist*freq)/299792458)**2
	a = 20*math.log10(dist/1000)
	b = 20*math.log10(freq)
	c = 92.45
	##print('dist:{}, freq:{}, PL:{}'.format(dist, freq, a+b+c))
	return a+b+c
	
def compareLL(l1, l2):
	'''
	Returns True if all elements of `list 1` are greater that `list 2`

	'''
	if not (len(l1) == len(l2)):
		#print 'Comparison of unequal lists not supported'
		return False
	
	res = [i>=j for (i,j) in zip(l1,l2)]
	##print res
	if not False in res:
		return True
	return False
	
def compareGLL(l1, l2):
	'''
	Returns True if all elements of `list 1` are greater that `list 2`

	'''
	if not (len(l1) == len(l2)):
		#print 'Comparison of unequal lists not supported'
		return False
	
	res = [i>j for (i,j) in zip(l1,l2)]
	##print res
	if not False in res:
		return True
	return False

def rf_get( pos=[[17, 23],[18, 22]],\
			htListT= [10,15,20,30,40],\
			htListR = [3,6,9,15] ,\
			reqThpt = 0
			):
	'''
		Returns 0 for diagonal elements and [[Throughputs(5.8,2.6,xx,xx)][TxHeight(5.8,2.6,xx,xx)][RxHeight(5.8,2.6,xx,xx)]] 

	'''
	txPower_5_8 = 11        #Transmitter power for 5.8
	if (pos[0][0]==pos[1][0]):
			if(pos[1][1]==pos[1][1]):
				return 0
	
	# ele = get_elevation_profile([pos[0][0],pos[0][1],pos[1][0],pos[1][1]],state,dist)
	latlong_query_str = '{},{} | {},{}'.format(pos[0][0],pos[0][1],pos[1][0],pos[1][1])
	#ele = getElevation(latlong_query_str,[pos[0][0],pos[0][1],pos[1][0],pos[1][1]])
	ele = get_elevation_profile([pos[0][0],pos[0][1],pos[1][0],pos[1][1]])
	lenEP = len(ele)
	##print lenEP
	dist = latlongdist(pos[0], pos[1])
	
	
	posTX = 0
	posRX = dist

	refLVL = min(ele)
	newEle = np.array(ele) - refLVL
	newEle = newEle.tolist()

	##-----------------------------
	elevationTX = newEle[0]
	elevationRX = newEle[-1]
	##print('Elevation TX:{}, Elevation RX:{}, posRX:{}'.format(elevationTX, elevationRX, posRX))
	delta = len(newEle)//3
	region1 = newEle[:delta]
	region2 = newEle[delta:2*delta]
	region3 = newEle[2*delta:]

	
	
	htTX0 =htListT[0] #max(region1)-elevationTX + MIN_ANT_HEIGHT 
	htRX0 =htListR[0] #max(region3)-elevationRX + MIN_ANT_HEIGHT
	htTX = htTX0
	htRX = htRX0
	##-----------------------------i802.11ac
	flag = False
	count = 0
	irx = 0
	itx = 0
	while True:
		fZ5_8 = createFirstFresnel(posTX , posRX ,htTX + elevationTX, htRX + elevationRX, lenEP, 5.8, dist/lenEP)
		
		if compareLL( fZ5_8, newEle):                                   ## IT appears that fZ5_8 and newEle are both array. 
																		## Comparing arrays in what sense ? Should all elements of {a} be > {b}
																		## 
			final_tx_ht_5_8 = htTX
			final_rx_ht_5_8 = htRX
			flag = True
			break
		else:
			if (irx == len(htListR)) and (itx == len(htListT)):
				##print 'Lets go out of loop.'
				break
			else:
				if count==0:                                            ## count is like a toggle variable
					
					##print 'increasing TX ht {5_8} from :', htTX,
					
					##print ' to :', htTX
					count =1
					if itx == len(htListT):
						#print 'saturated TX height'
						pass
					else:
						##print "itx" , itx, len(htListT)
						htTX = htListT[itx]
						itx += 1
						
				else:
					##print 'increasing RX ht {5_8} from :', htRX,
					htRX = htListR[irx]
					##print ' to :', htRX
					count =0
					if irx == len(htListR):
						#print 'saturated RX height'
						pass
					else:
						irx += 1
	
	
	
	ht_58 = htTX
	hr_58 = htRX
	maxTP5_8 = 0
	receivedSNR5_8 = -200
	receivedSNR2_6 = -200
	requiredSNR5_8 = -200
	if flag:    
		freq = 5.8
		distt = latlongdist_Lateral(pos[0], pos[1], abs(htTX - htRX))
		##print('distance : {}, Tx:{}, Rx:{}'.format(distt, pos[0], pos[1]))
		PL = freePathLoss(distt, 5.8)
		rsTable_5_8_Temp=[29.3, 58.5, 87.8, 117, 175.5, 234, 263.3, 292.5, 351, 390]
		rsTable_5_8_TP = [TPactual * i for i in rsTable_5_8_Temp]
		rsTable_5_8 = [[-96, -95, -92, -90, -86, -83 , -77, -74, -69, -65], rsTable_5_8_TP]#[[ -76, -78, -82], [ 54, 48, 36]]                 ## looks like some pre-calculated table ( RX sensitivity ?)
		# rsTable_5_8 = [[ -65, -69, -74, -77, -83, -86, -90, -92, -95, -96], [ 195, 175 , 146, 130, 117, 85, 59, 44, 27, 15]]
		# rsTable_5_8 = [[ -65, -69, -74, -77, -83, -86, -90, -92, -95, -96], [ 50, 45 , 40, 40, 30, 26, 24, 14, 10, 6]]                                                                ## Why 2 rows and 3 columns ??
		for i in xrange(len(rsTable_5_8[0])):
			RS_5_8 = rsTable_5_8[0][i]
			receivedSNR5_8 = txPower_5_8 + Gt_5_8 + Gr_5_8 - PL - NN_5_8
			requiredSNR5_8 = RS_5_8 - NN_5_8
			##print('rxSNR : {}, reqSNR : {}'.format(receivedSNR, requiredSNR))
			fadeMargin = receivedSNR5_8 - requiredSNR5_8
			#print('fademargin:{}, fadeMarginREQ:{}'.format(fadeMargin, FADE_MARGIN_REQ))
			receivedThpt = rsTable_5_8[1][i]
			if (fadeMargin > FADE_MARGIN_REQ) & (receivedThpt > reqThpt):
				maxTP5_8 = receivedThpt
				txPower_5_8 = (requiredSNR5_8 + FADE_MARGIN_REQ) - (Gt_5_8 + Gr_5_8 - PL - NN_5_8)
				break
	else:
		#print 'Ht is not able to clear the fresnel'
		maxTP5_8 =0
	
	
	##-----------------------------i 2.6 Ghz
	htTX0=htListT[0]
	htRX0=htListR[0]
	#hTX_base = htTX0
	#rTX_base = htRX0
	htTX = htTX0
	htRX = htRX0
	irx = 0
	itx = 0
	flag = False
	count = 0
	while True:
		fZ2_6 = createFirstFresnel(posTX, posRX, htTX + elevationTX, htRX + elevationRX, lenEP, 2.6, dist/lenEP)
		
		
		
		if compareLL( fZ2_6, newEle):                                   ## IT appears that fZ5_8 and newEle are both array. 
																		## Comparing arrays in what sense ? Should all elements of {a} be > {b}
																		## 
			final_tx_ht_2_6 = htTX
			final_rx_ht_2_6 = htRX
			flag = True
			break
		else:
			if (irx == len(htListR)) and (itx == len(htListT)):
				break
			else:
				if count==0:                                            ## count is like a toggle variable
					
					##print 'increasing TX ht {5_8} from :', htTX,
					
					##print ' to :', htTX
					count =1
					if itx == len(htListT):
						#print 'saturated TX height'
						pass
					else:
						htTX = htListT[itx]
						itx += 1
				else:
					##print 'increasing RX ht {5_8} from :', htRX,
					htRX = htListR[irx]
					##print ' to :', htRX
					count =0
					if irx == len(htListR):
						#print 'saturated RX height'
						pass
					else:
						irx += 1
	ht_26 = htTX
	hr_26 = htRX

	maxTP2_6 = 0
	if flag:    
		freq = 2.6
		distt = latlongdist_Lateral(pos[0], pos[1], abs(htTX - htRX))
		##print('distance : {}, Tx:{}, Rx:{}'.format(distt, pos[0], pos[1]))
		PL = freePathLoss(distt, 2.6)
		##print('free space path loss :{}'.format(PL))
		rsTable_2_6 = [[ -76, -78, -82], [ 54, 48, 36]]                               ## looks like some pre-calculated table ( RX sensitivity ?)
																		## Why 2 rows and 3 columns ??
		for i in xrange(len(rsTable_2_6[0])):
			
			RS_2_6 = rsTable_2_6[0][i]
			receivedSNR2_6 = txPower_2_6 + Gt_2_6 + Gr_2_6 - PL - NN_2_6
			requiredSNR = RS_2_6 - NN_2_6
			fadeMargin = receivedSNR2_6 - requiredSNR
			if fadeMargin > FADE_MARGIN_REQ:
				maxTP2_6 = rsTable_2_6[1][i] 
				#print maxTP2_6
				break
			else:
				print maxTP2_6, "right"
	else:
		# #print "This is not funny"
		# #print 'Ht is not able to clear the fresnel'
		maxTP2_6 = 0
	 
	return [[maxTP5_8, txPower_5_8, receivedSNR5_8, requiredSNR5_8],[ht_58, ht_26, 0, 0],[hr_58, hr_26, 0, 0]]
	
#if __name__ == '__main__':
	##print compareLL([3, 5, 7],[3, 2, 2])
#    #print latlongdist( [19.79842,72.79062], [19.78125,72.7959])
#    #print latlongdist_Lateral( [19.79842,72.79062], [19.78125,72.7959], 0)

def SINR(Sig, Intf):
	Sig = pow(10, float(Sig/10))
	IntfNN = pow(10, float(Intf/10)) + pow(10,float(NN_5_8/10))
	SINR = float(Sig/IntfNN)
	SINR =  10*np.log10(SINR)
	return SINR
	
def addIntf( Intf1, Intf2):
	Intf1 = pow(10, float(Intf1/10))
	Intf2 = pow(10, float(Intf2/10))
	Intf = float(Intf1+Intf2)
	Intf =  10*np.log10(Intf)
	return Intf
	
def subIntf( Intf1, Intf2):
	Intf1 = pow(10, float(Intf1/10))
	Intf2 = pow(10, float(Intf2/10))
	Intf = float(Intf1-Intf2)
	if Intf == 0 :
		Intf = -200
	else :
		Intf =  10*np.log10(Intf)
	return Intf


#if __name__ == '__main__':
	#with open('000.csv','r+') as f:
		#title = f.readline()
		#lines = f.readlines()
	
	#data_mat = [] 
	#i=0
	#error_count = 0 
	#for line in lines:
		###print 'line', line
		#res =  []
		#row = line.split(',')
		#for e in row:
			#res.append(float(e))

		#data_mat.append(res)
		#i = i+1
		
		
	#data_mat = np.array(data_mat)
	
	#i=1 
	#for dat in data_mat:
		#print('case:{}'.format(i))
		#ress = rf_get([[dat[0],dat[1]], [dat[2], dat[3]]],[400, 400],dat[4:])
		#print ress
		#i+=1
		#plt.plot([-2,len(dat[4:])+2],[0,0],'k',linewidth=0.5)
		#plt.plot(dat[4:], 'r-')
		#plt.plot([0,0],[0,dat[4]+ress[1][0]])
		#plt.plot([len(dat[4:]),len(dat[4:])],[0,dat[-1]+ress[2][0]])
		#plt.show()
		#plt.close()

def calcSINR(dictVilToGPAll,dictVilCon,listGPCon,thisVilID,thisGPID): #Pass list of already connected Villages and this GP as signaler
	#print "\n"
	listGPCon = copy(listGPCon)
	listGPCon.append(thisGPID)
	dictVilCon = dictVilCon.copy()
	dictVilCon[thisVilID] = thisGPID
	#print "listGPCon", listGPCon
	totalSINR = 0
	minVilSINR = 200
	maxVilSINR = -200
	listVilSINR = []
	keysVilCon = list(dictVilCon.keys())
	for thisVilID in keysVilCon:
		thisVilSig = -200
		thisVilIntf = -200
		thisVilGPConID = dictVilCon[thisVilID]
		#print "thisVilGPConID", thisVilGPConID
		keysVilGP = list(dictVilToGPAll[thisVilID][2].keys())
		for thisVilGPID in keysVilGP:
			#print "		thisVilGPID ", thisVilGPID 
			if thisVilGPID == thisVilGPConID:
				thisVilSig = dictVilToGPAll[thisVilID][2][thisVilGPID][0]	
				#print "Sig from ", thisVilGPID, "is ", thisVilSig
			elif thisVilGPID in listGPCon:
				thisVilIntf = addIntf(thisVilIntf,dictVilToGPAll[thisVilID][2][thisVilGPID][0])
		thisVilSINR = SINR(thisVilSig,thisVilIntf)
		totalSINR += SINR(thisVilSig,thisVilIntf)
		listVilSINR.append(thisVilSINR)
		
	#print "\n"	
	return listVilSINR
	
def reducThptBy(maxSINRGPID,thisVilReqThpt,dictGPThpt):
	dictGPThpt[maxSINRGPID] -= thisVilReqThpt
	return dictGPThpt

def isSuffThpt(dictGPThpt,thisGPID,thisVilReqThpt):
	if (thisGPID not in dictGPThpt.keys()) :
		return (thisVilReqThpt <= GPThptVal)
	return (dictGPThpt[thisGPID] >= thisVilReqThpt)

def swapRandomTwo(keysVilAll):
	keysVilAll_ = copy(keysVilAll)
	i = random.randint(0,len(keysVilAll)-1)
	j = random.randint(0,len(keysVilAll)-1)
	keysVilAll_[i],keysVilAll_[j] = keysVilAll[j],keysVilAll[i]
	
	return keysVilAll_
	
def calcNextVilList(V_n,dictGPSetTxPow,n,dictVilToGPAll,valLinkOnListVilSINR,listGPCon,vallistGPCon,valdictVilCon,dictGPTxPow):
    #V_n_ = swapRandomTwo(V_n)
    V_n_ = copy(V_n)
    dictGPSetTxPow_ = generate_GPPower(listGPCon,dictGPTxPow)
    
    [Rew_V_n_,valdictVilCon_,_] = rewardSINR(V_n_,dictGPSetTxPow_,dictVilToGPAll)
    [Rew_V_n,valdictVilCon,_] = rewardSINR(V_n,dictGPSetTxPow,dictVilToGPAll)
    Beta = math.log(1+n)
    #Beta = math.log(1+float(n/100))    
    #Beta = 1 - float(1/(1+n))
    print "Rew_V_n_",Rew_V_n_,"Rew_V_n",Rew_V_n
    if(Rew_V_n_ >= Rew_V_n):
        return [V_n_,valdictVilCon_]
    else:
        p = math.exp(Beta*(Rew_V_n_ - Rew_V_n))
        #print p
        if random.random() < p:
            return [V_n_,valdictVilCon_]
        else:
            return [V_n,valdictVilCon]
	
def rewardSINR(V_n,dictGPSetTxPow,dictVilToGPAll):
    keysVilAll = V_n
    listGPCon = []
    dictVilCon = {}
    dictGPThpt = {}
    dictGPTxPower = {}
    valdictGPThpt = {}
    maxLinkOnListVilSINR = []

    for keyVil in keysVilAll:
        thisVil = dictVilToGPAll[keyVil]
        maxLinkOnListVilSINR = []
        thisVilID = keyVil
        thisVilReqThpt = thisVil[1]
		#thisVilNoise = thisVil[2]
		#if(len(listSINR)==0):
		    #print thisVilID
		#totalSINR = []
		#totalSpec = []
        maxSigGPID = -1
        maxLinkSig = -200
        GPList = thisVil[2]
        keysGPAll = list(GPList.keys())
        for keyGP in keysGPAll :
            thisGPID = keyGP
            if thisGPID not in dictGPSetTxPow.keys():
                continue
            maxLinkOnListVilSINR = []
            thisLinkSig = calcGPSig(thisGPID,thisVilID,dictGPSetTxPow,dictVilToGPAll)
            thisLinkOnListVilSINR = calcSINR(dictVilToGPAll,dictVilCon,listGPCon,thisVilID,thisGPID) 
            minVilSINR = min(thisLinkOnListVilSINR)
            if (thisLinkSig > maxLinkSig) and isSuffThpt(dictGPThpt,thisGPID,thisVilReqThpt) and (minVilSINR > 20):
                maxLinkSig = thisLinkSig
                maxSigGPID = thisGPID
                dictVilCon[thisVilID] = maxSigGPID
		if (maxSigGPID not in listGPCon) and (maxSigGPID != -1):
                    listGPCon.append(maxSigGPID)
                    dictGPThpt[maxSigGPID] = 100
		if maxSigGPID != -1:
                    dictGPThpt = reducThptBy(maxSigGPID,thisVilReqThpt,dictGPThpt)
                    if(dictGPThpt[maxSigGPID] < 0):
                        print maxSigGPID,thisVilReqThpt,dictGPThpt
                        print "Error"
                        sys.exit()
                        
    return [len(dictVilCon),dictVilCon,dictGPThpt]

def generate_GPPower(listGPCon,dictGPTxPow):
    dictGPSetTxPow = {}
    for thisGPID in listGPCon:
        dictGPTxPow[thisGPID].append(0)
        dictGPSetTxPow[thisGPID] = random.choice(dictGPTxPow[thisGPID])
        if(dictGPSetTxPow[thisGPID] == 0):
            del dictGPSetTxPow[thisGPID]
    return dictGPSetTxPow
    
def calcGPSig(thisGPID,thisVilID,dictGPSetTxPow,dictVilToGPAll):
    #print dictGPSetTxPow,thisGPID
    SigDiff = dictVilToGPAll[thisVilID][2][thisGPID][1] - dictGPSetTxPow[thisGPID]
    #print SigDiff
    thisGPSig = dictVilToGPAll[thisVilID][2][thisGPID][0] - SigDiff
    #thisGPSig = dictVilToGPAll[thisVilID][2][thisGPID][0]
    return thisGPSig