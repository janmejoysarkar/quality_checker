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
-2024-07-05: Automated plot saving disabled.
-Error messages:
    zero_size_error: File size is not as per requirement.
    sun_center_error: Sun center does not fall on the sun, 
    or Sun radius is highly deviant.
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
    plt.figure(filt_name+"Quality Plot")
    plt.scatter(date_ls, mean_ls/np.max(mean_ls))
    plt.title(f'Quality plot- {filt_name} | Max: {round(np.max(mean_ls),0)}')
    plt.xticks(rotation=30)
    for bake_start, bake_end in bake_list:
        plt.axvline(datetime.strptime(bake_start, '%Y-%m-%d'), color='blue', linestyle='--', label= f"BakeStart_{bake_start}")
        plt.axvline(datetime.strptime(bake_end, '%Y-%m-%d'), color='red', linestyle='--', label= f"BakeEnd_{bake_end}")
    plt.ylabel("Exposure time normalized relative intensity")
    plt.legend()
    if (save == True): plt.savefig(f"{project_path}/products/{filt_name}.pdf", dpi=300)
    if show_plot: plt.show()

def data_gen(filt_name, data_folders_list, thres, imgshow=False):    
    size=250 #half dimension of analysis box
    date_ls=[] #blank date list
    mean_ls=[] #blank mean vals list
    for folder in data_folders_list: #looping through all folders
        file_list=glob.glob(folder+'/normal_4k/*'+filt_name+'.fits') #generating file list in each normal_4k folder
        file_list= file_list+glob.glob(folder+'/engg4/*'+filt_name+'.fits')
        for file in file_list: #looping through normal_4k folder for one day
            if os.path.getsize(file) < 1e6:
                print("zero_size_error:", os.path.basename(file))
                continue
            hdu= fits.open(file)[0]
            qdesc= hdu.header['QDESC']
            if (qdesc != 'Complete Image'): #checks if the image is complete image
                print('Partial File:', os.path.basename(file))
                continue
            naxis1= hdu.header['NAXIS1']
            if (naxis1 != 4096): #checks if the image is complete image
                print('Not_4k:', os.path.basename(file))
                continue
            col, row= int(hdu.header['CRPIX1']), int(hdu.header['CRPIX2']) #sun center val
            dt_obj= datetime.strptime(hdu.header['DHOBT_DT'].split('.')[0], '%Y-%m-%dT%H:%M:%S') #date time
            exp_t= hdu.header['CMD_EXPT']/1e3
            data=hdu.data
            data_crop= data[row-size:row+size,col-size:col+size] #cropped image
            mean= np.mean(data_crop) #mean value within size*2 box
            if (mean>thres and (1350 <hdu.header['R_SUN']< 1440)): 
                #threshold to remove door closed images and poor sun center fit images
                mean_ls.append(mean/exp_t) #Counts per second
                date_ls.append(dt_obj)
                if (imgshow==True): plot(file, data, col, row) #plot the sun image with sun center
                print("Plotting:", os.path.basename(file))
                break #break the loop if one image is found in the folder meeting these criteria.
            else:
                print('sun_cent_error:', os.path.basename(file))
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
    data_folders_list= data_folders_list[15:] 
    show_plot=False
    bake_list=[("2024-04-23", "2024-05-13"),("2024-08-01", "2024-08-09"), ("2024-08-12", "2024-08-20")]
    ########################
    
    filt_ls_thres_ls= [("NB01",1000),("NB02",1000),("NB03",1000),("NB04",1000),
                 ("NB05",1000),("NB06",25000),("NB07",25000),("NB08",3200),
                 ("BB01",1000),("BB02",1000),("BB03",18000)]
    
    with ProcessPoolExecutor() as executor:
        executor.map(process, filt_ls_thres_ls)