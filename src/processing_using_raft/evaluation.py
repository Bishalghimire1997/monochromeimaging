import cv2
import numpy as np
import matplotlib.pyplot as plt
import skimage
from skimage.color import  deltaE_ciede2000
from skimage import color
from skimage import filters
from skimage.metrics import structural_similarity as ssim
class Evaluation ():
    def __init__(self):
        pass 
    def get_structure_similarity(self,ref_images,target_images,channel = "all"):
        structure_similarity = []
        ref_cha = []
        targ_cha = []
        if channel == "b":
            for ref,targ in zip(ref_images,target_images):
                b_ref,g_ref,r_ref = cv2.split(ref)
                b_targ,g_targ,r_targ = cv2.split(targ)
                b_ssim = self.__str_sim(b_ref,b_targ)
                g_ssim = self.__str_sim(g_ref,g_targ)
                r_ssim = self.__str_sim(r_ref,r_targ)
                ref_cha.append(b_ref)               
                targ_cha.append(b_targ)
            return self.__str_sim(ref_cha,targ_cha)
        elif channel == "g":
            for ref,targ in zip(ref_images,target_images):
                b_ref,g_ref,r_ref = cv2.split(ref)
                b_targ,g_targ,r_targ = cv2.split(targ)
                ref_cha.append(g_ref)               
                targ_cha.append(g_targ)
            return self.__str_sim(ref_cha,targ_cha)
        elif channel == "r":
            for ref,targ in zip(ref_images,target_images):
                b_ref,g_ref,r_ref = cv2.split(ref)
                b_targ,g_targ,r_targ = cv2.split(targ)
                ref_cha.append(r_ref)               
                targ_cha.append(r_targ)
            return self.__str_sim(ref_cha,targ_cha)
        elif channel == "all":
            for ref,targ in zip(ref_images,target_images):
                L_ref,a_ref,b_ref = cv2.split(cv2.cvtColor(ref,cv2.COLOR_BGR2Lab))
                L_targ,a_targ,b_targ = cv2.split(cv2.cvtColor(targ,cv2.COLOR_BGR2Lab))
                ref_cha.append(L_ref)               
                targ_cha.append(L_targ)
            return self.__str_sim(ref_cha,targ_cha)
        else: return self.__str_sim(ref_images,target_images)
               
                
       
        return structure_similarity
    def edge_structural_similarity(self,ref_images,target_images):

        edge_similarity = []
        for ref, targ in zip(ref_images,target_images):           
            ref_edges,_ = self._get_edge_mask(ref)
            targ_edges,_edge_mask =  self._get_edge_mask(targ)
            dialeted_mask = self.__dialate_edges(_edge_mask)
            ssim_arr = ssim(ref_edges, targ_edges,data_range=255)
            ind = ssim(ref_edges, targ_edges,data_range=255)
            edge_similarity.append(ind)
        return edge_similarity
    def __str_sim(self,ref_edges,targ_edges):
        ind = []
        for ref, targ in zip(ref_edges,targ_edges):           
            ind.append(ssim(ref, targ,data_range=255))
        return ind

    def _get_edge_mask(self,image):
        edges = cv2.Canny(image, 100, 200)
        _, edge_mask = cv2.threshold(edges, 0, 255,cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            # cv2.imshow("binary",edge_mask)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()
        return edges, edge_mask
    def __dialate_edges(self,edges):
        kernel = np.ones((3,3),np.uint8)
        dialated_edges = cv2.dilate(edges,kernel,iterations = 2)
        return dialated_edges

    def Mse_edges(self,ref_Image,targ_image):
        error = []
        for ref,targ in zip(ref_Image,targ_image):
            ref_edges,ref_mask = self._get_edge_mask(ref)
            targ_edges,targ_mask = self._get_edge_mask(targ)
            mse = np.mean(ref_mask - targ_mask) ** 2
            error.append(mse)
        return error
    def MSE_Percentile(self,ref_images,target_images):
        error = []
        for ref,targ in zip(ref_images,target_images):
            ref_gr = cv2.cvtColor(ref,cv2.COLOR_BGR2GRAY)
            targ_gr = cv2.cvtColor(targ,cv2.COLOR_BGR2GRAY)
            ref_gr,ref_mask = self._get_edge_mask(ref_gr)
            targ_gr,targ_mask = self._get_edge_mask(targ_gr)
            abs_err = np.absolute(ref_mask - targ_mask)
           
            hist = self.__compute_hist(abs_err)
            print(hist)
            error.append(hist[-1])
        return error
    def __compute_hist(self,ref_mask):
        min_val = np.min(ref_mask)
        max_val = np.max(ref_mask)
        print(min_val,max_val)
        num_bins = max_val - min_val
        hist, bin_edges = np.histogram(ref_mask, bins=num_bins, range=(min_val, max_val)) 
       

        plt.figure()
        plt.bar(bin_edges[:-1], hist, width=1, edgecolor='black')
        plt.title("Histogram of MSE values")
        plt.xlabel("MSE Value")
        plt.ylabel("Frequency")
        plt.show()
        return hist
    def compute_del_e(self,ref_images,targ_images):
        del_e = []
        def scale(lab_cv):
            lab_cv = lab_cv.astype(np.float32)
            l = lab_cv[..., 0] * 100.0 / 255.0 
            a = lab_cv[..., 1] - 128.0
            b = lab_cv[..., 2] - 128.0

            l = l.astype(np.float32)
            a = a.astype(np.float32)
            b = b.astype(np.float32)
            lab_standard = np.stack([l, a, b], axis=-1)
            return lab_standard 
        for ref,targ in zip(ref_images,targ_images):

            # b,g,r = cv2.split(ref)
            # cv2.imshow("color",ref)
            # cv2.imshow("b",b)
            # cv2.imshow("g",g)
            # cv2.imshow("r",r)
            # cv2.waitKey(0)
            # cv2.destroyAllWindows()

            print("eef = ",ref)
            lab1=cv2.cvtColor(ref, cv2.COLOR_BGR2Lab)
            lab2 = cv2.cvtColor(targ, cv2.COLOR_BGR2LAB)
            print("lab 1 = ",lab1)
            
            lab1 = scale(lab1)
            lab2=scale(lab2)
            delta_e_00 = deltaE_ciede2000(lab1, lab2)
            del_e= delta_e_00
        return del_e
    def compute_del_e_new(self,ref_images,tar_images):
        delta_e =[]


        d_type = np.uint8

        ref_images =  filters.gaussian(ref_images, (0,1,1,0), preserve_range=True).astype(d_type)
        tar_images = filters.gaussian(tar_images,(0,1,1,0),preserve_range=True).astype(d_type)     
        xyz_ref = skimage.color.rgb2xyz(ref_images)
        xyz_target = skimage.color.rgb2xyz(tar_images)
        lab_ref = skimage.color.xyz2lab(xyz_ref)
        lab_targ = skimage.color.xyz2lab(xyz_target)
        delta_e=deltaE_ciede2000(lab_ref,lab_targ)
        avg = np.mean(delta_e,axis =(1,2) )

        print(f"The value of delta e are {avg} ")
        return avg


    
        

  