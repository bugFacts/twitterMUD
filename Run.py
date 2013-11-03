import twitter, os
import time
import sys, traceback
import Interactor
from collections import deque
from RosterMaker import *

############### LOGIN #################################

TOKEN = r'P:\python_twitter\scrips\DungeonMaster\token\dmtestCodes.txt'
tokens= []
with open(TOKEN, 'r') as fp:
	ftokens = fp.readlines()
	
for i in ftokens:
	tokens.append(i.strip())

api=twitter.Api(consumer_key = tokens[0],
				consumer_secret = tokens[1],
				access_token_key= tokens[2],
				access_token_secret= tokens[3]) 
############### LOGIN #################################
				
QFILE = r'P:\python_twitter\scrips\DungeonMaster\savefiles\savedQ.txt'
DFILE = r'P:\python_twitter\scrips\DungeonMaster\savefiles\doneList.txt'

#load action Q
def rebuild(TEXTFILE):
	textFileList = deque()
	try:
		with open(TEXTFILE, 'r') as fp:
			fload = fp.readlines()
		
		for item in fload:
			if item.strip() == '':
				continue
			textFileList.append(long(item))
	except Exception:
		print "nothing read from file!!"
	return textFileList
		
def amendQfromTwitter(actionQ,debug=False):
	KnownCommands = [
					'?start',
					'?name',
					'?xp',
					'?gear',
					'?hp',
					'?loc',
					]
					
	mentionList = deque()
	if not debug:
		mentionList = api.GetMentions()
	else:
		print "debug mode preventing mention grab from twitter"
		
	if mentionList:
		for tweet in mentionList:
			# print tweet.text
			if (
				any(word in KnownCommands for word in tweet.text.split(' ') ) and
				tweet.id not in actionQ
				):
				
				print "action present!", tweet.text
				actionQ.append(tweet.id)
				
	return actionQ

def saveList(slist, TEXTFILE):
	with open(TEXTFILE, 'w') as fp:
		fp.write('\n'.join(['%s' % (str(i)) for i in slist]))

		
#########################################################
# 				 LET'S ROLL MOTHERFUCKER				#
#########################################################

debug = False
############ load everything ################
actionQ = rebuild(QFILE)					#
actionQ = amendQfromTwitter(actionQ,debug)	#
############ load everything ################

KnownCommands = [
				'?start',
				'?name',
				'?xp',
				'?gear',
				'?hp',
				'?loc',
				]
					
# print "actionQ= ", actionQ

limit = len(actionQ)

while actionQ and limit:
	resolvedList = rebuild(DFILE)		#load done list from file
	impetusID = actionQ.popleft()		#grab first item from Q
	
	try:
		responseTweet = ''
		#DISCARD IF:
		if impetusID in resolvedList:
			print "tweet in resolvedList"
			print "tweet text: %s" % (api.GetStatus(id = impetusID).text)
			print "tweet id: %i" % (impetusID)
		else:
			if not debug:
				print "tweet passed checks! sending to Interactor!"
				impetusTweet = api.GetStatus(id = impetusID)
				responseTweet = Interactor.parseTweet(impetusTweet)
			else:
				print "debug mode is preventing Interactor from being called\n"
				print "putting impetusID back at top of deck"
				actionQ.appendleft(impetusID)
				saveList(resolvedList,DFILE)
		
	except Exception:
		#put back in Q if we fuck up
		#for example, exceeding rate limits t(-_-t) 
		print "error. putting tweet at back of Q"
		actionQ.append(impetusID)
		traceback.print_exc(file=sys.stdout)

	if responseTweet:
		twit_name = impetusTweet.user.screen_name
		if not debug:
			try:
				api.PostUpdate('@%s %s' % (twit_name, responseTweet), in_reply_to_status_id=impetusID)
				resolvedList.append(impetusID)		
				saveList(resolvedList,DFILE)
			except Exception:
				#this will happen if internet is down
				#or we exceeded rate limit
				#or we are duplicating messages (which propbably only happens when the doneList gets fuck up)
				#so lets put tweet at back of Q to try again later
				# actionQ.append(impetusID)
				#lets call it done for now
				resolvedList.append(impetusID)		
				saveList(resolvedList,DFILE)
				#traceback.print_exc(file=sys.stdout)
			
	
	limit -= 1
	############ save everything ################
	saveList(actionQ,QFILE)						#
	############ save everything ################



		
#do action
#clean up action Q