from flir_camera_parameter_package.parameter_interface import Parameters
import PySpin
from PySpin import Camera as cam
class ShutterTimeControl(Parameters):
    def __init__(self,camera:cam):
        pass
    def auto_shutter_time(self,camera:cam):
        return camera
       
    def manual_shutter(self,camera:cam,shutter_value:int):
        if camera.ExposureAuto.GetAccessMode() != PySpin.RW:
            return camera
        camera.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        if camera.ExposureAuto.GetAccessMode() != PySpin.RW:
            return camera
        camera.ExposureTimeMode.SetValue(min(shutter_value,cam.ExposureTime.GetMax()))

        return camera
      

    