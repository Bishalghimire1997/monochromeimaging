"""Test case to transform object that move while capturing images at different color"""
import cv2
from h5_file_format_package.h5_format import H5FormatRead
from h5_file_format_package.h5_format import H5FromatWrite
from image_processing_package.processing_routines import Processing
from image_processing_package.detect_changed_object import DetectChanges
from image_processing_package.tracking import Track
def loop():
    """loop to track and transform shifted objects
    """    
    read_imaegs = H5FormatRead()
    saveblue= H5FromatWrite("blue1",override=False)
    savegreen = H5FromatWrite("green1",override=False)
    savered = H5FromatWrite("red1",override=False)
    save_roi = H5FromatWrite("ROI",override=False)
    var=0
    dec_ch = DetectChanges()
    blue = read_imaegs.read_files("image.h5",str(var))
    roi,_ = dec_ch.select_and_crop_roi(blue)
    all_roi = []
    all_old_image=[]
    result =[]
    tr=Track("CSRT")
    tr.start_tracking(blue,roi)
    for i in range(950):
        b = str(var)
        g = str(var+1)
        r= str (var+2)
        var=var+3
        green = read_imaegs.read_files("image.h5",g)
        red = read_imaegs.read_files("image.h5",r)
        blue = read_imaegs.read_files("image.h5",b)
        all_new_images = [blue,green,red]
        if i==0:
            all_roi = tr.update_roi(all_new_images)
            result = DetectChanges.update_keypoints(all_new_images,all_roi)    
        else:
            updated_value = DetectChanges.update_keypoints_roi_case(result,all_roi,all_old_image,all_new_images,tr)
            result = updated_value[0]
            all_roi=updated_value[1]
            tr=updated_value[2]
        blue_image_key_points,blue_image_descriptor = result[0]
        green_image_key_points,green_image_descriptor = result[1]
        red_image_key_points,red_image_descriptor = result[2]
        all_old_image =[all_new_images[0].copy(),
                             all_new_images[1].copy(),
                             all_new_images[2].copy()]
        print(all_roi)
        param=dec_ch.check_for_match_second(blue_image_descriptor,
                                            blue_image_key_points,green_image_descriptor,
                                            green_image_key_points)
        green= dec_ch.transform(green,param[0],param[1],param[4])
        param= dec_ch.check_for_match_second(blue_image_descriptor,blue_image_key_points
                                             ,red_image_descriptor,red_image_key_points)
        red= dec_ch.transform(red,param[0],param[1],param[4])
        saveblue.record_images(blue,str(i))
        savegreen.record_images(green,str(i))
        savered.record_images(red,str(i))
        save_roi.record_images(all_roi[0],str(i))

def play_images_as_video( fps=20.0):
    """" Plays the corrected frams as a video"""
    obj2 = H5FormatRead()
    imagetransformed=[]
    for i in range(90):
        b= obj2.read_files("bcb.h5",str(i))
        g= obj2.read_files("bcg.h5",str(i))
        r=obj2.read_files("bcr.h5",str(i))
        imagetransformed.append(Processing.image_reconstruction(r,b,g))                                                                
    delay = int(1000 / fps)
    for image in imagetransformed:
        cv2.imshow('Image Stream', image)
        if cv2.waitKey(delay) & 0xFF == ord('q'):
            print("Playback interrupted.")
            break
    cv2.destroyAllWindows()

def play_images_as_video1( fps=20.0):
    """" Plays the corrected frams as a video"""
    obj2 = H5FormatRead()
    var=0
    imagetransformed=[]
    for i in range(300):
        b1= var
        b2 = var+1
        b3 = var+2
        var=var+3
        b= obj2.read_files("image.h5",str(b3))
        g= obj2.read_files("image.h5",str(b2))
        r=obj2.read_files("image.h5",str(b1))
        imagetransformed.append(Processing.image_reconstruction(b,g,r))                                                                
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
    read_imaegs = H5FormatRead()
    var=0
    for i in range(100):
        b = str(var)
        g = str(var+1)
        r= str (var+2)
        var = var+3
        blue_o.append(read_imaegs.read_files("image.h5",b))
        green_o.append(read_imaegs.read_files("image.h5",g))
        red_o.append(read_imaegs.read_files("image.h5",r))
        blue_t.append(read_imaegs.read_files("blue1.h5",str(i)))
        green_t.append(read_imaegs.read_files("green1.h5",str(i)))
        red_t.append(read_imaegs.read_files("red1.h5",str(i)))
        roi.append(read_imaegs.read_files("ROI.h5",str(i)))
        var=var+1
    print(roi[0])
    DetectChanges.reconstruct_background(blue_t,red_t,green_t,blue_o,green_o,red_o,roi)
if __name__ == '__main__':
    play_images_as_video1(1)
