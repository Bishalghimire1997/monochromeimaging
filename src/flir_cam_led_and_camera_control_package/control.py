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
        self.delay = 5
    def rgb_sequence_capture(self):
        """chapture the images in sequencxe of Red Green and Blue"""
        self.red_capture()
        self.blue_capture()
        self.green_capture()
    def w_rg_rb_bg_sequence_capture(self):
        """captures the image in white, Red-Green, Red-Blue and Blue-Green sequence"""
        self._white_capture()
        self._rg_capture()
        self._rb_capture()
        self._bg_capture()
    def bl_rgb_sequence(self):
        self._dark_capture()
        self.red_capture()
        self.blue_capture()
        self.green_capture()

    
    def _white_capture(self):
        self._param.path = "white"
        self._param.default_shutter_time = False
        self._param.shutter_time =30000
        camera= FlirCamera(self._param)
        white =[1,1,1]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(white, self.delay))        
        thread1.start()
        camera.take_snapshot()
        thread1.join()
        
       
       
    def red_capture(self):
        """Captures the images in the red spectrum of light """
        self._param.path = "red"
        self._param.default_shutter_time = False
        self._param.shutter_time =30000
        camera= FlirCamera(self._param)
        red =[0,1,0]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(red, self.delay ))
        thread1.start()
        camera.take_snapshot()
        thread1.join()
       
    def blue_capture(self):
        """Capture the images in the blue spectrum of the light"""
        self._param.path="blue"
        self._param.default_shutter_time = False
        self._param.shutter_time = 30000
        camera= FlirCamera(self._param)
        blue =[1,0,0]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(blue, self.delay ))
        thread1.start()
        camera.take_snapshot()
        thread1.join()
       
    def green_capture(self):
        """captures the images in the green spectrum of the light"""
        self._param.path="green"
        self._param.default_shutter_time = False
        self._param.shutter_time = 30000
        camera= FlirCamera(self._param)
        green =[0,0,1]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(green, self.delay ))
        thread1.start()
        camera.take_snapshot()
        thread1.join()
       
        
    def _dark_capture(self):
        self._param.path = "dark"
        dark = [0,0,0]
        self._param.default_shutter_time = False
        self._param.shutter_time = 30000
        camera= FlirCamera(self._param)
        thread1 = threading.Thread(target= self._led.simulate_color,args=(dark, self.delay ))
        thread1.start()
        camera.take_snapshot()
        thread1.join()
    def _rg_capture(self):
        self._param.path = "rg"
        self._param.default_shutter_time = False
        self._param.shutter_time =30000
        camera= FlirCamera(self._param)
        white =[0,1,1]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(white, self.delay))        
        thread1.start()
        camera.take_snapshot()
        thread1.join()
       
    def _rb_capture(self):
        self._param.path = "rb"
        self._param.default_shutter_time = False
        self._param.shutter_time =30000
        camera= FlirCamera(self._param)
        white =[1,1,0]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(white, self.delay))        
        thread1.start()
        camera.take_snapshot()
        thread1.join()
      
    def _bg_capture(self):
        self._param.path = "bg"
        self._param.default_shutter_time = False
        self._param.shutter_time =30000
        camera= FlirCamera(self._param)
        white =[1,0,1]
        thread1 = threading.Thread(target= self._led.simulate_color,args=(white, self.delay))        
        thread1.start()
        camera.take_snapshot()
        thread1.join()

       
        
        