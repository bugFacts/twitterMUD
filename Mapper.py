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

def initRoster():
	roster = Player_Dict().load_from_file()
	return roster
	
def saveRoster(roster):
	Player_Dict().save_to_file(roster)
	
playerRoster = initRoster()		
word_list = ['?loc']
strRespond = ''

twitName = 'DAMNFerrellmort'

# if twitName in playerRoster.keys():
	# print "player found!"
	
#if '?loc' in word_list:
	#print 'loc found!'
	#print "x pos: ", playerRoster[twitName].pos_x
	#print "y pos: ", playerRoster[twitName].pos_y
	#print "z pos: ", playerRoster[twitName].pos_z
	
def map_loader(FILE):
	### load a map file into a list of lists
	### each item is a raw tile
	with open(FILE, 'r') as fp:
		fmap = fp.readlines()
		
	map = []
	for row in fmap:
		map_row = row.strip().split(',')
		map.append(map_row)
	return map

def borderBound(centerOn, max_x, max_y):
	### sets a window size around a x,y point
	### that can be tailored for size
	### since tweets are limited to 140
	### 14x7 (98 + 7 returns = 105) works okay
	### plus '@' plus the user name (1+15+105=121)
	### leaves room for 19 char message
	### 'You are here:\n' (14) leaves 5 char buffer
	bound =  [ 
				centerOn[0]-max_x/2,	#left
				centerOn[0]+max_x/2,	#right			
				centerOn[1]+max_y/2,	#top
				centerOn[1]-max_y/2,	#bottom
			]
	return bound

# def replaceOneElement(old_list, new_element, index):
	# for item in index:
		# old_list
		
def tweetMapMaker(x,y,z,max_x=14,max_y=7,debug=False):
	print "call received from interactor..."
	playerPosition = [x,y]
	
	if z == 1:
		ZLEVEL = r'P:\python_twitter\scrips\DungeonMaster\savefiles\level1.txt'
	elif z ==2:
		ZLEVEL = r'P:\python_twitter\scrips\DungeonMaster\savefiles\level2.txt'
	elif z == 3:
		ZLEVEL = r'P:\python_twitter\scrips\DungeonMaster\savefiles\level3.txt'
	else:
		print "zlevel not found! using 1"
		ZLEVEL = r'P:\python_twitter\scrips\DungeonMaster\savefiles\level1.txt'
	
	fullMap = map_loader(ZLEVEL)
	
	rows = len(fullMap)
	cols = len(fullMap[0])
	
	#centerOn = []
	#centerOn = playerPosition
	centerOn = [x,y]
	window = borderBound(centerOn, max_x, max_y)

	######### ADJUST FOCAL POINT TO FIT FULL MAP WINDOW ######
	while window[0] < 0:
		#print "too far left"
		centerOn[0] += 1
		window = borderBound(centerOn, max_x, max_y)
	while window[1] > cols-1:
		#print "too far right"
		centerOn[0] -= 1
		window = borderBound(centerOn, max_x, max_y)	
	while window[2] > rows-1:
		#print "too far down"
		centerOn[1] -= 1
		window = borderBound(centerOn, max_x, max_y)
	while window[3] < 0:
		#print "too far up"
		centerOn[1] += 1
		window = borderBound(centerOn, max_x, max_y)
	############### FINISHED ADJUSTING WINDOW ###############
	
	fullMap[playerPosition[1]][playerPosition[0]] = 'P'
	
	map_window = []
	for top_bottom in range(window[3],window[2]):
		map_line = []
		for left_right in range(window[0],window[1]):
			map_line.extend( fullMap[top_bottom][left_right] )
		map_window.append(map_line)
	
	#print map_window
	
	if debug:
		patterns = \
		(
		(r'0', '0', '='),			### 0 = blank space (non-useable)
		(r'1', '1', '_'),			### 1 = floor tile (walkable)
		(r'2', '2', '#'),			### 2 = PLAIN WALL
		(r'3', '3', 'd'),			### 3 = PLAIN DOOR
		(r'4', '4', 'd'),			### 4 = LOCKED DOOR
		(r'H', 'H', '#'),			### H = HIDDEN DOOR
		(r'5', '5', 'k'),			### 5 = DOOR KEY
		(r'6', '6', '?'),			### 6 = OPEN LOOT
		(r'7', '7', '?'),			### 7 = LOCKED LOOT
		(r'8', '8', 'k'),			### 8 = LOOT KEY
		(r'W', 'W', '?'),			### W = WIN LOOT
		(r'C', 'C', '?'),			### C = LOOT MIMIC
		(r'9', '9', '_'),  			### 9 = EASY MONSTER
		(r'A', 'A', '_'), 			### A = HARD MONSTER
		(r'B', 'B', '_'),			### B = BOSS MONSTER
		(r'T', 'T', '_'),			### T = PLAIN TRAP
		(r'U', 'U', '/'),			### U = UP STAIRS
		(r'D', 'D', '\\'),			### D = DOWNSTAIRS
		(r'P', '$', '')				### P = YOU ARE HERE (DONT REPLACE PLAYER CODE)
		)
		
	else:
		patterns = \
		(
		(r'0', '0', u'\u2593'),			### 0 = blank space (non-useable)
		(r'1', '1', u'\u2591'),			### 1 = floor tile (walkable)
		(r'2', '2', u'\u2588'),			### 2 = PLAIN WALL
		(r'3', '3', u'\u237B'),			### 3 = PLAIN DOOR
		(r'4', '4', u'\u237B'),			### 4 = LOCKED DOOR
		(r'H', 'H', u'\u2588'),			### H = HIDDEN DOOR
		(r'5', '5', 'k'),			### 5 = DOOR KEY
		(r'6', '6', '?'),			### 6 = OPEN LOOT
		(r'7', '7', '?'),			### 7 = LOCKED LOOT
		(r'8', '8', 'k'),			### 8 = LOOT KEY
		(r'W', 'W', '?'),			### W = WIN LOOT
		(r'C', 'C', '?'),			### C = LOOT MIMIC
		(r'9', '9', u'\u2591'),  		### 9 = EASY MONSTER
		(r'A', 'A', u'\u2591'), 		### A = HARD MONSTER
		(r'B', 'B', u'\u2591'),			### B = BOSS MONSTER
		(r'T', 'T', u'\u2591'),			### T = PLAIN TRAP
		(r'U', 'U', u'\u25B2'),			### U = UP STAIRS
		(r'D', 'D', u'\u25BC'),			### D = DOWNSTAIRS
		(r'P', 'P', u'\u263F')			### P = YOU ARE HERE
		)

	strRow = ''
	strMap = ''
	switchList = map(buildRule, patterns)
	# pointerX = 0
	# pointerY = 0
	# print playerPosition
	# replaced = False
	# while replaced == False:
		# for row in fullMap:
			# print row
			# pointerX = 0
			# for col in row:
				# if pointerX == playerPosition[0] and pointerY == playerPosition[1]:
					# print "P found, replacing"
					# fullMap[pointerY][pointerX] = 'P'
					# replaced = True
				# pointerX += 1
			# pointerY += 1
	
	
	rowCount = 0
	for row in map_window:
		strRow=''
		for eachTile in row:
			for rule in switchList:
				sOut = rule(eachTile)
				if sOut: 
					strRow = ''.join([strRow,sOut])
			
		strMap = ''.join( ['\n'.join([strMap,strRow]) , str(rowCount)] )
		rowCount += 1
	return strMap
	print "map complete, sending back to interactor", type(strMap)
	
