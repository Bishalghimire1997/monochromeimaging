"""_summary_
a test case to check if teh camera is able to capture 500 
images and save it in single h5 file format
 """
import time
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
from flir_image_capture_package.flir_image_capture import FlirCamera
from h5_file_format_package.h5_format import H5FormatRead
start= time.time()
cameraParam = FlirCamParam()
cameraParam.snap_count = 10

def record_image_test():
    camera =FlirCamera(cameraParam)
    camera.activate(record=True)
    end_time = time.time()
    elapsed_time = end_time - start
    print(f"Time taken to run the block of code: {elapsed_time} seconds")
def read_and_display_image_test():
    image = H5FormatRead.read_files("image.h5","3")
    H5FormatRead.open_images(image)

read_and_display_image_test()