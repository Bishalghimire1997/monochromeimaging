"""
This module provides functionality for handling FLIR camera.

Modules:
    threading: Provides threading capabilities.
    PySpin: Provides access to the FLIR camera SDK.
    FlirCamParameters: Contains the FlirCamParam class for managing camera parameters.
"""
import threading
import PySpin
from camera_interface import CameraInterface
from flir_camera_parameters import FlirCamParam
class FlirCamera(CameraInterface):
    """A class to handle FLIR camera operations including taking snapshots and saving images."""
    def __init___(self):
        pass
    def take_snapshot(self,param:FlirCamParam):
        """_summary_ 
        takes "n" number of images. "n"  can be defined in "flir_camera_ prameter" class
        Args:
            param (FlirCamParam): Instance of FlirCamPara class
        """
        system= PySpin.System.GetInstance()
        camera = system.GetCameras()[0]
        camera.Init()
        processor = PySpin.ImageProcessor()
        processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)
        camera.BeginAcquisition()
        for i in range(param.get_snap_counts()):
            image = self.capture(camera)
            threading.Thread(target = self.save, args = (image,processor,i)).start()
        camera.EndAcquisition()
        camera.DeInit()
        del camera
        system.ReleaseInstance()
    def capture_continious(self,param:FlirCamParam):
        """_summary_
        captures the images until the trigger is on
        Args:
            param (FlirCamParam): _description_
        """
        system= PySpin.System.GetInstance()
        camera = system.GetCameras()[0]
        camera.Init()
        processor = PySpin.ImageProcessor()
        processor.SetColorProcessing(PySpin.SPINNAKER_COLOR_PROCESSING_ALGORITHM_HQ_LINEAR)
        camera.BeginAcquisition()
        while param.get_trigger():
            image = self.capture(camera)
            threading.Thread(target = self.save, args = (image,processor,i)).start()
        camera.EndAcquisition()
        camera.DeInit()
        del camera
        system.ReleaseInstance()

    def save(self,image_result,processor,itter):
        """_summary_ 
        saves the images generated by Flir camera as per the defined processign method

        Args:
            image_result (_type_): image from the Flir camera
            processor (_type_): instance of Pyspin.ImageProcessor()
            itter (int): Number of times image is taken
        """
        image_converted = processor.Convert(image_result, PySpin.PixelFormat_Mono8)
        image_converted.Save("Image"+str(itter)+".jpg")
        image_result.Release()
    def capture(self,camera):
        """_summary_

        Args:
            camera (_type_): _description_

        Returns:
            _type_: _description_ returs images
        """
        return camera.GetNextImage(1000)
    