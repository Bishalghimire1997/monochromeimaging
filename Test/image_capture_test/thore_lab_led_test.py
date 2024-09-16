"""Test cases fot thor's lab LED
"""
<<<<<<< HEAD
import time
import pyvisa
from thors_lab_led_control_package.thor_lab_led import Led
=======

import math
import pyvisa
from thors_lab_led_control_package.constant_brightness_mode import ConstantBrightness
>>>>>>> feature

resource_manager = pyvisa.ResourceManager()
resources = resource_manager.list_resources()
address  = resource_manager.list_resources()[0]
instrument = resource_manager.open_resource(address)

<<<<<<< HEAD
def on_test():
    """_summary_
    """
    led =Led(instrument)
    led.on()

def off_test():
    """_summary_
    """
    led =Led(instrument)
    led.off()

def set_led_brightness_test():
    """_summary_
    """
    led =Led(instrument)
    for i in range(100):
        led.set_led_brigntness(i)
        time.sleep(1)
def mode_test(mode:str):
    """_summary_

    Args:
        mode (str): _description_
    """
    led =Led(instrument)
    led.set_mode(mode)

# def beeper_test():
#     led =Led(instrument)
#     led.audio_signal(True)
=======
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
>>>>>>> feature




<<<<<<< HEAD

mode_test("CC")

off_test()
=======
ccb = ConstantBrightness(instrument)
simulate_sine(ccb)


>>>>>>> feature
