#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 15:11:02 2024
-Prepared running quality plotter in a more user friendly way.
-Uses CRPIX values to pick sun center position
-Set threshold for Sun center detemination
-This runs on entire data. Should be modified to update one text file.
@author: janmejoyarch
"""
import glob
import numpy as np
import pandas as pd
from datetime import datetime
import os 
from astropy.io import fits
import matplotlib.pyplot as plt
import pandas as pd

def plot(file, col, row): #for plotting full sun image with sun center
    plt.figure()
    plt.imshow(data, origin='lower')
    plt.plot(col, row, 'o', color='red')
    plt.title(file[-44:])
    plt.show()
    plt.close()
def qual_plot(date_ls, mean_ls):
    plt.figure("Quality Plot")
    plt.scatter(date_ls, mean_ls)
    plt.title('Quality plot- '+filt_name)
    plt.xticks(rotation=45)
    plt.show()

def data_gen(filt_name, data_folders_list, thres, imgshow=False):    
    size=250 #half dimension of analysis box
    date_ls=[] #blank date list
    mean_ls=[] #blank mean vals list
    for folder in data_folders_list: #looping through all folders
        file_list=glob.glob(folder+'/normal_4k/*'+filt_name+'.fits') #generating file list in each normal_4k folder
        for file in file_list: #looping through normal_4k folder for one day
            hdu= fits.open(file)[0]
            qdesc= hdu.header['QDESC']
            if (qdesc == 'Complete Image'): #checks if the image is complete image
                col, row= int(hdu.header['CRPIX1']), int(hdu.header['CRPIX2']) #sun center val
                dt_obj= datetime.strptime(hdu.header['DHOBT_DT'].split('.')[0], '%Y-%m-%dT%H:%M:%S') #date time
                data=hdu.data
                data_crop= data[row-size:row+size,col-size:col+size] #cropped image
                mean= np.mean(data_crop) #mean value within size*2 box
                if (mean>thres and (1380 <hdu.header['R_SUN']< 1440)): 
                    #threshold to remove door closed images and poor sun center fit images
                    mean_ls.append(mean)
                    date_ls.append(dt_obj)
                    if (imgshow==True): plot(file, col, row) #plot the sun image with sun center
                    break #break the loop if one image is found in the folder meeting these criteria.
                else:
                    print('Skipping', file[-64:])
            else:
                print('Partial File:', file[-64:])
    return(date_ls, mean_ls)

if __name__=='__main__':
    ##### USER-DEFINED #####
    filt_list=['NB01','NB02','NB03','NB04','NB05','NB06','NB07','NB08','BB01','BB02','BB03']
    filt_name=filt_list[5]
    project_path= os.path.expanduser('~/Dropbox/Janmejoy_SUIT_Dropbox/scripts/photometry/running_quality_checker_4k_v2_project/')
    data_folders_list= sorted(glob.glob(project_path+'data/raw/*/*/*/'))[13:] #list of folders normal_4k
    imgshow=False
    thres=1000
    ########################
    date_ls, mean_ls= data_gen(filt_name, data_folders_list, thres, imgshow=False)
    dict={'date': date_ls, 'mean': mean_ls}
    df= pd.DataFrame(dict)