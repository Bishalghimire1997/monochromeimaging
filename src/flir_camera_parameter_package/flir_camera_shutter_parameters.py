"""_summary_"""
import PySpin
from PySpin import Camera
class ShutterTimeControl():
    """
    changes the time interval to keep the shutter open in 
    """
    def __init__(self):
        pass
    def auto_shutter_time(self,cam:Camera):
        """resets the shutter time in camera instace to default

        Args:
            camera (cam): instance of PySpin camera

        Returns:
            cam: instance of pyspin camera
        """
        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            return cam
        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Continuous)
        return cam
    def manual_shutter(self,cam:Camera,shutter_value:int):
        """Sets the sutter open time manually to the camera instance

        Args:
            camera (cam): instance of PySpin camera class
            shutter_value (int): desired shutter open time in MocroSecond

        Returns:
            _type_: _description_
        """
        
        cam.ExposureTime.SetValue( min(cam.ExposureTime.GetMax(), shutter_value))
        return cam
    @staticmethod
    def turn_auto_shutter_off(cam:Camera):
        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            return cam
        cam.ExposureAuto.SetValue(PySpin.ExposureAuto_Off)
        if cam.ExposureAuto.GetAccessMode() != PySpin.RW:
            return cam
        return cam