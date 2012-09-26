#!/bin/env python
# -*- coding: utf-8 -*-
'''
Created on May 2, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import time
import sys
import re
import os

from xml.dom.minidom import parse, parseString
#from django.utils.encoding import smart_str
from geoUtils import clean_line

class XmlProcessing:
	
	def __init__( self, videoFilePath ):
		self.VFname = videoFilePath
		self.VFile = file( videoFilePath, 'r' )
		self.VBuffer = ""

	def filtering( self ):
		stopLines = [ "<UserName>", "<RealName>", '</RealName>' ]
		startWords = [ "<Contacts>", "Comments>" ]
		stopWords = [ "</Uploads>", "</Comments>", '</Description>' ]
		removing = False
		# start line parser
		for line in self.VFile:
			# filter entire line
			if self.isThereAMatch( stopLines, line ):
				continue

			if '<Description>' in line:
				if '</Description>' in line:
					continue
				else:
					removing = True
			# if we have to start filtering out
			for start in startWords:
				if start in line:
					removing = True
			
			# if we do not have to remove => copy
			if not removing:
				# filtering XML error as <[0-9]+>
				newL = re.sub("(<[0-9]*[a-f]*[0-9]*>)", "", line)
				self.VBuffer += newL#clean_line( newL, True )

			for stop in stopWords:
				if stop in line:
					removing = False

	def isThereAMatch( self, list, line ):
		for w in list:
			if w in line:
				return True

	def loadingVideo( self ):
		#print >> sys.stderr, "Parsing XML file in memory"
		try:
			# parse xml file
			vxml = parseString( self.VBuffer )
			cnt = 0
			vInfo = {}
			#for video in vxml.getElementsByTagName('Video'): 
			vInfo['videoId'] = vxml.getElementsByTagName('VideoID')[0].firstChild.data.strip()
			vInfo['title'] = vxml.getElementsByTagName('Title')[0].firstChild.data.strip()
			vInfo['url'] = vxml.getElementsByTagName('WatchLink')[0].firstChild.data.strip()
			# Try to extract the tags
			try:
				vInfo['tags'] = vxml.getElementsByTagName('Keywords')[0].firstChild.data.replace(",", "").strip()
			except:
				print >> sys.stderr, "NO TAGS for video: %s" % self.VFname
				vInfo['tags'] = ""
			#vInfo['description'] = vxml.getElementsByTagName('Description')[0].firstChild.data.strip()
			try:
				# Parse Location (lat,lng,region,locality,country)
				lat = vxml.getElementsByTagName('Latitude')[0].firstChild.data.strip()
				lng = vxml.getElementsByTagName('Longitude')[0].firstChild.data.strip()
				ctr = vxml.getElementsByTagName('Country')[0].firstChild.data.strip()
				reg = vxml.getElementsByTagName('Region')[0].firstChild.data.strip()
				loc = vxml.getElementsByTagName('Locality')[0].firstChild.data.strip()
				vInfo['videolocation'] = lat +"|" + lng +"|" + ctr +"|" + reg +"|" + loc
			except:
				vInfo['videolocation'] = ""
			# retrieve owner information
			userXml = vxml.getElementsByTagName('User')
			for user in userXml:
				alist = user.getElementsByTagName('UserID')
				for a in alist:
					userId = a.firstChild.data
				alist = user.getElementsByTagName('Location')
				for a in alist:
					userHome = a.firstChild.data
			vInfo['user'] = userId +"|"+ userHome
			self.serialize( vInfo )
		except:
			print >> sys.stderr, "* Unexpected error:", sys.exc_info()[0]
			print >> sys.stderr, "ERROR! on file:", self.VFname
			raise

	def serialize( self, vInfo ):
		filenameBlk = self.VFname.split("/")
		filename = filenameBlk[len(filenameBlk)-1]
		if len(vInfo['videolocation']) > 1:
			vbuffer = "%s\t%s|%s\t%s\t%s\t%s\t%s" % (vInfo['videoId'], filename, vInfo['title'], vInfo['url'], vInfo['tags'], vInfo['videolocation'], vInfo['user'])
#			vbuffer = vInfo['videoId'].strip() +"\t"+ vInfo['title'].strip() +"\t"+ vInfo['url'].strip() +"\t"+ vInfo['tags'].strip() +"\t"+ vInfo['videolocation'].strip() +"\t"+ vInfo['user'].strip()
		else:
			vbuffer = "%s\t%s|%s\t%s\t%s\t%s" % (vInfo['videoId'], filename, vInfo['title'], vInfo['url'], vInfo['tags'], vInfo['user'])
#			vbuffer = vInfo['videoId'].strip() +"\t"+ vInfo['title'].strip() +"\t"+ vInfo['url'].strip() +"\t"+ vInfo['tags'].strip() +"\t"+ vInfo['user'].strip()
		import unicodedata
		unicodedata.normalize('NFKD', vbuffer).encode('ascii','ignore')
		print >> sys.stdout, vbuffer.encode('utf8', 'ignore')

	def close( self ):
		self.VFile.close()

#-----------------------------------------
"""	Print information in case of wrong input """
def print_help():
	#~ if the input parameters are not correct
  print "\t Usage: python "+sys.argv[0]+" <video.xml> >> <allVideoInTxtFormat.txt>"
  sys.exit(1)	
#-----------------------------------------
""" Checking the arguments in input """
if len(sys.argv) < 2:
	print_help()
else:
	videoFilePath = sys.argv[1]
#-----------------------------------------

# Create the object and laod the input file
#print >> sys.stderr, "* parsing", videoFile
cl = XmlProcessing( videoFilePath )
# Load all the tags as key
cl.filtering()
cl.loadingVideo()
# Close the opened files
cl.close()