def PlayerMover(x=None,y=None,z=None,step_x=0,step_y=0,step_z=0):
	currentPos = [x,y]
	print "current:", currentPos
	desiredPos = [x+step_x, y+step_y]
	print "desired: ", desiredPos
	if z == 1:
		ZLEVEL = r'P:\python_twitter\scrips\DungeonMaster\savefiles\level1.txt'
	elif z ==2:
		ZLEVEL = r'P:\python_twitter\scrips\DungeonMaster\savefiles\level2.txt'
	elif z == 3:
		ZLEVEL = r'P:\python_twitter\scrips\DungeonMaster\savefiles\level3.txt'
	else:
		print "zlevel not found! using 1"
		ZLEVEL = r'P:\python_twitter\scrips\DungeonMaster\savefiles\level1.txt'
	
	fullMap = map_loader(ZLEVEL)

	NOPASS = [ 	'0',
				'2',
				'3',
				'4',
				'H',
			]
			
	print "step x: ", step_x
	print "step y: ", step_y
	if fullMap[y+step_y][x+step_x] not in NOPASS:
		playerRoster[twitName].pos_x += step_x
		playerRoster[twitName].pos_y += step_y
		saveRoster(playerRoster)
		
	else:
		#### cant move here!
		print "cant move that way!"
		pass
	if step_z != 0:
		if step_z == 1 and fullMap[y][x] == 'D':
			#go DOWN
			
			saveRoster(playerRoster)
			pass
		elif step_z == -1 and fullMap[y][x] == 'U': 
			#go UP
			
			saveRoster(playerRoster)
			pass
			
# debug = True		
# print tweetMapMaker(playerRoster[twitName].pos_x,playerRoster[twitName].pos_y,playerRoster[twitName].pos_z, debug=debug)

curX = playerRoster[twitName].pos_x
curY = playerRoster[twitName].pos_y
curZ = playerRoster[twitName].pos_z

PlayerMover(x=curX,y=curY,z=curZ, step_x = 1)

curX = playerRoster[twitName].pos_x
curY = playerRoster[twitName].pos_y
curZ = playerRoster[twitName].pos_z

debug = True		
print tweetMapMaker(curX,curY,curZ, debug=debug)

