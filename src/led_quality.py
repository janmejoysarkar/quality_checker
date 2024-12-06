#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Fri Dec  6 03:19:04 PM IST 2024
@author: janmejoy
@hostname: machine

DESCRIPTION
"""
import glob, os
import numpy as np
from astropy.io import fits
import matplotlib.pyplot as plt
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor

def img_eval(hdu):
    s= 200
    data= hdu.data
    dt_obj= datetime.strptime(hdu.header['DHOBT_DT'].split('.')[0],
                              '%Y-%m-%dT%H:%M:%S') #date time
    h,w= np.shape(data)
    data_crop= data[h//2-s:h//2+s, w//2-s:w//2+s]
    val= np.sum(data_crop)
    return (dt_obj, val)

def finder(folders, ledid):
    led_ls=[]
    for folder in folders:
        files= sorted(glob.glob(f'{folder}/*'))
        if files:
            for file in files:
                hdu= fits.open(file)[0]
                if hdu.header['LEDONOFF']==ledid:
                    print(os.path.basename(file))
                    led_ls.append(img_eval(hdu))
                    break
    return np.array(led_ls)

def plotting(led_stats, led_typ):
    y= (led_stats[:,1]-led_stats[:,1].min())/\
    (led_stats[:,1].max()-led_stats[:,1].min())
    plt.figure()
    plt.scatter(led_stats[:,0], led_stats[:,1]/np.max(led_stats[:,1]))
    plt.ylabel("Normalized Counts")
    plt.xlabel("Date")
    plt.title(f"{led_typ} nm")
    plt.savefig(f'{project_path}/products/LED_{led_typ}.pdf', dpi=300)
    plt.show()

def process(led):
    led_typ, led_id= led
    folders= sorted(glob.glob(os.path.join(project_path,
                   f'data/raw/2024/*/*/led{led_typ}/')))
    led_stats= finder(folders, led_id)
    plotting(led_stats, led_typ)

if __name__=='__main__':
    inpt= [('255','55'), ('355','5500')]
    project_path= os.path.expanduser('~/Dropbox/Janmejoy_SUIT_Dropbox/\
photometry/photometry_scripts/running_quality_checker_4k_v2_project/')
    with ProcessPoolExecutor() as executor:
       executor.map(process, inpt)
