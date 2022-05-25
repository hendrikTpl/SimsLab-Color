import sys, os
from matplotlib.pyplot import axis
import pandas as pd
import numpy as np

## need to read the label from img.id.txt

root = "/media/infinity/HT_HDD1/simslabColorDataset/"
path = os.path.join(root, "1_Sharp_Edge")
f_ext = 'tif'

full_path = []
data = []

for path, subdirs, files in os.walk(root):   
    for fname in files:
        if fname.endswith(f_ext):
            full_path.append(os.path.join(path, fname))
            print(os.path.join(path, fname))
    else:
        print("skipped, File with ext {} is selected".format(f_ext))
        continue
# sort the filenames             
#full_path.sort(key=lambda x: x.split("/")[-1]) 

for i in range(len(full_path)):
    d = full_path[i].split("/")
    data.append(d)
    #print(full_path[i])

def imgLabel(x):
    if x =='A':
        lbl = "original"
    elif x == 'AL':
        lbl = "edited_result"
    else:
        lbl = "black_white"
    return lbl

#parse the data into a pandas dataframe
data = pd.DataFrame(data)
data = data.iloc[:,-4:] # select last 4 column
# parse the data into database schema 
id = np.arange(start=1, stop=len(data) + 1, step=1) #auto increment id start from 1 to the length of data
img_id =data.iloc[:,2]
img_category =data.iloc[:,0] #1: sharp edge, 2: blurred edge
n_color = data.iloc[:,1]
img_type = data.iloc[:,3].str[:-4]
save_data = pd.DataFrame({"id":id, "img_id":img_id, "img_category":img_category, "n_color":n_color, "img_type":img_type})
save_data['isRGB']  = save_data['img_type'].apply(lambda x: 1 if x == 'A' or x =='AL' else 0)
save_data['img_label'] = save_data['img_type'].apply(lambda x: imgLabel(x))
#save to csv
save_data.to_csv("1_Sharp_Edge_DB.csv", index=False)