# -*- coding: utf-8 -*-
'''
Created on May 29, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
from geoUtils import *

class TagInfoClustersList():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor -> fmd: FlickrMediaData object
        '''
        self.tagslist = {} # tag -> TagInfo obj
    
    def addFmdObj(self, fmd):
    	self.updateTagInfoListFromFMD( fmd )
        
    def size(self):
      return len(self.tagslist)

    def getList(self):
      return self.tagslist
    
    def updateTagInfoListFromFMD(self, fmd):
    	# retrieve tags and mtags
    	tags = fmd.getTagsList()
    	mtags = fmd.getMtagsList()
    	# if there are mtags, merge them with tags
    	if len(mtags) > 0:
    		for mt in mtags:
    			if mt not in tags:
    				tags.append( mt )
    	del(mtags)
    	# for each tag, create a standard TagInfo Obj
    	# and check if it is present inside the list
    	for t in tags:
    		if len(t) < 2:
    			continue;
    		taginfo = TagInfo( t, fmd.getCoord() )
    		if self.tagslist.has_key(t):
    			self.tagslist[t].update( taginfo )
    		else:
    			self.tagslist[t] = taginfo


    '''
      Sorting Function
    '''
    def getSortedList(self):
      return sorted(self.tagslist, reverse=True)




class TagInfo():
	'''
		Define the object candidate containing the candidate [lat,lon]
	'''
	def __init__(self, tag="", coord=[]): 
		'''
			Constructor
		'''
		# directly from line
		self.tag = tag # unicode
		self.freq = 1
		self.clusters = {}
		if len(coord) > 0:
			self.clusters[-1] = []
			self.clusters[-1].append( coord )# [ (lon,lon) ] in the non-centroid
		self.centroids = [] # self.centroids[incrementalPosition] = centroid coordiantes
		self.ctrSize = {} # ctrId: ctrSize
		self.bestCoo = []

	''' 
		Set functions 
	'''
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
		return coordinates2String(self.bestCoo)

	def setFreq(self, f):
		self.freq = f

	def setBestCoo(self, coo):
		self.bestCoo = coo

	''' 
		Get functions 
	'''
	def getTag(self):
		return self.tag

	def getEncTag(self):
		return self.tag.encode('utf-8', 'ignore')

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
		# assign size of clusters
		for ctrIdx in self.clusters:
			self.ctrSize[ctrIdx] = len(self.clusters[ctrIdx])
		return len(self.clusters)

	def serialize( self, tagInfoFile ):
		''' Given an output file, serialize the information of this object
		'''
#		output = "%s %d %d %s\n" % (self.getEncTag(), self.getFreq(), self.getNrOfClusters(), self.getCtrsSizeStr())
		output = "%s %d %s %d %s\n" % (self.getEncTag(), self.getFreq(), self.getBestCoordinateStr(), self.getNrOfClusters(), self.getClustersStr())
		tagInfoFile.write( output )
		tagInfoFile.flush()

	def unserialize( self, line, type="full" ):
		''' Given an output file, serialize the information of this object
		'''
		# tag freq #ctrs ctr1:size1|ctr2:size2|..ctrN:sizeN
		blk = line.strip().split(" ")
		self.tag = blk[0]
		self.freq = int(blk[1])
		# loading centroids and clusters
		allCtrsSize = blk[3].split("|")
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



