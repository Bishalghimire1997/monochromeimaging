from thors_lab_led_control_package.led_interface import Led
import pyvisa
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
        
     
      
   def on(self):
      pass
   def off(self):
      pass
   def blink(self,frequency:int):
      pass
   def modulate(self):
      pass

ob=LedControl()