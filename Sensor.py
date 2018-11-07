import threading

import sys
import RPi.GPIO as GPIO
import time
import pygame
import pygame.camera
from pygame.locals import *

from heapq import heappush


def takePhotho():
	pygame.camera.init()
	filename=0
	try:
		cam = pygame.camera.Camera('/dev/video0')
		cam.start()
		filename = time.strftime("./photos/%Y-%m-%d_%H:%M:%S.jpg", time.gmtime())
		img = cam.get_image()
		pygame.image.save(img, filename)
		

	finally:
		cam.stop()
		return filename



class SensorThread(threading.Thread):
	
	def __init__(self,thread_id,main_h, h_lock,work_event,my_h,my_lock,my_event,stop):
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
		#GPIO.setmode(GPIO.BCM)
		# GPIO.setup(4, GPIO.IN,pull_up_down=GPIO.PUD_DOWN) #Pin 4 para recogida de datos, inicialmenete sin movimiento
		#time.sleep(2)  # to stabilize sensor
		h = []
		n = 0
		while not self.stop.isSet():
		    # print(GPIO.input(4))
		    # if GPIO.input(4):
		    if True:
		    	print("Motion Detected...")
		    	file = takePhotho()
		    	self.h_lock.acquire()
		    	heappush(self.main_h, (1,'motion',file))
		    	#heappush(self.main_h, (self.thread_id, 'foto','2018-04-04_09:20:46.jpg'))
		    	self.h_lock.release()
		    	if not self.work_event.isSet():
		    		self.work_event.set()
		    	time.sleep(20)
		    	n = n + 1
		    time.sleep(0.2)