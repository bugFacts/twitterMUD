from __future__ import unicode_literals
import twitter, os
import random
import linecache
import xlrd
import sys
import time
from string import maketrans  
import re
#from map_generator import *
from RosterMaker import *
from CharacterGen import *
from Mapper import *

def initRoster():
	## load the player roster into a dictionary so we can fiddle with it
	roster = Player_Dict().load_from_file()
	return roster
	
def saveRoster(roster):
	## save the modified roaster back into a text file
	Player_Dict().save_to_file(roster)
	
def AddNewPlayer(playerdict,usrName,usrID):
	## add a new player to the roster
	## and give the a bunch of starting gear & info
	
	print "AddNewPlayer called successfully"
	playerdict[usrName] = Player(userName=usrName, userID=usrID, reTime=time.time())
	
	#usrName from twitter
	#usrID from twitter
	#reTime updated
	
	playerdict[usrName].pos_x = 1
	playerdict[usrName].pos_y = 1
	playerdict[usrName].pos_z = 1
	
	playerdict[usrName].xp = 0
	playerdict[usrName].maxhp = random.randint(6,12)
	playerdict[usrName].hp = playerdict[usrName].maxhp
		
	#char_name input by player
	playerdict[usrName].char_class = ClassMaker()
	#char_race not used yet bcuz racism? assign from list?
	
	#char_helm
	playerdict[usrName].char_Chest = 'ripped tunic'
	playerdict[usrName].char_Hand = 'wooden sword'
	#char_Ring
	
	playerdict[usrName].char_inv1 = 'few gold coins'
	#char_inv2
	#char_inv3
	
	#enemy
	
	saveRoster(playerdict)

def ComputeLevel(xp):
	### compute level from xp
	### this way we don't have to store level in the roster explicitly
	### but will need to add a 'level up' check whenever we add xp to the roster
	
	level_list = [ [0,-1],
					[1,0],[2,1000],[3,3000],[4,6000],
					[5,10000],[6,15000],[7,21000],[8,28000],[9,36000],
					[10,45000],[11,55000],[12,66000],[13,78000],[14,91000],
					[15,105000],[16,120000],[17,136000],[18,153000],[19,171000],[20,190000],[21,210000],
					[22,231000],[23,253000],[24,276000],[25,300000],[26,325000],[27,351000],[28,378000],
					[29,406000],[30,435000],[31,465000],[32,496000],[33,528000],[34,561000],[35,595000],
					[36,630000],[37,666000],[38,703000],[39,741000],[40,780000],[41,820000],[42,861000],
					[43,903000],[44,946000],[45,990000],
					[46,1035000],[47,1081000],[48,1128000],[49,1176000],[50,1225000],
				]
	level = None

	if not xp or xp==0 or xp=="None":
		return 0
	else:
		xp = int(xp)
		while not level:
			#print "range: %s" % (len(level_list))
			for tier in range(len(level_list)):
				#print level_list[tier][1]
				if xp > level_list[tier][1]:
					continue
				elif xp <= level_list[tier][1]:
					level = level_list[tier][0]
					nextlevel = level_list[tier+1][1]
					return level, nextlevel

