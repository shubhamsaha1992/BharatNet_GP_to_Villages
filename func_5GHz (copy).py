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
from copy import copy,deepcopy
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





def getElevation(path, latlong_list, dist_filename, state="Maharashtra", dist="Nandurbar", samples="512",sensor="false", **elvtn_args):
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
	 	with open('elefile/eleFile_'+dist_filename, 'a+') as fo:
	 		lstr = ''
	 		for ht in elevationArray:
	 			lstr += str(ht)
	 			lstr += ','
	 		fo.write('{},{},{},{},{}\n'.format(latlong_list[0], latlong_list[1], latlong_list[2], latlong_list[3], lstr))
	
	return elevationArray



def get_elevation_profile(latlongPair,dist_filename,state='Maharashtra',dist='Nandurbar'):
    print "called at", time.time()
    print latlongPair
    if(os.path.exists('elefile/eleFile_'+dist_filename)):
        with open('elefile/eleFile_'+dist_filename, 'r+') as foo:
            lines = foo.readlines()
            for li in lines:
                if not li:
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
                    return elevationProfile
    latlong_query_str = '{},{} | {},{}'.format(latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3])
    try:
        return getElevation(latlong_query_str,[latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3]],dist_filename,state,dist)
    except IOError, e:
        if e.errno == 101 or e.errno == 'socket error' or e.errno == -3 or e.errno == -2 or e.errno == 1:
            time.sleep(1)
            return get_elevation_profile(latlongPair,state,dist,dist_filename)
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

