#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

### Configuration
cfg={
'cflurl': 'http://212.15.125.130:8090/pages/viewpage.action?pageId=65592#space-menu-link-content',
'cfluser': 'admin',
'cflpass': 'Telegraph!',
'imapserver': 'localhost',
'notificationtime': '09:00',
}

import json, time
from urlparse import urlparse
from functools import reduce
import requests
from bs4 import BeautifulSoup

def getresturl(cflurl):
	cflhosturl='{0}://{1}'.format(urlparse(cflurl)[0], urlparse(cflurl)[1])
	pageid=int(urlparse(cflurl)[4].split("=")[1])
	resturl='{0}/rest/api/content/{1}?expand=body.storage'.format(cflhosturl, pageid)
	return resturl

def makemaindict(resturl):
	pass

resturl=getresturl(cfg['cflurl'])

rawdata = requests.get(resturl, auth=requests.auth.HTTPBasicAuth(cfg['cfluser'], cfg['cflpass'])).json()['body']['storage']['value']

soup = BeautifulSoup(rawdata, 'html.parser')

tables=soup.findAll('table')

tableid=0
maindict={}

for table in tables:
	heads = tuple(map(lambda h: h.get_text().strip(), table.findAll('th')))
	rowsdict = tuple(map(lambda row: row, table.findAll('tr')))
#	print rowsdict
#	print heads
	for row in rowsdict:
		row=row.findAll('td')
		for i in row:
			print i.get_text().strip()
		try:
			index=row[0].get_text().strip()
			print index
			maindict[tableid][index]={}
		except:
			continue
		for i in range(1, len(heads)):
			print i
			maindict[tableid][index][heads[i]]=row[i].get_text().strip()
	print maindict

#	for each in rawrows:
#		print each
#		print 
#		print
#	for tr in rows:
#		cols = tr.findAll('td')
#		print cols
#		if 'cell_c' in cols[0]['class']:
#			digital_code, letter_code, units, name, rate = [c.text for c in cols]
#			print digital_code, letter_code, units, name, rate    	
