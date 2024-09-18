""" teste set for led_control class
    """
from thors_lab_led_control_package.led_control import LedControl

obj = LedControl()
obj.simulate_color([1,0,0],15) #100 = blue, 001 = green, 010= red
obj.close_resources()
