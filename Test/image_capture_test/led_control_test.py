""" teste set for led_control class
    """

from thors_lab_led_control_package.led_control import LedControl

class LedControlTest():
    """_summary_
    """    
    
    def detect_test(self):
        """_summary_
        """        
        led_obj = LedControl()
        
       
    def on_test(self):
        
        pass
    def off_test(self):
        led_obj = LedControl()
        led_obj.on()
   
    def blink_test(self):
        pass
    def mode_test(self):
        pass
obj= LedControlTest()

