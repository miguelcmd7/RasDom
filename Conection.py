#6357300 id Api A Coruña
#a49f0219a5cf208b5525b4acdf553a64 API key
import sys
import time
import base64
import requests
import threading
import json
from pprint import pprint
from heapq import heappush,heappop

apikey='YourAPI_KEY_from_openweather'
cityId='cityidfromopenweather'

url='http://api.openweathermap.org/data/2.5/weather'

urlPhotos='http://localhost:8080/photo'
urlState='http://localhost:8080/homestate'



def post():
	r=requests.post(urlPhotos,data={'number':1,'image':''})
	if (r.status_code == requests.codes.ok):
		print("Enviado!!")


def postPhoto(filename):
	try:
		image=open(filename,'rb').read()	
		r=requests.post(urlPhotos,data={'datetime':time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime()),'picture':base64.b64encode(image)})
	except:
		image=''
		r=requests.post(urlPhotos,data={'number':1,'image':image})
	if (r.status_code == requests.codes.ok):
		print("Enviado!!")

def postState(time_json,data):
	json={'blinds':data['blinds'],
			'temp':time_json['main']['temp'],
			'time':time_json['weather'][0]['main'],
			'clean':data['clean'],
			#'heating':data['heating'],
			'heating':data['heating'],
			'datetime':time.strftime("%Y-%m-%d_%H:%M:%S", time.gmtime()) }

	r=requests.post(urlState,data=json)
	if (r.status_code == requests.codes.ok):
		print("Enviado Estadoo!!")
	
	


def getWeather():
	r=requests.get(url,params={'id':cityId,'units':'metric','APPID':apikey});
	print(r.url)
	if (r.status_code == requests.codes.ok):
		#print(r.json)
		return r.json()
	return ''	

def getWeather2():
	with open('jsonTest/weather.json') as json_data:
		d = json.load(json_data)
		print(d)
	#print(r.json)
	return d
	

class ConectionThread(threading.Thread):

	def __init__(self,thread_id,main_h,h_lock,work_event,my_h,my_lock,my_event,stop):
		threading.Thread.__init__(self)
		self.thread_id=thread_id
		self.main_h=main_h
		self.h_lock=h_lock
		self.work_event=work_event
		self.my_h=my_h
		self.my_lock=my_lock
		self.my_event=my_event
		self.stop=stop
		self.time_json=''

	def run(self):
		n=0
		while not self.stop.isSet():				
			self.my_lock.acquire()
			while len(self.my_h)==0:
					self.my_event.clear()
					self.my_lock.release()
					print("Esperando por tareas a conectar")
					time.sleep(3)
					if self.stop.isSet():
						sys.exit(0)
					self.my_event.wait() 
					self.my_lock.acquire()
			
			(thread_id,order,data)=heappop(self.my_h)	
			
			self.my_lock.release()
			if order=='motion':
				if data!='':
					print('Enviando:',data)
					postPhoto(data)
				else:
					print('Enviando: nada')
					#post()
			if order=='time':
				print("Pidiendo tiempo")
				self.time_json=getWeather2()
				self.h_lock.acquire()
				heappush(self.main_h,(self.thread_id,'time',self.time_json))
				if not self.work_event.isSet():
					self.h_lock.release()
					self.work_event.set()
				else:
					self.h_lock.release()
			if order=='state':
				postState(self.time_json,data)
			n=n+1
