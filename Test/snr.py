import numpy as np
import re
from h5_file_format_package.h5_format import H5FormatRead
import matplotlib.pyplot as plt
from pathlib import Path

class SNR:
    def __init__(self, file_path):
        self.path = Path(file_path)
    def bayer_masks_rg8(self,image_shape, pattern='RGGB'):
        h, w = image_shape
        R = np.zeros((h, w), dtype=np.uint8)
        G = np.zeros((h, w), dtype=np.uint8)
        B = np.zeros((h, w), dtype=np.uint8)

        if pattern == 'RGGB':
            R[0::2, 0::2] = 1
            G[0::2, 1::2] = 1
            G[1::2, 0::2] = 1
            B[1::2, 1::2] = 1
        elif pattern == 'BGGR':
            B[0::2, 0::2] = 1
            G[0::2, 1::2] = 1
            G[1::2, 0::2] = 1
            R[1::2, 1::2] = 1
        elif pattern == 'GRBG':
            G[0::2, 0::2] = 1
            R[0::2, 1::2] = 1
            B[1::2, 0::2] = 1
            G[1::2, 1::2] = 1
        elif pattern == 'GBRG':
            G[0::2, 0::2] = 1
            B[0::2, 1::2] = 1
            R[1::2, 0::2] = 1
            G[1::2, 1::2] = 1
        else:
            raise ValueError(f"Unsupported Bayer pattern: {pattern}")


        return R, G, B

    def read_images(self, n_frames=100):
        images = []
        obj = H5FormatRead()
        Start_from = 300

        for i in range(n_frames):
            im = obj.read_files(str(self.path), str(i+Start_from))  # ensure string path
            images.append(im)
        h,w,c = images[0].shape 
        print(images[0].shape)

        
        b_mask,g_mask,r_mask = self.bayer_masks_rg8(image_shape=(h,w))

        np_im = np.array(images)

        mn = np.mean(np_im, axis=0) # mean over frame axis
        sd = np.std(np_im, axis=0) # std over frame axis

        mn_b = mn[:,:,0]
        mn_g = mn[:,:,1]
        mn_r = mn[:,:,2]



        mn_b_masked = mn_b#mn_b[b_mask == 1]
        mn_g_masked = mn_g#mn_g[g_mask == 1]
        mn_r_masked = mn_r#mn_r[r_mask == 1]

       


        
        sd_b = sd[:,:,0]
        sd_g = sd[:,:,1]
        sd_r = sd[:,:,2]
        sd_b_masked = sd_b#sd_b[b_mask == 1]
        sd_g_masked = sd_g#sd_g[g_mask == 1]
        sd_r_masked = sd_r#sd_r[r_mask == 1]
         
        


        
       

        print(f"\nFile: {self.path.name}")
        print("Global mean intensity =", np.mean(mn))
        print("Global mean std       =", np.mean(sd))
       

        return np.mean(mn_b_masked).item(),np.mean(mn_g_masked).item(),np.mean(mn_r_masked).item(), np.mean(sd_b_masked).item(),np.mean(sd_g_masked).item(),np.mean(sd_r_masked).item()

    def plot_maps(mean_blue, mean_green, mean_red, std_blue, std_green, std_red):
        x = range(len(mean_blue))  # x-axis = file index

        plt.figure(figsize=(10, 6))
        
        # Mean plots
        plt.plot(x, mean_blue, 'b-o', label='Mean Blue')
        plt.plot(x, mean_green, 'g-o', label='Mean Green')
        plt.plot(x, mean_red, 'r-o', label='Mean Red')

        # Std plots (dashed)
        plt.plot(x, std_blue, 'b--', label='Std Blue')
        plt.plot(x, std_green, 'g--', label='Std Green')
        plt.plot(x, std_red, 'r--', label='Std Red')

        plt.xlabel('File Index')
        plt.ylabel('Value')
        plt.title('Mean and Standard Deviation per Color Channel')
        plt.legend()
        plt.grid(True)
        plt.tight_layout()
        plt.show()

# Folder containing your .h5 files
data_dir = Path(r"C:\Users\SIU856587710\OneDrive - Southern Illinois University\Desktop\color sample\monochromeimaging\dark_current_experiment\images_taken_in_no_light")
def extract_number(filename):
    match = re.search(r'\d+', filename.stem)
    return int(match.group()) if match else 0

h5_files = sorted(data_dir.glob("*.h5"), key=extract_number)


# Loop over all .h5 files
mean_blue=[]
mean_green = []
mean_red = []
std_blue =[]
std_green=[]
std_red = []

for h5_file in h5_files:
    snr = SNR(h5_file)
    mean_b,mean_g,mean_r, std_b,std_g,std_r= snr.read_images(n_frames=100)  
    mean_blue.append(mean_b)
    mean_green.append(mean_g)
    mean_red.append(mean_r)
    std_blue.append(std_b)
    std_green.append(std_g)
    std_red.append(std_r)
print(len(mean_blue))
print(mean_blue)
SNR.plot_maps(mean_blue,mean_green,mean_red,std_blue,std_green,std_red)