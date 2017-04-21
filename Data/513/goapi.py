import hashlib
import hmac
import base64
import urlparse
try:
	import simplejson
except:
	import json as simplejson
import sys
import urllib
import os
import time
# from maps_blk import road_dist_block,update_road_dist
# from pse_2 import latlongdist


def sign_url(input_url=None, secret=None):

	if not input_url or not secret:
		raise Exception("Both input_url and secret are required")

	url = urlparse.urlparse(input_url)

	url_to_sign = url.path + "?" + url.query

	decoded_key = base64.urlsafe_b64decode(secret)

	signature = hmac.new(decoded_key, url_to_sign, hashlib.sha1)

	encoded_signature = base64.urlsafe_b64encode(signature.digest())

	original_url = url.scheme + "://" + url.netloc + url.path + "?" + url.query

	return original_url + "&signature=" + encoded_signature

if __name__ == "__main__":
	input_url = "https://maps.googleapis.com/maps/api/directions/json?client=gme-leptonsoftwareexport4"
	secret = 'xghu9DIoNr63z8_al_oJCSPWQh0='
	print input_url,"input url        ", secret
	print "Signed URL: " + sign_url(input_url, secret)


	# DIRECTIONS_BASE_URL='https://maps.googleapis.com/maps/api/directions/json'
	# units = 'Imperial'
	# travel= 'driving'
	# origin = + "," +
	# dest = + "," +
	# params = {'origin':origin,'destination':dest,'travel_mode':travel,'units': units }

	# url = DIRECTIONS_BASE_URL + '?' + urllib.urlencode(params)
	# print url
	# f= simplejson.load(urllib.urlopen(url)) #