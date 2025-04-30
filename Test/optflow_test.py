from image_processing_package.opt_flow import Flow
import numpy as np
import cv2
def test_compute_flow():
    #reading test image
    image=cv2.imread("test.PNG")
    b,g,r = cv2.split(image)
    fl_obj = Flow()
    #computing flow
    flow1 = fl_obj.compute_flow([np.copy(b),np.copy(g)])
    flow2 = fl_obj.compute_flow([np.copy(b),np.copy(r)])
    #applying transformation
    transformed1 = fl_obj.apply_transformation(g,flow1)
    transformed2 = fl_obj.apply_transformation(r,flow2)
    # Converting transformed images to uint8
    transformed1 = (transformed1 * 255).clip(0, 255).astype(np.uint8)
    transformed2 = (transformed2 * 255).clip(0, 255).astype(np.uint8)

    #merging images 
    merged_image = cv2.merge([b, transformed1, transformed2])
    # Display the merged image  
    cv2.imshow('Merged Image', merged_image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == "__main__":
   flow= test_compute_flow()

       