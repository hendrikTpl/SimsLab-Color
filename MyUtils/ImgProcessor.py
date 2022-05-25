import os
import numpy as np
import math
import collections
import numpy as np
import functools
from numpy.lib.stride_tricks import as_strided
from matplotlib.pyplot import imshow
from PIL import Image
from PIL import ImageFont #for watermark
from PIL import ImageDraw #for watermark
   

class ImgProcessor():
    
    def __init__(self, img_path):
        self.img_path = img_path
    
    def load_img(self):
        img = Image.open(self.img_path)
        img = img.convert('RGB')
        img = np.array(img)
        return img
    
    # width, height = im.size
    def detectColor(self, ori_im2arr):
        
        ori_im2arr = self.load_img()
        temp_img = []
        for i in range(len(ori_im2arr)):
            for j in range(len(ori_im2arr[0])):
                # getting the RGB pixel value.
                r, g, b= ori_im2arr[i][j]
                temp_img.append((r, g, b))

        dataColor= ([item for item, count in collections.Counter(temp_img).items() if count > 1])
        # print(len(dataColor))
        # print(dataColor)
        return dataColor
    
    def sortDetectColor(self,dataColor):
        dataColor = sorted(dataColor, key=functools.cmp_to_key(self.compare))    
        return dataColor        
    
    #to order from dark to light by HSP(Highly Sensitive Poo)
    def countHSP(self, item):
        r = int(item[0])
        g = int(item[1])
        b = int(item[2])
        hsp = math.sqrt(0.299 * (r * r) + 0.587 * (g * g) + 0.114 * (b * b))
        return hsp

    def compare(self, item1, item2):
        return self.countHSP(item1) - self.countHSP(item2)
    
    def processA_B(self, ori_im2arr, dataColor, rangeTopWhite, rangeLowerWhite):   
        temparr = []
        bwtemparr = []
        im2arr_largersmaller = []
        im2arr = np.copy(ori_im2arr)
        im2arr_white = im2arr
        im2arr_white =  np.where(im2arr_white < 255, 255, im2arr_white) #im2arr_white.fill(255)
        im2arr_largersmaller = np.copy(im2arr_white)

        for x in range(len(dataColor)):
            r = int(dataColor[x][0])
            g = int(dataColor[x][1])
            b = int(dataColor[x][2])
            if (r in range(rangeLowerWhite, rangeTopWhite+1) and g in range(rangeLowerWhite, rangeTopWhite+1) and b in range(rangeLowerWhite, rangeTopWhite+1)):
                # print("skip")
                continue;
            else:
                im2arr = np.copy(ori_im2arr) # im2arr.shape: height x width x channel

                # set default white
                im2arr_white = im2arr
                im2arr_white = np.where(im2arr_white < 255, 255, im2arr_white) #im2arr_white.fill(255)

                im2arr_process = np.copy(im2arr_white)
                bwim2arr_process = np.copy(im2arr_white)

                for i in range(len(im2arr)):
                    for j in range(len(im2arr[0])):
                        if (r == int(im2arr[i][j][0]) and g == int(im2arr[i][j][1]) and b == int(im2arr[i][j][2])):
                            im2arr_process[i][j] = [r,g,b]
                            bwim2arr_process[i][j] = (int(0), int(0), int(0))
                            im2arr_largersmaller[i][j] = (int(x)) #(int(x), int(x), int(x))

                temparr.append(im2arr_process)
                bwtemparr.append(bwim2arr_process)

        return temparr, bwtemparr, im2arr_largersmaller
    
    def generateFile(self, temparr, fileName, imageFormat, saveto):
        listFileName = []
        for i in range(len(temparr)):
            arr2im = Image.fromarray(temparr[i].astype(np.uint8))
            listFileName.append(fileName+str(i+1)+imageFormat) 
            arr2im.save(os.path.join(saveto, listFileName[i]), format="tiff", compression='tiff_lzw', tiffinfo={317: 2, 278: 1})
    
    def generateFileAL(self, newModiftemparr, dataColor, saveto):
        generateAL = []
        # generateAL = np.copy(newModiftemparr)
        generateAL = np.zeros([len(newModiftemparr), len(newModiftemparr[0]), 3], dtype=np.uint8)
        generateAL.fill(255)
        for i in range(len(newModiftemparr)):
            for j in range(len(newModiftemparr[i])):
                for x in range(len(dataColor)):
                    if(newModiftemparr[i,j] == x): #if(newModiftemparr[i][j][0] == x):
                        generateAL[i,j] = dataColor[x]
        
        modbwarr2im = Image.fromarray(generateAL.astype(np.uint8))  
        modbwarr2im.save(os.path.join(saveto,"AL.tif"), format="tiff", compression='tiff_lzw', tiffinfo={317: 2, 278: 1})
        
        return generateAL
    
    def sliding_window(self, arr, window_size):
        """ Construct a sliding window view of the array"""
        arr = np.asarray(arr)        
        window_size = int(window_size)        
        if arr.ndim != 2:
            raise ValueError("need 2-D input")
        if not (window_size > 0):
            raise ValueError("need a positive window size")
        shape = (arr.shape[0] - window_size + 1,
                arr.shape[1] - window_size + 1,
                window_size, window_size)        
        if shape[0] <= 0:
            shape = (1, shape[1], arr.shape[0], shape[3])
        if shape[1] <= 0:
            shape = (shape[0], 1, shape[2], arr.shape[1])        
        strides = (arr.shape[1]*arr.itemsize, arr.itemsize,
                arr.shape[1]*arr.itemsize, arr.itemsize)        
        return as_strided(arr, shape=shape, strides=strides)
    
    def modif_cell_neighbors(self, arr, arrCopy, i, j, d):
        """Return d-th neighbors of cell (i, j)"""    
        pixelNow = arr[i,j]        
        w = self.sliding_window(arr, 2*d+1)      
        ix = np.clip(i - d, 0, w.shape[0]-1)
        jx = np.clip(j - d, 0, w.shape[1]-1)
        i0 = max(0, i - d - ix)
        j0 = max(0, j - d - jx)
        i1 = w.shape[2] - max(0, d - i + ix)
        j1 = w.shape[3] - max(0, d - j + jx)
        n=0;  
        result = w[ix, jx][i0:i1,j0:j1].ravel()
        
        for x in range (i-d, i+d+1):
            for y in range (j-d, j+d+1):
                if -1 < x < len(arrCopy) and -1 < y < len(arrCopy[0]):
                    if(pixelNow > result[n]): #to check whether pixel larger or smaller than neigbor
                        
                        arrCopy[x,y] = pixelNow
                    # else:
                    #     arrCopy[x,y] = result[n]
                    n+=1
                                        
        return arrCopy
    
    def convertTo2DArray(self, oriArr, w, h):
        copyArr = [[0 for x in range(w)] for y in range(h)]
        for i in range(len(oriArr)):
            for j in range(len(oriArr[i])):
                copyArr[i][j] = oriArr[i][j][0]
    
        return copyArr
    
    
    def reorderDetectColor(self, oriDetectColor, newOrderIndex):
        newOrderColor = [oriDetectColor[i] for i in newOrderIndex]
        return newOrderColor 
    
    def processALNew(self, arrPixelNumberModif1, im2arr_largersmaller, newModiftemparr, sameManipulate=True):
        for i in range (len(im2arr_largersmaller)):
            for j in range (len(im2arr_largersmaller[i])):
                for p in [(i,j)]:
                    if(sameManipulate == True):
                        d = arrPixelNumberModif1
                    else:
                        if(im2arr_largersmaller[i][j] == 255):
                            d = 1
                        else:
                            d = arrPixelNumberModif1[im2arr_largersmaller[i][j]]
                        
                    resultManipulate = self.modif_cell_neighbors(im2arr_largersmaller, newModiftemparr, p[0], p[1], d=d)
        
        return resultManipulate
    
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
    
        
        
        

    
    
                                             
    
    


    
    
    
        