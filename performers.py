#!/usr/bin/env python3

from io import StringIO, BytesIO
from lxml import etree
import requests

import re
import mysql.connector as connector


class app:
	
	def __init__(self):
		
		self.url='https://tekstowo.pl'
		self.linkFormat='/artysci_na,%s,strona,%d.html'
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
		
		self.curLetter=0
		self.curPage=0
		self.letters=[
		{'letter':'A', 'pages':487 },
		{'letter':'B', 'pages':351 },
		{'letter':'C', 'pages':328 },
		{'letter':'D', 'pages':377 },
		{'letter':'E', 'pages':205 },
		{'letter':'F', 'pages':169 },
		{'letter':'G', 'pages':186 },
		{'letter':'H', 'pages':201 },
		{'letter':'I', 'pages':118 },
		{'letter':'J', 'pages':301 },
		{'letter':'K', 'pages':283 },
		{'letter':'L', 'pages':281 },
		{'letter':'M', 'pages':478 },
		{'letter':'N', 'pages':182 },
		{'letter':'O', 'pages':104 },
		{'letter':'P', 'pages':260 },
		{'letter':'Q', 'pages':14  },
		{'letter':'R', 'pages':245 },
		{'letter':'S', 'pages':518 },
		{'letter':'T', 'pages':443 },
		{'letter':'U', 'pages':43  },
		{'letter':'V', 'pages':106 },
		{'letter':'W', 'pages':129 },
		{'letter':'X', 'pages':16  },
		{'letter':'Y', 'pages':69  },
		{'letter':'Z', 'pages':62  },
		{'letter':'pozostale', 'pages':133 }
		]
		
		self.insertPerformerSql = "INSERT INTO performers (id,name,tracks_no,link) VALUES (%s, %s, %s, %s)"
		self.insertPageSql = "INSERT INTO performers_pages (letter,page,tracks_no) VALUES (%s, %s, %s)"
		
		self.timeout=12
		
	#this gets next link to evaluate. if end then empty string
	def getNextLink(self):
		
		#check end
		if(self.curLetter==len(self.letters)-1 and self.curPage==self.letters[-1]['pages']):
			print('KONIEC')
			return None
		
		#not end. lets check if pages inside letter has been exhausted
		if(self.curPage==self.letters[self.curLetter]['pages']):
			self.curLetter+=1
			self.curPage=1
		#not exhausted. lets go to the next page
		else:
			self.curPage+=1
		
		#lets return next link
		return {'letter':self.letters[self.curLetter]['letter'], 'page':self.curPage, 'link':'/artysci_na,%s,strona,%d.html' % (self.letters[self.curLetter]['letter'], self.curPage) }

	#daemon to proceed	
	def deamon(self):
		
		#private SQL connecttion
		db = connector.connect(
		  host="localhost",
		  user="biala",
		  password="mewa",
		  database="tekstowo"
		)
		cursor = db.cursor()
		
		
		#start with this link
		curLink=self.getNextLink()
		
		#while link is possible to get
		while(curLink!=None):
			
			try:
				#get page as html from
				response = requests.get(self.url+curLink['link'], headers=self.headers, timeout=self.timeout)		
				html=response.content.decode("utf-8")
				
				#preventing wrong root element for lxml
				if html[:15].lower()=='<!doctype html>':
					html=html[15:]
				
				#loading html as tree element
				parser = etree.XMLParser(recover=True)
				tree=etree.parse(StringIO(html),parser)
				
				#loading performers'  node elements
				rows=tree.xpath("//div[contains(@class, 'right-column')]//a[contains(@class, 'title')]");
				
				#for every of those elements
				for row in rows:
					#REGEXP DESCRIBE: matches=re.search('^(.*)\\s(\\(.*\\))\\s*$',row.text)
					#1. start of line ("^")
					#2. name of  performer ("(.*)")
					#3. a whitespace character ("\\s")
					#4. Catch letters in the last rounded brackets ("(\\(.*\\))")
					#5. May be omitted whitespace character ("\\s*")
					#6. end of line ("$") to prove that brackets in #4 was the last one
					
					#get info about everyone 
					matches=re.search('^(.*)\\s(\\(.*\\))\\s*$',row.text)
					name=matches.group(1)
					count=int(matches.group(2)[1:-9])
					link=row.get('href')
					
					#insert to database
					cursor.execute(self.insertPerformerSql, (None,name,count,link))
				
				#insert info about previous insertions to db
				cursor.execute(self.insertPageSql, (curLink['letter'],curLink['page'],len(rows)))
			except Exception as e:
				cursor.execute(self.insertPageSql, (curLink['letter'],curLink['page'],-1))
				print('Błąd litera: %s strona: %s' % (curLink['letter'],curLink['page']))
				print(e)
			
			#db commit
			db.commit()
			
			#lets go to the next link
			curLink=self.getNextLink()
			
	def run(self):
		import multiprocessing

		thread = multiprocessing.Process(target=self.deamon)
		thread.start()
			
			
app1=app()
app1.run()
