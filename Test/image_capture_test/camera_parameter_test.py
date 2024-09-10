from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
from flir_camera_parameter_package.flir_camera_shutter_parameters import ShutterTimeControl
from flir_image_capture_package.flir_image_capture import FlirCamera

param = FlirCamParam()
param.snap_count = 10
def auto():
    """initializing the camera with default shutter value"""
    camera1 = FlirCamera(param)
    camera1.take_snapshot()
    """Initializing the camera with shutter value 5000"""
    param.shutter_time = 5000
    
def manual():
    camera2 = FlirCamera(param)
    sutter_obj = ShutterTimeControl(camera2.camera)  
    updated_camera = sutter_obj.manual_shutter(camera2.camera,500)
    camera2.camera =updated_camera
    camera2.take_snapshot()
manual()