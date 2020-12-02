import pygame
import sys
import os
import socket
import random
import time
import math

from PIL import ImageOps, Image
import exifread
import logging

from image import ImageLib, Img, Fader
from log import Log
from imu import IMU
from settings import Settings 
from APIconnect import APIconnection

global DIR, MIN_SEC_FADE, MAX_SEC_FADE, SENSITIVITY, FADEIN_SPEED, FADEOUT_SPEED, AB_ID, DIM_X, DIM_Y

DIR = "Pola2020/python/"

"""Define initial settings here. The first image will be displayed using this setup. 
After this, the settings will be read from the csv file in Drive. """

AB_ID = "Standard"
MIN_SEC_FADE = 10
MAX_SEC_FADE = 20
SENSITIVITY = None #Not currently used, could be adapted for adjusting IMU sensitivity
FADEIN_SPEED = 70
FADEOUT_SPEED = 70

"""Define display resolution"""
DIM_X = 720
DIM_Y = 720

global log, film, display, setup, api

#Initialize pygame display and make it fullscreen
display = pygame.display.set_mode((DIM_X, DIM_Y), pygame.FULLSCREEN)
#Hide mouse
pygame.mouse.set_visible(False)  

#Create overlay film
film = Fader(DIM_X, DIM_Y)
log = Log()

#Wait x ms between screen refreshes
global wait
wait = 20    

def fadeIn(image):
    """Fade in the current image"""
    global AB_ID, FADEIN_SPEED, log
    log.logevent("Fade in", AB_ID)
    
    #Turn on backlight
    os.system("echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power")
    
    #Setup dark overlay
    alpha = 255
    film.setAlpha(alpha)
    display.blit(film.getFader(), (0, 0))    
        
    while alpha > 0:

        display.blit(image.getImage(),(image.x, image.y))
        film.setAlpha(alpha)
        display.blit(film.getFader(), (0, 0))
        """You can tweak these threshholds to change the speed and steps of the fade. 
        Currently, it is slow in the beginning and quicker towards the end. 
        """
        if alpha > 200:
            alpha -= 2
        elif alpha > 100:
            alpha -= 4
        elif alpha > 0:
            alpha -= 6

        #Currently, it takes 70 display updates to completely fade in an image.
        pygame.time.delay(int(FADEIN_SPEED/70))
        checkEvents()
        pygame.display.update()
        
def fadeOut(image):
    """Fade out the current image"""
    global AB_ID, FADEOUT_SPEED, log
    log.logevent("Fade out", AB_ID)
    
    #Set overlay film transparency to 0.
    alpha = 0
    while alpha < 255:
              
        display.blit(image.getImage(), (image.x, image.y))
        film.setAlpha(alpha)
        display.blit(film.getFader(), (0, 0))
        """You can tweak these threshholds to change the speed and steps of the fade. 
        Currently, it is slow in the beginning and quicker towards the end. 
        """          
        if alpha < 50:
            alpha += 2
        elif alpha < 200:
            alpha += 4
        elif alpha < 255:
            alpha += 6
            
        #Currently, it takes 70 display updates to completely fade out an image. 
        pygame.time.delay(int(FADEOUT_SPEED/70))
        checkEvents()
        pygame.display.update()
        
    #Turn off backlight
    os.system("echo 1 | sudo tee /sys/class/backlight/rpi_backlight/bl_power")
    
   
def checkEvents():
    """Checks keyboard input (used while debugging)"""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            os.system("echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power")
            log.logevent("Exit", AB_ID)
            pygame.display.quit()
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                os.system("echo 0 | sudo tee /sys/class/backlight/rpi_backlight/bl_power")
                log.logevent("Exit", AB_ID)
                pygame.display.quit()
                pygame.quit()
                sys.exit()
                
def hoursToMs(hours):
    ms = hours * 60*60*1000
    return ms

                
def main():
    """Main loop"""
    global AB_ID, MIN_SEC_FADE, MAX_SEC_FADE, log, wait
    
    #Launch intro image - to make it clear that the launch is on its way. Also: Feel free to update the image. I 
    introImage = Img("Img/polaIntro.jpeg")
    fadeIn(introImage)
    
    screenIsDark = True
    shakes = 0
    
    #Setup image library and API connection
    api = APIconnection()
    setup = Settings(api)    
    imageList = ImageLib(api)
    log.connect(api)
    
    log.logevent("Init", AB_ID)
    currentImage = imageList.getNextImage()
    
    #Fade out intro image - to make it clear that the Pola is ready to go
    fadeOut(IntroImage)
    
    while True: 
       
        #If no image is displayed - wait for shake
        if screenIsDark == True:
    
            imu = IMU()
            
            if imu.checkShake() == True:
            
                log.logevent("Shake", AB_ID)
                fadeIn(currentImage)
                
                screenIsDark = False
                shakes = 0
                
                """After the image fade-in is complete, we do most of our expensive api calls.
                This way, Pola will immediately be ready to show the next image after fadeout, 
                and users will never have to wonder if their shakes are being registered, 
                or if it is working on some other process"""
                
                
                #Immediately fade out offline-notifications 
                #(we do not want these to be visible for 6 hours if the wifi returns in 6 minutes)
                if currentImage.offline: 
                    fadeoutTime = 0
                
                else: 
                    fadeoutTime = random.randint(MIN_SEC_FADE, MAX_SEC_FADE)
                print("Fadeout Time: ",fadeoutTime)
                fadeoutCounter = 0
                nextImage = imageList.getNextImage()
                
                #Update prototype settings (A/B etc)
                settingUpdate = setup.update()
                if settingUpdate[0]:
                    AB_ID = settingUpdate[1]
                    MIN_SEC_FADE = hoursToMs(settingUpdate[2])
                    MAX_SEC_FADE = hoursToMs(settingUpdate[3])
                    SENSITIVITY = settingUpdate[4]
                    FADEIN_SPEED = settingUpdate[5]
                    FADEOUT_SPEED = settingUpdate[6]                 
                
        #If an image is displayed, check if it is time to stop displaying it.
        else:
             
            if fadeoutCounter == fadeoutTime:     
                fadeOut(currentImage)
                #Update the current image to the one we loaded wile displaying the current image
                currentImage.delete()
                currentImage = nextImage
                screenIsDark = True
                fadeoutTime = math.inf
                fadeoutCounter = 0
            
            else:
                #update fadeout timer
                fadeoutCounter += 1

        checkEvents()   
        pygame.time.delay(wait)
        pygame.display.update()   

if __name__== "__main__":
    main()
