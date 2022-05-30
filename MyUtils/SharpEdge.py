import os
import numpy as np
import math
import collections
import functools
from PIL import Image
from ImageProc import ImageProc

class SharpEdge(ImageProc):
    def __init__(self, img_path):
        super().__init__(img_path)
        self.img_path = img_path
    
    def detectColor(self):
        img = self.load_img() #inherect from ImageProc
        #TODO: define a function to detect color fro edge color
        
        return img
    
    #TODO: define a function for sharp edge
    def otherFuc(self):
        pass
       
#test of usage
img_src = './img_src/1_Sharp_Edge/03/LIU0125'
img_name = 'A.tif'
img_res = './img_result/1_Sharp_Edge/03/LIU0125/'
img_path = os.path.join(img_src, img_name)

sharpImg = SharpEdge(img_path)
color = sharpImg.detectColor()
print(color)
       

    

