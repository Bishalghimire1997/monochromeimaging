"""test case for hardware and software trigger"""
from flir_image_capture_package.hardware_trigger import FlirTriggerControl
from flir_image_capture_package.software_trigger import FlirTriggerControl as FTC
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
def hardware_trigger_test():
    """hardware trigger test"""    
    param= FlirCamParam()
    obj = FlirTriggerControl(param)
    obj.capture(feed = True,record=False)
def software_trigger_test():
    """software trigger test"""    
    param= FlirCamParam()
    obj = FTC(param)
    obj.capture()
if __name__ == "__main__":
    hardware_trigger_test()