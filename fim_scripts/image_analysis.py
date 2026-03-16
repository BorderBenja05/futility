import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
from mpl_toolkits.mplot3d import Axes3D
from fim_scripts.paths import FUTILITY_DIR, OUTSIDE_DIR
from pathlib import Path
from fim_scripts.get_sources import analyze_sources
from fim_scripts.plotting import plotter

def chunk_array(data,chunk_size=60):
    img_height, img_width = data.shape
    num_chunks_height = img_height // chunk_size
    num_chunks_width = img_width // chunk_size
    chunked_shape = (num_chunks_height + 1, num_chunks_width + 1)


    means = np.zeros(chunked_shape)
    medians = np.zeros(chunked_shape)
    stds = np.zeros(chunked_shape)
    
    # Iterate over the image in chunks of size chunk_size x chunk_size
    for i in range(num_chunks_height + 1):
        for j in range(num_chunks_width + 1):
            # Find the anchor corner
            start_i = i * chunk_size
            start_j = j * chunk_size

            # Define the chunk
            if i != num_chunks_height and j != num_chunks_width:
                chunk = data[start_i:start_i + chunk_size, start_j:start_j + chunk_size]
            elif i == num_chunks_height and j != num_chunks_width:
                chunk = data[start_i:img_height, start_j:start_j + chunk_size]
            elif j == num_chunks_width and i != num_chunks_height:
                chunk = data[start_i:start_i + chunk_size, start_j:img_width]
            else:
                chunk = data[start_i:img_height, start_j:img_width]
            
            median = np.median(chunk)
            mean = np.mean(chunk)
            std = np.std(chunk)
            medians[i, j] = median
            means[i, j] = mean
            stds[i, j] = std
    median = np.median(data)
    return median, medians, means, stds


def analyze_poisson_noise(infile, elev, azim, chunks, ortho, chunk_size=60, plots=True, output_dir='plots'):
    # Create the output directory if it doesn't exist
    if output_dir == None:
        output_dir='plots'

    if not os.path.exists(output_dir):
        os.makedirs(output_dir)


    #############################################################################################
    ## IF YOU ARE USING THIS FOR PROCESSED FITS FILES(these are generally anything over 200mb) ##
    ##     YOU MUST CHANGE THE HDUL[0] TO HDUL[3] OR IT WILL ANALYZE THE WRONG IMAGE           ##
    #############################################################################################

    # Load the FITS image


    with fits.open(infile) as hdul:
        if len(hdul) == 1:
            data = hdul[0].data
        elif len(hdul) == 6:
            data = hdul[4].data
        else:
            length = len(hdul)
            print(f'you gave me a fits file with {length} hudls?, seems like you aint from around here partner...')
            ans = input('just tell me the index of the hdul you wanna look at i guess: ')
            data = hdul[ans].data



    # Get image dimensions
    img_height, img_width = data.shape
    num_chunks_height = img_height // chunk_size
    num_chunks_width = img_width // chunk_size
    chunked_shape = (num_chunks_height + 1, num_chunks_width + 1)


        
    if chunks:    
        median, medians, means, stds = chunk_array(data,chunk_size=60)
    else:
        median = medians= means = stds= None
    

        
    
    

    # misnomer function my b, it just returns the rows of only star like sources
    x, y, fwhms, spreads, mags, elongations = analyze_sources(infile, chunksize = chunk_size, chunked_shape=chunked_shape)


    if not output_dir:
        output_dir=None
    

    plot_args = {
        'infile': infile,
        'chunks': chunks,
        'elev': elev,
        'azim': azim,
        'output_dir': output_dir,
        'chunkwidth': num_chunks_width,
        'chunkheight': num_chunks_height,
        'ortho': ortho,
    }
    data_stats = {
        'medians': medians,
        'means': means,
        'stds': stds,
        'fwhms': fwhms,
        'spreads': spreads,
        'mags': mags,
        'x': x,
        'y': y,
        'elongations': elongations,
    }
    plotter(plot_args, data_stats)
        



    
    return