class CandidatesCentroids():
	'''
		Define the object candidate containing the candidate [lat,lon]
	'''
	def __init__(self): 
		'''
			Constructor
		'''
		# directly from line
		self.centroids = [] # list of ctrCoordinates
		self.freqOf = {} # ctrStr: freq
		self.sizeOf = {} # ctrStr: size

	''' 
		Set functions 
	'''
	def addCentroid(self, ctr, size):
		# compute the ctrStr
		ctrStr = coordinates2String( ctr )
		if ctr not in self.centroids:
			self.centroids.append(ctr)	# update list of centroids
			self.freqOf[ctrStr] = 1
			self.sizeOf[ctrStr] = size
		else:
			self.centroids.append(ctr)	# Append in all the cases
			self.freqOf[ctrStr] += 1
			self.sizeOf[ctrStr] += size

	''' 
		Get functions 
	'''
	def size(self):
		return len(self.centroids)

	def getCentroids(self):
		return self.centroids

	def getTopFreq(self):
		''' Return the centroid with higher freq/size
			Usually it is called when there are not enough centroids to perform K-Means
		'''
		maxF = -1
		bestCtr = []
		for ctr in self.centroids():
			ctrStr = coordinates2String( ctr )
			if self.freqOf[ctrStr] > maxF:
				bestCtr = ctr
		return bestCtr, maxF

	def getTopSize(self):
		''' Return the centroid with higher freq/size
			Usually it is called when there are not enough centroids to perform K-Means
		'''
		maxS = -1
		bestCtr = []
		for ctr in self.centroids:
			ctrStr = coordinates2String( ctr )
			if self.sizeOf[ctrStr] > maxS:
				bestCtr = ctr
		return bestCtr, maxS

	def getBiggerCtrOfCtrs( self, ctrOfCtr, nassignList, topn=1 ):
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
 
 
	def getCtrsSizeStr(self, ctrOfCtr, nassignList, dis ):
		''' Return in string the centroids and the size of its cluster
		'''
		out = ""
		# fill the centroids size dictionary
		ctrsSize = []
		ctrs = []
		for i in range(0,len(nassignList)):
			ctrsSize.append(nassignList[i])
		# sort the centroids dictionary by size
		ctrsSize.sort()
		ctrsSize.reverse()
		# save in string and return it
		for size in ctrsSize:
			ctrId = nassignList.index(size)
			ctr = ctrOfCtr[ctrId]
			out += "%f,%f:%d:%f" % (ctr[0], ctr[1], size, dis[ctrId])
			out += "|" # separator from this cluster and the next one
		out = out[:-1]
		return out




class CtrsOfTagCentroids():
	'''
		Define the object candidate containing the candidate [lat,lon]
	'''
	def __init__(self, vectors, ctrOfCtr, qerr, dis, assign, nassign, k): 
		'''
			Constructor
		'''
		self.centroids = ctrOfCtr # ctrStr
		self.ctrSize = nassign
		self.ctrSumDist = [0.]*len(ctrOfCtr)
		self.ctrAvgDist = [0.]*len(ctrOfCtr)
		self.clusters = {} # ctrStr -> [ list of vectors inside this cluster ]
		self.qerr = qerr
		self.k = len(ctrOfCtr)
		# create each cluster (even the one that are empty for KMeans error)
		for cid in range(0,len(self.centroids)):
			self.clusters[cid] = []
		# parse each vector and check in which cluster it is
		for i in range(0,len(vectors)):
			v = vectors[i]
			vCtr = assign[i] # get the id of the centroid of v
			# append this vector in its cluster
			self.clusters[vCtr].append(v)
			# update the distance in this cluster
			self.ctrSumDist[vCtr] += dis[i]
		# compute average distances for each centroid
		for i in range(0,len(self.ctrSumDist)):
			self.ctrAvgDist[i] = self.ctrSumDist[i]/max(self.getSizeOf(i),1)

	''' 
		Get functions 
	'''
	def getSizeOf(self, ctrId):
		return len(self.clusters[ctrId])

	def getSizeOfallClusters(self):
		ctrSize = []
		for ctrId in self.clusters:
			ctrSize.append( len(self.clusters[ctrId]) )
		return ctrSize

	def getClusters(self, ctr):
		ctrId = self.centroids.index(ctr)
		return self.clusters[ctrId]

	def rankCentroids(self):
		rank = {} # ctrId -> score
		# select all the centroids with higher score
		clustersSize = self.getSizeOfallClusters()
		maxScore = max(clustersSize)
		bigCtrs = []
		for i in range(0,len(clustersSize)):
			if maxScore == clustersSize[i]:
				bigCtrs.append(i)
		# create the ranking dictionary
		for i in range(0,len(bigCtrs)):
			cId = bigCtrs[i]
			rank[cId] = self.ctrAvgDist[cId]
		# sort and return the best cluster
		sortedRankKeys = sorted(rank, key=rank.get, reverse=False) # descending order for avg distance
		return self.centroids[sortedRankKeys[0]]

	def printCentroidsInfo(self):
		for i in range(0,len(self.centroids)):
			size = self.getSizeOf(i)
			if size > 1:
				print >> sys.stdout, self.centroids[i],"size:%d, avgDist:%f, score:%f" % (size, self.ctrAvgDist[i], self.ctrAvgDist[i]/size)
			else:
				print >> sys.stdout, self.centroids[i],"size:%d, avgDist:%f" % (size, self.ctrAvgDist[i])







