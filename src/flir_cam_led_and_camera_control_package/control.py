"""Class to sync camera and LED 
    """
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
        """
        chapture the images in sequencxe of Red Green and Blue
        """
        red =[0,1,0]
        blue =[1,0,0]
        green = [0,0,1]
        self._led.simulate_color(red,5)
        self._led.simulate_color(green,5)
        self._led.simulate_color(blue,5)
        self._led.close_resources()
obj = Sync()
obj.capture_pause_capture()
