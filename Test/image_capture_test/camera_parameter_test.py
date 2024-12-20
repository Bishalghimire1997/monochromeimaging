"""
    just a test case
"""
import time
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
from flir_image_capture_package.flir_image_capture import FlirCamera

param = FlirCamParam()
param.snap_count = 3000
def auto():
    start = time.time()
    """initializing the camera with default shutter value"""
    camera1 = FlirCamera(param)
    camera1.take_snapshot()
    print("time = ",time.time()-start)
def manual():
    """
    Method for manual shutter value
    """
    param.default_shutter_time = False
    param.snap_count = 3000
    param.shutter_time = 5000
    camera2 = FlirCamera(param)
    camera2.take_snapshot()
auto()
