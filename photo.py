import time
import pygame
import pygame.camera
from pygame.locals import *

pygame.camera.init()
#cams=pygame.camera.list_camera() #Detectar si hay cámaras conectadas
try:
	cam = pygame.camera.Camera('/dev/video0')
	cam.start()
	img = cam.get_image()	
	pygame.image.save(img,time.strftime("%Y-%m-%d_%H:%M:%S.jpg", time.gmtime()))
finally:
	cam.stop()