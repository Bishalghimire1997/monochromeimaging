from ParameterInterface import Parameters as par
from  WebCamParameters import WebCamParam as wcp
import cv2
import threading
import time 
from CameraInterface import Camera
class Snapshot(Camera):
    def __init(self):
        pass
    def capture(self,par):
     cap = cv2.VideoCapture(0)
     print("image captured")
    pass
  
    def save(self,par,img):
        
            
        time.sleep(10)
        print("image saved "+ str(img))
        pass
    def takeSnapshot(self,par):
        for i in range(par.getSnapCounts()):
            img=i
            self.capture(par)
            thread = threading.Thread(target = self.save, args = (par,img,))
            thread.start()

            
        pass
obj = Snapshot()
param = wcp()
obj.takeSnapshot(param)

    