import sys
import threading
import signal
import time
from heapq import heappush,heappop


class DomControl(threading.Thread):

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


	
	def run(self):
		n=0
		while not self.stop.isSet():				
			self.my_lock.acquire()
			while len(self.my_h)==0:
					self.my_event.clear()
					self.my_lock.release()
					print("Esperando por tareas a conectar2")
					time.sleep(3)
					if self.stop.isSet():
						sys.exit(0)
					self.my_event.wait() 
					print("Ya tengo tareas!!")
					self.my_lock.acquire()
			(thread_id,order,name)=heappop(self.my_h)				
			self.my_lock.release()
			if order=='blinds':
				print("Cerrando ")
			if order=='clean':
				print("Vaccum cleaner running")
			if order=='heating':
				print("Calefaccion funcionando")
