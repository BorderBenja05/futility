import os
import numpy as np
import matplotlib.pyplot as plt
from astropy.io import fits
# import line_profiler

# @line_profiler.profile
def analyze_poisson_noise(data,chunk_size=30, just_return_denoise = False):
    print('analyzing noise...')
    # Get image dimensions
    img_height, img_width = shape = data.shape
    # print(f"Image dimensions: {img_height}x{img_width}")
    
    # Calculate the number of chunks
    num_chunks_height = img_height // chunk_size
    num_chunks_width = img_width // chunk_size

    means = np.zeros((num_chunks_height + 1, num_chunks_width + 1))
    medians = np.zeros((num_chunks_height + 1, num_chunks_width + 1))
    stds = np.zeros((num_chunks_height + 1, num_chunks_width + 1))
    denoised_data = np.zeros(shape)
    noise_shift = np.random.uniform(-300, 4000)
    # Iterate over the image in chunks of size chunk_size x chunk_size
    print(num_chunks_height)
    # chunkrow = 1
    for i in range(num_chunks_height + 1):
        # print(f'working on chunk row {chunkrow}')
        # chunkrow +=1
        for j in range(num_chunks_width + 1):
            
            # find the anchor corner
            start_i = i * chunk_size
            start_j = j * chunk_size

            # define the chunk
            if not i == num_chunks_height and not j == num_chunks_width:
                chunk = data[start_i:start_i + chunk_size, start_j:start_j + chunk_size]
            elif i == num_chunks_height and not j == num_chunks_width:
                chunk = data[start_i: img_height, start_j:start_j + chunk_size]
            elif j == num_chunks_width and not i == num_chunks_height:
                chunk = data[start_i: start_i + chunk_size, start_j : img_width]
            else:
                chunk = data[start_i: img_height, start_j : img_width]
            median = np.median(chunk)
            std = np.std(chunk)
            medians[i, j] = median
            stds[i, j] = std
            chunkshape = np.shape(chunk)

            denoised_data[start_i:start_i + chunkshape[0],start_j:start_j + chunkshape[1]] = chunk



            # print(chunk)

            # print(f"Processed chunk ({start_i}:{start_i + chunk_size}, {start_j}:{start_j + chunk_size}) - mean: {mean}, std: {std}")
    
    median = np.median(data)
    # print(denoised_data)
    # denoised_data += np.random.uniform(0,15,size=np.shape(denoised_data)).astype('uint16')
    # denoised_data -= np.random.uniform(0,15,size=np.shape(denoised_data)).astype('uint16')
    # denoised_data += noise_shift
    # denoised_data.clip(1,65535)
    if just_return_denoise:
        return denoised_data

    return medians, stds, median, shape



# def noise_killer(data, medians, stds):
#     for x, y in data:




def noise_maker1(file):
    # noise_shift = np.uint32(np.random.uniform(-300, 4000))
    
    # Open the FITS file and read the data
    with fits.open(file) as hdul:
        data = hdul[0].data
    
    # Copy the data to avoid modifying the original
    renoised_data = data.copy().astype('uint32')

    # Add and subtract uniform random noise
    # renoised_data += np.random.uniform(0, 15, size=renoised_data.shape).astype('uint32')
    # renoised_data -= np.random.uniform(0, 15, size=renoised_data.shape).astype('uint32')

    # Add noise shift
    # renoised_data += noise_shift
    renoised_data = renoised_data.clip( 1, 65535)
    renoised_data = renoised_data.astype('uint16')

    return renoised_data
# noise_maker1('/home/borderbenja/training_data/funpacked_fits/telescope_g_UGC_5900_2024_03_15_03_07_56.fits')
# # Example usage
# flats_file = '/home/borderbenja/training_data/funpacked_fits/telescope_g_UGC_5900_2024_03_15_03_07_56.fits'
# medians, stds, median = analyze_poisson_noise(flats_file)
# print(np.median(stds), median,median/np.median(stds))
# print(np.std(stds))

# flats_file = '/home/borderbenja/training_data/funpacked_fits/telescope_g_S240413p_5954_2024_04_14_23_26_43.fits'
# medians, stds, median = analyze_poisson_noise(flats_file, plots=True)
# print(np.median(stds), median,median/np.median(stds))
# print(np.std(stds))

# flats_file = '/home/borderbenja/training_data/funpacked_fits/telescope_g_UGC_4132_2024_04_13_00_02_24.fits'
# medians, stds, median = analyze_poisson_noise(flats_file, plots=True)
# print(np.median(stds), median,median/np.median(stds))
# print(np.std(stds))

# flats_file = '/home/borderbenja/training_data/funpacked_fits/telescope_r_ArturusA_2024_04_12_23_22_07.fits'
# medians, stds, median = analyze_poisson_noise(flats_file, plots=True)
# print(np.median(stds), median,median/np.median(stds))
# print(np.std(stds))

# flats_file = '/home/borderbenja/training_data/funpacked_fits/telescope_r_S240413p_6504_2024_04_14_22_10_16.fits'
# medians, stds, median = analyze_poisson_noise(flats_file, plots=True)
# print(np.median(stds), median,median/np.median(stds))
# print(np.std(stds))