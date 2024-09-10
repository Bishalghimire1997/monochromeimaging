"""_summary_
a test case to check if teh camera is able to capture 500 
images and save it in single h5 file format
 """
import time
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
from flir_image_capture_package.flir_image_capture import FlirCamera
start= time.time()
cameraParam = FlirCamParam()
cameraParam.snap_count = 10

camera =FlirCamera(cameraParam)
camera.take_snapshot()
end_time = time.time()
elapsed_time = end_time - start
print(f"Time taken to run the block of code: {elapsed_time} seconds")
