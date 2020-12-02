
class Settings():
   def __init__(self, api):
      """Get settings from online library, 
      Can be used for ex. A/B testing"""
      self.name = "settings.csv"
      self.api = api
        
   def update(self):
      """Read settings file and updatge parameters"""
      try: 
         self.api.getSettings(self.name)
            
         f = open(self.name, 'r')
         settings = f.readlines()
         f.close()
         
         info = []
         for line in settings: 
            line = line.split(',')
            info.append(line)
        
         ab_id = info[0][1]
         min_sec_fade = int(info[1][1])
         max_sec_fade = int(info[2][1])
         sensitivity = int(info[3][1])#Sensitivity is not currently being used. 
         fadein_speed = int(info[4][1])
         fadeout_speed = int(info[5][1])
         
         
         #print(ab_id, min_sec_fade, max_sec_fade, sensitivity, fadein_speed, fadeout_speed)
         return True, ab_id, min_sec_fade, max_sec_fade, sensitivity, fadein_speed, fadeout_speed
   
     
      except: 
         print("Could not read settings file ", self.name)
         return False, None
       
       
       
        