def rf_get(base_filename, pos=[[17, 23],[18, 22]],\
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
	ele = get_elevation_profile([pos[0][0],pos[0][1],pos[1][0],pos[1][1]],base_filename)
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
		rsTable_5_8_TP = [0.4 * TPactual * i for i in rsTable_5_8_Temp]
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

def calcSINR(dictVilToGPAll,thisVilID,dictGPSetTxPow):
    thisVilSig = -200
    maxGPSig = -200
    maxSigGPID = -1
    thisVilIntf = -200
    keysVilAll = list(dictVilToGPAll.keys())
    thisVil = dictVilToGPAll[thisVilID]
    GPList = thisVil[2]
    keysGPAll = list(GPList.keys())
    for keyGP in keysGPAll :
        thisGPID = keyGP
        if thisGPID not in dictGPSetTxPow.keys():
            continue
        thisGPSig = calcGPSig(thisGPID,thisVilID,dictGPSetTxPow,dictVilToGPAll)
        if(thisGPSig > maxGPSig):
            maxGPSig = thisGPSig
            maxSigGPID = thisGPID
        thisVilIntf = addIntf(thisVilIntf,thisGPSig)
    thisVilIntf = subIntf(thisVilIntf,maxGPSig)
    thisVilSINR = SINR(maxGPSig,thisVilIntf)
    return [thisVilSINR,maxSigGPID]
	
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
	
def localOpt(dictGPSetTxPow,dictGPTxPow,dictVilToGPAll):
    dictVilToGPAll_= deepcopy(dictVilToGPAll)
    dictGPSetTxPow_ = deepcopy(dictGPSetTxPow)
    dictGPTxPow_ = deepcopy(dictGPTxPow)
    #keysGPPowList = dictGPSetTxPow_.keys()
    keysGPPowList = dictGPTxPow_.keys()
    maxdictGPSetTxPow = deepcopy(dictGPSetTxPow)
    [maxRew,maxdictVilCon,_] = rewardSINR(maxdictGPSetTxPow,dictVilToGPAll)
    for keyGP in keysGPPowList:
        givenPowList = dictGPTxPow_[keyGP]
        givenPowList.sort()        
        
        print "Opt over all pre calc values"
        minPow = min(givenPowList)
        maxPow = max(givenPowList)
        print minPow, maxPow
        
        if keyGP in dictGPSetTxPow.keys():
            prevPow = dictGPSetTxPow_[keyGP]
            
            
            ##print "GP already lit"
            ##print "Opt over incrementally decr values"
            
            
            for setPow_ in np.arange(prevPow,minPow,-1):
                dictGPSetTxPow__ = deepcopy(dictGPSetTxPow_)
                dictGPSetTxPow__[keyGP] = setPow_
                [Rew_,_,_] = rewardSINR(dictGPSetTxPow__,dictVilToGPAll)
                print "Rew_",Rew_,"maxRew",maxRew
                if(Rew_ > maxRew):
                    maxRew = Rew_
                    maxdictGPSetTxPow = deepcopy(dictGPSetTxPow__)
                    print "maxdictGPSetTxPow changing"
            #print "dictGPSetTxPow_ setting to maxdictGPSetTxPow"
            dictGPSetTxPow_ =  maxdictGPSetTxPow
            [Rew_,_,_] = rewardSINR(maxdictGPSetTxPow,dictVilToGPAll_)
            print "Rew_",Rew_
            
            
            
            ##print "Opt over incrementally incr values"
            
            
            for setPow_ in np.arange(prevPow,maxPow,1):
                dictGPSetTxPow__ = deepcopy(dictGPSetTxPow_)
                dictGPSetTxPow__[keyGP] = setPow_
                [Rew_,_,_] = rewardSINR(dictGPSetTxPow__,dictVilToGPAll)
                print "Rew_",Rew_,"maxRew",maxRew
                if(Rew_ > maxRew):
                    maxRew = Rew_
                    maxdictGPSetTxPow = deepcopy(dictGPSetTxPow__)
                    print "maxdictGPSetTxPow changing"
            #print "dictGPSetTxPow_ setting to maxdictGPSetTxPow"
            dictGPSetTxPow_ =  maxdictGPSetTxPow
            [Rew_,_,_] = rewardSINR(maxdictGPSetTxPow,dictVilToGPAll_)
            print "Rew_",Rew_
            
        else:
            
            
            ##print "Lighting GP now"
            
            
            for setPow_ in np.arange(minPow,maxPow,1):
                dictGPSetTxPow__ = deepcopy(dictGPSetTxPow_)
                dictGPSetTxPow__[keyGP] = setPow_
                [Rew_,_,_] = rewardSINR(dictGPSetTxPow__,dictVilToGPAll)
                print "Rew_",Rew_,"maxRew",maxRew
                if(Rew_ > maxRew):
                    maxRew = Rew_
                    maxdictGPSetTxPow = deepcopy(dictGPSetTxPow__)
                    print "maxdictGPSetTxPow changing"
            #print "dictGPSetTxPow_ setting to maxdictGPSetTxPow"
            dictGPSetTxPow_ =  maxdictGPSetTxPow
            [Rew_,_,_] = rewardSINR(maxdictGPSetTxPow,dictVilToGPAll_)
            print "Rew_",Rew_
            

#        setPow = dictGPSetTxPow[keyGP]
#        if setPow is not 0 :
#            setPowIndex = givenPowList.index(setPow)
#        if setPowIndex > 0 :
#            print "Opt over incrementally decr values"
#            beginPow = givenPowList[setPowIndex-1]
#            #for setPow_ in np.arange(beginPow,setPow,1) :
#            for setPow_ in np.arange(beginPow,setPow,1):
#                dictGPSetTxPow_[keyGP] = setPow_
#                [Rew_,valdictVilCon_,_] = rewardSINR(dictGPSetTxPow_,dictVilToGPAll)
#                print "Rew_",Rew_,"maxRew",maxRew
#                if(Rew_ > maxRew):
#                    maxRew = Rew_
#                    maxdictGPSetTxPow = dictGPSetTxPow_
#                    maxdictVilCon = valdictVilCon_
#            dictGPSetTxPow_ =  maxdictGPSetTxPow                               
#                    
#        if setPowIndex < (len(givenPowList)-1):
#            print "Opt over incrementally incr values"
#            endPow = givenPowList[setPowIndex+1]
#            for setPow_ in np.arange(setPow,endPow,1) :
#                dictGPSetTxPow_[keyGP] = setPow_
#                [Rew_,valdictVilCon_,_] = rewardSINR(dictGPSetTxPow_,dictVilToGPAll)
#                print "Rew_",Rew_,"maxRew",maxRew
#                if(Rew_ > maxRew):
#                    maxRew = Rew_
#                    maxdictGPSetTxPow = dictGPSetTxPow_
#                    maxdictVilCon = valdictVilCon_
#            dictGPSetTxPow_ =  maxdictGPSetTxPow

  
            
    print("returned")
    return [maxdictGPSetTxPow,maxdictVilCon]
    
    

def calcNextVilList(dictGPSetTxPow,n,dictVilToGPAll,dictGPTxPow):
#    print dictGPSetTxPow

    dictGPSetTxPow_ = recomb_GPPower(dictGPSetTxPow,dictGPTxPow)
#    print"\n"
#    print dictGPSetTxPow
#    print"\n"
#    print dictGPSetTxPow_
    
    [Rew_,valdictVilCon_,_] = rewardSINR(dictGPSetTxPow_,dictVilToGPAll)
    [Rew,valdictVilCon,_] = rewardSINR(dictGPSetTxPow,dictVilToGPAll)
    Beta = math.log(1+n)
    #Beta = math.log(1+float(n/100))    
    #Beta = 1 - float(1/(1+n))
    print n,"Rew_",Rew_,"Rew",Rew
    if(Rew_ >= Rew):
        return [dictGPSetTxPow_,valdictVilCon_]
    else:
        p = math.exp(Beta*(Rew_ - Rew))
        #print p
        if random.random() < p:
            return [dictGPSetTxPow_,valdictVilCon_]
        else:
            return [dictGPSetTxPow,valdictVilCon]
	
def rewardSINR(dictGPSetTxPow,dictVilToGPAll):
    listGPCon = []
    dictVilCon = {}
    dictGPThpt = {}
    dictVilToGPAll = copy(dictVilToGPAll)
    dictGPSetTxPow = deepcopy(dictGPSetTxPow)
    keysVilAll = list(dictVilToGPAll.keys())
    

    for keyVil in keysVilAll:
        thisVil = dictVilToGPAll[keyVil]
        thisVilID = keyVil
        thisVilReqThpt = thisVil[1]
		#thisVilNoise = thisVil[2]
		#if(len(listSINR)==0):
		    #print thisVilID
		#totalSINR = []
		#totalSpec = []
        maxSINRGPID = -1
        maxLinkSINR = -200
        GPList = thisVil[2]
        keysGPAll = list(GPList.keys())
#        for keyGP in keysGPAll :
#            thisGPID = keyGP
#            if thisGPID not in dictGPSetTxPow.keys():
#                continue
        [thisVilSINR,maxSigGPID] = calcSINR(dictVilToGPAll,thisVilID,dictGPSetTxPow) 
        if (thisVilSINR > 20):
            maxSINRGPID = maxSigGPID
            if maxSINRGPID not in listGPCon:
                dictGPThpt[maxSINRGPID] = 100
                listGPCon.append(maxSINRGPID)
            
        if maxSINRGPID != -1 and isSuffThpt(dictGPThpt,maxSINRGPID,thisVilReqThpt):
            dictVilCon[thisVilID] = maxSINRGPID
            dictGPThpt = reducThptBy(maxSINRGPID,thisVilReqThpt,dictGPThpt)
    
    return [len(dictVilCon),dictVilCon,dictGPThpt]

def generate_GPPower(dictGPTxPow):
    dictGPSetTxPow = {}
    for thisGPID in list(dictGPTxPow.keys()):
        if(0 not in dictGPTxPow[thisGPID]):
            dictGPTxPow[thisGPID].append(0)
        dictGPSetTxPow[thisGPID] = random.choice(dictGPTxPow[thisGPID])
        if(dictGPSetTxPow[thisGPID] == 0):
            del dictGPSetTxPow[thisGPID]
    return dictGPSetTxPow
    
def recomb_GPPower(dictGPSetTxPow,dictGPTxPow):
    dictGPSetTxPow = copy(dictGPSetTxPow)
    thisGPID = random.choice(dictGPTxPow.keys())
    dictGPSetTxPow[thisGPID] = random.choice(dictGPTxPow[thisGPID])
    #print thisGPID,dictGPSetTxPow[thisGPID]
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