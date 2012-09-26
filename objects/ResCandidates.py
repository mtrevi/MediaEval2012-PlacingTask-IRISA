# -*- coding: utf-8 -*-
'''
Created on May 29, 2012
michele (.) trevisiol (at) google (.)com
@author: trevi
'''

import sys
from geoUtils import clean_line, tagsfilters

class ResCandidates():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.candidates = [] # list of candidates
    
    def addObj(self, CoordCandidate):
      self.candidates.append( CoordCandidate )
    
    def add(self, score, coord, text):
      cand = CoordCandidate( score, coord, text )
      self.candidates.append( cand )
    
    def size(self):
      return len(self.candidates)

    def getList(self):
      return self.candidates

    '''
      Sorting Function
    '''
    def getSortedList(self):
      return sorted(self.candidates, reverse=True)
    
    def getTopValues(self):
      tmpL = sorted(self.candidates, reverse=True)
      tmpScore = tmp
      
    def getTopCandidate(self):
      return sorted(self.candidates, reverse=True)[0]


class CoordCandidate():
    '''
        Define the object candidate containing the candidate [lat,lon]
    '''

    def __init__(self, score=-1.0, coord=[0.0,0.0], tags=""):
        '''
        Constructor
        '''
        self.score = score # float
        self.coord = coord # [float, float]
        self.tags = tags # str

    ''' 
      Set functions 
    '''
    def setScore(self, score):
      self.score = score
      
    def setCoord(self, lat, lon):
      self.coord = [ float(lat), float(lon) ]
    
    def setCoord(self, coord):
      self.coord = coord
    
    def setText(self, text):
      self.tags = text

    ''' 
      Get functions 
    '''
    def getScore(self):
      return self.score
    
    def getCoord(self):
      return self.coord
    
    def getLat(self):
      return self.coord[0]
    
    def getLon(self):
      return self.coord[1]
    
    def getCoordStr(self):
      return str(self.coord[0]) +","+ str(self.coord[1])
    
    def getText(self):
      return self.tags.encode("UTF-8")
    
    

class MatchCandidates():
    '''
    classdocs
    '''

    def __init__(self):
        '''
        Constructor
        '''
        self.matches = {} # groupOfTags -> score
    
    def update(self, key, val=1):
      # check if the doesn't exist
      if not self.matches.has_key( key ):
        self.matches[key] = 0
      # update the score
      self.matches[key] += val
    
    def size(self):
      return len(self.matches)
    
    def getKeys(self):
      return self.matches.keys()

    def getValue(self, key):
      return self.matches[key]

    def getKeysWithGivenScores(self, scores):
      keys = []
      minScore = min(scores)
      for k in self.matches.keys():
        if self.matches[k] >= minScore:
           keys.append(k)
      return keys

    def getTopNScores(self, topn):
      ''' Return the topn results with the higher score '''
      if len(self.matches) == 0:
        return [-1]
      # save all the different scores into a list
      scores = []
      for k in self.matches:
        if self.matches[k] not in scores:
          scores.append( self.matches[k] )
      # sorting the list
      sortedList = sorted( scores, reverse=True )
      # get the topn higher scores
      ress = []
      for i in range(0, min(topn, len(scores)) ):
        ress.append(sortedList[i])
      return ress

    def getTopScore(self):
      sortedList = sorted(self.matches, key=self.matches.get, reverse=True)
      if len(sortedList) > 0:
        return sortedList[0]
      else:
        return -1
    
    def getSortedScores(self):
      return sorted(matches, key=matches.get, reverse=True)

    def computeScores(self, scoreMetric, nrTags=1):
      for key in self.matches:
        # 0 METHOD: "frequency"
        if scoreMetric == 'frequency': 
          continue
          self.matches[key] = float(self.matches[key])
        # 1st METHOD
        elif scoreMetric == 'trevi':
          nrTrainTags = len(key.split(" "))
          self.matches[key] = float(self.matches[key])/nrTrainTags * float(self.matches[key])/nrTags
        # 2nd METHOD: "binary overlap with MAX instead of min"
        elif scoreMetric == 'binaryMax':
          nrTrainTags = len(key.split(" "))
          self.matches[key] = float(self.matches[key])/max(nrTags,nrTrainTags)
        # 2nd METHOD: "binary overlap with MAX instead of min"
        elif scoreMetric == 'binaryMin':
          nrTrainTags = len(key.split(" "))
          self.matches[key] = float(self.matches[key])/min(nrTags,nrTrainTags)
        # remove the matching if it is lower than 0.2
#        if len(got) < 2:
#          del(matches[got])
#          continue
        # remove the smallest values
#        if matches[got] < 0.1:
#          del(matches[got])
#          continue



