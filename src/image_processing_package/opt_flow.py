import multiprocessing as mp
from skimage.transform import PiecewiseAffineTransform, warp
import cv2
import numpy as np
class Flow:
    def __init__(self):
        pass
    def compute_flow(self,images):
        ref_image, target_image = images
        """Computes the optical flow between two images using the TVL1 algorithm."""
        # Convert images to float32 for optical flow calculation
        ref_image = ref_image.astype(np.float32)
        target_image = target_image.astype(np.float32)

        # Create a TVL1 optical flow object
        tvl1 = cv2.cuda.OpticalFlowDual_TVL1.create()

        # Upload images to GPU
        frame1 = cv2.cuda_GpuMat(ref_image)
        frame2 = cv2.cuda_GpuMat(target_image)

        # Compute optical flow
        flow = tvl1.calc(frame1, frame2, None)

        # Download flow from GPU to CPU
        flow = flow.download()

        return flow
    def apply_transformation(self,image,flow):
         grid_size=2
         rows, cols = image.shape
         src_cols = np.linspace(0, cols, grid_size)
         src_rows = np.linspace(0, rows, grid_size)
         src_rows, src_cols = np.meshgrid(src_rows, src_cols)
         src = np.dstack([src_cols.flat, src_rows.flat])[0]
         u,v = flow[..., 0], flow[..., 1]
         dst = src + np.stack([u.flat, v.flat], axis=-1)[:src.shape[0]]
         tform = PiecewiseAffineTransform()
         tform.estimate(src, dst)
         warped = warp(image, tform, output_shape=image.shape)
         return warped
    def __parallel_flow(self,image_pairs,num_workers=2):
        num_workers = len(image_pairs)
        with mp.get_context("spawn").Pool(processes=num_workers) as pool:
            results = pool.starmap(self.compute_flow, image_pairs)
        return results
    
    def __apply_transformation_parallel(self,images,flows,num_workers=2):
        num_workrers = min(len(images))
        with mp.get_context("spawn").Pool(processes=num_workers) as pool:
            results = pool.starmap(self.apply_transformation, zip(images, flows))
        return results
    
    def compute(self,fixed,floating_images,):
        #computing fixed,floating image pair
        return_imgs = []
        return_imgs.append(fixed)

        image_pairs = [(fixed, floating) for floating in floating_images]
        #computing optical flow in parallel    
        flows = self.__parallel_flow(image_pairs)
        transformed = self.compute_batch_transformation(floating_images,flows)
        return_imgs.extend(transformed)
        return return_imgs

        return 
    def compute_batch_transformation(self,floating_images,flows):    
        transformed_images = self.__apply_transformation_parallel(floating_images, flows)
        return transformed_images





       



    


       
       
    
