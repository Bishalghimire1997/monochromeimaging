import cv2
import numpy as np
from matplotlib import pyplot as plt
from concurrent.futures import ThreadPoolExecutor
import multiprocessing as mp
from skimage.transform import PiecewiseAffineTransform, warp

# ---------------- GPU Optical Flow Wrapper ---------------- #
class Flow:
    def __init__(self,numbItterations=2, tau=4, lambda_=0.5, theta=0.06, epsilon=1e-3):
        self.tvl1 = cv2.cuda.OpticalFlowDual_TVL1.create()
        self.tvl1 .setNumIterations(numbItterations)
        self.tvl1 .setTau(tau)
        self.tvl1 .setLambda(lambda_)
        self.tvl1 .setTheta(theta)
        self.tvl1 .setEpsilon(epsilon)   

    def compute_flow(self, images):
        fi=cv2.GaussianBlur(images[0], (5, 5), 1)
        fl = cv2.GaussianBlur(images[1], (5, 5), 1)  
        images = [fi, fl]         
        
       
        ref, floating = [i.astype(np.float32) / 255.0 for i in images]

        gpu_ref = cv2.cuda_GpuMat()
        gpu_flt = cv2.cuda_GpuMat()
        gpu_ref.upload(ref)
        gpu_flt.upload(floating)

        flow_gpu = self.tvl1.calc(gpu_ref, gpu_flt, None)
        return flow_gpu.download()

class FlowGPU:

    def coarse_mesh_registration_gpu(self,ref_img, float_img, flow, grid_size=2):
        rows, cols = ref_img.shape
        src_cols = np.linspace(0, cols - 1, grid_size)
        src_rows = np.linspace(0, rows - 1, grid_size)
        src_rows, src_cols = np.meshgrid(src_rows, src_cols)
        src = np.dstack([src_cols, src_rows]).reshape(-1, 2)

        u, v = flow[..., 0], flow[..., 1]
        flow_at_points = np.array([
            [u[int(y), int(x)], v[int(y), int(x)]] for x, y in src
        ])
        dst = src + flow_at_points

        tform = PiecewiseAffineTransform()
        tform.estimate(src, dst)
        warped = warp(float_img, tform, output_shape=ref_img.shape)
        return warped

    def fine_registration_gpu(self,ref_img, float_img, flow):
        u, v = flow[..., 0], flow[..., 1]
        h, w = ref_img.shape
        grid_y, grid_x = np.meshgrid(np.arange(h), np.arange(w), indexing='ij')
        map_x = (grid_x + u).astype(np.float32)
        map_y = (grid_y + v).astype(np.float32)

        warped = cv2.remap(float_img.astype(np.float32), map_x, map_y, interpolation=cv2.INTER_CUBIC)
        return warped

    # ---------------- Histogram Visualization ---------------- #

    def compute_histogram(self,image, title='Histogram'):
        if len(image.shape) == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        hist = cv2.calcHist([image], [0], None, [256], [0, 256]).flatten()
        plt.figure()
        plt.bar(range(256), hist, width=1.0, edgecolor='black')
        plt.title(title)
        plt.xlabel('Pixel Value')
        plt.ylabel('Frequency')
        plt.xlim([0, 255])
        plt.show()
        return hist

    # ---------------- Main Pipeline ---------------- #

    def optical_flow_impl_gpu_parallel(self,blue,green,red):
        
        


        #compute_histogram(blue, "Blue (Ref)")
        #compute_histogram(green, "Green Before")
        #compute_histogram(red, "Red Before")

        flow_engine1 = Flow()
        flow_engine2 = Flow()
        

        with ThreadPoolExecutor(max_workers=2) as executor:
            future_g = executor.submit(flow_engine1.compute_flow, [blue, green])
            future_r = executor.submit(flow_engine2.compute_flow, [blue, red])

            flow_g = future_g.result()
            flow_r = future_r.result()
        #coarse registration
        coarse_g = self.coarse_mesh_registration_gpu(np.copy(blue), np.copy(green), flow_g)
        coarse_r =self.coarse_mesh_registration_gpu(np.copy(blue), np.copy(red), flow_r)
        # Fine registration
        fine_g = self.fine_registration_gpu(np.copy(blue), coarse_g, flow_g)
        fine_r = self.fine_registration_gpu(np.copy(blue), coarse_r, flow_r)

        fine_g = (fine_g * 255).clip(0, 255).astype(np.uint8)
        fine_r = (fine_r * 255).clip(0, 255).astype(np.uint8)

        #compute_histogram(fine_g, "Green After")
        #compute_histogram(fine_r, "Red After")
        return cv2.merge([blue, fine_g, fine_r])

   
