from flir_image_capture_package.hardware_trigger import FlirTriggerControl
from flir_image_capture_package.software_trigger import FlirTriggerControl as FTC
from flir_camera_parameter_package.flir_camera_parameters import FlirCamParam
def hardware_trigger_test():
    param= FlirCamParam()
    obj = FlirTriggerControl(param)
    obj.capture()
def software_trigger_test():
    param= FlirCamParam()
    obj = FTC(param)
    obj.capture()

hardware_trigger_test()