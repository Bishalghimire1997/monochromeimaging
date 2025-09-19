from experiments.local_deformation_correction.sample import RGBMisalignmentSimulator
import cv2
import numpy as np
class Sample_test():
    def __init__(self):
        self.sim = RGBMisalignmentSimulator(path="image.h5")
        pass 
    def run(self): 
        
        ref,target = self.sim.generate()
      
        for i,j in zip(ref,target):
            i_np = i.detach().cpu().numpy()
            j_np = j.detach().cpu().numpy()

    # if float in [0,1], scale to [0,255]
            if i_np.dtype != np.uint8:
                i_np = (i_np).clip(0, 255).astype(np.uint8)
                j_np = (j_np).clip(0, 255).astype(np.uint8)
                if i.shape != j.shape:
                    j_np = cv2.resize(j_np, (i.shape[1], i.shape[0]))
    
                # Horizontally stack for side-by-side comparison
                split_screen = cv2.hconcat([i_np, j_np])

                # Show combined image
                cv2.imshow("Unregistered (Left)  |  Registered (Right)", split_screen)
                key = cv2.waitKey(0)
                cv2.destroyAllWindows() 

            
        
    pass
obj = Sample_test()
obj.run()