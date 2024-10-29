"""Controls the 3 LED clusters

    Returns:
        _type_: _description_
    """
import math
import time
import threading
from pyvisa import ResourceManager
from thors_lab_led_control_package.constant_brightness_mode import ConstantBrightness
class LedControl():
    """ Class to control the LED cluster in Constant Current Mode
    """
    def __init__(self):
        self._leds=[]
        self._resource_manager = ResourceManager()
        self._cluster_brightness = 100
        self._leds = self._detect_led()

    def _detect_led(self):
        relevant_resources=[]
        resources = self._resource_manager.list_resources()
        print(resources)
        relevant_resources.append(resources [0])
        relevant_resources.append(resources [1])
        relevant_resources.append(resources [2])
        return self._open_resources(relevant_resources)
    def _sim_sine(self,phase:int,obj: ConstantBrightness):
        """Simalates the sine wave 
        """
        obj.on()
        for i in range (360*10):
            perc = math.sin(math.radians(i+phase))*100
            obj.set_led_brigntness(perc)
        obj.off()
    def _open_resources(self,relevant_resourcss:list):
        temp =[]
        for i in relevant_resourcss:
            temp.append(self._resource_manager.open_resource(i))
        return temp
    def close_resources(self):
        """Method to close the resources
        """
        self._resource_manager.close()

    def _turn_on(self,list_cb_obj:list):
        thread1= threading.Thread(target=list_cb_obj[0].on())
        thread2= threading.Thread(target=list_cb_obj[1].on())
        thread3= threading.Thread(target=list_cb_obj[2].on())
        thread1.start()
        thread2.start()
        thread3.start()

    def _turn_off(self,list_cb_obj:list):
        thread1= threading.Thread(target=list_cb_obj[0].off())
        thread2= threading.Thread(target=list_cb_obj[1].off())
        thread3= threading.Thread(target=list_cb_obj[2].off())
        thread1.start()
        thread2.start()
        thread3.start()
    def _set_brightness(self,list_cb_obj:list,vect:list):
        thread1= threading.Thread(target=list_cb_obj[0].set_led_brigntness(vect[0]))
        thread2= threading.Thread(target=list_cb_obj[1].set_led_brigntness(vect[1]))
        thread3= threading.Thread(target=list_cb_obj[2].set_led_brigntness(vect[2]))
        thread1.start()
        thread2.start()
        thread3.start()
    def simulate_sine_at(self,phase_r:int,phase_b:int,phase_g:int):
        """runs the three LED in sine wave at the phase difference
        indicated by phase_r, phase_b and phase_g

        Args:
            phase_r (int): phase differennce of red LED 
            phase_b (int): phase differennce of blue LED 
            phase_g (int): phase differennce of green LED 
        """
        obj_cb_red = ConstantBrightness(self._leds[0])
        obj_cb_blue = ConstantBrightness(self._leds[1])
        obj_cb_green = ConstantBrightness(self._leds[2])
        thread1 = threading.Thread (target= self._sim_sine, args =[phase_r,obj_cb_red])
        thread2 = threading.Thread (target= self._sim_sine, args =[phase_b,obj_cb_blue])
        thread3 = threading.Thread (target= self._sim_sine, args =[phase_g,obj_cb_green])
        thread1.start()
        thread2.start()
        thread3.start()
        
    def simulate_color(self,ratio:list, delay):
        """genere color for delay interval of time 

        Args:
            ratio (list): ratio of color mix for RGB LED 
            delay (int): duration after which all the LED are turned off
        """
        list_cb_obj = []
        for i in self._leds:
            list_cb_obj.append(ConstantBrightness(i))
        self._set_brightness(list_cb_obj,self._brightness_vect(ratio))
        self._turn_on(list_cb_obj)
        time.sleep(delay)
        self._turn_off(list_cb_obj)

    def turn_dedicated_on(self,ratio:list):
        list_cb_obj = []
        for i in self._leds:
            list_cb_obj.append(ConstantBrightness(i))
        self._set_brightness(list_cb_obj,self._brightness_vect(ratio))
        self._turn_on(list_cb_obj)
        return list_cb_obj
      
    def turn_dedicated_off(self,list_cb_object):
        self._turn_off(list_cb_object)

        pass


    def _brightness_vect(self,ratio:list):
        br = []
        ratio_sum = sum(ratio)
        print(ratio_sum)
        if ratio_sum<1:
            for i in range(3):
                br.append(0)
            return br
        for i in ratio:
            br.append(self._cluster_brightness*i/ratio_sum)   
        print(br)
        return br
    
    
    