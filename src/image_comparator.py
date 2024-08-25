from astropy.io import fits
import numpy as np
import matplotlib.pyplot as plt
import glob, os

def fx(hdu, size):
    data= hdu.data
    col, row= int(hdu.header['CRPIX1']), int(hdu.header['CRPIX2']) 
    data_crop= data[row-size:row+size,col-size:col+size] #cropped image
    SUM= np.sum(data_crop)
    return(data_crop, SUM)
    
size=250
folder1= '/home/janmejoyarch/sftp_drive/suit_data/level1fits/2024/08/10/engg4'
folder2= '/home/janmejoyarch/sftp_drive/suit_data/level1fits/2024/08/22/engg4'

filters= ['NB01', 'NB02', 'NB03', 'NB04', 'NB05', 'NB06', 'NB07', 'NB08',
          'BB01', 'BB02', 'BB03']
i=1
sum_im1_ls, sum_im2_ls= [], []

plt.figure("Crop")
for filt in filters:
    print(filt)
    file1= glob.glob(os.path.join(folder1, f'*{filt}.fits'))[0]
    file2= glob.glob(os.path.join(folder2, f'*{filt}.fits'))[0]
    hdu1= fits.open(file1)[0]
    crop1= fx(hdu1, size)
    sum_im1_ls.append(crop1[1])
    hdu2= fits.open(file2)[0]
    crop2= fx(hdu2, size)
    sum_im2_ls.append(crop2[1])
    
    plt.subplot(3,4,i)
    plt.hist(hdu1.data.flatten(), bins=100)
    plt.hist(hdu2.data.flatten(), bins=100, alpha= 0.5)
    plt.title(filt)
    i=i+1
    
    '''
    plt.subplot(6,4,i)
    plt.imshow(crop1[0], origin='lower')
    plt.colorbar()
    plt.title(f"2024-08-10_{filt}")
    i=i+1
    plt.subplot(6,4,i)
    plt.imshow(crop2[0], origin='lower')
    plt.title(f"2024-08-22_{filt}")
    plt.colorbar()
    i=i+1
    '''
plt.show()

plt.figure("Sum Plot")
plt.plot(sum_im1_ls, 'o')
plt.plot(sum_im2_ls, 'o')
plt.xticks(ticks=np.arange(11), labels=filters)
plt.show()