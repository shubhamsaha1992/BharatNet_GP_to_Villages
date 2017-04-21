from scipy.signal import argrelextrema
import csv
import decimal
import numpy as np
import math
import os
from goapi import sign_url
from geopy.distance import vincenty
# import simplejson
try:
    import simplejson
except:
    import json as simplejson
import urllib

ELEVATION_BASE_URL = 'https://maps.google.com/maps/api/elevation/json'


def getElevation(path,latlong_list,state,dist,samples="512",sensor="false", **elvtn_args):
	'''
		path contains a '|' seperated lat long eg
			lat0, long0 | lat1, long1
	'''
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
	#print signedurl,"signed url"	
	# print (response)


	# Create a dictionary for each results[] object
	elevationArray = []

	for resultset in response['results']:
		elevationArray.append(int(resultset['elevation']))
		# print (elevationArray)
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

def get_elevation_profile(latlongPair,state,dist):
	'''
		RETURNS a list of two elements
		First element is status. 
			If status is true, Second element will return elevation profile.
	'''
	if(os.path.exists('elefile/eleFile_'+str(state)+'_'+str(dist))):
		with open('elefile/eleFile_'+str(state)+'_'+str(dist), 'r+') as foo:
			lines = foo.readlines()

		for li in lines:
			if not li:
				print "hi"
				continue
			tokens = li.split(',')
			if ((latlongPair[0] == float(tokens[0])) \
			and (latlongPair[1] == float(tokens[1])) \
			and (latlongPair[2] == float(tokens[2])) \
			and (latlongPair[3] == float(tokens[3]))):
				elevationProfile = map(lambda x: int(x,10), tokens[4:-1])
				#print 'elevation was found in file'
				return elevationProfile
			elif ((latlongPair[0] == float(tokens[2])) \
			and (latlongPair[1] == float(tokens[3])) \
			and (latlongPair[2] == float(tokens[0])) \
			and (latlongPair[3] == float(tokens[1]))):
				elevationProfile = map(lambda x: int(x,10), tokens[4:-1])
				elevationProfile=elevationProfile[::-1]
				print 'elevation profile reversed'
				# print "reverse",latlongPair, elevationProfile
				return elevationProfile
	print latlongPair
	latlong_query_str = '{},{} | {},{}'.format(latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3])
	print 'elevation will be fetched now',latlongPair
	#return getElevation(latlong_query_str,[latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3]],state,dist)
	try:
		return getElevation(latlong_query_str,[latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3]],state,dist)
	except IOError, e:
		if e.errno == 101 or e.errno == 'socket error' or e.errno == -3 or e.errno == -2 or e.errno == 1:
			print "Network Error"
			time.sleep(1)
					#return get_distance(orig_coord,dest_coord,state,dist) 
			return get_elevation_profile(latlongPair,state,dist)
			#return getElevation(latlong_query_str,[latlongPair[0], latlongPair[1], latlongPair[2], latlongPair[3]],state,dist)         
		else:
			raise             

def diff_variable(begin,end,index,f,distance,elevation):
	d1 = (distance[index] - distance[begin])/1000
	d2 = (distance[end] - distance[index])/1000
	h = elevation[index] - (elevation[begin] + (elevation[end] - elevation[begin])*(d1/(d1+d2)))
	r = 548 * math.sqrt(d1*d2/(f*(d1+d2)))
	#print(begin,index,end)
	var = h/r
	return var
	
def diff_loss(var):
	if(var < 0): return 0
	a_m = 16 + 20*math.log10(var)
	if(a_m < 0): return 0
	return a_m

def calc_loss(begin,end,f,distance,elevation):
	#print(begin,end)
	radius = 50
	elevation = np.array(elevation)
	elev = elevation[begin:end]
	#dist = distance[begin:end]
	knifeedgeindex = argrelextrema(elev, np.greater, order = radius)
	knifeedgeindex = knifeedgeindex[0] + begin
	if(len(knifeedgeindex) == 0):
		return 0
	maxindex = knifeedgeindex[0]
	for index in knifeedgeindex:
		if diff_variable(begin,end,index,f,distance,elevation) > diff_variable(begin,end,maxindex,f,distance,elevation):
			maxindex = index
			
	diff_var = diff_variable(begin,end,maxindex,f,distance,elevation)
	total_loss = diff_loss(diff_var) + calc_loss(begin,maxindex,f,distance,elevation) + calc_loss(maxindex,end,f,distance,elevation)
	return total_loss


def path_loss(L1,L2,f,ht,hr):
	latlongPair = L1 + L2
	Dist = vincenty(L1, L2).km * 1000
	#print(Dist)	
	samples = 512
	distance = np.arange(0,Dist,float(Dist)/samples)
	elevation = get_elevation_profile(latlongPair,'Maharashtra','Nandurbar')
	#print distance
	#print elevation
	elevation[0] = elevation[0] + ht
	elevation[-1] = elevation[-1] + hr
	N = len(distance) -1
	diff_loss = calc_loss(0,N,f,distance,elevation)
	return diff_loss
	

#print path_loss([19.7002778,72.8560556],[19.7311205,72.8567291],510,0,0)

