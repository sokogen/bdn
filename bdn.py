#!/usr/bin/env python
# -*- coding: utf-8 -*-

### Configuration
cfg={
### Настройка доступа к Confluence
# URL страницы с таблицей:
'cflurl': 'http://212.15.125.130:8090/pages/viewpage.action?pageId=65592#space-menu-link-content',
'cfluser': 'admin',				# Логин для доступа к Confluence
'cflpass': 'Telegraph!',			# Пароль для доступа к Confluence


### Настройка формата данных таблицы
'fnamecol': 'ФИО',				# Заголовок колонки с полным именем
'bdcol': 'День рождения',			# Заголовок колонки с датами дней рождений
'emailcol': 'email',				# Заголовок колонки с адресами e-mail
'directioncol': 'Направление работы',		# Заголовок колонки с направлениями работы
'firedstaffcol': 'Комната',			# Заголовок колонки для помечания уволенных сотрудников
'firedstaffmarks': ('уволен','Уволен'),		# Метки для помечания уволенных сотрудников в колонке "Комната"

### Настройка оповещений
'smtpserver': 'localhost',			# Адрес SMTP сервера
'bdaysrange': (-1, 7),				# Количество дней "вокруг" дня рождения
'notificationtime': '09:00',			# Время рассылки оповещений
'notificationweekdays': (1,2,3,4,5),		# Номера дней недели для оповещений
'mailsender': 'noreply@server',			# Отправитель сообщения в поле "From:"
'mailsubject': 'Дни рождения',			# Тема письма ('Subject:')
}

# Лечение возможных проблем кодировок
import setupcon
setupcon.setup_console('utf-8', False)

# Стандартные библиотеки
import json, re, smtplib
from urlparse import urlparse
from datetime import datetime, timedelta
from time import sleep
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
# Внешние зависимости ()
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
		self.cflhosturl='{0}://{1}'.format(urlparse(self.cflurl)[0], urlparse(self.cflurl)[1])
		self.pageid=int(urlparse(self.cflurl)[4].split("=")[1])
		self.resturl='{0}/rest/api/content/{1}?expand=body.storage'.format(self.cflhosturl, self.pageid)
		return self.resturl

	def gettablesdict(self):
		# Собираем все словари таблиц в одну коллекцию
		self.createtablesdata(self.resturl)
		## It can be rewritten
		self.tablesdict = tuple(reduce(lambda d, t: d.extend(t), map(lambda table: self.createtabledict(table), self.tables)))
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
		return filter(lambda person: person[self.firedstaffcol].strip() not in self.firedstaffmarks, self.tablesdict)

class BDNotice():
	"""
	Класс получает данные от парсера таблиц Confluence,
	формирует письмо с информацией о ближайших днях рождения сотрудников,
	и отправляет его остальным.
	"""
	def __init__(self, cfg=cfg):
		self.bdstaffdict = {'bd':{},'recipients':[]}
		self.bdcol = cfg['bdcol'].decode('utf-8')
		self.emailcol = cfg['emailcol'].encode('utf-8')
		self.fnamecol = cfg['fnamecol'].decode('utf-8')
		self.directioncol = cfg['directioncol'].decode('utf-8')

		self.mailbody_temp = str(open('mail_template/mail_body.txt').read())
		self.maildates_temp = str(open('mail_template/dates.txt').read())
		self.mailperson_temp = str(open('mail_template/person.txt').read())

	def run(self):
		while True:
			if self.checktime():
				self.createbdnotice(CflPageParser().getstaffdict())
			sleep(31)

	def checktime(self):
		# Проверяем день недели и время
		self.today = datetime.now()
		self.notificationtime = '{0} {1}'.format(self.today.strftime("%Y-%m-%d"), cfg['notificationtime'])
		return self.today.strftime("%Y-%m-%d %H:%M") == self.notificationtime and self.today.isoweekday() in cfg['notificationweekdays']

	def cronrun(self):
		self.createbdnotice(CflPageParser().getstaffdict())

	def createbdnotice(self, staffdict):
		# Проверяем даты рождений у всех сотрудников.
		# Именинников раскладываем по датам, остальных в список адресатов.
		for person in staffdict:
			bddate = self.checkbddate(person[self.bdcol])
			if bddate != None:
				try:
					self.bdstaffdict['bd'][bddate].append(person)
				except KeyError:
					self.bdstaffdict['bd'][bddate]=list()
					self.bdstaffdict['bd'][bddate].append(person)
			else:
				self.bdstaffdict['recipients'].append(person[self.emailcol])

		# Генерируем тело письма
		self.dateslist = str()
		for date in self.bdstaffdict['bd'].keys():
			self.personslist = str()
			for person in self.bdstaffdict['bd'][date]:
				self.personslist+=(self.mailperson_temp.format(email=person[self.emailcol], name=person[self.fnamecol], direction=person[self.directioncol]))
			self.dateslist+=self.maildates_temp.format(date=date, persons=self.personslist)
		self.mailhtml=self.mailbody_temp.format(dates=self.dateslist)

		# Отсылаем письмо адресатам
		for rec in self.bdstaffdict['recipients']:
			self.sendbdnotice(rec, self.mailhtml)


	def checkbddate(self, bddate):
		self.marginlow = self.today + timedelta(days=int(cfg['bdaysrange'][0]))
		self.marginhigh = self.today + timedelta(days=int(cfg['bdaysrange'][-1]))
		# На всякий случай удаляем из даты все кроме цифр и точек
		bddate=re.compile(r'[^\d.]+').sub('', bddate.encode('utf-8').strip())
		# Прекращаем проверку, если это не дата
		if len(bddate) < 3: return None
		# Добавляем даты др соседних годов
		bddates=[]
		for i in (-1, 0, 1):
			bddates.append('{0}.{1}'.format(bddate, int(self.today.strftime("%Y")) + i))
		# Возвращаем дату, если она находится в искомом диапазоне
		for date in bddates:
			date=datetime.strptime(date, '%d.%m.%Y')
			#print self.marginlow<=date and date<self.marginhigh
			if self.marginlow<=date<self.marginhigh:
				return date.strftime("%d.%m.%Y")

	def sendbdnotice(self, recipient, message):
		msg = MIMEMultipart('alternative')
		msg['Subject'] = cfg['mailsubject']
		msg['From'] = cfg['mailsender']
		msg['To'] = recipient

		msg.attach(MIMEText(message, 'html'))

		s = smtplib.SMTP(cfg['smtpserver'])
		s.sendmail(cfg['mailsender'], recipient, msg.as_string())
		s.quit()

if __name__ == '__main__':
	BDNotice().run()
