import multiprocessing.process
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
from flir_image_capture_package.flir_image_capture import FlirCamera
from image_processing_package.processing_routines import Processing
import cv2
import time
import multiprocessing
import numpy as np
from h5_file_format_package.h5_format import H5Fromat
from h5_file_format_package.h5_format_read import ReadH5

"""Idea is to stream the video live and apply the processing algorithm on real time 
     1. camera captures a image as an independent process 
     2. the image is prosessed as an independent process
"""
class Stream ():
    def __init__(self ):
        self.__param  = FlirCamParam()
        self.__param._snap_count = 3000
        self.__process = Processing()
        self.fps =10
        self.stream = True
        pass 
    def sream(self):
        lock = multiprocessing.Lock()
        process1 = multiprocessing.Process(target = self.capture_image)
        process2 = multiprocessing.Process(target = self.play_video)
        process1.start()
        time.sleep(5)
        process2.start()

    def stream_color(self):
        pass
    def play_video(self):
        print("video play back activated ")
        obj2 = ReadH5()  
        i= 0
        while self.sream:
            
            b= obj2.read_image_multi("image.h5",str(i))
            g= obj2.read_image_multi("image.h5",str(i+1))
            r=obj2.read_image_multi("image.h5",str(i+2))
            i=i+1
            image = self.__process.image_reconstruction(b,g,r)                                                                    
            delay = int(1000 /self.fps)
            cv2.imshow('Image Stream', image)
            if cv2.waitKey(delay) & 0xFF == ord('q'):
                print("Playback interrupted.")
                break
                cv2.destroyAllWindows()

    def capture_image( self):
        self.__camera = FlirCamera(self.__param)       
        print("camra activated")
        self.__camera.take_snapshot_single()


 