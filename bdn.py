#!/usr/bin/env python
#
#

### Configuration
cfg={
'cflurl': 'http://localhost:8090/pages/viewpage.action?pageId=65592#space-menu-link-content',
'cfluser': 'admin',
'cflpass': 'Telegraph!',
'imapserver': 'localhost',
'notificationtime': '09:00',
}

import requests
import json
from bs4 import BeautifulSoup
from urlparse import urlparse

def getresturl(cflurl):
	pageid=urlparse("http://localhost:8090/pages/viewpage.action?pageId=65592#space-menu-link-content")[4].split("=")[1]
	resturl='http://localhost:8090/rest/api/content/{}?expand=body.storage'.format(pageid)
	return resturl

url=getresturl(cfg['cflurl'])

rawdata = requests.get(url, auth=requests.auth.HTTPBasicAuth(cfg['cfluser'], cfg['cflpass'])).json()['body']['storage']['value'].encode('UTF-8')

soup = BeautifulSoup(rawdata, 'html.parser')

tables=soup.findAll('table')

for table in tables:
	heads=[]
	rows=[]
	rawheads = table.findAll('th')
	rawrows = table.findAll('tr')
	for head in rawheads:
		heads.append(head.get_text().strip())
	print rawrows
	for each in heads:
		print each.encode('utf-8')
#	for tr in rows:
#		cols = tr.findAll('td')
#		print cols
#		if 'cell_c' in cols[0]['class']:
#			digital_code, letter_code, units, name, rate = [c.text for c in cols]
#			print digital_code, letter_code, units, name, rate    	