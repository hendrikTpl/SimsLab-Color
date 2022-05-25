from re import template
from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.template import loader
from webapp.models import add_img_table, img_categories, img_helper_table, img_processed_table
from webapp.forms import add_img_form
import os
from django.conf import settings

#for image processing
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw
import numpy as np
import math
import collections
import numpy as np
import functools
from numpy.lib.stride_tricks import as_strided
import base64
from io import BytesIO

# class for image processing tools here
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
        w = self.sliding_window(arr, 2*(int(d))+1)  # d-th neighbors    
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

    # using to generate thumbnail image
    def ImgWatermark(self, imgArr, saveto, fname, ext,  watermark='SimsLab', watermark_size=50, watermark_pos=(0, 0), font="Montserrat-Light.ttf", clr=(255, 255, 255),stroke_width=2, stroke_fill='black'):
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
        font_path = os.path.join(settings.BASE_DIR, 'static/fonts/'+font)
        fnt = ImageFont.truetype(font_path, watermark_size)        
        # add watermark
        draw.text(watermark_pos, watermark, color=clr, font=fnt, stroke_width=stroke_width, stroke_fill=stroke_fill)
        watermark_image.save(os.path.join(saveto, fname+ext))  
    
#########################################################################################################
## menu    
#########################################################################################################
# Create your views here.
#home
def home(request):
    last_six = add_img_table.objects.order_by('-id')[:5]
    last_processed = img_processed_table.objects.order_by('-id')[:5]
    return render(request,'home.html',{'last_six':last_six, 'last_processed':last_processed})

#add image
def add_img(request):

    template = loader.get_template('process_img.html')

    if request.method =="GET":
        addform = add_img_form()
        return render(request, "add.html",{"addform":addform})
    else: #POST
        addform = add_img_form(request.POST, request.FILES)
        if addform.is_valid():
            addform.save()
            # display the image and another form to process the image
            img_ori = add_img_table.objects.order_by('-id')[:1] #last added image            
            
            context = {
                'img_ori': img_ori,
            }
            return HttpResponse(template.render(context, request))
         

