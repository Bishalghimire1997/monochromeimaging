import cv2
from h5_file_format_package.h5_format_read import ReadH5
from h5_file_format_package.h5_format import H5Fromat
from image_processing_package.processing_routines import Processing
from image_processing_package.detect_changed_object import DetectChanges 
from image_processing_package.tracking import Track

def inaitial_analysis():
    """initial test case"""
    obj2 = ReadH5()
    blue1 = obj2.read_files("image.h5","60")
    green = obj2.read_files("image.h5","61")
    red = obj2.read_files("image.h5","62")
    Processing.open_images(Processing.image_reconstruction(blue1,green,red),'reconstrucrted')
    obj = DetectChanges()
    obj1 = DetectChanges()
    roi,_= obj1.select_and_crop_roi(blue1)
    param=obj.check_for_match_second(roi,blue1,green)
    green= obj.transform(green,param[0],param[1],param[4])
    param= obj1.check_for_match_second(roi, blue1,red)
    red= obj.transform(red,param[0],param[1],param[4])
    Processing.open_images(Processing.image_reconstruction(blue1,green,red),"after transformation ")
    blue2 = obj2.read_files("image.h5","63")
    green = obj2.read_files("image.h5","64")
    red = obj2.read_files("image.h5","65")
    roi = DetectChanges.updateRoi(roi,blue1,blue2)
    print(roi)
    param=obj.check_for_match_second(roi,blue2,green)
    green= obj.transform(green,param[0],param[1],param[4])
    param= obj1.check_for_match_second(roi, blue2,red)
    red= obj.transform(red,param[0],param[1],param[4])
    Processing.open_images(Processing.image_reconstruction(blue2,green,red),"after transformation ")
def loop():
    """Corrects the ROI in each frame"""
    read_imaegs = ReadH5()
    saveblue= H5Fromat("blue")
    savegreen = H5Fromat("green")
    savered = H5Fromat("red")
    save_roi = H5Fromat("ROI")
    var=60
    dec_ch = DetectChanges
    blue = read_imaegs.read_files("image.h5",str(var))
    roi,_ = dec_ch.select_and_crop_roi(blue)
    tr=Track("CSRT")
    tr.start_tracking(blue,roi)
    for i in range(300):
        b = str(var)
        g = str(var+1)
        r= str (var+2)
        var=var+3     
        green = read_imaegs.read_files("image.h5",g)
        red = read_imaegs.read_files("image.h5",r)
        blue = read_imaegs.read_files("image.h5",b)    
        if i!= 0:
            _,roi = tr.update_tracking(blue)
            _,roi = tr.update_tracking(green)
            _,roi = tr.update_tracking(red)
            print(roi)
        param=dec_ch.check_for_match_second(roi,blue,green)
        green= dec_ch.transform(green,param[0],param[1],param[4])
        param= dec_ch.check_for_match_second(roi, blue,red)
        red= dec_ch.transform(red,param[0],param[1],param[4])
        saveblue.record_images(blue,str(i))
        savegreen.record_images(green,str(i))
        savered.record_images(red,str(i))
        save_roi.record_images(roi,str(i))
def play_images_as_video( fps=20.0):
    """" Plays the corrected frams as a video"""
    obj2 = ReadH5()
    imagesblue = []
    imagegreen=[]
    imagered=[]
    imagetransformed=[]
    for i in range(175):
        imagesblue.append(obj2.read_files("bcb.h5",str(i)))
        imagegreen.append(obj2.read_files("bcg.h5",str(i)))
        imagered.append(obj2.read_files("bcr.h5",str(i)))
        imagetransformed.append(Processing.image_reconstruction(obj2.read_files("bcb.h5",str(i)),
                                                                obj2.read_files("bcg.h5",str(i)),
                                                                obj2.read_files("bcr.h5",str(i))))
    delay = int(1000 / fps)

    for image in imagetransformed:
        cv2.imshow('Image Stream', image)
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            print("Playback interrupted.")
            break
    cv2.destroyAllWindows()

def correct_background():
    """Corects the background after transformation """
    blue_o=[]
    green_o=[]
    red_o=[]
    blue_t=[]
    green_t=[]
    red_t=[]
    roi= []
    read_imaegs = ReadH5()
    var=60
    for i in range(200): 
        b = str(var)
        g = str(var+1)
        r= str (var+2)
        blue_o.append(read_imaegs.read_files("image.h5",b))
        green_o.append(read_imaegs.read_files("image.h5",g))
        red_o.append(read_imaegs.read_files("image.h5",r))
        blue_t.append(read_imaegs.read_files("blue.h5",str(i)))
        green_t.append(read_imaegs.read_files("green.h5",str(i)))
        red_t.append(read_imaegs.read_files("red.h5",str(i)))
        roi.append(read_imaegs.read_files("ROI.h5",str(i)))
        var=var+3
    print(roi[0])
    DetectChanges.reconstruct_background(blue_t,red_t,green_t,blue_o,green_o,red_o,roi)
play_images_as_video(1)

