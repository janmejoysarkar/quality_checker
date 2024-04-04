#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 15:11:02 2024
-Prepared running quality plotter in a more user friendly way.
-Introduced modules as functions.
-Quality plot is yet to be introduced.
@author: janmejoyarch
"""
import glob
import numpy as np
import pandas as pd
from datetime import datetime
from astropy.time import Time
import pandas as pd
import os 
from astropy.io import fits
import matplotlib.pyplot as plt

def suncenter(target):
    '''
    Takes time as input.
    Finds closest sun center value and returns it.
    '''
    sc_files=glob.glob('/home/janmejoyarch/sftp_drive/suitproducts/masterlimbfit/*')
    df= pd.DataFrame()
    for file in sc_files:        
        data_df= pd.read_csv(file, sep='\t', header=None, parse_dates=[0])
        df= pd.concat([df, data_df], ignore_index=True)
    filtered= df[df[5].between(1370, 1430)]
    dt_obj= datetime.strptime(target, '%Y-%m-%dT%H.%M.%S')
    filtered[0]= np.abs(filtered[0]-dt_obj) #filtered based on sun radius
    output= filtered[filtered[0] == filtered[0].min()]
    col, row, rad= output[1].iloc[0], output[3].iloc[0], output[5].iloc[0]
    return(col, row, rad)

def date_finder():
    '''
    Finds common dates between images and sun center files.
    '''
    masterlimbfit='/home/janmejoyarch/sftp_drive/suitproducts/masterlimbfit/'
    #list all dates for which masterlimbfit exists. Make a set of it.
    masterlimbfit_datelist=set([file.split(".")[0] for file in sorted(os.listdir(masterlimbfit))])
        
    filelists= '/home/janmejoyarch/Dropbox/Janmejoy_SUIT_Dropbox/photometry/filelists/'
    #list all dates for which image files exist. Make a set of it.
    files_datelist=set([file.split('-realpath')[0] for file in sorted(os.listdir(filelists))])

    #Common terms from two sets are found and is converted to a list with sorted.
    #This gives the list of dates with both images and suncenter files.
    datelist=sorted(masterlimbfit_datelist & files_datelist)
    return(datelist)

def image(realpath, col, row, size, plot=None):
    '''
    Reads the fits. Plots the image and SC info.
    Finds mean of a cropped region. Returns mean val.
    '''
    data= fits.open(realpath)[0].data
    data_crop= data[col-size:col+size, row-size:row+size]
    mean= np.mean(data_crop)
    print(mean)
    #time= datetime.strftime(realpath[-37:-18], '%Y-%m-%dT%H.%M.%S')
    if plot==True:
        plt.figure(realpath)
        plt.imshow(data, origin='lower')
        plt.plot(row, col,'o', color='red') #marks center on the sun
        plt.title(realpath[-64:])
        plt.show()
        plt.close()
    return(mean)



filt='NB03'
realpath_file_folder= '/home/janmejoyarch/Dropbox/Janmejoy_SUIT_Dropbox/photometry/filelists/'
datelist= date_finder()
realpath_list= [realpath_file_folder+realpath_date+'-realpath.csv' for realpath_date in datelist]

flux_ls, time_ls=[], [] #blank lists
for realpath_file in realpath_list:
    realpath_file_txt= open(realpath_file, 'r')
    lines= realpath_file_txt.readlines()
    print("Num of lines:", len(lines))
    if (len(lines) != 0): #check if the file is empty
        realpath_ls=[line[:-1] for line in lines if line.endswith(filt+".fits\n")]
        if (len(realpath_ls) != 0): #check if list of files is empty
            print("Num of realpaths:", len(realpath_ls))
            realpath= realpath_ls[0]
            if (int(realpath[-77:-75]) == int(realpath[-29:-27])): 
                #checks if image date and folder date are the same
                col, row, rad= suncenter(realpath[-37:-18])
                print(realpath[-64:], row, col, rad)
                image(realpath, int(col), int(row), 100, plot=True)