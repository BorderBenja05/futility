import numpy as np
import os
from fim_scripts.paths import FUTILITY_DIR, FIM_DATA_DIR, CAT_DIR, FIM_SCRIPTS_DIR


def read_txt_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Skip the first 8 lines
        data_lines = lines[8:]
        
        # Process the remaining lines
        for line in data_lines:
            # Only process lines that are not empty or comments
            if line.strip() and (line[0].isdigit() or line[0] == ' '):
                # Split the line into elements and convert to appropriate types
                row = [float(x) if '.' in x or 'e' in x.lower() else int(x) for x in line.split()]
                data.append(row)
                
    return data

def get_indexes_above_threshold(data, threshold=0.02):
    indexes = []
    for i, row in enumerate(data):
        if row[1] > threshold:
            if row[2] >80 and row[2] < 9495:
                if row[3] > 80 and row[3] < 6307:
                    indexes.append(i)
    print(f'there are {len(indexes)} sources that pass the galaxy check')
    return indexes

def get_indexes_of_stars(data, threshold=.007, max_size = 20):
    indexes = []
    for i, row in enumerate(data):
        if row[1] < threshold and (row[4] + row[5]) < max_size: #max size is the max sum of the major and minor axis'
            if row[2] >80 and row[2] < 9495:
                if row[3] > 80 and row[3] < 6307:
                    indexes.append(i)
    print(f'there are {len(indexes)} sources that pass the star check for size and spread')
    return indexes

def get_indexes_of_all_stars(data, threshold=.012):
    indexes = []
    for i, row in enumerate(data):
        if row[1] < threshold: #max size is the max sum of the major and minor axis'
            if row[2] >80 and row[2] < 9495:
                if row[3] > 80 and row[3] < 6307:
                    indexes.append(i)
    print(f'there are {len(indexes)} sources that pass the star check for size and spread')
    return indexes

def getcenter(infile):
    fname = infile.replace('.fits', '.starfinder.cat')
    fname= os.path.basename(fname)
    if not os.path.exists(f'{CAT_DIR}/{fname}'):
        os.system(f'source-extractor {infile}     -c {FIM_DATA_DIR}/default.sex     -FILTER_NAME {FIM_DATA_DIR}/default.conv     -PARAMETERS_NAME {FIM_DATA_DIR}/starfinder.param     -CATALOG_NAME {CAT_DIR}/{fname} -PSF_NAME {FIM_DATA_DIR}/default.psf')
    print(f'using catalog {fname}')
    data = read_txt_file(f'{CAT_DIR}/{fname}')
    indexes = get_indexes_above_threshold(data)
    galdex = []
    gals = []
    try:
        for i, index in enumerate(indexes): 
            galdex.append(indexes[i])
            gals.append([data[galdex[i]][2], data[galdex[i]][3]])
    except:
        gals = None
    # print(gals)
    return gals

def getStars(infile):
    fname = infile.replace('.fits', '.starfinder.cat')
    fname= os.path.basename(fname)
    if not os.path.exists(f'{CAT_DIR}/{fname}'):
        os.system(f'source-extractor {infile}     -c {FIM_DATA_DIR}/default.sex     -FILTER_NAME {FIM_DATA_DIR}/default.conv     -PARAMETERS_NAME {FIM_DATA_DIR}/starfinder.param     -CATALOG_NAME {CAT_DIR}/{fname} -PSF_NAME {FIM_DATA_DIR}/default.psf')
    print(f'using catalog {fname}')
    data = read_txt_file(f'{CAT_DIR}/{fname}')
    indexes = get_indexes_of_stars(data)
    stardex = []
    stars = []
    try:
        for i, index in enumerate(indexes): 
            stardex.append(index)
            stars.append([data[stardex[i]][2], data[stardex[i]][3]])
    except:
        stars = None
    # print(gals)

    return stars
        
def analyze_sources(infile, chunksize = 60, chunked_shape=None):
    fname = infile.replace('.fits', '.analysis.cat')
    fname= os.path.basename(fname)

    if not os.path.exists(f'{CAT_DIR}/{fname}'):
        os.system(f'source-extractor {infile}     -c {FIM_DATA_DIR}/default.sex     -FILTER_NAME {FIM_DATA_DIR}/default.conv     -PARAMETERS_NAME {FIM_DATA_DIR}/analysis.param     -CATALOG_NAME {CAT_DIR}/{fname} -PSF_NAME {FIM_DATA_DIR}/default.psf')
    else:
        print(f'using analysis catalog {fname}')
    data = read_txt_file(f'{CAT_DIR}/{fname}')
    indexes = get_indexes_of_all_stars(data)
    new_data = []
    for index in indexes:
        new_data.append(data[index])

    x = []
    y = []
    fwhms = []
    spreads = []
    mags = []
    elongations = []
    for rownum, row in enumerate(new_data):
        x.append(int(new_data[rownum][3]))
        y.append(int(new_data[rownum][2]))
        fwhms.append(new_data[rownum][5])
        spreads.append(new_data[rownum][1])
        mags.append(new_data[rownum][4])
        elongations.append(new_data[rownum][6])


    return x, y, fwhms, spreads, mags, elongations




# # Example usage
# file_path = 'funpacked_fits/test.cat'
# getcenter(file_path, 4)
# # print(indexes)
