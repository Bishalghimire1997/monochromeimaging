""" teste set for led_control class
    """
import math
from thors_lab_led_control_package.constant_brightness_mode import ConstantBrightness
import pyvisa

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
sim_sine(obj_cb)