def parseTweet(impetusTweet):
	twitName = impetusTweet.user.screen_name
	twitID = impetusTweet.user.id
	playerRoster = initRoster()		
	word_list = impetusTweet.text.split(' ')
	strRespond = ''
	
	stars = "********************************************************"
	print "%s\nuser info:\ntwitter id: %i\ntwitter handle: %s\ntweet text: %s\ntweet id: %s\n%s" % (stars, twitID, twitName, word_list, impetusTweet.id, stars)
	
	# if twitName in playerRoster.keys():
		# print "returning player!", playerRoster[twitName].char_name
		
	#####################################
	# 				 ?start				#
	#####################################	
	if '?start' in word_list:
		print "\nstart present"
		if twitName in playerRoster.keys():
			print "?start command already resolved why is this tweet getting passed to interactor???"
			strRespond = "Yes, yes. I know! Try ?name!"
		else:
			print "tying to add new player"
			AddNewPlayer(playerRoster, twitName, twitID)
			strRespond = "Welcome, Pupil! Select your Name by typing '?name' followed by the name you wish to use on your Adventure!"
			
	#####################################
	# 				 ?name				#
	#####################################		
	if '?name' in word_list:
		#print word_list
		if twitName not in playerRoster.keys():
			strRespond = "I'm sorry, Pupil. You must begin with '?start' to confirm your Desire to begin your Adventure!"
		elif playerRoster[twitName].char_name is None or playerRoster[twitName].char_name == "None":
			desiredName = ' '.join(word_list[word_list.index('?name')+1:]).strip()
			print desiredName
			print playerRoster[twitName].char_name
			if desiredName:
				if len(desiredName) >= 10:
					strRespond = "Please don't be difficult Pupil! I cannot pronounce such a long Name."
				else:
					playerRoster[twitName].char_name = desiredName
					print playerRoster[twitName].char_name
					saveRoster(playerRoster)
					strRespond = "Greetings, %s! You are a level %s _ from the land of _!" % (playerRoster[twitName].char_name, ComputeLevel(playerRoster[twitName].xp),playerRoster[twitName].char_class )
			else:
				strRespond = "Pupil! Try typing an actual name after '?name' "
			
		else:
			strRespond = "Ah, %s. I'm afraid you cannot change your name so easily" % (playerRoster[twitName].char_name)
			pass
		
	#####################################
	# 				 ?xp				#
	#####################################
	if '?xp' in word_list:
		xp = playerRoster[twitName].xp
		level, nextlevel = ComputeLevel(xp)
		#print xp
		
		if not level or level == 0 or xp == 0:
			strRespond = "You do not have any experience points!"
			#print "no xp??"
		else:
			strRespond = "You are currently level %s and have %s/%s experience points towards level %s!" % (level, xp, nextlevel, level+1)
			#print "xp: %s\nlevel: %s" % (xp, level)
		
	#####################################
	# 				 ?hp				#
	#####################################
	if '?hp' in word_list:
		hp = playerRoster[twitName].hp
		maxhp = playerRoster[twitName].maxhp
		if hp == maxhp:
			strRespond = "You have full health! (%shp)" % (hp)
		else:
			strRespond = "You have %s out of %shp remaining." % (hp, maxhp)
 
	#####################################
	# 			 attacks				#
	#####################################
	if ('?kill' in word_list or
		'?stab' in word_list or
		'?kick' in word_list or
		'?fight' in word_list):
		pass
	#####################################
	# 				?GEAR				#
	#####################################
	if '?gear' in word_list:
		pass
	#####################################
	# 				 ?loc				#
	#####################################
	if '?loc' in word_list or '?pos' in word_list:
		print "Loc found, sending to map maker"
		# playerdict[usrName].pos_x = 1
		# playerdict[usrName].pos_y = 1
		# playerdict[usrName].pos_z = 1
		debug = False
		
		#strRespond = "You are here:\n", tweetMapMaker(playerRoster[twitName].pos_x,playerRoster[twitName].pos_y,playerRoster[twitName].pos_z, debug=debug)
		strMap = tweetMapMaker(playerRoster[twitName].pos_x,playerRoster[twitName].pos_y,playerRoster[twitName].pos_z, debug=debug)
		
		strRespond = '\n'.join(['You are here:', strMap])
		
	if '?N' in word_list:
		new_y = -1
	if '?E' in word_list:
		new_x = 1
	if '?S' in word_list:
		new_y = 1
	if '?W' in word_list:
		new_x = -1
	PlayerMover(x=curX,y=curY,z=curZ,step_x = new_x, step_y = new_y)
	#####################################
	# 				 ?whoAmI			#
	#####################################
	if '?who' in word_list:
		pass
	
	if strRespond:	
		print "sending tweet back to runner!"
		#print "returning tweet: %s\n" % (strRespond)
		return strRespond
	else:
		print "tweet returned from interactor!"
		
	