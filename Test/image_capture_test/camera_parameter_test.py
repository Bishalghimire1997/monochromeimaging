"""
    just a test case
"""
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
from flir_image_capture_package.flir_image_capture import FlirCamera

param = FlirCamParam()
param.snap_count = 150
def auto():
    """initializing the camera with default shutter value"""
    camera1 = FlirCamera(param)
    camera1.take_snapshot()
def manual():
    """
    Method for manual shutter value
    """
    param.default_shutter_time = False
    param.shutter_time = 150
    camera2 = FlirCamera(param)
    camera2.take_snapshot()
auto()

