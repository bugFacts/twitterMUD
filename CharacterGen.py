from __future__ import unicode_literals
import twitter, os
import random
import linecache
import xlrd
import sys
import time
from string import maketrans  
import re

import unicodedata

wb = xlrd.open_workbook(r'P:\python_twitter\scrips\DungeonMaster\corpus\nova.xls')

shCLASS = wb.sheet_by_name(u'CLASS')

def SimplePicker(sheet, column):
	col_list = filter(None, sheet.col_values(column,1))
	strOut = random.choice(col_list)
	return strOut

def buildRule( (pattern, search, replace) ): 
	#enables Pluralizer() and similar to apply a list of regular expressions
	#to a string via map()
    return lambda word: re.search(pattern, word, flags=re.I) and re.sub(search, replace, word, flags=re.I)
	
def ClassMaker():
	format = SimplePicker(shCLASS,0)
	#print format
	
	patterns = \
		(
		(r'<BASE1>','<BASE1>', 	SimplePicker(shCLASS,1).strip()),
		(r'<BASE2>','<BASE2>', 	SimplePicker(shCLASS,1).strip()),
		(r'<ITEM>','<ITEM>', 	SimplePicker(shCLASS,2).strip()),
		(r'<SUFFIX>','<SUFFIX>',SimplePicker(shCLASS,3).strip()),
		(r'<DOER>','<DOER>', 	SimplePicker(shCLASS,4).strip()),
		(r'$', '$', ''),	#everything else??
		)
		
	ruleList = map(buildRule, patterns)
	strOut = format
	for rule in ruleList:
		if rule(strOut):
			strOut = rule(strOut)
	return strOut.title()
	
#charClass = ClassMaker()

#print charClass