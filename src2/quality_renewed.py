#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 15:11:02 2024
-Prepared running quality plotter in a more user friendly way.
-Uses CRPIX values to pick sun center position
-Set threshold for Sun center detemination
-This runs on entire data. Should be modified to update one text file.
-2024-06-19: Added Vertical line to mark date of baking ending.
- Added check for files <1000 byte size
@author: janmejoyarch
"""
import glob
import numpy as np
import pandas as pd
from datetime import datetime
import os 
from astropy.io import fits
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor

def plot(file, data, col, row): #for plotting full sun image with sun center
    plt.figure()
    plt.imshow(data, origin='lower')
    plt.plot(col, row, 'o', color='red')
    plt.title(file[-44:])
    plt.show()
    plt.close()
    
def qual_plot(filt_name, date_ls, mean_ls, save=False):
    plt.figure(filt_name+"Quality Plot", dpi=300)
    plt.scatter(date_ls, mean_ls/np.max(mean_ls))
    plt.title(f'Quality plot- {filt_name} | Max: {round(np.max(mean_ls),0)}')
    plt.xticks(rotation=30)
    plt.axvline(datetime.strptime("2024-05-13", '%Y-%m-%d'), color='black', label= "Baking Completion (2024-05-13)")
    plt.legend()
    if (save == True): plt.savefig(f"{project_path}/products/{filt_name}.pdf", dpi=300)
    plt.show()

def data_gen(filt_name, data_folders_list, thres, imgshow=False):    
    size=250 #half dimension of analysis box
    date_ls=[] #blank date list
    mean_ls=[] #blank mean vals list
    for folder in data_folders_list: #looping through all folders
        file_list=glob.glob(folder+'/normal_4k/*'+filt_name+'.fits') #generating file list in each normal_4k folder
        for file in file_list: #looping through normal_4k folder for one day
            print(file[-64:])
            if (os.path.getsize(file) < 1000):
                continue
            hdu= fits.open(file)[0]
            qdesc= hdu.header['QDESC']
            if (qdesc != 'Complete Image'): #checks if the image is complete image
                print('Partial File:', file[-64:])
                continue
            col, row= int(hdu.header['CRPIX1']), int(hdu.header['CRPIX2']) #sun center val
            dt_obj= datetime.strptime(hdu.header['DHOBT_DT'].split('.')[0], '%Y-%m-%dT%H:%M:%S') #date time
            data=hdu.data
            data_crop= data[row-size:row+size,col-size:col+size] #cropped image
            mean= np.mean(data_crop) #mean value within size*2 box
            if (mean>thres and (1380 <hdu.header['R_SUN']< 1440)): 
                #threshold to remove door closed images and poor sun center fit images
                mean_ls.append(mean)
                date_ls.append(dt_obj)
                if (imgshow==True): plot(file, data, col, row) #plot the sun image with sun center
                break #break the loop if one image is found in the folder meeting these criteria.
            else:
                print('Skipping', file[-64:])
    qual_plot(filt_name, date_ls, mean_ls, True)
    return(date_ls, mean_ls)

def process(filt_thres):
    filt_name, thres= filt_thres
    date_ls, mean_ls= data_gen(filt_name, data_folders_list, thres, imgshow=False)
    dict={'date': date_ls, 'mean': mean_ls}
    df= pd.DataFrame(dict)
    df.to_csv(f'{project_path}data/interim/qual_data_{filt_name}.csv',index=False, header=False, sep='\t')
    
if __name__=='__main__':
    ##### USER-DEFINED #####
    project_path= os.path.expanduser('~/Dropbox/Janmejoy_SUIT_Dropbox/photometry/photometry_scripts/running_quality_checker_4k_v2_project/')
    data_folders_list= sorted(glob.glob(project_path+'data/raw/*/*/*/')) #list of folders normal_4k
    data_folders_list= data_folders_list[13:] #data_folders_list[13:105]+data_folders_list[-55:-3]
    imgshow=True
    ########################
    
    filt_ls_thres_ls= [("NB01",1000),("NB02",1000),("NB03",1000),("NB04",1000),
                 ("NB05",1000),("NB06",25000),("NB07",25000),("NB08",3200),
                 ("BB01",1000),("BB02",1000),("BB03",18000)] 
    #list of filter names and corresponding threshold values
    
    with ProcessPoolExecutor() as executor:
        executor.map(process, filt_ls_thres_ls)
    
'''    
    filt_list=['NB01','NB02','NB03','NB04','NB05','NB06','NB07','NB08','BB01','BB02','BB03']
    thres_list=[1000]*5+[25000]*2+[3200]+[1000]*2+[18000] #thres values for each filter
    
    for filt_name, thres in zip(filt_list,thres_list):
        date_ls, mean_ls= data_gen(filt_name, thres, imgshow=False)
        dict={'date': date_ls, 'mean': mean_ls}
        df= pd.DataFrame(dict)
        df.to_csv(f'{project_path}data/interim/qual_data_{filt_name}.csv',index=False, header=False, sep='\t')
'''        