class TestItem():
	''' Parsing the line of the Test Video '''
	def __init__(self, line, tag2code, withMTags=False):
		blk = line.strip().split("\t")
		# get the tagsStr
		self.id = int( blk[0] )
		if withMTags:
			self.codes = self.saveTags( blk[3], tag2code )
			self.mcodes = self.saveTags( blk[4], tag2code )
			self.coo = self.saveCoordiantes( blk[5].strip() )
		else:
			self.codes, self.mcodes = self.saveRawTags( blk[3], tag2code )
			self.coo = self.saveCoordiantes( blk[4].strip() )
		self.ownId, self.ownTown, self.ownTownTags = self.saveOwnerInfo( blk[ len(blk)-1 ].strip(), tag2code )

	def saveRawTags(self, strTags, tag2code):
		codeList = []
		mCodeList = []
		# filterTags
		tags, mtags = tagsfilters( strTags.strip() ) 
		# check if tag exists and save the id
		for t in tags.split(" "):
			if len(t) > 1:
				if tag2code.has_key( t ):
					print t, tag2code[t]
					codeList.append( tag2code[t] )
		# check if machine-tag exists and save the id
		for mt in mtags.split(" "):
			if len(mt) > 1:
				if tag2code.has_key( mt ):
					mCodeList.append( tag2code[mt] )
		return codeList, mCodeList

	def saveTags(self, strTags, tag2code):
		codeList = []
		tagStrList = strTags.split(" ")
		for tstr in tagStrList:
			tstr = clean_line( tstr )
			# check if the tag exist
			if tag2code.has_key( tstr ):
				codeList.append( tag2code[tstr] )
		return codeList

	def saveCoordiantes(self, location):
		''' Read Real Location: "45.516639|-122.681053|16|Portland|Oregon|etats-Unis|16 '''
		return [float(location.split("|")[0]), float(location.split("|")[1])]

	def saveOwnerInfo(self, ownStr, tag2code):
		''' Owner location: ['14678786@N00', 'milwaukee, United States'] '''
		hometown = []
		hometownTags = []
		blk = ownStr.split("|")
		if len(blk) > 1:
			for hw in ownStr.split("|")[1].split(","):
				hw_clear = clean_line(hw)
				hometown.append( hw_clear )
				if tag2code.has_key( hw_clear ):
					hometownTags.append( tag2code[hw_clear] )
		return ownStr.split("|")[0], hometown, hometownTags

	def getId(self):
		return self.id

	def getCoo(self):
		return self.coo

	def getOwnId(self):
		return self.ownId

	def getOwnTown(self):
		return self.ownTown

	def hasOwnTownTags(self):
		if len(self.ownTownTags) > 1:
			return True
		else:
			return False

	def getOwnTownTags(self):
		return self.ownTown

	def getOwnTownTagsCode(self):
		return self.ownTownTags

	def getTagsString(self, code2tag):
		out = ""
		for c in self.codes:
			out += code2tag[c] +" "
		return out[:-1].encode('utf-8', 'ignore')

	def getMTagsString(self, code2tag):
		out = ""
		for mc in self.mcodes:
			out += code2tag[mc] +" "
		return out[:-1].encode('utf-8', 'ignore')

	def getCodeString(self, fillZeros=0):
		out = ""
		# Convert tags codes to string
		for c in self.codes:
			out += str(c) +" "
		# fill with -1 if there are not enough tags
		if (fillZeros-len(self.codes)) > 0:
			for i in range(0,fillZeros-len(self.codes)):
				out += "-1 "
		return out[:-1]

	def getAllCodeString(self, fillZeros=0):
		out = ""
		# Convert tags codes to string
		for c in self.codes:
			out += str(c) +" "
		# Convert mtags codes to string
		for mc in self.mcodes:
			out += str(mc) +" "
		# fill with -1 if there are not enough tags
		totTags = len(self.codes) + len(self.mcodes)
		if (fillZeros-totTags) > 0:
			for i in range(0,fillZeros-totTags):
				out += "-1 "
		return out[:-1]

	def getTagsCode(self):
		return self.codes

	def getMTagsCode(self):
		return self.mcodes

	def getTagsEnc(self, code2tag):
		tags = []
		for c in self.codes:
			tags.append( code2tag[c].encode('utf-8', 'ignore') )
		return tags

	def getMTagsEnc(self, code2tag):
		mtags = []
		for mc in self.mcodes:
			mtags.append( code2tag[mc].encode('utf-8', 'ignore') )
		return mtags

	def hasTags(self):
		return True if len(self.codes) > 0 else False

	def hasMTags(self):
		return True if len(self.mcodes) > 0 else False
	
	

class MatlabItem():
	''' Parsing the line of the Matlab Results:
			4558143542,9699:0.375882,16686:0.373681,20310:0.364020
	'''
	def __init__(self, line):
		info = line.strip().split("\t")
		blk = info[1].split(",") if len(info) > 1 else ""
		self.imgId = int( info[0] )
		self.bot = [] # list of [ (score,botId), .. ]
		self.saveMatlabResults( blk ) # candidates BoT
		self.sortBoT() # sort in descending order the candidates

	def saveMatlabResults(self, blk):
		for i in range(0,len(blk)):
			botScore = blk[i].split(":")
			self.bot.append( (float(botScore[1]), int(botScore[0])) )

	def sortBoT(self):
		self.bot.sort()
		self.bot.reverse()





