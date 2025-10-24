import PySpin
from PySpin import Camera 
import cv2
import h5py
import time
import threading
from flir_camera_parameter_package.flir_camera_shutter_parameters import ShutterTimeControl
from flir_camera_parameter_package .flir_camera_parameters import FlirCamParam
import queue
from thors_lab_led_control_package.led_state_pulse import StateMachinePulse
class FlirTriggerControl():
    def __init__(self,param:FlirCamParam):
        self._param= param
        self.shutter = 3000
        self._system= PySpin.System.GetInstance()
        self._cam:Camera = self._system.GetCameras()[0]
        self._cam.Init()    
        self._shutter = ShutterTimeControl(self._cam)
        self._cam =self._shutter.manual_shutter(self._cam,self.shutter)       
        self._cam.AcquisitionMode.SetValue(PySpin.AcquisitionMode_Continuous)
        self.set_color_image_format()
        self.disable_camera_gamma(self._cam)
        print("shyuuter time  = ",self.shutter)
        pass 
    def set_color_image_format(self):
        nodemap = self._cam.GetNodeMap()
        pixel_format = PySpin.CEnumerationPtr(nodemap.GetNode("PixelFormat"))

        if not PySpin.IsAvailable(pixel_format):
            print("PixelFormat node not available")
            return
        current_entry = PySpin.CEnumEntryPtr(pixel_format.GetCurrentEntry())
        current_name = current_entry.GetSymbolic() if current_entry else "Unknown"
        
        if not PySpin.IsWritable(pixel_format):
            print(f"PixelFormat not writable. Using current: {current_name}")
            self._is_bayer = "Bayer" in current_name
            return

        # Try preferred formats
        for fmt in ["BGR8", "RGB8", "BayerRG8"]:
            entry = pixel_format.GetEntryByName(fmt)
            if entry and PySpin.IsAvailable(entry) and PySpin.IsWritable(entry):
                pixel_format.SetIntValue(entry.GetValue())
                print(f"PixelFormat set to {fmt}")
                self._is_bayer = "Bayer" in fmt
                return

        print(f"No preferred writable PixelFormat found, using current: {current_name}")
        self._is_bayer = "Bayer" in current_name

    def initialize_trigger_control_software(self):
        self._cam.TriggerMode.SetValue(PySpin.TriggerMode_Off)  
        self._cam.TriggerSelector.SetValue(PySpin.TriggerSelector_FrameStart)  
        if self._cam.TriggerSource.GetAccessMode() == PySpin.RW:
            self._cam.TriggerSource.SetValue(PySpin.TriggerSource_Software)
            self._cam.TriggerMode.SetValue(PySpin.TriggerMode_On) 
        else:
            print("TriggerSource feature not writable or not supported.")

        pass 

    import PySpin

    def disable_camera_gamma(self,camera):
        """
        Disable gamma correction on a PySpin camera.
        This method sets the Gamma node to linear (1.0) and disables GammaEnable if available.

        Parameters:
            camera : PySpin.Camera
                The camera object (must be initialized).

        Returns:
            bool : True if gamma was successfully disabled or not available, False on error.
        """
        try:
            nodemap = camera.GetNodeMap()

            # First, try to disable GammaEnable if available
            gamma_enable_node = PySpin.CBooleanPtr(nodemap.GetNode("GammaEnable"))
            gamma_enable_node.SetValue(False)
            print("GammaEnable node disabled.")
       

            return True

        except PySpin.SpinnakerException as ex:
            print(f"Error disabling gamma: {ex}")
            return False

    def set_camera_gamma(self,camera, value):
        """
        Set the Gamma value of a PySpin camera safely.

        Parameters:
            camera : PySpin.Camera
                The camera object.
            value : float
                Desired gamma value.
        """
        try:
            nodemap = camera.GetNodeMap()
            gamma_node = PySpin.CFloatPtr(nodemap.GetNode("Gamma"))

            if not PySpin.IsAvailable(gamma_node):
                print("Gamma node not available on this camera.")
                return False

            if not PySpin.IsWritable(gamma_node):
                print("Gamma node is not writable.")
                return False

            # Clamp the value within the allowed range
            gamma_min = gamma_node.GetMin()
            gamma_max = gamma_node.GetMax()
            gamma_value = max(min(value, gamma_max), gamma_min)

            gamma_node.SetValue(gamma_value)
            print(f"Gamma set to {gamma_value}")
            return True

        except PySpin.SpinnakerException as ex:
            print(f"Error setting gamma: {ex}")
            return False
    def set_to_newest_only_buffer_mode(self):
         s_node_map = self._cam.GetTLStreamNodeMap()
         handling_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferHandlingMode'))
         handling_mode_entry = PySpin.CEnumEntryPtr(handling_mode.GetCurrentEntry())
         handling_mode_entry = PySpin.CEnumEntryPtr(handling_mode.GetCurrentEntry())
         stream_buffer_count_mode = PySpin.CEnumerationPtr(s_node_map.GetNode('StreamBufferCountMode'))
         stream_buffer_count_mode_manual = PySpin.CEnumEntryPtr(
             stream_buffer_count_mode.GetEntryByName('Manual'))
         stream_buffer_count_mode.SetIntValue(stream_buffer_count_mode_manual.GetValue())
         buffer_count = PySpin.CIntegerPtr(s_node_map.GetNode('StreamBufferCountManual'))
         buffer_count.SetValue(1)
         handling_mode_entry = handling_mode.GetEntryByName('NewestOnly')
         handling_mode.SetIntValue(handling_mode_entry.GetValue())


    def capture(self,feed = True, record = True, led_flash = False):
        self.initialize_trigger_control_software()
        self.set_to_newest_only_buffer_mode()
        #self.set_color_image_format() 
        self._cam.BeginAcquisition()    
    
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
        #time.sleep(2)       
        for i in range(1000):
            print(i)
            if led_flash:                 
                 state.activate() 
            image_result = self._capture(i)                
            if feed:
                image_reduced= self.reduce_image_quality(image_result)
                data_queue_disp.put(("h",image_reduced))
            if record:
                data_queue_write.put((str(i),image_result))
            if led_flash:
                state = state.get_next_state() 
               
        self._cam.EndAcquisition()
        self._cam.DeInit()
        del self._cam

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
                h5_file.create_dataset(itter, data=image)
    def __display_images(self, data_queue):
        thr = True
        fps = 20
        while thr:
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
                #image = self.__processing(image_flag, images_batch)
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

    # def __processing(self,flag:list,image_batch):
    #     b= 0#flag.index("B")
    #     g= 1#flag.index("G")
    #     r= 2#2flag.index("R")
    #     image = cv2.merge([image_batch[g],image_batch[r],image_batch[b]])
    #     #image =  Processing.corrrect_color(image,self.weight)
        # return image    

    def _capture(self,i):    
        self._cam.TriggerSoftware.Execute()  
        self.image_result = self._cam.GetNextImage()
        #self.image_result = self.image_result.Convert(PySpin.PixelFormat_BGR8, PySpin.HQ_LINEAR)
        image= self.image_result.GetNDArray()
        color_image  = cv2.cvtColor(image,cv2.COLOR_BAYER_BG2BGR)
        self.image_result.Release()
        
        return color_image

