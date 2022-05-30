import os
import numpy as np
import math
import collections
import functools
from PIL import Image
from PIL import ImageFont #for watermark
from PIL import ImageDraw #for watermark

class ImageProc():
    
    def __init__(self, img_path):
        self.img_path = img_path
    
    def load_img(self):
        img = Image.open(self.img_path)
        img = img.convert('RGB')
        img = np.array(img)
        return img
    
    def ImgWatermark(self, imgArr, saveto, fname, ext,  watermark='SimsLab', watermark_size=50, watermark_pos=(0, 0), font="arial.ttf", clr=(255, 255, 255),stroke_width=2, stroke_fill='black'):
        """
        Add watermark to an image.
        :param imgArr: numpy array of the image to add watermark to
        """ 
        imgArr = np.asarray(imgArr) #convert to numpy array
        img = Image.fromarray(imgArr.astype('uint8')).resize(size=(500,500)) #load to image and resize
        # text Watermark
        watermark_image = img.copy()
        #editable image
        draw = ImageDraw.Draw(watermark_image)
        # ("font type",font size)
        fnt = ImageFont.truetype(font, watermark_size)        
        # add watermark
        draw.text(watermark_pos, watermark, color=clr, font=fnt, stroke_width=stroke_width, stroke_fill=stroke_fill)
        watermark_image.save(os.path.join(saveto, fname+ext))
    
    ## TODO
    # add general function that all child class can use
    # for example: detect color, sort color for each category in the image
    
    def generalFunction(self):
        pass
    