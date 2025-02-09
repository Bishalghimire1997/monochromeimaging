import PySpin
from PySpin import Camera 
import cv2
import h5py
import threading
from flir_camera_parameter_package.flir_camera_shutter_parameters import ShutterTimeControl
from flir_camera_parameter_package .flir_camera_parameters import FlirCamParam
from flir_image_capture_package.arduino_control import ArduinoControl
import queue
class FlirTriggerControl():
    """Sets the camera to trigger mode"""
    def __init__(self,param:FlirCamParam):
        self._param= param
        self.shutter = 10000
        self._system= PySpin.System.GetInstance()
        self._cam:Camera = self._system.GetCameras()[0]
        self._cam.Init()
        self._shutter = ShutterTimeControl(self._cam)
        self._cam =self._shutter.manual_shutter(self._cam,self.shutter)       
        self._cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        self.ard= ArduinoControl()
        self.thr = True
        #self._cam.AcquisitionFrameCount.SetValue(100)    

        pass 
    def chunk_enable(self):
        """Enables all the writeable chunk features"""
        nodemap = self._cam.GetNodeMap()
        chunk_mode_active = PySpin.CBooleanPtr(nodemap.GetNode('ChunkModeActive'))      
        chunk_mode_active.SetValue(True)      
        chunk_selector = PySpin.CEnumerationPtr(nodemap.GetNode('ChunkSelector'))
        entries = [PySpin.CEnumEntryPtr(chunk_selector_entry) for chunk_selector_entry in chunk_selector.GetEntries()]
        # Iterate through our list and select each entry node to enable
        for chunk_selector_entry in entries:
            chunk_selector.SetIntValue(chunk_selector_entry.GetValue())              
            chunk_enable = PySpin.CBooleanPtr(nodemap.GetNode('ChunkEnable'))
            if PySpin.IsWritable(chunk_enable):            
                chunk_enable.SetValue(True)
 
    def get_led_status(self,image):
        """This method returns 0,1, or 2 based on the LED Status at the end of expousere time while capturing the image
        it returns 0 if the light is blue, 1, if the light is green and 2 if the light is red"""  
        chunk_data = image.GetChunkData()
        end_line_status = chunk_data.GetExposureEndLineStatusAll()
        if end_line_status == 5:
            return 1
        elif end_line_status == 9:
            return 0
        elif end_line_status == 13:
            return 2
        else:
            raise ValueError("Plese make sure the The red wire of camera is connected to pin 7, green is connected to pin 2, blue is connected to ground and black is connected to pin 10")
     

    def initialize_trigger_control_hardware(self):
        self._cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)  
        self._cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)  
        if self._cam.TriggerSource.GetAccessMode() == PySpin.RW:
            self._cam.TriggerSource.SetValue(PySpin.TriggerSource_Line0)
            self._cam.TriggerMode.SetValue(PySpin.TriggerMode_On) 
        else:
            print("TriggerSource feature not writable or not supported.")

        pass 
    def set_to_newest_only_buffer_mode(self):
         s_node_map = self._cam.GetTLStreamNodeMap()
         handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
         handling_mode_entry = PySpin.CEnumEntryPtr(handling_mode.GetCurrentEntry())
         handling_mode_entry = PySpin.CEnumEntryPtr(handling_mode.GetCurrentEntry())
         stream_buffer_count_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferCountMode'))
         stream_buffer_count_mode_manual = PySpin.CEnumEntryPtr(stream_buffer_count_mode.GetEntryByName('Manual'))
         stream_buffer_count_mode.SetIntValue(stream_buffer_count_mode_manual.GetValue())
         buffer_count = PySpin.CIntegerPtr(s_node_map.GetNode('StreamBufferCountManual'))
         buffer_count.SetValue(1)
         handling_mode_entry = handling_mode.GetEntryByName('NewestOnly')
         handling_mode.SetIntValue(handling_mode_entry.GetValue())

    def capture(self,feed = True, record = True):
        self.initialize_trigger_control_hardware()
        self.set_to_newest_only_buffer_mode()
        self.chunk_data_from_nod_map()
        self._cam.BeginAcquisition() 
        data_queue_disp = queue.Queue() if feed else None
        data_queue_write = queue.Queue() if record else None
        display_thread = threading.Thread(target=self.__display_images,args =(data_queue_disp,))
        writer_process = threading.Thread(target = self.__save,
                                          args = (self._param.path,data_queue_write))
        if feed:
            display_thread.daemon = True
            display_thread.start()
        if record:
            writer_process.daemon = True
            writer_process.start()      
        for i in range(1000):
            led_status,image_result = self._capture(i)      
            if feed:
                image_reduced= self.reduce_image_quality(image_result)
                data_queue_disp.put((led_status,image_reduced))
            if record:
                data_queue_write.put((str(i),image_result))
        self.thr = False       
        self._cam.EndAcquisition()
        self._cam.DeInit()
        self.ard.stop()
       
        del self._cam
        

    def __save(self, path, data_queue):
        """Saves the images in .h5 file format."""
       
        with h5py.File(path, "w") as h5_file:
            while self.thr:
                try:
                    item = data_queue.get(timeout=20)  # Add a timeout to prevent indefinite blocking
                except queue.Empty:
                    print("Queue is empty, terminating.")
                    break
                if item is None:
                    self.thr = False
                    break  # Terminate the loop when a None item is received
                itter, image = item
                # Save the image in the HDF5 file
                h5_file.create_dataset(itter, data=image)
                if int(itter) % 100 == 0:
                    h5_file.flush()
    def __display_images(self, data_queue):
       
        while self.thr:
            images_batch = []  # List to hold the three images
            image_flag = []
            for _ in range(3):  # Get three images at once
                item = data_queue.get(block = True,timeout = 3)
                if item is None:
                    self.thr = False  # Exit the loop if None item is received
                flag, image = item
                images_batch.append(image)  # Append the image to the batch
                image_flag.append(flag)
            if images_batch:
                image = self.__processing(image_flag, images_batch)
                cv2.imshow('stream', image)
                cv2.waitKey(1)
        cv2.destroyAllWindows()  # Close all OpenCV windowss

    def reduce_image_quality(self, image):
        """Reduces the quality of the image for smoother display.
        Args:
            image: The image captured by the camera.
        Returns:
            A reduced-quality version of the image."""
        reduced_image = cv2.resize(image, (640, 480), interpolation=cv2.INTER_LINEAR)
        return reduced_image

    def __processing(self,flag:list,image_batch):
        print(flag)
        b= flag.index(0)
        g= flag.index(1)
        r= flag.index(2)
        image = cv2.merge([image_batch[b],image_batch[g],image_batch[r]])
        #image =  Processing.corrrect_color(image,self.weight)
        return image    

    def _capture(self,i):  
        if i == 0:
            self.ard.start()
        raw = self._cam.GetNextImage()     
        image = raw.GetNDArray()
        status = self.get_led_status(raw)
           
        return [status,image]
param= FlirCamParam()
mode = FlirTriggerControl(param)
mode.capture()
