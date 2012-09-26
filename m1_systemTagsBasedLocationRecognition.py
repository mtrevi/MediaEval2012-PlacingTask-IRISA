#!/bin/env python
# -*- coding: utf-8 -*-
'''
Created on May 2, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import time
import sys
from geoUtils import *
from objects.ResCandidates import *
from itertools import izip_longest
from threading import Lock


class TagsProcessing:
	
	def __init__( self, testFilePath, verbose, topn, selectCoordMethod, scoreMetric, matchingType, distanceKmThreshold, runNr, groupname ):
		self.TestFile = file( testFilePath, 'r' )
		# Initialize the dictionary structure
		self.TrainTagCoord = {} # tags: [ ([lat, lng, acc],frequency), ([...],freq), .. ]
		# For Filters
		self.UserPlaces = {}
		self.GeoNames = {}
		self.GeoNamesIndex = {}
		self.geoTags = []
		# for content-based results
		self.FnCoo = {} # filename (or imageId) -> coordinates
		self.FnRes = {} # filename (or imageId) -> [ list of coordinates ]
		# Global Variables
		self.runNr = runNr
		self.groupname = groupname
		self.topn = topn
		self.verbose = verbose
		self.selectCoordMethod = selectCoordMethod
		self.distanceKmThreshold = distanceKmThreshold
		self.scoreMetric = scoreMetric
		self.matchingType = matchingType
		self.maxKMeansError = 0.5
		#[35.75615310668945, 139.73165893554688] 25397 ~ Tokio
		#[49.36097717285156, -123.12287139892578] 17343 ~ Vancouver
	 	#[32.87230682373047, -96.91407775878906] 15874 ~ Dallas
		self.defaultCoordinates = [35.76, 139.73]#[39.83,-98.58] ~ old one
		# Global Variables in Test Function
		self.userMostProbableLocation = 0
		self.userHomeCoordinates = 0
		self.nullCoordinates = 0
		self.noTags = 0
		# Multithreading
		self.lockVar = Lock()
		# For statistics
		self.stats = {}
		self.limits = [1, 10, 100, 1000, 10000]
		for k in self.limits:
			self.stats[k] = 0

	def prepareGeoNamesFilter( self, geoNamesFile ):
		''' Load the external files used by the filters '''
		#self.GeoNamesFile = file( geoNamesFile, 'r' )
		#self.GeoNames, self.GeoNamesIndex = loadGeoNamesSplittingKeys( self.GeoNamesFile )
		# read GeoNames from file
		self.GeoNames, self.GeoNamesIndex = unserializeGeoNamesFilterDB( geoNamesFile )
		# loading the geoNames in memory
		#self.geoTags = geographicTagsFiltering( self.TrainFile, self.GeoNames, self.stopword )

	''' Parsing dictionary file: filename(or imageId) <tab> lat,lon <tab> imageId '''
	def prepareFilenameCooDiz(self, dizFilePath):
		print >> sys.stderr, "*> [Loading Filename-Coordinates Dictionary]", 
		dizFile = open( dizFilePath, 'r' )
		for line in dizFile:
			blk = clean_line( line.strip() ).split("\t")
			fn = blk[0]
			lat = float(blk[1].split(",")[0])
			lon = float(blk[1].split(",")[1])
			self.FnCoo[fn] = [lat,lon]
		dizFile.close()
		print >> sys.stderr, "%d filename-coordiantes entries loaded" % len(self.FnCoo)

	def prepareContentBasedResultsCandidates(self, resultsFilePath):
		''' Load Video Content Results Candidates, e.g.
				00026.mp4 <tab> 3397235887.jpg:0.021265 <tab> 2270299951.jpg:0.019961 <tab> 395899439.jpg:0.019936 
		'''
		print >> sys.stderr, "*> [Content-Based]",
		resultsFile = open(resultsFilePath, 'r')
		for res in resultsFile:
			blk = res.strip().split("\t")
			qfn = blk[0]
			if not self.FnRes.has_key(qfn):
				self.FnRes[qfn] = []
			for i in range(1,len(blk)):
				candFn = blk[i].split(":")[0]
				if 'jpg' in candFn:
					candFn = candFn.replace(".jpg", "")
				if self.FnCoo.has_key(candFn):
					coo = self.FnCoo[candFn]
					self.FnRes[qfn].append( coo )
		resultsFile.close()
		print >> sys.stderr, "%d queries (with results) loaded" % len(self.FnRes)

	def prepareUsersCommonestPlaces( self, userPlacesFilePath ):
		''' Load the users commonest places
		'''
		print >> sys.stderr, "*> [UserPlaces]",
		t1 = time.time()
		totUsers = 70755.0
		users = 0
		UserPlacesFile = file( userPlacesFilePath, 'r' )
		for line in UserPlacesFile:
			users += 1
			blk = line.strip().split( "\t" )
			uId = blk[0].lower()
			# adding new users
			if not self.UserPlaces.has_key( uId ):
				self.UserPlaces[uId] = []
			# parsing the coordinates
			CoordFreqStrList = blk[1].split( "|" )
			for coordFreqStr in CoordFreqStrList:
				coordFreq = coordFreqStr.split( "," )
				lat = float( coordFreq[0] )
				lon = float( coordFreq[1] )
				acc = int( coordFreq[2] )
				freq = int( coordFreq[3] )
				self.UserPlaces[uId].append( [lat, lon, acc, freq] )
			# print info
			if users % 10000:
				print >> sys.stderr, "\r*> [UserPlaces] parsed %d [%2.2f%s]" % ( users, users/totUsers*100, '%'),
		print >> sys.stderr, "\r*> [UserPlaces] %d total users [%2.2f%s]" % (len(self.UserPlaces), users/totUsers*100, '%')

	def prepareTrainingSet( self, trainFilePath ):
		''' Load the tags in group and the coordinates 
			and also prepare the self.TrainTagIndex that will increase the speed
			to access to the related train tags
		'''
		try:
			# un-serialize train set DB
			self.TrainTagCoord, self.TrainTagIndex = unserializeTrainSetDB( trainFilePath )
		except:
			# load and process each tag
			self.TrainTagCoord, self.TrainTagIndex = loadGroupOfTagsFromConvertedFile( trainFilePath )

	def getContentVideoResults(self, filename):
		resCandidates = ResCandidates()
		if self.FnRes.has_key( filename ):
			# get list of coordiantes
			listOfCoo = self.FnRes[ filename ]
			# Select the best coo among the ones in the listOfCoo
			coo, sumOfD = self.identifyCloserCoordinatesInTuple( listOfCoo )
			# Add the best coordinattes in the result
			resCandidates.add( sumOfD, coo, "_byContentMatching" )
		return resCandidates


	def getMostLikelihoodCoordinates( self, CoordInfoList ):
		''' Given a list of coordinates with frequency and with the same rank,
			detect with is the best coordinate to return
		'''
		# CoordInfoList[0] = [(('51.333417', '-0.267094', -1), 1)]
		bestCoord = []
		if len(CoordInfoList) == 0:
			return []
		elif len(CoordInfoList) == 1:
			coord = CoordInfoList[0]
			bestCoord = [float(coord[0][0]), float(coord[0][1])]
			return bestCoord
		# if there are just two coordinates with the same frequency, return the first one
		elif len(CoordInfoList) == 2:
			coord1 = CoordInfoList[0]
			coord2 = CoordInfoList[1]
			if coord1[1] == coord2[1]:
				bestCoord = [float(coord1[0][0]), float(coord1[0][1])]
				return bestCoord

		# Define which technique to use
		technique = self.selectCoordMethod
		################################
		# Apply Biggest Group from top scores
		################################
		if technique == "byBiggestGroupOnTopScore":
			coordList = []
			for coord in CoordInfoList:
				# read the frequency
				freq = int(coord[1])
				# Add many times this coordinates as the number of its frequency 
				for i in xrange(0,freq):
					newC = str(coord[0][0]) +","+ str(coord[0][1])
					coordList.append( newC )
			# compute the center of the biggest group
			bestCoord, sumOfD = self.computeBiggestGroupOfCoordinates(coordList)
		################################
		# Apply frequency -> return the most frequent
		################################
		elif technique == "byFrequency":
			lc = []
			maxF = 0
			for coord in CoordInfoList:
				freq = int(coord[1])
				if max( freq, maxF ) == freq:
					bestCoord = [float(coord[0][0]), float(coord[0][1])]
					maxF = freq
		################################
		# APPLY K-Means
		################################
		elif technique == "byKMeans":
			# CoordInfoList[0] = [(('51.333417', '-0.267094', -1), 1)]
			coordList = []
			# Create list of coordinates (x, y, z)
			for coordFreq in CoordInfoList:
				# cartesianCoord = convert2cartesian( float(coordFreq[0][0]), float(coordFreq[0][1]) )
				cartesianCoord = [ float(coordFreq[0][0]), float(coordFreq[0][1]) ]
				coordList.append( cartesianCoord )
			# Call K-Means algorithm
			centroids, positions = applyKMeansCluster( coordList, 1, 1000, self.maxKMeansError )
			# Compute the biggest cluster
			posList = map(None, positions)
			p = max(posList, key=posList.count)
			bestCoord = map(None, centroids[p])
		################################
		# APPLY Yael K-Means
		################################
		elif technique == "byYaelKMeans":
			# CoordInfoList[0] = [(('51.333417', '-0.267094', -1), 1)]
			coordList = []
			# Create list of coordinates (x, y, z)
			for coordFreq in CoordInfoList:
				# cartesianCoord = convert2cartesian( float(coordFreq[0][0]), float(coordFreq[0][1]) )
				cartesianCoord = [ float(coordFreq[0][0]), float(coordFreq[0][1]) ]
				coordList.append( cartesianCoord )
			# Call K-Means algorithm
			centroids, qerr, dis, positions, nassign, k = applyYaelKMeans( coordList, 1, 1000, self.maxKMeansError/10 )
			# Compute the biggest cluster
			posList = map(None, positions)
			p = max(posList, key=posList.count)
			bestCoord = map(None, centroids[p])

		return bestCoord
		# consider the accuracy ?!

	def computeYaelKmeansOfCoordinates(self, coordList):
		''' Given a list of Coordinates, return the coordinates with minDist sum of all the others 
		'''
		# Call K-Means algorithm
		centroids, qerr, dis, positions, nassign, k = applyYaelKMeans( coordList, 1, 20, self.maxKMeansError )
		if self.verbose:
			print >> sys.stderr, "computeYaelKmeansOfCoordinates] qerr=%f, centroids=%d, k=%d " % (qerr, len(centroids), k)
		if len(centroids) > 0:
			# Identify the coordinates closer to all the other
			bigCtrIdx = nassign.index( max(nassign) )
			return centroids[ bigCtrIdx ] 
		else:
			return ""

	def computeBiggestGroupOfCoordinates(self, coordList):
		''' Given a list of Coordinates, return the coordinates with minDist sum of all the others 
		'''
		strBiggestGroup = createCloserGroups( coordList, self.distanceKmThreshold, self.verbose )
		if self.verbose:
			print >> sys.stderr, "computeBiggestGroupOfCoordinates] strBiggestGroup:", strBiggestGroup
		if len(strBiggestGroup) > 0:
			# Identify the coordinates closer to all the other
			centerCoo, sumOfD = identifyCloserCoordinatesInGroup( strBiggestGroup, self.verbose )
			return centerCoo, sumOfD
		else:
			return "", -1

	def computeBiggestCoordinatesFromResults( self, resCandidates ):
		''' Given all the results, compute the biggest group and return a random coordinates inside 
		'''
		# results e.g. [ [5.0, [lat,lon], "tags"] ]
		newResCandidates = ResCandidates()
		coordList = []
		for res in resCandidates.getList():
			# get coordinates in string format: for [computeBiggestGroupOfCoordinates]
			strCoo = res.getCoordStr()
			coordList.append( strCoo )
#			coo = res.getCoord()	# for [computeYaelKmeansOfCoordinates]
#			coordList.append( coo )
		# Print input coordinates list
		if self.verbose:
			print >> sys.stderr, ""
			print >> sys.stderr, "computeBiggestCoordinatesFromResults] coordList:", coordList
		# Compute the biggest group
		centerCoo, sumOfD = self.computeBiggestGroupOfCoordinates( coordList )
#		centerCoo = self.computeYaelKmeansOfCoordinates( coordList )
		# find the relative "result" with all the info
		if len(centerCoo) > 0:
			for res in resCandidates.getList():
				coord = res.getCoord()
				if coord == centerCoo:
					newResCandidates.addObj( res )
					return newResCandidates
		# otherwise something went wrong
		newResCandidates.add( 0.0, self.defaultCoordinates, "no results" )
		return newResCandidates

	def getUserMostProbableLocation( self, uId ):
		''' Return the most probable location of the userId Given
		'''
		resCandidates = ResCandidates()
		if not self.UserPlaces.has_key(uId):
			return resCandidates
		# check the coordinates with highest frequency
		maxFreq = 0
		bestCoord = self.defaultCoordinates
		for coordFreq in self.UserPlaces[uId]:
			lat = coordFreq[0]
			lon = coordFreq[1]
			acc = coordFreq[2]
			freq = coordFreq[3]
			if max(maxFreq, freq) == freq:
				bestCoord = [ lat, lon ]
		if bestCoord != self.defaultCoordinates:
			resCandidates.add( -1, bestCoord, uId+"_userPlaces" )
#			resCandidates = [[ -1, bestCoord, uId+"_userPlaces" ]]
		return resCandidates


	def matchWithGroupsOfTags( self, tagsLine, mtagsLine ):
		''' Compare the Test Video Tags and MTags with the TrainSet and GeoNames DB.
			Higher priority to the mtags (if there are, I filter the GroupOfTags just with matches of mtags),
			Otherwise, same procedure for tags. After, we recheck all the matches, and compute the number of 
			tag included in each GroupOfTags -> computing score.
		'''
		# create output with all the top Result Candidates
		resCandidates = ResCandidates()
		matches = MatchCandidates()
		tags = tagsLine.strip().split(" ")
		
		########################################################
		# Get the GoT where the index matches with mtag or tag #
		########################################################
		# If there are Machine Tags, retrieve the GroupOfTags just from them
		if len(mtagsLine.strip()) > 2:
			mtags = mtagsLine.strip().split(" ")
			tags = tags + mtags # Merge the mtags with the tags
			for mtag in mtags:
				# Check the TrainSet
				if self.TrainTagIndex.has_key(mtag):
					for groupOfTags in self.TrainTagIndex[mtag]:
						matches.update(groupOfTags, 0)
				# Check the GeoNames
				if self.GeoNamesIndex.has_key(mtag):
					for groupOfTags in self.GeoNamesIndex[mtag]:
						matches.update(groupOfTags, 0)
		# If the mtags didn't find any match, use the tags
		if matches.size() == 0:
			# Create the list of GroupOfTags containing the TestTags
			for tag in tags:
				# Check the TrainSet
				if self.TrainTagIndex.has_key(tag):
					for groupOfTags in self.TrainTagIndex[tag]:
						matches.update(groupOfTags, 0)
				# Check the GeoNames
				if self.GeoNamesIndex.has_key(tag):
					for groupOfTags in self.GeoNamesIndex[tag]:
						matches.update(groupOfTags, 0)

		# if there are no matches, return 0
		if matches.size() == 0:
			return resCandidates
		
		###################################################################
		# Count the number of matches between the tags+mtags and the candidates #
		###################################################################
		# Checking how many matches there are in all the GoT
		for tag in tags:
			for groupOfTags in matches.getKeys():
				gotSplit = groupOfTags.strip().split(" ")
				# check a partial match inside the entire groupOfTags
				if matchingType == 'partial':
					if tag in groupOfTags:
						matches.update(groupOfTags, 1)
				# check the match for every tag inside the groupOfTags
				elif matchingType == 'perfect':
					for got in gotSplit:
						# perfect match = exact
							if tag == got:
								matches.update(groupOfTags, 1)
#								break
		
		# computing the score for each groups of tags
		matches.computeScores( self.scoreMetric, len(tags) )
		# get the scores of the topN matches
		maxScores = matches.getTopNScores( self.topn )
		# get the keys of the topnN matches
		topnKeys = matches.getKeysWithGivenScores( maxScores )
		if self.verbose:
			print >> sys.stderr, "matchWithGroupOfTags] we are here, maxScores: %d, topNelements: %d" % ( maxScores[0], len(topnKeys))

		########################################################################
		# From all the topN candidates compute the most likelihood coordinates #
		########################################################################
		# for all the topN matches, return the most likelihood coordinates
		for got in topnKeys:
			# check if the key is from TrainTags
			if self.TrainTagCoord.has_key(got):
				coord = self.getMostLikelihoodCoordinates( self.TrainTagCoord[got] )
      # check if the key is from GeoNames
			elif self.GeoNames.has_key(got):
				coord = self.getMostLikelihoodCoordinates( self.GeoNames[got] )
			else:
				continue
			# if coord is empty
			if len(coord) == 0:
				continue
			# update the results
			resCandidates.add( matches.getValue(got), coord, got )
		# return all the results
		return resCandidates

	def getInfoFromTestVideo(self, line, withMtags=True):
		''' Given the line of TestVideo, extract tags, mtags and geoLocation '''
		blk = line.strip().split("\t")
		if withMtags:
			# get the tags
			tags = clean_line( blk[3] )
			mtags = clean_line( blk[4] )
			# apply tags filters -> mtags contain the geo machine tags
			#	if len(mtags) > 1:
			#		tags += " "+ mtags # give more power to the geo tags
			# Read Real Location: "45.516639|-122.681053|16|Portland|Oregon|etats-Unis|16"
			location = blk[5].strip()
			# Owner location: ['14678786@N00', 'milwaukee, United States']
			ownGeo = blk[6].split("|")
		else:
			# get filtered tags and mtags
			tags, mtags = tagsfilters( blk[3] )
			# get geo location
			location = blk[4].strip()
			# Owner location: ['14678786@N00', 'milwaukee, United States']
			ownGeo = blk[5].split("|")
		# extract geo
		geo = location.split("|")
		acc = geo[2]
		return tags, mtags, geo, ownGeo

	def parseTestVideos(self, withMtags=True, officialRun=False ):
		''' Given the TestSet file, read and parse each video meta-data,
			select the tags and retrieve the most suitable places for those tags
		'''
		print >> sys.stderr, "*> [SelectCoordMethod: %s] [ScoreMetric: %s] [MatchingType: %s]" % ( self.selectCoordMethod, self.scoreMetric, self.matchingType )
		print >> sys.stderr, "*> [TestSet]",
		t1 = time.time()
		userMostProbableLocation = 0
		userHomeCoordinates = 0
		nullCoordinates = 0
		contentbased = 0
		noTags = 0
		totLines = 4532.0
		lines = 0
		# videoId <t> title <t> url <t> tags <t> mtags <t> location <t> ownerLocation
		for line in self.TestFile:
			lines += 1
			print >> sys.stderr, "---"
			methodUsed = "All Methods"
			################
			# get filename and url
			blk = line.strip().split("\t")
			url = blk[2].strip()
			filename = blk[1].split("|")[0]
			if '.jpg' in filename:
				filename.replace('.jpg', '')
			################
			# get the tags, mtags, geo and ownGeo
			tags, mtags, geo, ownGeo = self.getInfoFromTestVideo( line, withMtags )
			# print info
#			if type(tags) == 'unicode':
#				print >> sys.stderr, "* input tags: %s [mtags: %s]" % (tags.encode('utf-8','ignore'), mtags.encode('utf-8','ignore'))
#			else:
#				print >> sys.stderr, "* input tags: %s [mtags: %s]" % (tags, mtags)
			realCoord = [float(geo[0]), float(geo[1])] if not officialRun else ""
			resCandidates = ResCandidates()
			
			# 1st METHOD: check tags in training set
			if len(tags) > 1:
				methodUsed = "TrainSet"
				resCandidates = self.matchWithGroupsOfTags( tags, mtags )
			else:
				noTags += 1
			# print out info
			if self.verbose:
				print >> sys.stderr, "*> parseTestVideos] got %d results with" % resCandidates.size(), methodUsed
			
			# 2nd METHOD: (if there are NOT RESULTS) use the most probable location for this user
			if resCandidates.size() == 0:
				methodUsed = "UserCommonLocation"
				ownId = ownGeo[0]
				resCandidates = self.getUserMostProbableLocation( ownId.lower() )
				if resCandidates.size() > 0:
					print >> sys.stderr, "*> Used UserCommonLocation for user %s" % ownId
					userMostProbableLocation += 1
				else:
					print >> sys.stderr, "*> NO UserCommonLocation for user %s" % ownId
				# print out info
				if self.verbose:
					print >> sys.stderr, "*> parseTestVideos] got %d results with" % resCandidates.size(), methodUsed

			# 3rd METHOD: (if there are NOT RESULTS) USE the USER HOMETOWN as tags
			if resCandidates.size() == 0:
				methodUsed = "HomeTown"
				# prepare hometown tags
				ht = ownGeo[1].split(",")
				hometownTags = ""
				for w in ht:
					if len(w) > 1:
						hometownTags += w +" "
				hometownTags = hometownTags[:-1]
				if (hometownTags) < 2:
					continue
				# check with the new set of tags
				resCandidates = self.matchWithGroupsOfTags( hometownTags, "" )
				if resCandidates.size() > 0:
					userHomeCoordinates += 1
				# print out info
				if self.verbose:
					print >> sys.stderr, "*> parseTestVideos] got %d results with" % resCandidates.size(), methodUsed

			# 4th METHOD: Check Content-Video results
			if resCandidates.size() == 0:
				resCandidates = self.getContentVideoResults( filename )
				if resCandidates.size() > 0:
					print >> sys.stderr, "*> Used Content-Based Approach"
					contentbased += 1
				else:
					print >> sys.stderr, "*> NO Content-Based Information"

			# 4th METHOD: (if there are NOT RESULTS) define zero position
			if resCandidates.size() == 0:
				methodUsed = "DefaultCoordinates"
				nullCoordinates += 1
				hometown = False
				resCandidates.add( -1.0, self.defaultCoordinates, "no results" )
				# print out info
				if self.verbose:
					print >> sys.stderr, "*> parseTestVideos] defined default coordinates"

			# return the bigger coordinates group 
			if resCandidates.size() > 2:
				# print out info
				if verbose:
					print >> sys.stderr, "*> parseTestVideos] BiggestCoordinatesGroup: from %d results got 1" % resCandidates.size()
					candies = []
					for res in resCandidates.getList():
						candies.append( str(res.getScore()) +","+ str(res.getCoord()[0]) +"|"+ str(res.getCoord()[1]) ) 
				resCandidates = self.computeBiggestCoordinatesFromResults( resCandidates )
				# print out info
				if self.verbose:
					for can in candies:
						print >> sys.stderr, can
					print >> sys.stderr, "*> parseTestVideos] FINAL => ", resCandidates.getList()[0].getCoord()

			# write the buffer into a file
			if not officialRun:
				self.serialize( resCandidates, realCoord, methodUsed )
				self.serializeFormatted( resCandidates, filename, url )
			else:
				self.serializeFormatted( resCandidates, filename, url )
			# print info
			if (lines % 100) == 0:
				print >> sys.stderr, "\r*> [TestSet] %2.2f%s parsed [%d usrLoc, %d usrHome, %d content-based, %d defCoordinates, %d noTags]" % ( (lines/totLines*100), '%', userMostProbableLocation, userHomeCoordinates, contentbased, nullCoordinates, noTags ),
		# final info
		t2 = time.time()
		print >> sys.stderr, "\r*> [TestSet]  %d videos [%d userLocation, %d hometown, %d content-based, %d defaultCoordinates, %d with no tags] ~%.2fs" % ( lines, userMostProbableLocation, userHomeCoordinates, contentbased, nullCoordinates, noTags, (t2-t1)*1.0 )
		# compute the average of the statistics
		print >> sys.stderr, "---"
		if not officialRun:
			for k in self.limits:
				p = float(self.stats[k])/lines*100
				print >> sys.stderr, "*> [TestSet] %d videos (%.2f%s) inside a radius of %dkm" % (self.stats[k], p, '%', k)
		# close test file
		self.TestFile.close()


	def multithreadTestVideosParser(self, line, varLock=""):
		'''
		'''
		methodUsed = "All Methods"
		blk = line.strip().split("\t")
		# get the tags
		tags = clean_line( blk[3] )
		mtags = clean_line( blk[4] )
		print >> sys.stderr, "---"
		print >> sys.stderr, "* input tags: %s [mtags: %s]" % (tags, mtags)
		# apply tags filters -> mtags contain the geo machine tags
#			if len(mtags) > 1:
#				tags += " "+ mtags # give more power to the geo tags
		# Read Real Location: "45.516639|-122.681053|16|Portland|Oregon|etats-Unis|16"
		location = blk[5].strip()
		geo = location.split("|")
		acc = geo[2]
		realCoord = [float(geo[0]), float(geo[1])]
		resCandidates = ResCandidates()
			
		# 1st METHOD: check tags in training set
		if len(tags) > 1:
			methodUsed = "TrainSet"
			resCandidates = self.matchWithGroupsOfTags( tags, mtags )
		else:
			self.updateLockVariables( methodUsed )
		# print out info
		if self.verbose:
			print >> sys.stderr, "*> parseTestVideos] got %d results with" % resCandidates.size(), methodUsed
			
		# 2nd METHOD: (if there are NOT RESULTS) use the most probable location for this user
		if resCandidates.size() == 0:
			methodUsed = "UserCommonLocation"
			ownGeo = blk[6].split("|")
			ownId = ownGeo[0]
			resCandidates = self.getUserMostProbableLocation( ownId )
			if resCandidates.size() > 0:
				self.updateLockVariables( methodUsed )
			# print out info
			if self.verbose:
				print >> sys.stderr, "*> parseTestVideos] got %d results with" % resCandidates.size(), methodUsed

		# 3rd METHOD: (if there are NOT RESULTS) USE the USER HOMETOWN as tags
		if resCandidates.size() == 0:
			methodUsed = "HomeTown"
			# Owner location: ['14678786@N00', 'milwaukee, United States']
			ownGeo = blk[6].split("|")
			# prepare hometown tags
			ht = ownGeo[1].split(",")
			hometownTags = ""
			for w in ht:
				if len(w) > 1:
					hometownTags += w +" "
			hometownTags = hometownTags[:-1]
			if (hometownTags) >= 1:
				# check with the new set of tags
				resCandidates = self.matchWithGroupsOfTags( hometownTags, "" )
				if resCandidates.size() > 0:
					self.updateLockVariables( methodUsed )
					# print out info
				if self.verbose:
					print >> sys.stderr, "*> parseTestVideos] got %d results with" % resCandidates.size(), methodUsed

		# 4th METHOD: (if there are NOT RESULTS) define zero position
		if resCandidates.size() == 0:
			methodUsed = "DefaultCoordinates"
			self.updateLockVariables( methodUsed )
			hometown = False
			resCandidates.add( -1.0, self.defaultCoordinates, "no results" )
			# print out info
			if self.verbose:
				print >> sys.stderr, "*> parseTestVideos] defined default coordinates"

		# return the bigger coordinates group 
		if resCandidates.size() > 2:
			# print out info
			if verbose:
				print >> sys.stderr, "*> parseTestVideos] BiggestCoordinatesGroup: from %d results got 1" % resCandidates.size()
				candies = []
				for res in resCandidates.getList():
					candies.append( str(res.getScore()) +","+ str(res.getCoord()[0]) +"|"+ str(res.getCoord()[1]) ) 
			resCandidates = self.computeBiggestCoordinatesFromResults( resCandidates )
			# print out info
			if self.verbose:
				for can in candies:
					print >> sys.stderr, can
				print >> sys.stderr, "*> parseTestVideos] FINAL => ", resCandidates.getList()[0].getCoord()

		# write the buffer into a file
		self.serialize( resCandidates, realCoord, methodUsed )
		print >> sys.stderr, "---\n"


	def updateLockVariables(self, methodUsed):
		self.lockVar.acquire()
		try:
			if methodUsed == "TrainSet":
				self.noTags += 1
			elif methodUsed == "UserCommonLocation":
				self.userMostProbableLocation += 1
			elif methodUsed == "HomeTown":
				self.userHomeCoordinates += 1
			elif methodUsed == "DefaultCoordinates":
				self.nullCoordinates += 1
		finally:
			self.lockVar.release()

	def grouper(self, n, iterable, padvalue=None):
		"""	grouper(3, 'abcdefg', 'x') --> ('a','b','c'), ('d','e','f'), ('g','x','x')
		"""
		return izip_longest(*[iter(iterable)]*n, fillvalue=padvalue)


	def parseTestVideosMT(self):
		''' Given the TestSet file, read and parse each video metadata,
			select the tags and retrieve the most suitable places for those tags
		'''
		print >> sys.stderr, "*> [SelectCoordMethod: %s] [ScoreMetric: %s] [MatchingType: %s]" % ( self.selectCoordMethod, self.scoreMetric, self.matchingType )
		print >> sys.stderr, "*> [TestSet]",
		t1 = time.time()
		totLines = 4532.
		# videoId <t> title <t> url <t> tags <t> mtags <t> location <t> ownerLocation
		
		# read entirely the file in memory
		TestData = []
		lines = 0
		for line in self.TestFile:
			lines += 1 
			TestData.append( line )
		print >> sys.stderr, "\r*> [TestSet] LOADED %s lines in memory" % line(TestData)
		
		# multithreading call
		import multiprocessing.dummy as mpd
		pool = mpd.Pool()
		for chunk in self.grouper(1133, TestData):	# PROBLEM DURING THE DIVISION IN CHUNK: if it is not perfect it returns an error
			accumulator = list( pool.imap( self.multithreadTestVideosParser, chunk ) )
#		accumulator = list( pool.imap( self.multithreadTestVideosParser, TestData ) )
		
		# final info
		t2 = time.time()
		print >> sys.stderr, "\r*> [TestSet]  %d videos [%d userLocation, %d hometown, %d defaultCoordinates, %d with no tags] ~%.2fs" % ( lines, self.userMostProbableLocation, self.userHomeCoordinates, self.nullCoordinates, self.noTags, (t2-t1)*1.0 )
		# compute the average of the statistics
		print >> sys.stderr, "---"
		for k in self.limits:
			p = float(self.stats[k])/lines*100
			print >> sys.stderr, "*> [TestSet] %d videos (%.2f%s) <= %dkm" % (self.stats[k], p, '%', k)
		# close test file
		self.TestFile.close()


	''' Write the formatted output for the official run '''
	def serializeFormatted( self, resCandidates, filename, url ):
		buff = ""
		for res in resCandidates.getSortedList():
			candCoo = res.getCoord()
			fn = filename.replace('.xml', '').replace('.mp4', '')
			# run#;groupname;filename;latitue;longitude
			print >> sys.stdout, "%s;%s;%s;%f;%f;%s" % (self.runNr, self.groupname, filename, res.getLat(), res.getLon(), url)
			break

	def serialize( self, resCandidates, realCoord, methodUsed="" ):
		# for each results compute the haversine distance
		buff = ""
		# Printing output information about this test video
		print >> sys.stdout, "* %s used [%s, %s] => %d result(s)" % ( methodUsed, realCoord[0], realCoord[1], resCandidates.size() )
		# results = [ rank, [lat,lon], "tags" ]
		cnt = 0
		for res in resCandidates.getSortedList():
			pred = res.getCoord()
			d = haversine( realCoord, pred )
			buff += str(res.getScore()) +"|"+ str(d) +"\t"
			# Print output info
			print >> sys.stdout, "\t res[%d]: %f|%f(km)|real:(%f,%f)|estim:(%f,%f)|%s" % (cnt, res.getScore(), d, realCoord[0], realCoord[1], res.getLat(), res.getLon(), res.getText())
			# update the statistics just for the first match
			if cnt == 0:
				for k in self.limits:
					#print >> sys.stderr, d, "<?>", k
					if d <= k:
						self.stats[k] += 1
				# if no verbose, break
				if not self.verbose:
					break
			# update the result counter
			cnt += 1


#-----------------------------------------
"""	Print information in case of wrong input """
def print_help():
	#~ if the input parameters are not correct
  print >> sys.stderr, "\t Usage: python "+sys.argv[0]+" <train_set.txt> <test_set.txt> > <outputFile.txt>"
  print >> sys.stderr, "\t e.g. python systemTagsBasedLocationRecognition.py dataset/flickrVideosTrain_ok.txt dataset/flickrVideosTest_10_geo.txt  >  prova"
  sys.exit(1)	
#-----------------------------------------
""" Checking the arguments in input """
if len(sys.argv) < 3:
	print_help()
else:
	trainFilePath = sys.argv[1]
	testFilePath = sys.argv[2]
#-----------------------------------------

# Read global variables
import ConfigParser
config = ConfigParser.RawConfigParser()
config.read('mediaeval.cfg')

userPlacesFilePath = config.get('systemTagsBasedLocationRecognition', 'userplacesfilepath')
geoNamesFilePath = config.get('systemTagsBasedLocationRecognition', 'geonamesfilepath')
topn = config.getint('systemTagsBasedLocationRecognition', 'topn')
multithread = config.getboolean('systemTagsBasedLocationRecognition', 'multithread')
contentBasedResultsFilePath = config.get('systemTagsBasedLocationRecognition', 'contentBasedResultsFilePath')
dizFilePath = config.get('systemTagsBasedLocationRecognition', 'dictionaryFilePath')

verbose = config.getboolean('systemTagsBasedLocationRecognition', 'verbose')
officialRun = config.getboolean('systemTagsBasedLocationRecognition', 'officialrun') # True if the results have to be in the final format
runNr = config.get('systemTagsBasedLocationRecognition', 'runNr')
groupname = config.get('systemTagsBasedLocationRecognition', 'groupname')

selectCoordMethod = config.get('systemTagsBasedLocationRecognition', 'selectCoordMethod') # byFrequency byBiggestGroupOnTopScore byKMeans byYaelKMeans
scoreMetric = config.get('systemTagsBasedLocationRecognition', 'scoreMetric') # frequency binaryMax binaryMin trevi
matchingType = config.get('systemTagsBasedLocationRecognition', 'matchingType') # perfect partial
distanceKmThreshold = config.getint('systemTagsBasedLocationRecognition', 'distanceKmThreshold') 

if officialRun:
	print >> sys.stderr, "\t FORMATTED OUTPUT FOR OFFICIAL RUN"
	print >> sys.stderr, "---"
print >> sys.stderr, "*> Multi-Threading:", multithread
# Create the object and load the input file
cl = TagsProcessing( testFilePath, verbose, topn, selectCoordMethod, scoreMetric, matchingType, distanceKmThreshold, runNr, groupname )

# Load users commonest places
cl.prepareUsersCommonestPlaces( userPlacesFilePath )

# Load Filename-Coordinates dictionary
# output: [filename(or imageId)] -> [lat,lon]
cl.prepareFilenameCooDiz(dizFilePath)
# Load Content-Based Results Candidates
cl.prepareContentBasedResultsCandidates(contentBasedResultsFilePath)

# EXTERNAL RESOURCES - Gazetteer, etc.
# cl.prepareGeoNamesFilter( geoNamesFilePath )

# Load all the tags as key
cl.prepareTrainingSet( trainFilePath )

withMtags = False
# Evaluate Test Videos
if multithread:
	cl.parseTestVideosMT() # multithread
else:
	cl.parseTestVideos( withMtags, officialRun )




