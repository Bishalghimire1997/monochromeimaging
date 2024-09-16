""" teste set for led_control class
    """
import time
import math
import pyvisa
from thors_lab_led_control_package.constant_brightness_mode import ConstantBrightness
rm = pyvisa.ResourceManager()
resources = rm.list_resources()
instrument = rm.open_resource(resources[0])
obj_cb = ConstantBrightness(instrument)

def sim_sine(obj: ConstantBrightness):
    """Simalates the sine wave 
    """
    obj.on()
    for i in range (360*10):
        perc = math.sin(math.radians(i))*100
        obj.set_led_brigntness(perc)
    obj.off()


def sim_pulse(obj: ConstantBrightness):
    """Simulates pulse 

    Args:
        obj (ConstantBrightness): instance of ConstantBrightness class 
    """
    obj.set_led_brigntness(100)
    for i in range(10):
        obj.on()
        time.sleep(1)
        obj.off()
        time.sleep(1)
        
sim_sine(obj_cb)
sim_pulse(obj_cb)
