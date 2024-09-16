import pyvisa
import math
class LedControl():
   def __init__(self):
      self._leds=[]
      self._detect_led()
      pass
   def _detect_led(self):
        resource_manager = pyvisa.ResourceManager()
        resources = resource_manager.list_resources()
        self._leds.append(resources[0])
        print(self._leds)