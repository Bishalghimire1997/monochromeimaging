from flir_image_capture_package.flir_image_capture import FlirCamera
from flir_image_capture_package.flir_image_capture import FlirCamParam
def save_only():
    campara = FlirCamParam()
    cam = FlirCamera(campara)
    cam.activate(feed=False,record=True,led_flash=False)

def feed_only():
    campara = FlirCamParam()
    cam = FlirCamera(campara)
    cam.activate(feed=True,record=False,led_flash=False)

def feed_and_save():
    campara = FlirCamParam()
    cam = FlirCamera(campara)
    cam.activate(feed=True,record=True,led_flash=False)

def color_feed():
    campara = FlirCamParam()
    cam = FlirCamera(campara)
    cam.activate(feed=True,record=False,led_flash=True)

if __name__ == "__main__":
    color_feed()
