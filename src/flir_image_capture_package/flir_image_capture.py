"""
This module provides functionality for handling FLIR camera.

Modules:
    threading: Provides threading capabilities.
    PySpin: Provides access to the FLIR camera SDK.
    FlirCamParameters: Contains the FlirCamParam class for managing camera parameters.
"""
import time
import threading
import queue
import h5py
import PySpin
import cv2
from PySpin import Camera
from h5_file_format_package.h5_format import H5FormatRead
from flir_camera_parameter_package.flir_camera_shutter_parameters import ShutterTimeControl
from flir_camera_parameter_package .flir_camera_parameters import FlirCamParam
from thors_lab_led_control_package.led_state_pulse import StateMachinePulse
class FlirCamera():
    """A class to handle FLIR camera operations including taking snapshots and saving images."""
    def __init__(self,param:FlirCamParam):
        self._param = param
        self.stop_thread= True
        self._system= PySpin.System.GetInstance()
        self._cam:Camera = self._system.GetCameras()[0]
        self.read_obj = H5FormatRead()
        self._cam.Init()
        self.weight= self.read_obj.read_files("weight.h5","0")
        self._lock = threading.Lock()
        self._shutter = ShutterTimeControl(self._cam)
        self._cam.BeginAcquisition()

        if not param.default_shutter_time: #Check if manual shutter time is requested
            self._cam =self._shutter.manual_shutter(self._cam,50000) #150000
        else: 
            self.cam = self._shutter.auto_shutter_time(self._cam)
       
    def activate(self,feed = True, record = True, led_flash = False):
        """_summary_ 
        takes "n" number of images. "n"  can be defined in "flir_camera_ prameter" class
        Args:
            param (FlirCamParam): Instance of FlirCamPara class """
        data_queue_disp = queue.Queue() if feed else None
        data_queue_write = queue.Queue() if record else None
        state = StateMachinePulse().get_first_state() if led_flash else None
        display_thread = threading.Thread(target=self.__display_images,args =(data_queue_disp,))
        writer_process = threading.Thread(target = self.__save,
                                          args = (self._param.path,data_queue_write))
        if feed:
            display_thread.daemon = True
            display_thread.start()
        if record:
            writer_process.daemon = True
            writer_process.start()
        print("Taking ", self._param.snap_count, " Images")
        for i in range(self._param.snap_count):
            if led_flash:
                 state.activate()
            image = self.__capture(self._cam)
            state = state.get_next_state()
            if (not image.IsIncomplete()):
                #state_flag =state.get_flag()
                if feed:
                    image_reduced= self.reduce_image_quality(image)
                    data_queue_disp.put(("h",image_reduced))
                if record:
                    data_queue_write.put((str(i),image))
            else:
                print(image.IsIncomplete())
            #state= state.get_next_state()
        if led_flash:
            StateMachinePulse().close_resources()
        self._cam.EndAcquisition()
        self._cam.DeInit()
        del self._cam
        self._system.ReleaseInstance()
    def __save(self, path, data_queue):
        """Saves the images in .h5 file format."""
        thr = True
        with h5py.File(path, "w") as h5_file:
            while thr:
                try:
                    item = data_queue.get(timeout=5)  # Add a timeout to prevent indefinite blocking
                except queue.Empty:
                    print("Queue is empty, terminating.")
                    break
                if item is None:
                    thr = False
                    break  # Terminate the loop when a None item is received
                itter, image = item
                # Save the image in the HDF5 file
                image_array = image.GetNDArray()
                h5_file.create_dataset(itter, data=image_array)
    def __display_images(self, data_queue):
       
        thr = True
        fps = 20
        time_t = []
        while thr:
            start =time.time()
            images_batch = []  # List to hold the three images
            image_flag = []
            for _ in range(3):  # Get three images at once
                item = data_queue.get(block = True)
                if item is None:
                    thr = False  # Exit the loop if None item is received
                flag, image = item
                images_batch.append(image)  # Append the image to the batch
                image_flag.append(flag)
            if images_batch:
                image = self.__processing(image_flag, images_batch)
                delay = int(1)
                cv2.imshow('stream', image)
                cv2.waitKey(delay)
                time_t.append(time.time()-start)
                print("average time to display = ",sum(time_t)/len(time_t))
               
        cv2.destroyAllWindows()  # Close all OpenCV windowss
        
        
    def __processing(self,flag:list,image_batch):
        b= 0#flag.index("B")
        g= 1#flag.index("G")
        r= 2#2flag.index("R")
        image = cv2.merge([image_batch[g],image_batch[r],image_batch[b]])
        #image =  Processing.corrrect_color(image,self.weight)
        return image                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                            

    def reduce_image_quality(self, image):
        """Reduces the quality of the image for smoother display.
        Args:
            image: The image captured by the camera.
        Returns:
            A reduced-quality version of the image."""
        image_array = image.GetNDArray()
        reduced_image = cv2.resize(image_array, (640, 480), interpolation=cv2.INTER_LINEAR)
        return reduced_image

    def __capture(self,camera):
        """_summary_
        Args:
        camera (_type_): _description_
        Returns:
            _type_: _description_ returs images
        """
        return camera.GetNextImage()
    
  
    

