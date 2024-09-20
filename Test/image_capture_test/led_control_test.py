""" teste set for led_control class
    """
from thors_lab_led_control_package.led_control import LedControl
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
                obj.simulate_color(vect,5)

obj.simulate_sine_at(0,20,90)
obj.close_resources()