import threading
import queue
import time
import datetime
import signal
import sys
import re

from heapq import heappop,heappush

from domControl import *
import Sensor 
import Conection

NUMBER_TH=3
TH0_ID=0
TH1_ID=1
TH2_ID=2
TH3_ID=3

TIME_CALL=20
SERVER_REFRESh=30
HOUR_START=[10,30]
HOUR_FINISH=[20,30]


MIN_TEMP=3


class MainThread(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		
																	#Main thread variables:
		
		self.ths=[] 														
																			#Each thread arguments:
		
		self.th_heaps=[[] for i in range(NUMBER_TH)]
		self.th_locks=[threading.Lock() for i in range(NUMBER_TH)]
		self.th_events=[threading.Event() for i in range(NUMBER_TH)]
																		#Share with all thread:
		
		self.heap=[]
		self.h_lock=threading.Lock()
		self.work_event=threading.Event()								#Condition lock for the heap that MainThread is going to observe
		self.n_lock=threading.Lock()
		self.stop=threading.Event()
		start=HOUR_START[0]*60+HOUR_START[1]
		finish=HOUR_FINISH[0]*60+HOUR_FINISH[1]
		self.init_clenner_hour=(finish*60-start*60)/4
		self.clean=False
		self.blinds=False
		self.heating=False
		self.rexpresion=re.compile('(21[12])?(5[01][0-9])?(7[0-9][2-9])?(9[0-9][0-9])?')	

		#signal.signal(signal.CTRL_C_EVENT, self.stop.set())
		signal.signal(signal.SIGINT,  self.exit_gracefully)
		#signal.signal(signal.SIG_DFL,  self.exit_gracefully)
	
	def exit_gracefully(self, frame,other):
	 	self.stop.set()
	 	sys.exit(0)

	def run(self):
		
		SensorTh=Sensor.SensorThread(TH1_ID,self.heap,self.h_lock,self.work_event,self.th_heaps[TH1_ID-1],					#Init all threads
									self.th_locks[TH1_ID-1],self.th_events[TH1_ID-1],self.stop)
		
		ConnectionTh=Conection.ConectionThread(TH2_ID,self.heap,self.h_lock,self.work_event,self.th_heaps[TH2_ID-1],
												self.th_locks[TH2_ID-1],self.th_events[TH2_ID-1],self.stop)
		
		DomControlTh=domControl.DomControl(TH3_ID,self.heap,self.h_lock,self.work_event,self.th_heaps[TH3_ID-1],
												self.th_locks[TH3_ID-1],self.th_events[TH3_ID-1],self.stop)
		lastTimeCall=0
		lastRefresh=0 
		SensorTh.start()
		ConnectionTh.start()
		DomControlTh.start()

		hour_init_min= HOUR_START*60
		hour_finish_min=HOUR_FINISH*60
		while not self.stop.isSet():
			self.h_lock.acquire()
			while len(self.heap)==0:
				self.work_event.clear()
				self.h_lock.release()
				self.work_event.wait() 
				self.h_lock.acquire()
			(th_id,action,data)=heappop(self.heap)
			self.h_lock.release()


			now = datetime.datetime.now()

			print("From id: ",th_id,"do the action: ", action)
			if th_id==TH1_ID:
				print('Photo catched... Send it',action,data)
				addToHeap(self.th_heaps[TH2_ID-1],(TH0_ID,'motion', data),self.th_locks[TH2_ID-1],self.th_events[TH2_ID-1])
			
			if th_id==TH2_ID:
				print('Conection Thread Packet')
				if action=='request':
					print('request')
					#process the request
				if action=='time':
					temp = data['main']['temp']
					if self.rexpresion.match(str(data['weather'][0]['id'])):
						addToHeap(self.th_heaps[TH3_ID-1],(TH0_ID,'blinds',''),self.th_locks[TH3_ID-1],self.th_events[TH3_ID-1])
					if temp<=MIN_TEMP:
						addToHeap(self.th_heaps[TH3_ID-1],(TH0_ID,'heating',''),self.th_locks[TH3_ID-1],self.th_events[TH3_ID-1])
					print("Time request")
			
			if th_id==TH3_ID:
				print("Info de el control de la casa")
			
			if lastTimeCall+TIME_CALL<=now.hour*60+now.minute:
				lastTimeCall=now.hour*60+now.minute
				addToHeap(self.th_heaps[TH2_ID-1],(TH0_ID,'time',''),self.th_locks[TH2_ID-1],self.th_events[TH2_ID-1])
				
			if not self.clean and self.init_clenner_hour<now.hour*60+now.minute:
				addToHeap(self.th_heaps[TH3_ID-1],(TH0_ID,'clean',''),self.th_locks[TH3_ID-1],self.th_events[TH3_ID-1])
				self.clean=True;

			if lastRefresh+SERVER_REFRESh<=now.hour*60+now.minute and lastTimeCall!=0:
				lastRefresh=now.hour*60+now.minute
				json= {'blinds':self.blinds,
						'heating':self.heating,
						'clean':self.clean}
				addToHeap(self.th_heaps[TH2_ID-1],(TH1_ID,'state',json),self.th_locks[TH2_ID-1],self.th_events[TH2_ID-1])



def addToHeap(heap,data,lock,event):
	lock.acquire()
	heappush(heap,(data))	
	print("Tarea mandada",data)
	if not event.isSet():
		lock.release()
		event.set()
	else:
		lock.release()
"""
def exit_gracefully(self, frame):
 	MainThread.exit_gracefully()
"""
if __name__=='__main__':
	#signal.signal(signal.SIG_IGN,  exit_gracefully)
	#signal.signal(signal.SIG_DFL,  exit_gracefully)
	MainThread=MainThread()
	MainThread.start()
