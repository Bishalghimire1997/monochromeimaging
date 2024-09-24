"""Class to sync camera and LED 
    """
import threading
from flir_image_capture_package.flir_image_capture import FlirCamera ,FlirCamParam
from thors_lab_led_control_package.led_control import LedControl

class Sync():
    """
    class to sync camera and LED
    """
    def __init__(self):
        self._param = FlirCamParam()
        self._cam = FlirCamera(self._param)
        self._led = LedControl()
    def capture_pause_capture(self):
        """chapture the images in sequencxe of Red Green and Blue"""
        self._red_capture()
        self._blue_capture()
        self._green_capture()
        self._white_capture()
        self._dark_capture()
    
    
    def _white_capture(self):
        self._param.path = "white"
        self._param.default_shutter_time = False
        self._param.shutter_time =30000
        camera= FlirCamera(self._param)
        white =[1,1,1]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(white,5))        
        thread1.start()
        camera.take_snapshot()
        thread1.join()
        
       
       
    def _red_capture(self):
        self._param.path = "red"
        self._param.default_shutter_time = False
        self._param.shutter_time =30000
        camera= FlirCamera(self._param)
        red =[0,1,0]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(red,5))
        thread1.start()
        camera.take_snapshot()
        thread1.join()
       
    def _blue_capture(self):
        self._param.path="blue"
        self._param.default_shutter_time = False
        self._param.shutter_time = 30000
        camera= FlirCamera(self._param)
        blue =[1,0,0]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(blue,5))
        thread1.start()
        camera.take_snapshot()
        thread1.join()
       
    def _green_capture(self):
        self._param.path="green"
        self._param.default_shutter_time = False
        self._param.shutter_time = 30000
        camera= FlirCamera(self._param)
        green =[0,0,1]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(green,5))
        thread1.start()
        camera.take_snapshot()
        thread1.join()
       
        
    def _dark_capture(self):
        self._param.path = "dark"
        dark = [0,0,0]
        self._param.default_shutter_time = False
        self._param.shutter_time = 30000
        camera= FlirCamera(self._param)
        thread1 = threading.Thread(target= self._led.simulate_color,args=(dark,5))
        thread1.start()
        camera.take_snapshot()
        thread1.join()
       
        
        