#!/bin/env python
# -*- coding: utf-8 -*-
'''
Created on May 2, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import time
import sys
from geoUtils import haversine, tagsfilters, geographicTagsFiltering, loadGeoNamesSplittingKeys, loadStopword, clean_line, serializeGeoNamesFilterDB, loadGroupOfTagsFromConvertedFile, serializeTrainSetDB


#-----------------------------------------
"""	Print information in case of wrong input """
def print_help():
	#~ if the input parameters are not correct
  print >> sys.stderr, "\t Usage: python "+sys.argv[0]+" <train_set.txt> <geoNames.txt> <test_set.txt> > <outputFile.txt>"
  print >> sys.stderr, "\t e.g. python convertDatasetsIntoDBformat.py dataset/bak/flickrVideosTrain_ok.txt dataset/flickrVideosTrain_db extra/allCountries.txt extra/allCountries_db dataset/bak/flickrVideosTest_10_geo.txt dataset/flickrVideosTest_db"
  sys.exit(1)	
#-----------------------------------------
""" Checking the arguments in input """
if len(sys.argv) < 4:
	print_help()
else:
	inFile = sys.argv[1]
	outFile = sys.argv[2]
	typefile = sys.argv[3]
#-----------------------------------------

print >> sys.stderr, "Processing %s" % typefile

if typefile == 'geonames':
	# Read GeoNames
	GeoNames, GeoNamesIndex = loadGeoNamesSplittingKeys( inFile )
	# Specify which filter use
	serializeGeoNamesFilterDB( GeoNames, GeoNamesIndex, outFile )
elif typefile == 'trainset':
	# Read train set
	TrainTagCoord, TrainTagIndex = loadGroupOfTagsFromConvertedFile( inFile )
	# Serialize train set 
	serializeTrainSetDB( TrainTagCoord, TrainTagIndex, outFile )





