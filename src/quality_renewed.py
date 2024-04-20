#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 15:11:02 2024
-Prepared running quality plotter in a more user friendly way.
-Uses CRPIX values to pick sun center position
@author: janmejoyarch
"""
import glob
import numpy as np
import pandas as pd
from datetime import datetime
import os 
from astropy.io import fits
import matplotlib.pyplot as plt

def plot(file, col, row): #for plotting full sun image with sun center
    plt.figure()
    plt.imshow(data, origin='lower')
    plt.plot(col, row, 'o', color='red')
    plt.title(file[-44:])
    plt.show()
    plt.close()


if __name__=='__main__':
    ##### USER-DEFINED #####
    filt_name='NB06'
    project_path= os.path.expanduser('~/Dropbox/Janmejoy_SUIT_Dropbox/scripts/photometry/running_quality_checker_4k_v2_project/')
    ########################
    
    data_folders_list= sorted(glob.glob(project_path+'data/raw/*/*/*/'))[13:]
    size=100
    
    date_ls=[]
    mean_ls=[]
    for folder in data_folders_list:
        file_list=glob.glob(folder+'/normal_4k/*'+filt_name+'.fits')
        for file in file_list:
            hdu= fits.open(file)[0]
            qdesc= hdu.header['QDESC']
            if (qdesc == 'Complete Image'):
                col, row= int(hdu.header['CRPIX1']), int(hdu.header['CRPIX2'])
                dt_obj= datetime.strptime(hdu.header['DHOBT_DT'].split('.')[0], '%Y-%m-%dT%H:%M:%S')
                data=hdu.data
                data_crop= data[row-size:row+size,col-size:col+size]
                mean= np.mean(data_crop)
                if (mean>1000):
                    mean_ls.append(mean)
                    date_ls.append(dt_obj)
                    plot(file, col, row)
                    break
                else:
                    print('Door Closed:', file[-64:])
            else:
                print('Partial File:', file[-64:])
    plt.figure("Quality Plot")
    plt.scatter(date_ls, mean_ls)
    plt.title('Quality plot- '+filt_name)
    plt.xticks(rotation=45)
    plt.show()
