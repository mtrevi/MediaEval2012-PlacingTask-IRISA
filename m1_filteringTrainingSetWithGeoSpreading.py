#!/bin/env python
# -*- coding: utf-8 -*-
'''
Created on -, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
import time
from geoUtils import haversine, clean_line, loadGroupOfTagsFromConvertedFile, serializeTrainSetDB


def geographicSpread( TrainTagCoord, TrainTagIndex, minMatches=100, maxAvg=100.0 ):
	''' Given the Trainset filter out the tags with lower geographic spread 
	'''
	print >> sys.stderr, "*> [PreparingTrainTagDB]",
	t1 = time.time()
	newTrainCoord = {}
	newTrainIndex = {}
	termGeoSpread = {} # term -> [#got, [coord1, coord2, .. ]]
	lines = 0
	# e.g 	key: "merel jong seriemerel nest" 
	#		value: "[((52.346561, 6.671104, -1), 3)]"
	for termKey in TrainTagIndex:
		lines += 1
		# size of matches
		matches = len(TrainTagIndex[termKey])
		# compute list of coordinates
		geoList = []
		for got in TrainTagIndex[termKey]:
			for coordFreq in TrainTagCoord[got]:
				freq = int(coordFreq[1])
				for i in range(0,freq):
					geoList.append( coordFreq[0] )
		# compute avg distance for all the coordinates
		totDist = 0.0
		cnt = 0
		for i in range(0,len(geoList)-1):
			coord1 = geoList[i]
			coord2 = geoList[i+1]
			totDist += haversine( coord1, coord2 )
			cnt += 1
		rank = 0.0
		avgDist = cnt
		if cnt > 0:
			avgDist = float(totDist) / cnt
			if avgDist > 0:
				rank = matches/avgDist
		# # create new dictionaries
		# if avgDist < maxAvg and matches > minMatches:
		# 	print >> sys.stdout, termKey.encode('utf-8', 'ignore') +"\t"+ str(matches) +"\t"+ str(avgDist) +"\t"+ str(rank)
		# 	newTrainIndex[termKey] = TrainTagIndex[termKey]
		# 	for got in newTrainIndex[termKey]:
		# 		newTrainCoord[got] = TrainTagCoord[got]
		# save tags with GOOD geo spread
		if avgDist < maxAvg and matches > minMatches:
			if termGeoSpread.has_key( termKey ):
				termGeoSpread[ termKey ] += 1
			else:
				termGeoSpread[ termKey ] = 0
		# print info
		if (lines % 100) == 0:
			print >> sys.stderr, "\r*> [PreparingTrainTagDB] %d lines [%2.2f%s parsed]" % ( lines, (float(lines)/len(TrainTagIndex)*100), '%' ),
	# create new dictionaries keeping only the tags with GOOD geo spread
	for termKey in termGeoSpread:
		print >> sys.stdout, termKey.encode('utf-8', 'ignore') +"\t"+ str(matches) +"\t"+ str(avgDist) +"\t"+ str(rank)
		# check all the current group of tags where the termKey is presents
		for got in TrainTagIndex[termKey]:
			newGot = ""
			tags = got.split(" ")
			# split the tags of the group of tags
			for tag in tags:
				# preserve just the tags that are present in the termGeoSpread dictionary
				if termGeoSpread.has_key( tag ):
					newGot += tag +" "
			# write the new Group of Tags
			newGot = newGot[:-1]
			# create the new index and db with the new group of tags
			if len(newGot) > 2:
				if not newTrainIndex.has_key( termKey ):
					newTrainIndex[ termKey ] = []
				if newGot not in newTrainIndex[termKey]:
					newTrainIndex[termKey].append( newGot )
					newTrainCoord[newGot] = TrainTagCoord[got]
	# final info
	t2 = time.time()
	print >> sys.stderr, "\r*> [PreparingTrainTagDB]  %d train tag indexes [%2.2f%s parsed] ~%.2fs" % ( lines, (float(lines)/len(TrainTagIndex)*100), '%', (t2-t1)*1.0 )
	# return dictionaries
	TrainTagCoord = {}
	TrainTagIndex = {}
	return newTrainCoord, newTrainIndex

#-----------------------------------------
def print_help():
	"""	Print information in case of wrong input """
	#~ if the input parameters are not correct
	print >> sys.stderr, "\t Usage: python "+sys.argv[0]+" <train_set.txt>  <out_new_train_set>  <train_set_geoSpread.txt>"
	print >> sys.stderr, "\t e.g. python filteringTrainingSetWithGeoSpreading.py dataset/flickrVideosTrain_ok.txt dataset/flickrVideosTrain_db_geoSpread  > dataset/flickrVideosTrain_ok_geoSpread.txt "
	sys.exit(1)	
#-----------------------------------------
""" Checking the arguments in input """
if len(sys.argv) < 3:
	print_help()
else:
	trainFilePath = sys.argv[1]
	outFilePath = sys.argv[2]
#-----------------------------------------

# Loading Train Set
TrainTagCoord, TrainTagIndex = loadGroupOfTagsFromConvertedFile( trainFilePath, False )

minMatches=50
maxAvg=200.0
newTrainTagCoord, newTrainTagIndex = geographicSpread( TrainTagCoord, TrainTagIndex, minMatches, maxAvg )

serializeTrainSetDB( newTrainTagCoord, newTrainTagIndex, outFilePath )
