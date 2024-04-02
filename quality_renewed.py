#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 15:11:02 2024
Under Construction
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

def concat():
    sc_files=glob.glob('/home/janmejoyarch/sftp_drive/suitproducts/masterlimbfit/*')
    sav= '/home/janmejoyarch/temp/'
    concat_sc= open(sav+'concat_sc.txt', 'w')
    for file in sc_files:
        sc= open(file, 'r')
        lines= sc.read()+'\n'
        concat_sc.write(lines)
        sc.close()
    concat_sc.close()

def suncenter(target):
    #target= '2024-03-19T04.11.17'
    sav= '/home/janmejoyarch/temp/'
    df= pd.read_csv(sav+'concat_sc.txt', sep='\t', header=None, parse_dates=[0])
    filtered= df[df[5].between(1370, 1430)]
    dt_obj= datetime.strptime(target, '%Y-%m-%dT%H.%M.%S')
    filtered[0]= np.abs(filtered[0]-dt_obj) #filtered based on sun radius
    output= filtered[filtered[0] == filtered[0].min()]
    col, row, rad= output[1].iloc[0], output[3].iloc[0], output[5].iloc[0]
    return(col, row, rad)

def date_finder():
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
    data= fits.open(realpath)[0].data
    data_crop= data[col-size:col+size, row-size:row+size]
    mean= np.mean(data_crop)
    print(mean)
    time= datetime.strftime(realpath[-37:-18], '%Y-%m-%dT%H.%M.%S')
    if plot==True:
        plt.figure(realpath)
        plt.imshow(data, origin='lower')
        plt.plot(row, col,'o', color='red') #marks center on the sun
        plt.show()
        plt.close()
    return(mean, time)



filt='NB07'
realpath_file_folder= '/home/janmejoyarch/Dropbox/Janmejoy_SUIT_Dropbox/photometry/filelists/'
realpath_list= [realpath_file_folder+realpath_date+'-realpath.csv' for realpath_date in date_finder()]

flux_ls, time_ls=[], [] #blank lists
for realpath_file in realpath_list:
    realpath_file_txt= open(realpath_file, 'r')
    lines= realpath_file_txt.readlines()
    if (len(lines) != 0):
        realpath_ls=[line[:-1] for line in lines if line.endswith(filt+".fits\n")]
        realpath= realpath_ls[0]
        if (int(realpath[-77:-75]) == int(realpath[-29:-27])):
            row, col, rad= suncenter(realpath[-37:-18])
            #image(realpath, col, row, 100)