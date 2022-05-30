import os
import numpy as np
import time
from MyUtils.ImgProcessor import *

def main():
    #settings
    img_src = './img_src/1_Sharp_Edge/03/LIU0125'
    img_name = 'A.tif'
    img_res = './img_result/1_Sharp_Edge/03/LIU0125/'
    img_path = os.path.join(img_src, img_name) 
    # settings for color boundary
    rangeTopWhite = 255
    rangeLowerWhite = 240
    pix_modify = int(1)
        
    # If folder doesn't exist, then create it.
    directory = os.path.dirname(img_res)
    try:
        os.mkdir(directory)
        print("created folder : ", directory)
        
    except FileExistsError:
        # directory already exists
        print(directory, "folder already exists, Thus Directory will not created.")
      
    # Start timing the process
    t1_start = time.process_time() 
    # class constructor
    imgProc = ImgProcessor(img_path)
    #load img
    img_arr = imgProc.load_img()
    img_h = img_arr.shape[0]
    img_w = img_arr.shape[1]
    img_ori = np.array(img_arr)
    print("Image has been loaded: {} size: {}x{}".format(img_path, img_h, img_w))
    ##detect color
    dt_color = imgProc.detectColor(img_arr)
    dt_color = np.array(imgProc.sortDetectColor(dt_color))
    t1_stop = time.process_time()
    print("Color has been detected: ", dt_color)
    t2_start = time.process_time()
    temparr, bwtemparr, im2arr_largersmaller = imgProc.processA_B(img_arr,dt_color,rangeTopWhite,rangeLowerWhite)
    #print("temparr: {} \n bwtemarr: {} \n im2arr_largersmaller: {}".format(temparr,bwtemparr, im2arr_largersmaller ) )
       
    saveto = img_res
    imgProc.generateFile(temparr,"A",".tif",saveto)
    imgProc.generateFile(bwtemparr,"B",".tif",saveto)
    t2_stop = time.process_time() #stop process time A and B
    
    t3_start = time.process_time() # start process AL
    sameManipulate = True
    arrPixelNumberModif = pix_modify # make sure as int, pixel of image to manipulate
    newModiftemparr = []
    h, w, c = im2arr_largersmaller.shape
    # width, height = img.size
    copyIm2arr_largersmaller = np.array(imgProc.convertTo2DArray(im2arr_largersmaller, w, h))
    newModiftemparr = np.array(imgProc.convertTo2DArray(im2arr_largersmaller, w, h)) #np.copy(copyIm2arr_largersmaller)
    newModiftemparr = imgProc.processALNew(arrPixelNumberModif, copyIm2arr_largersmaller, newModiftemparr, sameManipulate)
    
    #generated new image with manipulated pixels (AL)
    generateAL = imgProc.generateFileAL(newModiftemparr,dt_color, saveto)
    #print("generateAL: ",generateAL)
    t3_stop = time.process_time() #stop process time AL
    
    t4_start = time.process_time() # start process 1,2,3, .., n-mask images
    temparrAL = []
    bwtemparrAL = []
    im2arr_largersmallerAL = []
    temparrAL, bwtemparrAL, im2arr_largersmallerAL = imgProc.processA_B(generateAL, dt_color, rangeTopWhite, rangeLowerWhite)
    imgProc.generateFile(bwtemparrAL, "", ".tif", saveto=saveto)
    t4_stop = time.process_time() # stop process 1,2,3, .., n-mask images
  
    # # save to file for thumbnail
    t5_start = time.process_time() # start process thumbnail and watermark A1,A2,A3, .., n-mask images
    for i in range(len(temparr)):
        #img_arr= temparr[i]
        imgProc.ImgWatermark(imgArr=temparr[i], saveto=saveto, fname='A'+str(i+1)+'_thumbnail', ext=".png")
    t5_stop = time.process_time() # stop process thumbnail and watermark A1, A2, A3, ..., An
    t6_start = time.process_time() # start process thumbnail and watermark B1,B2,B3, .., n-mask images
    for i in range(len(bwtemparr)):
        #img_arr= bwtemparr[i]
        imgProc.ImgWatermark(imgArr=bwtemparr[i], saveto=saveto, fname='B'+str(i+1)+'_thumbnail', ext=".png")
    t6_stop = time.process_time() # stop process thumbnail and watermark B1, B2, B3, ..., Bn
    #1,2,..., n image
    t7_start = time.process_time() # start process thumbnail and watermark 1,2,3, .., n-mask images
    for i in range(len(bwtemparrAL)):
        #img_arr= bwtemparrAL[i]
        imgProc.ImgWatermark(imgArr=bwtemparrAL[i], saveto=saveto, fname=str(i+1)+'_thumbnail', ext=".png")
    t7_stop = time.process_time() # stop process thumbnail and watermark 1, 2, 3, ..., n
    # AL image
    t8_start = time.process_time() # start process thumbnail and watermark AL image
    imgProc.ImgWatermark(imgArr=generateAL, saveto=saveto, fname='AL_thumbnail', ext=".png")
    t8_stop = time.process_time() # stop process thumbnail and watermark AL image
    #original image
    t9_start = time.process_time() # start process thumbnail and watermark original image
    imgProc.ImgWatermark(imgArr=img_ori,saveto=saveto, fname='A'+'_thumbnail', ext=".png")
    t9_stop = time.process_time() # stop process thumbnail and watermark original image        
       
    print("Time for image loading and color detection: {} sec".format(t1_stop - t1_start) )
    print("Time for processing A and B: {} sec".format(t2_stop - t2_start))
    print("Time for processing AL: {} sec".format(t3_stop - t3_start))
    print("Time for processing 1,2,3, .., n-mask images: {} sec".format(t4_stop - t4_start))
    print("Time for processing thumbnail and watermark A1,A2,..An images: {} sec".format(t5_stop - t5_start))
    print("Time for processing thumbnail and watermark B1,B2,..Bn images: {} sec".format(t6_stop - t6_start))
    print("Time for processing thumbnail and watermark 1,2,3, .., n-mask images: {} sec".format(t7_stop - t7_start))
    print("Time for processing thumbnail and watermark AL image: {} sec".format(t8_stop - t8_start))
    print("Time for processing thumbnail and watermark original image: {} sec".format(t9_stop - t9_start))   
    
if __name__ == '__main__':
    main()
    