#process image from add_img
def process_img(request):
    #TODO: process image (A) to get the color mask(A1,..An) and the black-white image mask(B1,..Bn)
    #    and take (B) to get the corrected image (1,.., n) and then reconstruct back to RGB imge to get final image (AL)
    template = loader.get_template('processed.html')

    if request.method =="GET":
        return HttpResponseRedirect(reverse('add_img'))

    elif request.method =="POST":        
        #get the parameters from the form
        rangeTopWhite = 255
        rangeLowerWhite = 248
        pix_modify =  request.POST['pix_modify']
        id = request.POST['id_']
        imgID = request.POST['img_id_']
        imgCat = request.POST['img_cat_']
        imgClr = request.POST['img_color_']

        #get the image from add_img_table
        img_ori=add_img_table.objects.get(id=id)
        img_ori_path = img_ori.img_file.path      
        
        """
            process the image using the sharp edge method
        """
        # class constructor
        imgProc = ImgProcessor(img_ori_path)
        # get the image as numpy array
        #load img
        img_arr = imgProc.load_img()
        img_h = img_arr.shape[0]
        img_w = img_arr.shape[1]        
        #detect color
        dt_color = imgProc.detectColor(img_arr)
        dt_color = np.array(imgProc.sortDetectColor(dt_color))
        #making the color mask and image mask
        temparr, bwtemparr, im2arr_largersmaller = imgProc.processA_B(img_arr,dt_color,rangeTopWhite,rangeLowerWhite)
        #save the image to the folder media
        savepath = imgCat+"/"+imgClr+"/"+imgID #savepath = "cat/color/id"
        saveto = os.path.join(settings.MEDIA_ROOT, savepath)
        imgProc.generateFile(temparr, "A", ".tif", saveto)
        imgProc.generateFile(bwtemparr, "B", ".tif", saveto)        

        #process AL
        sameManipulate = True
        arrPixelNumberModif = int(pix_modify) #make sure it is integer
        newModiftemparr = []
        h, w, c = im2arr_largersmaller.shape
        copyIm2arr_largersmaller = np.array(imgProc.convertTo2DArray(im2arr_largersmaller, w, h))
        newModiftemparr = np.array(imgProc.convertTo2DArray(im2arr_largersmaller, w, h)) #np.copy(copyIm2arr_largersmaller)
        newModiftemparr = imgProc.processALNew(arrPixelNumberModif, copyIm2arr_largersmaller, newModiftemparr, sameManipulate)

        #save the AL image to the folder media   
        #generated new image with manipulated pixels (AL)
        generateAL = imgProc.generateFileAL(newModiftemparr,dt_color, saveto)
        temparrAL = []
        bwtemparrAL = []
        im2arr_largersmallerAL = []
        temparrAL, bwtemparrAL, im2arr_largersmallerAL = imgProc.processA_B(generateAL, dt_color, rangeTopWhite, rangeLowerWhite)
        imgProc.generateFile(bwtemparrAL, "", ".tif", saveto=saveto)

        """
        #adding Thumbnails Image that already watermarked
        """
        #original image
        imgProc.ImgWatermark(imgArr=img_arr,saveto=saveto, fname='A'+'_thumbnail', ext=".png")    
        #color mask image
        for i in range(len(temparr)):
            #img_arr= temparr[i]
            imgProc.ImgWatermark(imgArr=temparr[i], saveto=saveto, fname='A'+str(i+1)+'_thumbnail', ext=".png")
        #black-white image
        for i in range(len(bwtemparr)):
            # img_arr= bwtemparr[i]
            imgProc.ImgWatermark(imgArr=bwtemparr[i], saveto=saveto, fname='B'+str(i+1)+'_thumbnail', ext=".png")
        #1,2,..., n image
        for i in range(len(bwtemparrAL)):
            # img_arr= bwtemparrAL[i]
            imgProc.ImgWatermark(imgArr=bwtemparrAL[i], saveto=saveto, fname=str(i+1)+'_thumbnail', ext=".png")
        # AL image
        imgProc.ImgWatermark(imgArr=generateAL, saveto=saveto, fname='AL_thumbnail', ext=".png")

        """
        save the image to the database
        """
        # original image(A)# update thumbnail
        img_ori.img_thumbs = savepath+"/A_thumbnail.png"
        img_ori.save()
        
        #color mask image (A1,..An)
        A_list = []       
        for i in range(len(temparr)):
            rec_A = img_processed_table(
                img_file = savepath+"/A"+str(i+1)+".tif", 
                img_thumbs = savepath+"/A"+str(i+1)+"_thumbnail.png",
                img_category = img_categories.objects.get(img_categ=imgCat),
                n_color = imgClr,
                img_id = imgID,
                img_h = img_h,
                img_w = img_w,
                img_type = "A"+str(i+1),
                isRGB = False,
                img_label = img_ori.img_label
                )
            A_list.append(rec_A)
        img_processed_table.objects.bulk_create(A_list)
        
        # #black-white image (B1,..Bn)
        B_list = []       
        for i in range(len(bwtemparr)):
            rec_B = img_processed_table(
                img_file = savepath+"/B"+str(i+1)+".tif",
                img_thumbs = savepath+"/B"+str(i+1)+"_thumbnail.png",
                img_category = img_categories.objects.get(img_categ=imgCat),
                n_color = imgClr,
                img_id = imgID,
                img_h = img_h,
                img_w = img_h,
                img_type = "B"+str(i+1),
                isRGB = False,
                img_label = img_ori.img_label,
            )
            B_list.append(rec_B)    
        img_processed_table.objects.bulk_create(B_list)
        
        # #1,2,..., n image (type 1,2,..n)image to the database
        img12n_list = []           
        for i in range(len(bwtemparrAL)):
            rec_12n = img_processed_table(
                img_file = savepath+"/"+str(i+1)+".tif",
                img_thumbs = savepath+"/"+str(i+1)+"_thumbnail.png",
                img_category = img_categories.objects.get(img_categ=imgCat),
                n_color = imgClr,
                img_id = imgID,
                img_h = img_h,
                img_w = img_h,
                img_type = str(i+1),
                isRGB = False,
                img_label = img_ori.img_label
            )
            img12n_list.append(rec_12n)
        img_processed_table.objects.bulk_create(img12n_list)

        ##AL image to the database
        AL_list = [] 
        rec_AL = img_processed_table(
            img_file = savepath+"/AL"+".tif",
            img_thumbs = savepath+"/AL_thumbnail.png",
            img_category = img_categories.objects.get(img_categ=imgCat),
            n_color = imgClr,
            img_id = imgID,
            img_h = img_h,
            img_w = img_h,
            img_type = "AL",
            isRGB = True,
            img_label = img_ori.img_label
        )
        AL_list.append(rec_AL)
        img_processed_table.objects.bulk_create(AL_list)
        
        # saveImgA = img_processed_table()        
        # for i in range(len(temparr)):                        
        #     saveImgA.img_file = savepath+"/A"+str(i+1)+".tif"
        #     saveImgA.img_thumbs = savepath+"/A"+str(i+1)+"_thumbnail.png"
        #     saveImgA.img_category = img_categories.objects.get(img_categ=imgCat)
        #     saveImgA.n_color = imgClr
        #     saveImgA.img_id = imgID
        #     saveImgA.img_h = img_h
        #     saveImgA.img_w = img_w
        #     saveImgA.img_type = "A"+str(i+1)
        #     saveImgA.isRGB = False
        #     saveImgA.img_label = img_ori.img_label
        #     saveImgA.save()
        # #black-white image (B1,..Bn)   
        # saveImgB = img_processed_table()     
        # for i in range(len(bwtemparr)):
        #     saveImgB.img_file = savepath+"/B"+str(i+1)+".tif"
        #     saveImgB.img_thumbs = savepath+"/B"+str(i+1)+"_thumbnail.png"
        #     saveImgB.img_category = img_categories.objects.get(img_categ=imgCat)
        #     saveImgB.n_color = imgClr
        #     saveImgB.img_id = imgID
        #     saveImgB.img_h = img_h
        #     saveImgB.img_w = img_h
        #     saveImgB.img_type = "B"+str(i+1)
        #     saveImgB.isRGB = False
        #     saveImgB.img_label = img_ori.img_label
        #     saveImgB.save()
        # #1,2,..., n image (type 1,2,..n)image to the database
        # saveImg1 = img_processed_table()            
        # for i in range(len(bwtemparrAL)):
        #     saveImg1.img_file = savepath+"/"+str(i+1)+".tif"
        #     saveImg1.img_thumbs = savepath+"/"+str(i+1)+"_thumbnail.png"
        #     saveImg1.img_category = img_categories.objects.get(img_categ=imgCat)
        #     saveImg1.n_color = imgClr
        #     saveImg1.img_id = imgID
        #     saveImg1.img_h = img_h
        #     saveImg1.img_w = img_h
        #     saveImg1.img_type = str(i+1)
        #     saveImg1.isRGB = False
        #     saveImg1.img_label = img_ori.img_label
        #     saveImg1.save()

        # #AL image to the database       
        # saveImgAL = img_processed_table() 
        # for i in range(len(generateAL)):
        #     saveImgAL.img_file = savepath+"/AL"+".tif"
        #     saveImgAL.img_thumbs = savepath+"/AL_thumbnail.png"
        #     saveImgAL.img_category = img_categories.objects.get(img_categ=imgCat)
        #     saveImgAL.n_color = imgClr
        #     saveImgAL.img_id = imgID
        #     saveImgAL.img_h = img_h
        #     saveImgAL.img_w = img_h
        #     saveImgAL.img_type = "AL"
        #     saveImgAL.isRGB = True
        #     saveImgAL.img_label = img_ori.img_label
        #     saveImgAL.save()        

        # img_proc_info = {
        #     'img_id': imgID, 
        #     'img_h': img_h, 
        #     'img_w': img_w, 
        #     'pix_modify': pix_modify,
        #     'img_label':img_ori.img_label,
        #     #'img_categ':img_ori.img_category.img_categ,
        #     #'img_type':img_ori.img_category.img_type,
        #     'img_thumbs':savepath+"/AL_thumbnail.png",
        #     }
        # context = {
        #         'img_proc_info': img_proc_info,
        #         'img_ori_info': img_ori,
        #     }
        # return HttpResponse(template.render(context, request)) 
        return HttpResponseRedirect(reverse('home'))      


    #TODO
    # if imgCat == '1': # 1_Sharp_Edge
    #   pass
    # elif imgCat == '2': # 2_Blury_Edge
    #     pass
    # elif imgCat == '3': # 3_Scan_Image
    #     pass
    # elif imgCat == '4': # 4_Dyed_Fabric
    #     pass
    # elif imgCat == '5': # 5_Broken_Image
    #     pass
     


