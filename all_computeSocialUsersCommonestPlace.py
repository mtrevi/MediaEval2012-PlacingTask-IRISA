#!/bin/env python
# -*- coding: utf-8 -*-
'''
Created on -, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
from geoUtils import clean_line, getGeoDataFromConvertedFile


''' Load the user common location(s) into a dictionary '''
def loadUserLocations( usersLocationFilePath, totUsers ):
	print >> sys.stderr, "*> Loading Users Commonest Places",
	inputFile = usersLocationFile = file( usersLocationFilePath, 'r' )
	UserPlaces = {}
	users = 0
	# usrId <tab> lat,lon,acc,freq|lat,lon,..|...
	for line in inputFile:
		users += 1
		blk = line.strip().split( "\t" )
		uId = blk[0].lower()
		# adding new users
		if not UserPlaces.has_key( uId ):
			UserPlaces[uId] = []
		# parsing the coordinates
		CoordFreqStrList = blk[1].split( "|" )
		for coordFreqStr in CoordFreqStrList:
			coordFreq = coordFreqStr.split( "," )
			lat = float( coordFreq[0] )
			lon = float( coordFreq[1] )
			acc = int( coordFreq[2] )
			freq = int( coordFreq[3] )
			UserPlaces[uId].append( [lat, lon, acc, freq] )
		# print info
		if users % 1000:
			print >> sys.stderr, "\r*> [UserPlaces] parsed %d [%2.2f%s]" % ( users, float(users)/totUsers*100, '%'),
	print >> sys.stderr, "\r*> [UserPlaces] %d total users [%2.2f%s]" % (len(UserPlaces), float(users)/totUsers*100, '%')
	inputFile.close()
	return UserPlaces

''' Loading users social connection -> if they didn't have a common location, 
	get the common location of its connection and write them as output '''
def updateUsrPlacesDiz( UserPlaces, usersSocialFilePath, totLines ):
	print >> sys.stderr, "*> Computing Users Social Commonest Places",
	inputFile = usersLocationFile = file( usersSocialFilePath, 'r' )
	lines = 0
	usrNoInfo = 0
	# usrId <tab> usrId:score usrId:score ... (score: 0:contact, 1:friend, 2:family, 3:friend+family)
	for line in inputFile:
		lines += 1
		blk = line.strip().split( "\t" )
		usrId = blk[0].lower()
		if UserPlaces.has_key(usrId) or len(blk) == 1:
			continue
		# load the social graph
		connections = blk[1].split(" ")
		highScore = 0
		sg = {}
		for conn in connections:
			conId = conn.strip().split(":")[0].lower()
			score = int(conn.strip().split(":")[1])
			# select the higher score (if there are family member, we will consider only them)
			if score > highScore:
				highScore = score
			# add connection Id to the list of the relative score
			if not sg.has_key(score):
				sg[score] = []
			# retrieve the common location for this connection Id
			if UserPlaces.has_key(conId):
				for CooFreq in UserPlaces[conId]:
					sg[score].append( CooFreq )
		# Update UserPlaces with the new info of this user
		if len(sg[highScore]) > 0:
			UserPlaces[usrId] = sg[highScore]
		else:
			usrNoInfo += 1
		# print info
		if lines % 500:
			print >> sys.stderr, "\r*> Computing Users Social Commonest Places [%2.2f%s]" % ( float(lines)/totLines*100, '%'),
	print >> sys.stderr, "\r*> Computing Users Social Commonest Places: %d lines [%2.2f%s] -> %d users with no info" % (lines, float(lines)/totLines*100, '%', usrNoInfo)
	inputFile.close()
	return UserPlaces
			
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
	print >> sys.stderr, "\t Usage: python "+sys.argv[0]+" <users_commonest_places_2012.txt> <users_social_connections_2012.txt>  >  <users_social_commonest_places.txt>"
	sys.exit(1)	
#-----------------------------------------
""" Checking the arguments in input """
if len(sys.argv) < 3:
	print_help()
else:
	usersLocationFilePath = sys.argv[1]
	usersSocialFilePath = sys.argv[2]
#-----------------------------------------


# Parsing User Common Location: usrId -> [ [lat1,lon1,acc1,freq1], [lat2,lon2,acc2,freq2], ... ]
UsersPlaces = loadUserLocations( usersLocationFilePath, 71240 )

# Parsing User social connections and compute its common location (if it's not already present)
UsersPlaces = updateUsrPlacesDiz( UsersPlaces, usersSocialFilePath, 3840 )

# Write output
serializeUsrPlacesDiz( UsersPlaces )