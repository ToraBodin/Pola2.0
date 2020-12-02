import time

class Log():
   def __init__(self):
      """
      Setup log system for A/B testing
      Has online + offline info gathering
      """
      self.name = "PolaLog.csv"
      self.api = ""
      
      
   def connect(self, api):
      self.api = api 
      
   def logevent(self, eventInfo, ID):
      """Log an event.
      Current format is timestamp, type of event (Init/Fade-in/Fade-out/Exit), setting ID
      """ 
      year, mon, day, hour, mi, sec, wday, yday, isdst = time.localtime()
      timestamp = ("%i-%i-%i , %i:%i:%i" % (year, mon, day, hour, mi, sec))
      
      logData = timestamp + "," + eventInfo + "," + ID + "\n"
      print(logData)
      
      
      f = open(self.name, "a+")
      f.write(logData)
      f.close()
         
     
      """
      TBD - implement log file upload to drive folder//wherever you'd like to put it. 
      Might not be neccessary to do this immediately whn the event occurs, perhaps only when a new image is loaded?
      """
      #self.api.sendLogfile(self.name)
                  
           
