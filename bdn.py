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

import json
from datetime import datetime, timedelta
from urlparse import urlparse
from functools import reduce
import requests
from bs4 import BeautifulSoup

### For Test Only
def getresturl(cflurl):
	#print "_getresturl"
	# Берем стандартный URL и возвращаем REST URL.
	cflhosturl='{0}://{1}'.format(urlparse(cflurl)[0], urlparse(cflurl)[1])
	pageid=int(urlparse(cflurl)[4].split("=")[1])
	resturl='{0}/rest/api/content/{1}?expand=body.storage'.format(cflhosturl, pageid)
	return resturl

class CflPageParser:
	def __init__(self, cflurl, cfluser='admin', cflpass='admin'):
		self.cflurl = cflurl
		self.cfluser = cfluser
		self.cflpass = cflpass
		self.collecttablesdict()

	def collecttablesdict(self):
		# print "_collecttablesdict"
		# Собираем все словари таблиц в одну коллекцию
		self.createresturl(self.cflurl)
		self.createrawdata(self.resturl)
		self.createtablesdata(self.rawdata)
		# It must be rewritten
		self.tablesdict = list(map(lambda table: self.collecttabledict(table), self.tables))
		self.tablesdict = tuple(reduce(lambda d, t: d.extend(t), self.tablesdict))
		return self.tablesdict

	def collecttabledict(self, table):
		# print "_collecttabledict"
		# Формируем таблицу в словаре
		self.createtableheadsdict(table)
		self.createtablerowsdict(table)
		self.createtabledict(self.rowsdict, self.headsdict)
		return self.tabledict

	def createresturl(self, cflurl):
		# print "_createresturl"
		# Берем стандартный URL и возвращаем REST URL.
		self.cflhosturl='{0}://{1}'.format(urlparse(self.cflurl)[0], urlparse(self.cflurl)[1])
		self.pageid=int(urlparse(self.cflurl)[4].split("=")[1])
		self.resturl='{0}/rest/api/content/{1}?expand=body.storage'.format(self.cflhosturl, self.pageid)
		return self.resturl

	def createrawdata(self, resturl):
		# print "_createrawdata"
		# Выполняем REST запрос и готовим "суп"
		self.rawdata = requests.get(self.resturl, auth=requests.auth.HTTPBasicAuth(self.cfluser, self.cflpass)).json()['body']['storage']['value']
		self.rawdata = BeautifulSoup(self.rawdata, 'html.parser')
		return self.rawdata
	
	def createtablesdata(self, rawdata):
		# print "_createtablesdata"
		# Выбирем только содержание таблиц со страницы
		self.tables = self.rawdata.findAll('table')
		return self.tables
	
	def createtableheadsdict(self, table):
		# print "_createtableheadsdict"
		# Выбираем заголовки колонок
		self.headsdict = tuple(map(lambda h: h.get_text().strip(), table.findAll('th')))
		return self.headsdict
	
	def createtablerowsdict(self, table):
		# print "_createtablerowsdict"
		# Собираем и вычищаем информационную часть таблицы
		self.rowsdict = tuple(map(lambda row: (map (lambda col: col.get_text(), row.findAll('td'))), table.findAll('tr')))
		return self.rowsdict
	
	def createtabledict(self, rows, heads):
		# print "_createtablesdict"
		# Комбинируем заголовки с данными
		self.tabledict = list(map(lambda row: dict(zip(self.headsdict, row)), filter(lambda row: len(row)==len(self.headsdict), self.rowsdict)))
		return self.tabledict

	def getstaffdict(self):
		#staffdict = tuple(map(lambda table: map(lambda person: filter(lambda room: room != "уволен", person[u'\u041a\u043e\u043c\u043d\u0430\u0442\u0430']),table), self.tablesdict))
		staffdict = filter(lambda person: person[u'\u041a\u043e\u043c\u043d\u0430\u0442\u0430'].strip() != u'\u0443\u0432\u043e\u043b\u0435\u043d', self.tablesdict)
		return staffdict

	def getemaillist(self, dict):
		# Берем лист словарей сотрудников и возвращаем список e-mail.
		emaillist = map(lambda person: person['email'],dict)
		return emaillist


if __name__ == '__main__':
	page = CflPageParser(cfg['cflurl'], cfg['cfluser'], cfg['cflpass'])
	staffdict = page.getstaffdict()
	print staffdict
	emaillist = page.getemaillist(staffdict)


	print emaillist



	

#	resturl=getresturl(cfg['cflurl'])
#	
#	rawdata = requests.get(resturl, auth=requests.auth.HTTPBasicAuth(cfg['cfluser'], cfg['cflpass'])).json()['body']['storage']['value']
#	
#	soup = BeautifulSoup(rawdata, 'html.parser')
#	
#	tables=soup.findAll('table')
#	
#	tableid=0
#	maindict={}
#	
#	for table in tables:
#		# Выбираем заголовки колонок
#		headsdict = tuple(map(lambda h: h.get_text().strip(), table.findAll('th')))
#		# Собираем и вычищаем информационную часть таблицы
#		rowsdict = tuple(map(lambda row: (map (lambda col: col.get_text(), row.findAll('td'))), table.findAll('tr')))
#		# Комбинируем заголовки с данными
#		tabledict = tuple(map(lambda row: dict(zip(headsdict, row)), filter(lambda row: len(row)==len(headsdict), rowsdict)))
#		#print filter(lambda row: len(row)==len(headsdict), rowsdict)
#		for row in tabledict:
#			for key, value in row.items():
#				print '{} - {}'.format(key.encode('utf-8'), value.encode('utf-8'))
#	
#			print;print;
#		
#	#
