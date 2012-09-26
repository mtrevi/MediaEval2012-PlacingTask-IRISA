#!/bin/env python
'''
Created on May 2, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
from geoUtils import *
from objects.TagInfoClusters import *

#-----------------------------------------
"""	Print information in case of wrong input """
def print_help():
	#~ if the input parameters are not correct
  print "\t Usage: cat <location_distribution.txt> | python "+sys.argv[0]
  sys.exit(1)	
#-----------------------------------------
""" Checking the standard input """
if not sys.stdin:
	print_help()
#-----------------------------------------

# Parsing the location distribution, e.g. 
# 37.617393,-122.466446,-1        1       1
cList = []
lines = 0
print >> sys.stderr, "Parsing input file:",
for line in sys.stdin:
	lines += 1
	blk = line.strip().split( "\t" )
	lat = float( blk[0].split(",")[0] )
	lon = float( blk[0].split(",")[1] )
	strLat = blk[0].split(",")[0]
	strLon = blk[0].split(",")[1]
	times = int( blk[1] )
	users = int( blk[1] )
	#coord = strLat +","+ strLon
	coord = [lat, lon]
	# Convert to Cartesian coordinates
	# coord = convert2cartesian( lat, lon )
	# Append the coordinates how many times it appeared in the train set
	for i in range(0,times):
		cList.append( coord )
print >> sys.stderr, "%d lines" % lines


###############################
# Call Yael K-Means algorithm #
###############################
def getBiggerCtrOfCtrs( ctrOfCtr, nassignList, topn=1 ):
	''' ctrOfCtr is a list with the centroids in coordinates
		nassirgn is a list of the same length with the size of each centroids
	'''
	# define lists
	ctrsOfCtrs = []
	ctrsOfCtrsSize = []
	# if we have to extract the topN biggest clusters
	if topn > 1:
		sortedSize = sorted(nassignList)
		sortedSize.reverse()
		for s in sortedSize:
			idx = nassignList.index(s)	# pick the current biggest size idx
			if len(ctrsOfCtrs) > 0 or ctrOfCtr[idx] > 1: # if the size is > 1 proceed
				ctrsOfCtrs.append( ctrOfCtr[idx] )
				ctrsOfCtrsSize.append( s )
			# stop condition
			topn -= 1
			if topn == 0:
				break
	# if we have to extract only the biggest cluster
	else:
		biggestCtrIdx = nassignList.index(max(nassignList))
		ctrsOfCtrs.append( ctrOfCtr[ biggestCtrIdx ] )
		ctrsOfCtrsSize.append( nassignList[ biggestCtrIdx ] )
	# return lists of biggest centroid and its size
	return ctrsOfCtrs, ctrsOfCtrsSize

stopval = 5
topn = 3
ctrOfCtr, qerr, dis, assign, nassign, k = applyYaelKMeans( cList, 1000, 500000, stopval )
ctrsOfCtrs = CtrsOfCentroids( cList, ctrOfCtr, qerr, dis, assign, nassign, k)
# GET THE HIGHER SCORE CENTROIDS OF Coordiantes
ctrList, scoreList = getBiggerCtrOfCtrs( ctrOfCtr, nassign, topn )
for i in range(0,len(ctrList)):
	print ctrList[i], scoreList[i]

##########################
# Call K-Means algorithm #
##########################
# print >> sys.stderr, "Computing K-Means"
# centroids, positions = applyKMeansCluster( cList, 2000, 10000, 0.5 )
# print "nr. of centroids", len(centroids)

# # Compute the biggest cluster
# print >> sys.stderr, "Get the biggest cluster"
# posList = map(None, positions)
# p = max(posList, key=posList.count)

# bestCoord = map(None, centroids[p])
# print centroids[p]
# # Convert to LatLon
# # bestCartCoord = map(None, centroids[p])
# # bestCoord = convertFromCartesian( bestCartCoord[0], bestCartCoord[1], bestCartCoord[2] )

# print bestCoord


##########################
# 	 Call CloserGroup 	 #
##########################
#createCloserGroups( cList, 3 )