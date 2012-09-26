#!/bin/env python
# -*- coding: utf-8 -*-
'''
Created on -, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
from geoUtils import clean_line, getGeoDataFromConvertedFile


def updateUsrPlacesDiz( UsrPlaces, inputFile, totLines ):
	''' Given the dictionary and the input file
		update the usersCommonestPlaces
	'''
	print >> sys.stderr, "*> Computing Users Commonest Places",
	lines = 0
	# imgId <tab> title <tab> url <tab> tags <tab> coordinates <tab> hometown_coordinates
	for line in inputFile:
		lines += 1
		blk = line.strip().split( "\t" )
		usrId = blk[5].split("|")[0]
		# usrId = clean_line( usrId )
		lat, lon, acc = getGeoDataFromConvertedFile( blk[4] )
		if not UsrPlaces.has_key(usrId):
			UsrPlaces[usrId] = []
		found = False
		for i in range(0,len(UsrPlaces[usrId])):
			coordFreq = UsrPlaces[usrId][i]
			# print >> sys.stderr, "\n", coordFreq
			cLat = coordFreq[0]
			cLon = coordFreq[1]
			cAcc = coordFreq[2]
			if lat == cLat and lon == cLon:
				cAcc = max(cAcc, acc)
				freq = coordFreq[3] + 1
				UsrPlaces[usrId][i] = [cLat, cLon, cAcc, freq]
				found = True
		if not found:
			UsrPlaces[usrId].append( [lat, lon, acc, 1] )
		# print info
		if lines % 1000:
			print >> sys.stderr, "\r*> Computing Users Commonest Places [%2.2f%s]" % ( float(lines)/totLines*100, '%'),
	print >> sys.stderr, "\r*> Computing Users Commonest Places: %d lines [%2.2f%s]" % (lines, float(lines)/totLines*100, '%')
			
def serializeUsrPlacesDiz( UsrPlaces ):
	''' Serialize the given dictionary to standard output
	'''
	print >> sys.stderr, "*> Serialize Users Commonest Places",
	users = 0
	totLines = float(len(UsrPlaces))
	for uId in UsrPlaces:
		output = ""
		output = uId +"\t"
		for coordFreq in UsrPlaces[uId]:
			lat = str( coordFreq[0] )
			lon = str( coordFreq[1] )
			acc = str( coordFreq[2] )
			freq = str( coordFreq[3] )
			output += lat +","+ lon +","+ acc +","+ freq +"|"
		output = output[:-1]
		print >> sys.stdout, output
		users += 1
		# print info
		if users % 1000:
			print >> sys.stderr, "\r*> Serialize Users Commonest Places [%2.2f%s]" % ( users/totLines*100, '%'),
	print >> sys.stderr, "\r*> Serialize Users Commonest Places: %d users [%2.2f%s]" % (users, users/totLines*100, '%')





#-----------------------------------------
def print_help():
	"""	Print information in case of wrong input """
	#~ if the input parameters are not correct
	print >> sys.stderr, "\t Usage: python "+sys.argv[0]+" <train_set.txt>  >  <users_commonest_places.txt>"
	print >> sys.stderr, "\t e.g. python computeUsersCommonestPlace.py dataset/flickrVideosTrain_ok.txt dataset/flickrVideosTest_ok.txt > extra/usersCommonestPlaces.txt "
	sys.exit(1)	
#-----------------------------------------
""" Checking the arguments in input """
if len(sys.argv) < 2:
	print_help()
else:
	trainFilePath = sys.argv[1]
#-----------------------------------------


UsrPlaces = {} # usrId -> [ [lat1,lon1,acc1,freq1], [lat2,lon2,acc2,freq2], ... ]

# Parsing train set
trainFile = file( trainFilePath, 'r' )
print >> sys.stderr, "Parsing Train Set"
updateUsrPlacesDiz( UsrPlaces, trainFile, 3195410 )
trainFile.close()

# Write output
print >> sys.stderr, "Serialize Dictionary"
serializeUsrPlacesDiz( UsrPlaces )