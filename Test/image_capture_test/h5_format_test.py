"""_summary_
a test case to check if teh camera is able to capture 500 
images and save it in single h5 file format
 """
from flir_image_capture_package.flir_camera_parameters import FlirCamParam
from flir_image_capture_package.flir_image_capture import FlirCamera
cameraParam = FlirCamParam()
cameraParam.snap_count = 500
camera =FlirCamera(cameraParam)
camera.take_snapshot()
