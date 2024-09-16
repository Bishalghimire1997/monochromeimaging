"""Test cases fot thor's lab LED
"""

import math
import pyvisa
from thors_lab_led_control_package.constant_brightness_mode import ConstantBrightness

resource_manager = pyvisa.ResourceManager()
resources = resource_manager.list_resources()
address  = resource_manager.list_resources()[0]
instrument = resource_manager.open_resource(address)

def simulate_sine(cl:ConstantBrightness):
    """Simulates the sine wave

    Args:
        cl (_type_): instance of constant brightness class 
    """
    cl.on()
    for i in range(360*10):
        print(i)
        per = math.sin(math.radians(i))*100
        cl.set_led_brigntness(per)
    cl.off()




ccb = ConstantBrightness(instrument)
simulate_sine(ccb)


