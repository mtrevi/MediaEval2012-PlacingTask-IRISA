#!/bin/env python
# -*- coding: utf-8 -*-
'''
Created on May 2, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
import os
from geoUtils import getGeoDataFromImageMeta, clean_line

#-----------------------------------------
"""	Print information in case of wrong input """
def print_help():
	#~ if the input parameters are not correct
  print "\t Usage: cat <flickr-images-meta.txt> | python "+sys.argv[0]+"  > <flickrImagesMeta.txt>"
  sys.exit(1)	
#-----------------------------------------
""" Checking the standard input """
if not sys.stdin:
	print_help()
#-----------------------------------------

# example of input line:
#10012147@N04/3893830426 : http://farm4.static.flickr.com/3468/3893830426_cdb64a0876.jpg : GeoData[longitude=11.009545 latitude=45.43996 accuracy=14] : glass yellow restaurant lomo lomography verona lea  : 1249565412000 : 1252260976000
# 0: user/photoId
# 1: url
# 2: geoData
# 3: tags
# 4: timestamp
# 5: timestamp

# example of output line:
#4876969322	Boats on The Thames at Penton Hook Lock	http://www.flickr.com/photos/37413900@N04/4876969322/	thames pleasure boats penton hook lock gates laleham staines surrey barge	51.414745|-0.500274|16|Staines|Surrey|Angleterre|Royaume Uni|16	37413900@N04|Greater London, England United Kingdom
# 0: imageId
# 1: Title
# 2: url
# 3: tags
# 4: coordinates
# 5: userId|hometown

totLines = 3185258.0
lines = 0
print >> sys.stderr, "*> Convert Images MetaData",
for line in sys.stdin:
	lines += 1
	blk = line.strip().split(" : ")
	usrId, imgId = blk[0].split( "/" )
	title = ""
	url = blk[1]
	lat, lon, acc = getGeoDataFromImageMeta( blk[2] )
	coord = lat +"|"+ lon +"|"+ acc 
	tags = clean_line( blk[3] )
	print >> sys.stdout, "%s\t%s\t%s\t%s\t%s\t%s" % (imgId.encode('utf-8'), title, url.encode('utf-8'), tags.encode('utf-8'), coord.encode('utf-8'), usrId.encode('utf-8'))
	if lines % 200000:
		print >> sys.stderr, "\r*> Converting Images MetaData [%2.2f%s]" % ( float(lines)/totLines*100, '%'),
print >> sys.stderr, "\r*> Converting Images MetaData: %d lines" % lines

