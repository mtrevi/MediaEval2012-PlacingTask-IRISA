# -*- coding: utf-8 -*-
'''
Created on May 29, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
from geoUtils import *

class FlickrMediaDataList():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.flickrset = [] # list of flickrMediaData object
    
    def addObj(self, flickrMediaData):
      self.flickrset.append( flickrMediaData )
        
    def size(self):
      return len(self.flickrset)

    def getList(self):
      return self.flickrset

    '''
      Sorting Function
    '''
    def getSortedList(self):
      return sorted(self.flickrset, reverse=True)
    


class FlickrMediaData():
    '''
        Define the object candidate containing the candidate [lat,lon]
    '''

    def __init__(self, line, sep="\t"):
        '''
        Constructor
        '''
        # videoId <t> title <t> url <t> tags <t> mtags <t> location <t> ownerLocation
        # location e.g. '-32.959093|-60.623738|Argentina|Santa Fe|Rosario', 
        # ownerLocation e.g. '39556080@N00|Rosario, Argentina'
        b = clean_line( line ).split(sep)
        
        self.id = b[0] # int
        self.title = b[1] # str
#        self.url = b[2] # str
        self.tags = b[3] # str
        self.mtags = b[4] # str
        self.setCoordFromStr( b[5] ) # [lon, lon]
        self.setOwnCoordFromStr( b[6] )
        
        self.gotFloatOwnCoord = False

    ''' 
      Set functions 
    '''
    def setId(self, id):
      self.id = score
    
    def setTitle(self, title):
      self.title = title  
    
    def setTags(self, tags):
      self.tags = tags
    
    def setMtags(self, mtags):
      self.mtags = mtags
    
    def setCoord(self, lat, lon):
      self.coord = ( float(lat), float(lon) )
    
    def setCoord(self, coord):
      self.coord = coord
      
    def setCoordFromStr(self, coordStr ):
      lat = coordStr.split("|")[0]
      lon = coordStr.split("|")[1]
      self.coord = ( float(lat), float(lon) )
    
    def setOwnCoord(self, lat, lon):
      self.ownCoord = [ float(lat), float(lon) ]
      self.gotFloatOwnCoord = True
    
    def setOwnCoord(self, ownCoord):
      self.ownCoord = ownCoord
    
    def setOwnId(self, ownId):
      self.ownId = ownId
    
    def setOwnCoordFromStr(self, ownLocation):
      ownCoordStr = ownLocation.split("|") # str
      self.ownId = ownCoordStr[0]
      if len(ownCoordStr) > 1:
        self.ownCoord = ownCoordStr[1] # str or [lat, lon]
      else:
        self.ownCoord = ""

    ''' 
      Get functions 
    '''
    def getId(self):
      return self.id
    
    def getCoord(self):
      return self.coord
    
    def getLat(self):
      return self.coord[0]
    
    def getLon(self):
      return self.coord[1]
    
    def getOwnCoord(self):
      if self.gotFloatOwnCoord:
        return self.ownCoord
      else:
        return -1.0
    
    def getOwnLat(self):
      if self.gotFloatOwnCoord:
        return self.ownCoord[0]
      else:
        return -1.0
    
    def getOwnLon(self):
      if self.gotFloatOwnCoord:
        return self.ownCoord[1]
      else:
        return -1.0
    
    def getCoordStr(self):
      return str(self.coord[0]) +","+ str(self.coord[1])
    
    def getOwnCoordStr(self):
      if self.gotFloatOwnCoord:
        return str(self.ownCoord[0]) +","+ str(self.ownCoord[1])
      else:
        return self.ownCoord
    
    def getTags(self):
      return self.tags.encode("UTF-8")
    
    def getTagsList(self):
      tlist = []
      T = self.tags.split(" ")
      for t in T:
        if t not in tlist:
          tlist.append(t)
      return tlist
    
    def getMtags(self):
      return self.mtags.encode("UTF-8")
    
    def getMtagsList(self):
      mtlist = []
      MT = self.mtags.split(" ")
      for mt in MT:
        if mt not in mtlist:
          mtlist.append(mt)
      return mtlist




    