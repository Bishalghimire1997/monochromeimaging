from skimage.color import rgb2lab,deltaE_cie76,deltaE_ciede2000
class ColorDifference():
    def __init__(self):
        pass 
    def cied_2000(self,image1,image2):
        """This method computes the color difference between two images
        image1 and image2 are the two images to be compared
        The method returns the difference between the two images"""
        lab1 = rgb2lab(image1)
        lab2 = rgb2lab(image2)
        delta_e_map = deltaE_ciede2000(lab1, lab2) 
        lab1 = rgb2lab(image1)
        lab2 = rgb2lab(image2)
        print(delta_e_map.mean())   
     
    def cie_76(self,image1,image2):
        """This method computes the color difference between two images
        image1 and image2 are the two images to be compared
        The method returns the difference between the two images"""
        lab1 = rgb2lab(image1)
        lab2 = rgb2lab(image2)
        delta_e_map = deltaE_cie76(image1, image2) 
        lab1 = rgb2lab(image1)
        lab2 = rgb2lab(image2)
        print(delta_e_map.mean())
        pass
      
