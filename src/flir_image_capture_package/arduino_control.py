import serial
import time
class ArduinoControl():
    def __init__(self):
        self.port = "COM5"
        self.bud_rate = 9600
        self.ser = serial.Serial(self.port, self.bud_rate)
        time.sleep(2)
    def start(self):
        self.ser.write(b'1')
    def stop(self):
        self.ser.write(b'0')
    