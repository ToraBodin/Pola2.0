import pygame
import exifread
import os
import urllib.request
from settings import * 
from PIL import Image
#import heicTojpg as h2jpg

class ImageLib():
    def __init__(self, api):
        """
        Loads images from online path or from alternative offline path
        """
        self._onlinePath = "Img/"
        self._offlinePath = "ImgOffline/"
        #self._path = path
        self._api = api
        self._images = []
        self._currentIndex = -1
        self._image = None
        
    def getImages(self):
        """Goes into provided directory and returns list with all image paths"""
        pass
        
        #self._images = []
        
        #try:
            #self._images = os.listdir(self._dir)
            #self._path = self._dir
            
        #except:
            ## Use offline folder
            #print("No internet connection available")
            #self._images = os.listdir(self._altDir)
            #self._path = self._altDir
            
        #print("Directory: ", self._path, "\n", "Images found:  ", len(self._images))

        
    def getNextImage(self):
        """Updates image to the next one"""
        self._images = self._api.updateImageNames()
        
        #Get index from local txt file. 
        #This ensures that the image queue does not reset if the Pola restarts.
        try: 
            f = open("memoryIndex.txt", 'r')
            self._currentIndex = int((f.read()))
            f.close()
        except: 
            self._currentIndex = -1
    
        self._currentIndex = (self._currentIndex + 1) % len(self._images)
        
        f = open("memoryIndex.txt", 'w')
        f.write(str(self._currentIndex))
        f.close()
        
        
        #If there is an internet connection, go online. If not, get the "no wifi error"- image queue
        try:
            urllib.request.urlopen('http://torabodin.com/')
            try: 
                imageName = self._api.downloadImage(self._currentIndex)
                print(1, imageName)
                self._image= self.loadImage(imageName, True)
                print (self._image)
                
            except: 
                self._image = self.getNextImage()
              
        except:
            self._image = self.loadImage(None, False)
      
        
        return self._image
    
    def loadImage(self, name, online):
        if online: 
            image = self._onlinePath + name
        
        else:
            image = self._offlinePath + str(self._currentIndex % 3) + ".jpeg"
        
        """
        Converting HEIF and HEIC images does not work at the moment. 
        If they are present, they will be downloaded and then just ignored, as python cannot open them. 
        """
        #image = h2jpg.convert(image, None, 100)    
        
        pygameImage = Img(image)
        pygameImage.offline = not online
        return pygameImage
    
    
class Img():
    """Image class. Loads pygame image from image filename"""

    def __init__(self, filename):
        print(2, filename)
        self._name = filename
        self.x = 0
        self.y = 0
        self._image = pygame.image.load(self._name)
        self.offline = True
        
        
        self.rotate()
        self.scaleZoomed(720, 720)
        self.positionZoomed()
        
    def delete(self):
        """Used to delete image after it has been displayed, 
        so that we do not accidentally fill up our PI memory with old photos. 
        Do note that images that are not showed (ex. heic images) will not be deleted either at the moment. """
        os.system("rm "+self._name) 

    def rotate(self):
        """Rotate image based on exif tags (if any) """
        val = None
        try:
            """Get rotation tags"""
            f = open(self._name, 'rb')
            tags = exifread.process_file(f)
            f.close()
            orientation = tags["Image Orientation"]
            val = orientation.values

        except:
            return True

        if 3 in val:
            rotation = 180

        elif 6 in val:
            rotation = 270

        elif 8 in val:
            rotation = 90

        else:
            rotation = 0

        self._image = pygame.transform.rotate(self._image, rotation)

    def scaleZoomed(self, bx, by):
        """Scales the image so that it will fill the entire screen. 
        Image will be cropped if neccessary"""
        ix, iy = self._image.get_size()
        if ix > iy:
            # fit to width
            scale = bx/float(iy)
            sy = scale * ix
            if sy > by:
                scale = by/float(iy)
                sx = scale * ix
                sy = by
            else:
                sx = bx
        else:
            # fit to height
            scale = by/float(ix)
            sx = scale * iy
            if sx > bx:
                scale = bx/float(ix)
                sx = bx
                sy = scale * iy
            else:
                sy = by

        self._image = pygame.transform.scale(self._image, (int(sx), int(sy)))
        
    def positionZoomed(self):
        """Positions image so that the middle-part of the image will be shown.
        Image will be cropped if neccessary"""
        rect_size = self._image.get_rect()

        if rect_size.width > 720:
            self.x = (int((720 - rect_size.width ) / 2))

        if rect_size.height > 720:
            self.y = (int((720 - rect_size.height) / 2))

    
    def getImage(self):
        """returns image object"""
        return self._image
    
    """
    The functions that are commented out can be used to display the entire image without cropping it. 
    This version will provide black borders if the image is not square. 
    """
        
    #def scaleFull(self, bx, by):
        #""" Scales image to fit into the frame.
         #This method will retain the original image's aspect ratio 
         #Black borders will be shown on sides/top/bottom when neccessary"""
        #ix, iy = self._image.get_size()
        #if ix > iy:
            ## fit to width
            #scale_factor = bx/float(ix)
            #sy = scale_factor * iy
            #if sy > by:
                #scale_factor = by/float(iy)
                #sx = scale_factor * ix
                #sy = by
            #else:
                #sx = bx
        #else:
            ## fit to height
            #scale_factor = by/float(iy)
            #sx = scale_factor * ix
            #if sx > bx:
                #scale_factor = bx/float(ix)
                #sx = bx
                #sy = scale_factor * iy
            #else:
                #sy = by

        #self._image = pygame.transform.scale(self._image, (int(sx), int(sy)))

    
    #def positionFull(self):
    #"""Positions scaled image in center of screen. 
    #Black borders will be shown on sides/top/bottom when neccessary"""
        #rect_size = self._image.get_rect()

        #if rect_size.width < 720:
            #self.x = abs(int((rect_size.width - 720) / 2))

        #if rect_size.height < 720:
            #self.y = abs(int((rect_size.height - 720) / 2))

        #print("X and Y position: ", self.x, self.y)


class Fader():
    """The"fader film" that goes on top of the image to change opacity"""

    def __init__(self, x, y):
        self._film = pygame.Surface((x, y))
        self._alpha = None
        self.setAlpha(0)

    def getFader(self):
        """returns fader object"""
        return self._film

    def setAlpha(self, alpha):
        """set fade opacity"""
        self._alpha = alpha
        self._film.set_alpha(self._alpha)
