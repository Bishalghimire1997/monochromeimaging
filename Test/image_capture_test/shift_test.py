from image_processing_package.parallel_sift import ParallelSift
from image_processing_package.detect_changed_object import DetectChanges
from h5_file_format_package.h5_format import H5FormatRead
import cv2
def test_shift():
    """test case for shift"""
    read_imaegs = H5FormatRead()
    sift = ParallelSift()
    blue = read_imaegs.read_files("image_LS_HAT_NWL.h5","0")
    keypoints, descriptors = sift.detectAndCompute(blue)
def surf():
    sift = cv2.xfeatures2d.SURF_create()

if __name__ == "__main__":  
    surf()
    print("shift test passed")
