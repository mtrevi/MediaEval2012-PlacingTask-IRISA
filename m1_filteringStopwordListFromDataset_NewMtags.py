#!/bin/env python
# -*- coding: utf-8 -*-
'''
Created on -, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
from geoUtils import loadStopword, clean_line, tagsfilters

#-----------------------------------------
def print_help():
	"""	Print information in case of wrong input """
	#~ if the input parameters are not correct
	print >> sys.stderr, "\t Usage: cat <input_set.txt> | python "+sys.argv[0]+" <stopword_list.txt>  >  <input_set_swfMtags.txt>"
	print >> sys.stderr, "\t e.g. cat dataset/flickrVideosTrain_ok.txt | python filteringStopwordListFromDataset.py extra/all_stopword_lists.txt > dataset/flickrVideosTrain_ok_swf.txt "
	sys.exit(1)	
#-----------------------------------------
""" Checking the arguments in input """
if len(sys.argv) < 2:
	print_help()
else:
	stopwordsFilePath = sys.argv[1]

#-----------------------------------------

# Loading Stopword
stopwordFile = file( stopwordsFilePath, 'r' )
stopworddiz = loadStopword( stopwordFile )

print >> sys.stderr, "*> [InputSet] Parsing tags",
lines = 0
#totLines = 10152.0
totLines = 3195410.0
for line in sys.stdin:
	lines += 1
	# blk = ['2408552791', 'La electricidad est\xc3\xa1tica', 'http://flickr.com/photos/39556080@N00/2408552791',
	# 'museo pelos pelo carina van de graaff', '-32.959093|-60.623738|Argentina|Santa Fe|Rosario', '39556080@N00|Rosario, Argentina']
	blk = clean_line( line ).split("\t")
	# Extract tags and mtags
	tags, mtags = tagsfilters( blk[3] )
	tags = tags.strip()
	mtags = mtags.strip()
	
	for tag in tags:
		if len(tag) < 2:
			continue
		# check if it is a stopword
		# for key in stopworddiz.keys():
		# 	if tag in key or key in tag:
		if stopworddiz.has_key(tag):
			continue
		tags += tag +" "
	# clean tags
	tags = tags[:-1]
	# write output
	outstr = ""
	for i in range(0,len(blk)):
		if i == 3:
			outstr += tags +"\t" + mtags +"\t"
		else:
			outstr += blk[i] +"\t"
	# clean outstr
	outstr = outstr[:-1]
	print >> sys.stdout, outstr.encode( 'utf-8', 'ignore')
	# print info
	if (lines % 1000) == 0:
		print >> sys.stderr, "\r*> [InputSet] Parsing %2.2f%s of the file" % ( (lines/totLines*100), '%' ),
# write statistics
print >> sys.stderr, "\r*> [InputSet] %d lines parsed [ %2.2f%s]" % ( lines, (lines/totLines*100), '%' )






