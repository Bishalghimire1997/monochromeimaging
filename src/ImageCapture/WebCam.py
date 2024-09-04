from ParameterInterface import Parameters as par
from CameraInterface import Camera
from  WebCamParameters import WebCamParam as wcp

import threading
import time 
import cv2

class Snapshot(Camera):
    def __init(self):
        pass
    def capture(self,par):
     cap = cv2.VideoCapture(0)
     if not cap.isOpened():
      print("Error: Could not open camera.")
      exit() 
      ret, frame = cap.read()
      if ret:
         return frame,cap
      else:
         print("Error: Could not open camera.")
         exit() 

    
  
    def save(self,par,fromCapture):
     cv2.imwrite("Image", fromCapture[0])
     fromCapture[1].release()
       
        
            
        
    def takeSnapshot(self,par):
        for i in range(par.getSnapCounts()):
            
            fromCam= self.capture(par)
            thread = threading.Thread(target = self.save, args = (par,fromCam,))
            thread.start()

            
        pass


    