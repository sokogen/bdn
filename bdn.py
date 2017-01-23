#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#

### Configuration
cfg={
### Настройка доступа к Confluence
# URL страницы с таблицей:
'cflurl': 'http://212.15.125.130:8090/pages/viewpage.action?pageId=65592#space-menu-link-content',
'cfluser': 'admin',								# Логин для доступа к Confluence
'cflpass': 'Telegraph!',						# Пароль для доступа к Confluence


### Настройка формата данных таблицы
'bdcol': 'День рождения',						# Заголовок колонки с датами дней рождений
'emailcol': 'email',							# Заголовок колонки с адресами e-mail
'firedstaffcol': 'Комната',						# Заголовок колонки для помечания уволенных сотрудников
'firedstaffmarks': ('уволен','Уволен'),			# Метки для помечания уволенных сотрудников в колонке "Комната"

### Настройка рассылок
'smtpserver': 'localhost',						# Адрес SMTP сервера
'notificationtime': '09:00',					# Время рассылки оповещений
'notificationweekdays': (1,2,3,4,5),			# Номера дней недели для оповещений
}

import json
from urlparse import urlparse
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup


class CflPageParser:
	def __init__(self, cfg=cfg):
		self.cflurl = cfg['cflurl']
		self.cfluser = cfg['cfluser']
		self.cflpass = cfg['cflpass']
		self.firedstaffcol = cfg['firedstaffcol'].decode('utf-8')
		self.firedstaffmarks = tuple(map(lambda mark: mark.decode('utf-8'), cfg['firedstaffmarks']))
		self.createresturl(self.cflurl)
		self.gettablesdict()

	def createresturl(self, cflurl):
		# Берем стандартный URL и возвращаем REST URL.
		self.cflhosturl='{}://{}'.format(urlparse(self.cflurl)[0], urlparse(self.cflurl)[1])
		self.pageid=int(urlparse(self.cflurl)[4].split("=")[1])
		self.resturl='{}/rest/api/content/{}?expand=body.storage'.format(self.cflhosturl, self.pageid)
		return self.resturl

	def gettablesdict(self):
		# Собираем все словари таблиц в одну коллекцию
		self.createtablesdata(self.resturl)
		## It must be rewritten
		self.tablesdict = list(map(lambda table: self.createtabledict(table), self.tables))
		self.tablesdict = tuple(reduce(lambda d, t: d.extend(t), self.tablesdict))
		return self.tablesdict

	def createtablesdata(self, resturl):
		# Выполняем REST запрос и готовим "суп"
		self.rawdata = requests.get(self.resturl, auth=requests.auth.HTTPBasicAuth(self.cfluser, self.cflpass)).json()['body']['storage']['value']
		self.rawdata = BeautifulSoup(self.rawdata, 'html.parser')
		# Выбирем только содержание таблиц со страницы
		self.tables = self.rawdata.findAll('table')
		return self.tables
	
	def createtabledict(self, table):
		# Выбираем заголовки колонок
		self.headsdict = tuple(map(lambda h: h.get_text().strip(), table.findAll('th')))
		# Собираем и вычищаем информационную часть таблицы
		self.rowsdict = tuple(map(lambda row: (map (lambda col: col.get_text(), row.findAll('td'))), table.findAll('tr')))
		# Комбинируем заголовки с данными
		self.tabledict = map(lambda row: dict(zip(self.headsdict, row)), filter(lambda row: len(row)==len(self.headsdict), self.rowsdict))
		return self.tabledict

	def getstaffdict(self):
		#staffdict = tuple(map(lambda table: map(lambda person: filter(lambda room: room != "уволен", person[u'\u041a\u043e\u043c\u043d\u0430\u0442\u0430']),table), self.tablesdict))
		return filter(lambda person: person[self.firedstaffcol].strip() not in self.firedstaffmarks, self.tablesdict)

class BDNotice:
	def __init__(self, cfg=cfg):
		self.curdate = datetime.now()
		self.staffdict = CflPageParser().getstaffdict()
		print (self.curdate-timedelta(days=65)).strftime("%Y-%m-%d")

	def createbdnoticedict(self, staffdict):
		# Добавляем даты др "соседних" годов, для правильного определения на границах годов
		
		pass

	def sendbdnotice():
		pass

if __name__ == '__main__':
#	page = CflPageParser()
#	staffdict = page.getstaffdict()
#
#	print staffdict
	n = BDNotice()


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
