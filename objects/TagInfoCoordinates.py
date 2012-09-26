# -*- coding: utf-8 -*-
'''
Created on May 29, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
from geoUtils import *

class TagInfoCoordiantes():
	''' Define the object candidate containing the candidate [lat,lon] '''
	def __init__(self, code=-1, coord=[]): 
		''' Constructor '''
		self.code = code # tag code (integer)
		self.freq = 1
		self.clusters = {}
		if len(coord) > 0:
			self.clusters[-1] = []
			self.clusters[-1].append( coord )# [ (lon,lon) ] in the non-centroid
		self.centroids = [] # self.centroids[incrementalPosition] = centroid coordiantes
		self.ctrSize = {} # ctrId: ctrSize
		self.bestCoo = []

	''' Set functions '''
	def addCoord(self, coord, ctr=-1):
		if not self.clusters.has_key(ctr):
			self.clusters[ctr] = []
		self.clusters[ctr].append( coord )

	def addCoordFromStr(self, coordStr, ctr=-1 ):
		lat = coordStr.split("|")[0]
		lon = coordStr.split("|")[1]
		self.clusters[ctr].append( (float(lat), float(lon)) )

	def update(self, ti, ctr=-1):
		self.freq += ti.getFreq()
		for c in ti.getCluster( ctr ):
			self.clusters[ctr].append( c )

	def setFreq(self, f):
		self.freq = f

	def setBestCoo(self, coo):
		self.bestCoo = coo

	''' Get functions '''
	def getCode(self):
		return self.code

	def getTag(self, code2tag):
		return code2tag[ self.code ]

	def getEncTag(self, code2tag):
		tag = code2tag[ self.code ]
		return tag.encode('utf-8', 'ignore')

	def getAllClusters(self):
		allClusters = []
		for ctrId in self.clusters:
			allClusters += self.clusters[ctrId]
		return allClusters

	def getBiggestCluster(self):
		# find hte biggest size
		ctrIdx,bigS = max(self.ctrSize.iteritems(), key=lambda x:x[1])
		# return size and centroid
		return bigS, self.clusters[ctrIdx]

	def identifyCloserCoordinatesInTuple(self, coordList):
		''' Given a list of Coordinates, return the coordinates with minDist sum of all the others 
		'''
		print >> sys.stdout, "[identifyCloserCoordinatesInTuple] Received %d coordinates" % len(coordList)
		strCoo = []
		for coo in coordList:
			strCoo.append(coordinates2String(coo))
		# Identify the coordinates closer to all the other
		return identifyCloserCoordinatesInGroup( strCoo, self.verbose )

	def computeBestCoordinate(self):
		size, cluster = self.getBiffestCluster()
		coo, sumOfD = self.identifyCloserCoordinatesInTuple( cluster )
		self.setBestCoo(coo)
		return self.bestCoo

	def getBestCoordinate(self):
		return self.bestCoo

	def getBestCoordinateStr(self):
		return string2Coordiantes(self.bestCoo)

	def getCluster(self, ctrId=-1):
		return self.clusters[ctrId]

	def getClusterByCoo(self, ctr):
		ctrId = self.centroids.index( ctr )
		return self.clusters[ctrId]

	def getClustersStr(self):
		out = ""
		for ctrId in self.clusters: # iter each centroid
			if ctrId != -1:
				ctr = self.centroids[ctrId]
				out += "%f,%f:" % (ctr[0], ctr[1])
			for c in self.clusters[ctrId]: # iter each coord inside this cluster
				out += "%f,%f:" % (c[0], c[1])
			out = out[:-1] +"|" # separator from this cluster and the next one
		out = out[:-1]
		return out

	def getCtrsSizeCntStr(self):
		''' Return in string the centroids and the size of its cluster,
			counting how many coordinates there are in each cluster
		'''
		out = ""
		ctrsSize = {}
		# prepare the dictionary with Centroid:size
		for ctrId in self.clusters: # iter each centroid
			ctrsSize[ctrId] = len(self.clusters[ctrId])
		# sort the centroids dictionary by size
		ctrsSizeSort = sorted(ctrsSize.items(), key=lambda ctrsSize: ctrsSize[1]) # return the sorted list of centroidIds
		ctrsSizeSort.reverse()
		# save in string and return it
		for ctrId, size in ctrsSizeSort: # iter each centroid
			ctr = self.centroids[ctrId]
			out += "%f,%f:%d" % (ctr[0], ctr[1], size)
			out += "|" # separator from this cluster and the next one
		out = out[:-1]
		return out

	def getCtrsSizeStr(self):
		''' Return in string the centroids and the size of its cluster,
			simply reading the self.ctrSize dictionary (created in the unserialize step)
		'''
		out = ""
		# compute vector of centroids size
		ctrsSize = self.getDizSizeOfAllClusters()
		# sort the centroids dictionary by size
		ctrsSizeSort = sorted(ctrsSize.items(), key=lambda ctrsSize: ctrsSize[1]) # return the sorted list of centroidIds
		ctrsSizeSort.reverse()
		# save in string and return it
		for ctrId, size in ctrsSizeSort: # iter each centroid
			ctr = self.centroids[ctrId]
			out += "%f,%f:%d" % (ctr[0], ctr[1], size)
			out += "|" # separator from this cluster and the next one
		out = out[:-1]
		return out

	def getDizSizeOfAllClusters(self):
#		print >> sys.stderr, "totCentroids:%d, totClusters:%d" % ( len(self.centroids), len(self.clusters))
#		clusterSize = {}
#		for i in range(0,totClusters):
#			clusterSize[i] = len(self.clusters[i])
		return self.ctrSize

	def getSizeOfAllClusters(self):
		clusterSize = []
		for i in range(0,len(self.ctrSize)):
#			clusterSize.append( len(self.clusters[i]) )
			clusterSize.append( len(self.ctrSize[i]) )
		return clusterSize

	def getSizeOf(self, ctr):
		ctrId = self.centroids.index( ctr )
		return self.ctrSize[ ctrId ]

	def getFreq(self):
		return self.freq

	def getNrOfClusters(self):
		return len(self.centroids)

	def getCentroids(self):
		ctrCoo = []
#		print >> sys.stderr, "len centroids:%d, len ctrSize:%d, len clusters:%d" % (len(self.centroids), len(self.ctrSize), len(self.clusters))
		for cid in range(0,len(self.centroids)):	# the indexes are the centroids_ids
			if self.ctrSize[cid] > 0:
				ctr = self.centroids[cid]
				ctrCoo.append( ctr )
		return ctrCoo

	def getWeight(self):
		return float(len(self.clusters))/self.freq # nrOfClusters/freq    


	''' 
		Other functions 
	'''
	def computeCentroids(self, stopval=0.05):
		if len(self.clusters[-1]) > 1:
#			print >> sys.stderr, "clustering of", self.clusters[-1]
			# where 0.05 is the minVariation from two consecutive avg_distances of kmeans computations
			centroids, qerr, dis, assign, nassign, k = applyYaelKMeans( self.clusters[-1], 1, 20, stopval )
			self.centroids = centroids
			# initialize all the clusters
			for i in range(0,len(self.centroids)):
				self.clusters[i] = []
			print >> sys.stderr, "centroids", self.centroids
			print >> sys.stderr, "nassign", nassign
			# copy each coordinate inside its cluster
			for cooIdx in xrange(0,len(self.clusters[-1])):
				coo = self.clusters[-1][cooIdx]
				ctrIdx = assign[cooIdx]
				# append coordinate into cluster
				self.clusters[ ctrIdx ].append( coo )
#		elif len(self.clusters[-1]) == 2:
#			for i in range(0,len(self.clusters[-1])):
#				coo = self.clusters[-1][i]
#				# create the centroids 0 (equal to the only coordinate present)
#				self.centroids.append(coo)
#				# move the coordinate to the only cluster present
#				self.clusters[i] = []
#				self.clusters[i].append(coo)
		else:
			coo = self.clusters[-1][0]
			# create the centroids 0 (equal to the only coordinate present)
			self.centroids = [coo]
			# move the coordinate to the only cluster present
			self.clusters[0] = []
			self.clusters[0].append(coo)
		# remove the non-centroid data
		del(self.clusters[-1])
		return len(self.clusters)

	def serialize( self, code2tag, tagInfoFile ):
		''' Given an output file, serialize the information of this object
		'''
#		output = "%s %d %d %s\n" % (self.getEncTag(), self.getFreq(), self.getNrOfClusters(), self.getCtrsSizeStr())
		self.computeBestCoordinate()
		output = "%s %d %s %d %s\n" % (self.getEncTag(code2tag), self.getFreq(), self.getBestCoordinateStr(), self.getNrOfClusters(), self.getClustersStr())
		tagInfoFile.write( output )
		tagInfoFile.flush()

	def unserialize( self, tag2code, code2tag, line, type="full" ):
		''' Given an output file, serialize the information of this object
		'''
		# tag freq #ctrs ctr1:size1|ctr2:size2|..ctrN:sizeN
		blk = line.strip().split(" ")
		tag = clean_line(blk[0])
		# update Tag2code and Code2Tag
		if not tag2code.has_key( tag ):
			tag2code[ tag ] = len(tag2code)
		tcode = tag2code[ tag ]
		if not code2tag.has_key( tcode ):
			code2tag[ tcode ] = tag
		# assign tag_code and frequency
		self.code = tcode
		self.freq = int(blk[1])
		self.bestCoo = string2Coordinates( blk[2] )
		# loading centroids and clusters
		allCtrsSize = blk[4].split("|")
		if type == "size":
			for ctrsSize in allCtrsSize:
				ctrStr = ctrsSize.split(":")[0] 
				size = len(ctrsSize.split(":"))
				ctr = string2Coordinates( ctrStr )
				# append new centroids
				self.centroids.append( ctr )
				# add cluster size by centroid id
				self.ctrSize[ self.centroids.index(ctr) ] = size
		elif type == "full":
			for ctrsSize in allCtrsSize: # ctr1:coo1:coo2:coo3:..|ctr2:coo1:..
				coordinates = ctrsSize.split(":")
				ctrStr = coordinates[0]
				ctr = string2Coordinates( ctrStr )
				# append new centroids
				cId = len(self.centroids)
				self.centroids.append( ctr )
				# create new cluster
				self.clusters[ cId ] = []
				for i in xrange(1,len(coordinates)): 
					cooStr = coordinates[i]
					coo = string2Coordinates( cooStr )
					# add cluster size by centroid id
					self.clusters[ cId ].append( coo )
				# define the size of this cluster
				self.ctrSize[ cId ] = len(self.clusters[cId])
				# self.printInput()

	def saveCentroids(self, centroids):
		for i in xrange(0,len(centroids)):
			self.centroids.append( centroids[i] ) # self.centroids[incrementalPosition] = centroid coordiantes
	
	'''
		Development Tools
	'''
	def printInput(self):
		# print info related to thi TagInfo object to check anomalies 
		for cId in range(0,len(self.centroids)):
			print >> sys.stderr, "CentroidId: %d" % cId, "CtrCoo:", self.centroids[cId]
			print >> sys.stderr, "Cluster Size: %d, Cluster Elements: %d" % (self.ctrSize[cId], len(self.clusters[cId]))
			print >> sys.stderr, "Elements:", self.clusters[cId]



class CandidatesCooIntersection():
	''' Given the Video Test information, 
			Compute the triples [(cooT1, cooT2, cooT3), sumOfDistances] 
	'''

	def __init__(self): 
		self.coo = {} # tcode -> list of coordiantes
		self.inters = [] # [ ( score, (cooTag1, cooTag2, ..cooTagM)), ..] 
		self.hasInters = False

	''' Set/Get functions '''
	def addTestTag(self, tagNodes, tcode):
		# compute the ctrStr
		c = [] # list of coordiantes associated to this tag
		tInfo = tagNodes[tcode] # retrieve the tInfo
		cooList = tInfo.getAllClusters()
		# save list of coordinates
		self.coo[tcode] = cooList
		print >> sys.stdout, "[intersections.addTestTag] for tag %d added %d coordiantes" % (tcode, len(cooList))
	
	def size(self):
		return len(self.coo)

	''' Computational functions '''
	def computeIntersection(self, kmTh):
		tcodes = self.coo.keys()
		if len(tcodes) > 1:
			for i in range(0,len(tcodes)-1):
				curTCode = tcodes[i]
				nextTCode = tcodes[i+1]
				pairsList = self.findPairsFromListsOfCoo( self.coo[curTCode], self.coo[nextTCode], kmTh )
				self.mergeSmallListIntoBigList( pairsList, kmTh )
		# if there are intersection change the flag
		if len(self.inters) > 0:
			self.hasInters = True
		print "[computeIntersection] tcodes:", tcodes, "intersections: %d" % len(self.inters)

	def findPairsFromListsOfCoo(self, list1, list2, kmth):
		''' Given two lists of coordinates, compare each possible pairs
			between them, and return the list of pairs that is closer than 
			a given threshold 
		'''
		pairsList = []
		for c1 in list1: 
			for c2 in list2:
#				print "[findPairsFromListsOfCoo] c1:", c1, " c2:", c2, " d:", haversine(c1, c2) 
				if haversine(c1, c2) <= kmth:
					pairsList.append( [c1,c2] )
		return pairsList

	def mergeSmallListIntoBigList(self, smallist, kmth):
		''' biglist: [ [c1,c2,c3], [c4,c5,c6,c8], ...]
			pairsList: [ [cc1, cc2], [cc4,cc8] .. ]
		'''
		if len(self.inters) == 0:
			self.inters = smallist
		# if biglist is not empty
		for i in range(0,len(self.inters)):
			bigTuple = self.inters[i]
			for tmpTuple in smallist:
				# compare bigTuple and tmpTuple
				if self.areCloserTheseTuples( bigTuple, tmpTuple, kmth ):
					self.inters[i] = self.mergeTuples( bigTuple, tmpTuple )
				else:
					self.inters.append( tmpTuple )

	def areCloserTheseTuples(self, tuple1, tuple2, kmth):
		''' Given two tuples (of any lenght) return true if 
			there are coordinates clsoer than the given threshold
		'''
		for c1 in tuple1:
			for c2 in tuple2:
				if haversine( c1, c2 ) <= kmth:
					return True
		return False

	def mergeTuples(self, tuple1, tuple2):
		for e in tuple2:
			if e not in tuple1:
				tuple1.append(e)
		return tuple1

	def getTopNInters(self, topn, kmth):
		''' Sort the tuples and return the top<n> '''
		# If there are not intersection return all the coordinates in a list
		if not self.hasInters:
			print >> sys.stdout, "[getTopNInters] nr. of intersections: %d => using bigger cluster" % len(self.inters)
			return 0, [] # Return list of tcodes: we want to use the biggest centroids of the tags
		# Detecting max nr of coordinates inside the tuples
		maxSize = -1
		print >> sys.stdout, self.inters
		for tup in self.inters:
			if len(tup) >= maxSize:
				maxSize = len(tup)
		# Compute sum of distances among all the coordinates in each tuple
		sumOfDist = {} # sumOfDistances: [tuple1, tuple2, ..]
		for i in range(0,len(self.inters)):
			tuple = self.inters[i]
			# we will add only the 
			if len(tuple) >= maxSize:
				sumOfD = self.computeDistAmongCoo( tuple )
				# add this tuple
				if not sumOfDist.has_key(sumOfD):
					sumOfDist[sumOfD] = []
				sumOfDist[sumOfD].append( tuple )
		# Sorting tuples by sum of distances
		keys = sumOfDist.keys()
		keys.sort()
		keys.reverse()
		# Define other method to better order them
		return keys[0], sumOfDist[keys[0]][0]

	def computeDistAmongCoo(self, tuple):
		sum = 0
		for i in range(0,len(tuple)-1):
			c1 = tuple[i]
			for j in range(i+1,len(tuple)):
				c2 = tuple[j]
				sum += haversine(c1, c2)
		return sum
			