#search image
def search(request):
    
    if 'qry_search' in request.GET:
        qry_search=request.GET['qry_search']
        if not qry_search or qry_search == "":
            return render(request, 'search.html')
        else:
            search=img_processed_table.objects.filter(img_id__icontains=qry_search)
    else:
        search=img_processed_table.objects.order_by('-id')[:5]
    return render(request, "search.html",{"search":search})

def show_ori(request, id):
    res1=add_img_table.objects.get(id=id)
    template = loader.get_template('show_ori.html')
    
    img = Image.open(res1.img_file.path)
    img_h = img.height
    img_w = img.width
    img_path = res1.img_file.path
    img_info = {'img_h': img_h, 'img_w': img_w, 'img_path': img_path}    

    context = {
        'show_ori': res1,
        'img_info': img_info,
    }
    return HttpResponse(template.render(context, request))


def show_real(request, id):
    res=img_processed_table.objects.get(id=id)   
    template = loader.get_template('show_real.html')
    context = {
        'show_real': res,
    }
    return HttpResponse(template.render(context, request))



def show_img(request):
    # template = loader.get_template('show_img.html')
    # return HttpResponse(template.render())
    AddImg = img_helper_table.objects.all().values()
    template = loader.get_template('show_img.html')
    context = {
        'coba': AddImg,
    }
    return HttpResponse(template.render(context, request))

def guide(request):
    template = loader.get_template('guide.html')
    return HttpResponse(template.render({}, request))

def tambah(request):
    template = loader.get_template('tambah.html')
    return HttpResponse(template.render({}, request))

def tambah_proc(request):
    imgID = request.POST['img_id_']
    imgCat = request.POST['img_cat_']
    imgColor = request.POST['img_color_']
    data = img_helper_table(img_id=imgID, img_category=imgCat, n_color=imgColor)
    data.save()
    return HttpResponseRedirect(reverse('show_img'))

def hapus(request, id):
    hps = img_helper_table.objects.get(id=id)
    hps.delete()
    return HttpResponseRedirect(reverse('show_img'))

def edit_img(request):
    pass

def remove_img(request):
    pass

def showlist(request):
    results=img_helper_table.objects.all
    return render(request, "showlist.html",{"showcateg":results})