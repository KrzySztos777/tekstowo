from io import StringIO, BytesIO
from lxml import etree
import requests

import re
import mysql.connector as connector
from math import ceil

class app:
	
	def __init__(self):
		self.url='https://tekstowo.pl'
		self.headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
			
		self.tracksPerPage=30
		self.timeout=12
		self.reconns=3

		self.dbHost="localhost"
		self.dbUser="biala"
		self.dbPassword="mewa"
		self.dbDatabase="tekstowo"
		
		self.selectPerformersSql= 'SELECT performers.id,performers.`name`, performers.tracks_no, performers.link from tracks right join performers on performers.id=tracks.performer group by performers.id  having count(tracks.id)<performers.tracks_no LIMIT %s, %s' # %(offset, count)
		self.insertTracksSql= 'INSERT INTO tracks(id,performer,name,yt_id_available,yt_id,link,page_no) VALUES(%s,%s,%s,%s,%s,%s,%s)'
	
	def getPerformerTracks(self,performerId,performerName,tracksNo,link):
		
		results=[]
		
		for page in range(1,ceil(tracksNo/self.tracksPerPage)+1):
			results.extend(self.getPerformerPage(page,performerId,performerName,link))
		
		return results
			
	def getPerformerPage(self,page,performerId,performerName,link):
		
		#variable to store results
		results=[]
		
		#generate proper link
		curLink=link[:-5]+',alfabetycznie,strona,%d.html' % page
		
		#try to get http response 
		reconn=0
		response=None
		while reconn<self.reconns:
			try:
				response = requests.get(self.url+curLink, headers=self.headers, timeout=self.timeout)		
			except:
				reconn+=1
			else:
				break
		
		#if requests fails
		if reconn==self.reconns:
			#print error
			print('CONNERROR %d %d %s' % (page,performerId,link))
			#terminate this method
			return results
		
		#else proceed...
		html=response.content.decode("utf-8")
		
		#preventing wrong root element for lxml
		if html[:15].lower()=='<!doctype html>':
			html=html[15:]
		
		#load html tree
		parser = etree.XMLParser(recover=True)
		tree=etree.parse(StringIO(html),parser)
		
		rows=tree.xpath("//div[contains(@class, 'right-column')]//div[contains(@class, 'ranking-lista')]//div[contains(@class, 'box-przeboje')]");
		
		#for every track on this page
		for row in rows:
			try:
				#unpack needed info and put them into variables
				a=row.xpath(".//a")[0]
				name=a.text[len(performerName)+3:-1]
				link=a.get('href')
				teledysk='YES' if len(row.xpath(".//i[@title='teledysk'][contains(@class, 'icon_kamera')]")) else 'NO'
				
				#puyt these vars to list prepared to SQL insert
				results.append((None,performerId,name,teledysk,None,link,page,))
			except:
				print('INFOERROR %d %s %s' %( performerId,performerName,a.text) )
		
		return results
		
	def tracksDeamon(self, offset, count):
		
		#create db cursor for selecting performers
		selectorDb = connector.connect(
		  host=self.dbHost,
		  user=self.dbUser,
		  password=self.dbPassword,
		  database=self.dbDatabase
		)
		selectorCursor = selectorDb.cursor()
		
		#create db cursor for inserting tracks
		insertorDb = connector.connect(
		  host=self.dbHost,
		  user=self.dbUser,
		  password=self.dbPassword,
		  database=self.dbDatabase
		)
		insertorCursor = insertorDb.cursor()
		
		#select performers to preec with
		selectorCursor.execute(self.selectPerformersSql % (offset,count))
		
		#loop for every performer
		performerRow=selectorCursor.fetchone()
		while(performerRow):
			
			#download performer's track
			trackRows=self.getPerformerTracks(*performerRow)
			#insert them to db
			insertorCursor.executemany(self.insertTracksSql,trackRows)
			insertorDb.commit()
			#go to the next one
			performerRow=selectorCursor.fetchone()
		
		print("KONIEC %d %d" % (offset,count))
	
	def getTracks(self):
		import multiprocessing

		threads=[]
		performersCount=4
		performersOffset=1
		
		#lets run as much as possible of deamons
		for offset in range(0,performersCount,performersOffset):

			thread = multiprocessing.Process(target=self.tracksDeamon,args=(offset,performersOffset,))
			threads.append(thread)
			thread.start()
			print('Thread started from %d and proceed next %d performers'%(offset,performersOffset,))
		
app1=app()
app1.getTracks()
