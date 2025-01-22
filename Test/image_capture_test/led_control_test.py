""" teste set for led_control class
    """
import time
from thors_lab_led_control_package.led_control import LedControl
from thors_lab_led_control_package.led_states import StateBlue
from thors_lab_led_control_package.led_states import StateGreen
from thors_lab_led_control_package.led_states import StateRed
obj = LedControl()
#simulate sine wave 
#obj.simulate_sine_at(0,90,180) #100 = blue, 001 = green, 010=print(obj.detect_led())

#simulate on off

def cluster_on_off_test():
    """simulates on off condition for all the possoible LEDS combinatons
    """    
    for i in range(2):
        for j in range(2):
            for k in range(2):
                vect =[i,j,k]
                print(vect)
                obj.simulate_color(vect,5)
def state_test(): 
    _b= StateBlue()
    _g= StateGreen()
    _r=StateRed()
    _b.set_next_state(_g)
    _g.set_next_state(_r)
    _r.set_next_state(_b)
    state= _b
    for i in range(10):
        state.activate()
        state = state.get_next_state()
        time.sleep(0.5)
    state.deactivate()
if __name__ == "__main__":
    state_test()

