
import os
import PySpin
import sys  
import threading
from FlirCamParameters import FlirCamParam


class FlirCAmera():
    def __init___():
        pass

    def takeSnapshot(self,param): 
        system = PySpin.System.GetInstance()      
        cam_list = system.GetCameras() 
        par =FlirCamParam()    
        cam =   cam_list[0]  
        cam.Init() 
        processor = PySpin.ImageProcessor()       
        processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)         
        cam.BeginAcquisition()
        for i in range(param.getSnapCounts()):
            image = self.capture(cam)
            thread = threading.Thread(target = self.save, args = (image,processor,i)).start()
                   
        cam.EndAcquisition()
        cam.DeInit()  
        del cam    
        cam_list.Clear()    
        system.ReleaseInstance()   


    def save(self,image_result,processor,itter):
     
                    
         image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)                
         filename = 'Acquisition-%d.jpg' % itter
         image_converted.Save(filename)  
                                
         image_result.Release()  

    def capture(self,cam):
        return cam.GetNextImage(1000)
par = FlirCamParam()
cam = FlirCAmera()
cam.takeSnapshot(par)
