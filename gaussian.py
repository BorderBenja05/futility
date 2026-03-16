from astropy.io import fits
import sys
import numpy as np
import time 
import numpy as np
from astropy.io import fits
import os
try:
    from .flats_noise import noise_maker1
except ImportError:
    from flats_noise import noise_maker1

def inject_star(dat, galx, galy, siga, sigb, injections):
        amp = np.random.uniform(675,5000)
        sigma = np.random.uniform(siga, sigb)
        small_array_size = 10
        gaussian_star = amp * gaussian(small_array_size, small_array_size, sigma)
        gaussian_star = gaussian_star.astype(np.uint16)

        print(f'***********gaussian array = {gaussian_star}')

        phi = np.random.uniform(0, .5* np.pi)
        randshift = np.random.randint(7, 40) * 2
        xsign=np.random.choice([1,-1])
        ysign=np.random.choice([-1,1])
        xrandshift = xsign*int(randshift * np.cos(phi))
        yrandshift = ysign*int(randshift * np.sin(phi))

        half_window = int(small_array_size / 2)

        start_x = max(0, min(dat.shape[1] - 1, galx - half_window + xrandshift))
        end_x = max(0, min(dat.shape[1] - 1, galx + half_window + xrandshift))
        start_y = max(0, min(dat.shape[0] - 1, galy - half_window + yrandshift))
        end_y = max(0, min(dat.shape[0] - 1, galy + half_window + yrandshift))

        target_shape = (end_y - start_y, end_x - start_x)
        gaussian_star = gaussian_star[:target_shape[0], :target_shape[1]]

        dat[start_y:end_y, start_x:end_x] += gaussian_star
        print(galx - half_window + xrandshift, galx + half_window + xrandshift, galy - half_window + yrandshift, galy + half_window + yrandshift)
        print(f'inserted star @ {galx + xrandshift}, {galy + yrandshift}')
        x = galx + xrandshift
        y = galy + yrandshift

        injections.append([x, y, sigma, amp])
        return dat, injections

        
def gaussian(xlength, ylength, sigma):
    """
    Create a 2D Gaussian function with radial symmetry.
    
    Parameters:
    xlength (int): The length of the grid in the x direction.
    ylength (int): The length of the grid in the y direction.
    sigma (float): The standard deviation of the Gaussian.
    
    Returns:
    numpy.ndarray: A 2D array representing the Gaussian function.
    """
    
    xshift = np.random.uniform(-1,1)
    yshift = np.random.uniform(-1,1)
    
    x = np.linspace(-xlength / 2, xlength / 2, xlength)
    y = np.linspace(-ylength / 2, ylength / 2, ylength)
    x, y = np.meshgrid(x, y)
    
    # Calculate the radius from the center
    r = np.sqrt((x+xshift)**2 + (y+yshift)**2)
    
    # Compute the Gaussian function
    gaussian = np.exp(-r**2 / (2 * sigma**2))
    
    return gaussian

# print(gaussian(10,10,.5)*1000)

def insert_gaussians(f_in,f_out, siga, sigb, gals, iter):
    print(f'********* Opening {f_in}')
    f = fits.open(f_in)
    filename = f_in.split('/')[-1]
    print(f"****** {filename}")
    fname = filename.replace('.fits', '')
    print(f'********* Working with {fname}.fits')
    
    #### get poisson info
    noise = noise_maker1(f_in)

    dat = noise
    dat = np.clip(dat, 1, 65535)
    
    # Ensure the data type is uint16
    dat = dat.astype('uint16')
    # print("THE NOISE IS$$$$$$$$$$$$$$$")
    # print(dat)
    # dat = analyze_poisson_noise(dat, just_return_denoise=True)

    # for row in range(len(medians)):
    #     row_array = []
    #     for column in range(len(row)):
    #         localnoise = np.random.normal(medians[row,column],stds[row,column],(15,15))
    #         row_array = np.concatenate((row_array,localnoise), 1)

    
    injections = []
    
    # print(f'########## dat is: {dat}')
    for galx, galy in gals:
        print(galx, galy)
        print('BENNNSA:LJA:LKJD:LJF:LJDKJFKS')
        dat, injections = inject_star(dat, galx, galy, siga, sigb, injections)

    # print(dat)
    newhdu = fits.PrimaryHDU(dat)  # This creates a new HDU based on the old
    newhdu.name='primary'  # And gives it the name 'primary'

    # This copies each key from the old HDU to the new one
    for key in f['primary'].header:
        try:
            newhdu.header[key] = f['primary'].header[key]
            # print(f"************** {key}, {f['primary'].header[key]}")
        except: 
            print('failed')

    # Create a name for the new file
    newname = os.path.join(f_out,fname)
    newname=str(newname) + (f'.injected{iter}.fits')
    # print(mean, median)
    # And write out the entire file to disk 
    # (will just do this locally, where the script is called, for now)
    # print(dat)
    # print(newname)
    newhdu.writeto(newname,overwrite=True, output_verify='ignore')

    return newname, injections

# file_path = 'funpacked_fits/telescope_g_UGC_5900_2024_03_15_03_07_56.fits'


# def make_trainer(infile):
#     tstart =time.time()
#     # gal_order = np.random.randint(0,4)
#     # print(gal_order)
#     x,y =4300, 3969
#     x = int(x); y = int(y)
#     x, y , sigma, amp, small_array_size, newname =insert_gaussian(infile,'injected_fits/', .2, 1.6, x, y, 0)
#     print(time.time()-tstart)
#     print(x,y)
# make_trainer(file_path)
