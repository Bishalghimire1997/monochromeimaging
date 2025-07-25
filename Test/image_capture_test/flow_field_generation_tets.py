from processing_using_raft.gen_field import PerlinCrush
import numpy as np
import torch
import h5py
import cv2
class FlowFieldGenerationTest():
    def __init__(self):
        self.roi = None
        pass
    def read_sample(self,file_path,dataset_name = "reference",number_of_frames = 10, esc= 0,crop =False): 

          image1 = []     
          image2 = []          
          offset = 20+esc 
          with h5py.File(file_path, 'r') as f:
              if dataset_name not in f:
                  print(f"Dataset '{dataset_name}' not found in the file.")
                  return
              
              video_data1 = f["reference"]  # Assume shape (num_frames, H, W [,C])
              video_data2 = f["target"]  # Assume shape (num_frames, H, W [,C])
              num_frames = video_data1.shape[0]

              print(f"Video shape: {video_data1.shape}, dtype: {video_data1.dtype}")

              for i in range(number_of_frames):
                 
                  frame1 = video_data1[i+offset]
                  frame2 = video_data2[i+offset]
                  # Normalize if necessary
                  if frame1.dtype != np.uint8:
                      frame1 = (255 * (frame1 - frame1.min()) / (frame1.ptp() + 1e-8)).astype(np.uint8)
               
                  image1.append(cv2.resize(frame1, (960, 540),interpolation=cv2.INTER_AREA))
                  image2.append(cv2.resize(frame2, (960, 540),interpolation=cv2.INTER_AREA)) 
          if crop:
                image1_crop = []
                image2_crop = []
                if self.roi is None:
                    self.roi = cv2.selectROI("image",image1[0],fromCenter=False)
                for ref,targ in zip(image1,image2):
                    ref = ref[self.roi[1]:self.roi[1]+self.roi[3],self.roi[0]:self.roi[0]+self.roi[2]]
                    targ = targ[self.roi[1]:self.roi[1]+self.roi[3],self.roi[0]:self.roi[0]+self.roi[2]]
                    image1_crop.append(ref)
                    image2_crop.append(targ)
                #print(f"Image1 crop shape: {len(image1_crop)}, Image2 crop shape: {image2_crop.shape}")
                return self.to_tensor(image1_crop),self.to_tensor(image2_crop)
          else:
                return self.to_tensor(image1),self.to_tensor(image2)

    def to_tensor(self,img_list):
        arr = np.stack(img_list)  # [N, H, W] or [N, H, W, C]
        if arr.ndim == 3:  # grayscale: [N, H, W]
            arr = arr[:, None, :, :]  # add channel dimension
        else:  # RGB: [N, H, W, C]
            arr = arr.transpose(0, 3, 1, 2)  # -> [N, C, H, W]
        return torch.from_numpy(arr).float() / 255.0  # normalize to [0,1]
    def read_from_camera1(self,path):   
        image = []
        im1 = []        
        with h5py.File(path, 'r') as f:
            k=0
            for i in range(500):
                for j in range(3):
                   im1.append(f[str(k+j)][:]) 
                   print(k+j)

                imtemp=[]
                b=im1[0]
                g = im1[2]
                r=im1[1]
                imtemp.append(b)
                imtemp.append(g)
                imtemp.append(r)
                im = cv2.merge(imtemp) 
                # cv2.imshow("merged",im)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows()

                image.append(cv2.resize(im, (960, 540),interpolation=cv2.INTER_AREA))
                im1 = []
                k = k+3
        return image     
    def read_from_camera(self,path,channel):
        image = []
       
        imtemp_blue=[]
        imtemp_green=[]
        imtemp_red=[]
        blue_3 = []
        green_3 = []
        red_3 = []        
        with h5py.File(path, 'r') as f:                
            k=0            
            for i in range(1000):
                im1 = []
                for j in range(3):
                   im1.append(f[str(k+j)][:]) 
                   print(k+j)
                b=im1[0]
                g = im1[1]
                r=im1[2] 
                imtemp_blue.append(g)
                imtemp_green.append(r)
                imtemp_red.append(b)
                k=k+3
                # cv2.imshow("merged",im)
                # cv2.waitKey(0)
                # cv2.destroyAllWindows() 
            if channel == "b":
                print("reading blue channel") 
                for i in range(len(b)):
                    temp = []         
                   
                    for j in range(3):              
                        if i+k>len(imtemp_blue)-3:
                            return blue_3
                        else:
                            temp.append(imtemp_blue[k+j])
                            print(j+k)
                    temporary_hold = cv2.merge(temp)
                    blue_3.append(cv2.resize(temporary_hold, (1920, 1080),interpolation=cv2.INTER_AREA))
                    # cv2.imshow("blue",cv2.merge(temp))
                    # cv2. itKey(0)
                    # cv2.destroyAllWindows()
                    k=k+3
                return blue_3
            elif channel == "g":
                k=0
                for i in range(len(b)):
                    temp = []
                    for j in range(3):
                        if i+k>len(imtemp_blue)-3:
                            return blue_3
                        else:
                            temp.append(imtemp_green[k+j])
                            print(j+k)
                    temporary_hold = cv2.merge(temp)
                    blue_3.append(cv2.resize(temporary_hold, (1920, 1080),interpolation=cv2.INTER_AREA))
                    k=k+3
                return blue_3            
            elif channel == "r":
                 k=0
                 for i in range(len(b)):
                    temp = []
                    for j in range(3):
                        if i+k>len(imtemp_green)-3:
                            return blue_3
                        else:
                            temp.append(imtemp_green[k+j])
                    temporary_hold = cv2.merge(temp)
                    blue_3.append(cv2.resize(temporary_hold, (1920, 1080),interpolation=cv2.INTER_AREA))
                    k=k+3
                 return blue_3  
            else:
                return self.read_from_camera1(path) 
    def run(self):
        path = "video081"
        image1, image2 = self.read_sample(path, dataset_name="reference", number_of_frames=10, esc=0, crop=True)
        field_obj = PerlinCrush()
        warped,_ = field_obj.warp_image(image2)
        # image2 = field_obj.warp_image(image2)

        for i in range(len(image2)):
            cv2.imshow("warped", warped[i].detach().cpu().numpy().transpose(1, 2, 0))
            # cv2.imshow("image1", image1[i])
            cv2.waitKey(0)
            cv2.destroyAllWindows()
    
t= FlowFieldGenerationTest()
t.run()