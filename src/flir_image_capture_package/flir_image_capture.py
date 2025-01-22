"""
This module provides functionality for handling FLIR camera.

Modules:
    threading: Provides threading capabilities.
    PySpin: Provides access to the FLIR camera SDK.
    FlirCamParameters: Contains the FlirCamParam class for managing camera parameters.
"""
import threading
import queue
import h5py
import PySpin
import cv2
from PySpin import Camera
from flir_camera_parameter_package.flir_camera_shutter_parameters import ShutterTimeControl
from flir_camera_parameter_package .flir_camera_parameters import FlirCamParam
from thors_lab_led_control_package.led_states import StateBlue ,StateGreen,StateRed
class FlirCamera():
    """A class to handle FLIR camera operations including taking snapshots and saving images."""
    def __init__(self,param:FlirCamParam):
        self._param = param
        self.stop_thread= False
        self._system= PySpin.System.GetInstance()
        self._cam:Camera = self._system.GetCameras()[0]
        #self.read_obj = ReadH5()
        self._cam.Init()
        #self.weight= self.read_obj.read_files("weight.h5","0")
        self._lock = threading.Lock()
        self._shutter = ShutterTimeControl(self._cam)
        if not param.default_shutter_time: #Check if manual shutter time is requested         
            self._cam =self._shutter.manual_shutter(self._cam,param.shutter_time)
        else:
            self.cam = self._shutter.auto_shutter_time(self._cam)

    
    def activate(self,feed = True, record = True, led_flash = False):
        """_summary_ 
        takes "n" number of images. "n"  can be defined in "flir_camera_ prameter" class
        Args:
            param (FlirCamParam): Instance of FlirCamPara class """

        self._cam.BeginAcquisition()       
        data_queue_disp = queue.Queue() if feed else None
        data_queue_write = queue.Queue() if record else None
        state = self.__led_state() if led_flash else None
        display_thread = threading.Thread(target=self.__display_images,args =(data_queue_disp,))
        writer_process = threading.Thread(target = self.__save, args = (self._param.path,data_queue_write))
        if feed:           
             display_thread.daemon = True
             display_thread.start()
        if record:           
            writer_process.daemon = True       
            writer_process.start()
        print("Taking ", self._param.snap_count, " Images")
        for i in range(self._param.snap_count):
            print(i)
            if led_flash:
                state.activate() 
                state = state.get_next_state()

            image = self.__capture(self._cam)
            if not image.IsIncomplete() &  i>8:   
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
            state.deactivate()

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
        while thr:
            try:
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
                    image = self.process(image_flag, images_batch)
                    cv2.imshow('stream', image)
                    cv2.waitKey(1)
            except Exception as e:
                print(f"Error in display thread: {e}")
                break
        cv2.destroyAllWindows()  # Close all OpenCV windows

                
    def process(self,flag:list,image_batch):
        b= 0#flag.index("B")
        g= 1#flag.index("G")
        r= 2#flag.index("R")
        image = cv2.merge([image_batch[g],image_batch[r],image_batch[b]])
        #image =  Processing.corrrect_color(image,self.weight) 
        return image                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                           

    def reduce_image_quality(self, image):
        """Reduces the quality of the image for smoother display.

        Args:
            image: The image captured by the camera.

        Returns:
            A reduced-quality version of the image.
        """
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
    
    def __led_state(self):
        _b= StateBlue()
        _g= StateGreen()
        _r=StateRed()
        _b.set_next_state(_g)
        _g.set_next_state(_r)
        _r.set_next_state(_b)
        return _b
    

