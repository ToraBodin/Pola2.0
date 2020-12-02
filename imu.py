import board
import busio
import adafruit_mpu6050
import log
from settings import * 
import time

class IMU():
    """Acceleorometer class"""
    def __init__(self):
        """Sets up connection to IMU sensor"""
        try:  
            self.i2c = busio.I2C(board.SCL, board.SDA)
            self.mpu = adafruit_mpu6050.MPU6050(self.i2c)
            
        except: 
            print("No IMU connection")
        
        
    def getGyro(self):
        """Get gyro input"""
        return self.mpu.gyro
    
    def getAcc(self):
        """Get accelerometer input"""
        return self.mpu.acceleration
    
    
    def checkShake(self):
        """Check for shake"""
        shaken = False
        #Sensor sensitivity threshold
        """
        These values can definitely be modified. You can also add specific 
        threshholds for the different x/y/z-values if you'd like. 
        """
        gyroThresh = 90
        accThresh = 15
        try:
            for value in self.getGyro():
                #print(value)
                if abs(float(value)) > gyroThresh:
                    #print(value)
                    shaken = True
                  
            for value in self.getAcc():
                #print(value)
                
                if abs(float(value)) > accThresh:
                    #print(value)
                    shaken = True     
        except: 
            print("No IMU values")
            pass   
                
        return shaken
    
    def test(self):
        """For calibrating sensitivity (rewrite so that it is useful)"""
        while True: 
            gyX, gyY, gyZ = self.getGyro()
            accX, accY, accZ = self.getAcc()
            print("Gyroscope: X: %.2f  Y: %.2f  Z: %.2f" %(gyX,gyY,gyZ))
            print("Accelerom: X: %.2f  Y: %.2f  Z: %.2f" %(accX,accY,accZ))
            
            time.sleep(0.5)
            