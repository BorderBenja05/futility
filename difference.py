import sys
import numpy as np
from sklearn.neighbors import KDTree
try:
    from .paths import CAT_DIR
except ImportError:
    from paths import CAT_DIR
import os


def check_for_matches(reference, science):
    new = []
    
    reference = np.array(reference)
    science = np.array(science)
    print(f'{len(reference)} objects detected in reference image')
    print(f'{len(science)} objects detected in science image')
    science = science[:,2:4]
    reference = reference[:,2:4]
    tree = KDTree(reference, leaf_size=10)

    for row in science:
        row = [list(row)]
        # print(row)
        matches = tree.query_radius(row, r=4, count_only=True)
        if matches == 0:
            new.append(row[0])

    return new


def read_cat_file(file_path):
    data = []
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        # Process the lines, skipping comments and header
        for line in lines:
            if line.strip() and not line.startswith('#'):
                elements = line.split()
                
                # Convert elements to appropriate types
                row = [int(elements[0])]
                row.extend([float(x) for x in elements[1:]])
                
                data.append(row)
                
    return data




def find_new_row(array1, array2):
    """
    Find the new row added in array2 compared to array1.

    Args:
    - array1 (list): First array of lists.
    - array2 (list): Second array of lists.

    Returns:
    - list or None: The new row added in array2 compared to array1, or None if no new row is found.
    """
    new = []
    for row2 in array2:
        value2 = (int(np.round(row2[2])), int(np.round(row2[3])))
        found = False
        for row1 in array1:
            value1 = (int(np.round(row1[2])), int(np.round(row1[3])))
            if value1 == value2:
                found = True
                break
        if not found:
            new.append(row2)

    return new

# Example usage
# array1 = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
# array2 = [[1, 2, 3, 4], [5, 6, 7, 8], [13, 14, 15, 16],[9, 10, 11, 12]]
# new = find_new_row(array1, array2)
# print("New row:", new)








if __name__ == "__main__":
    # reference = sys.argv[1]
    # science = sys.argv[2]

    reference = '/home/borderbenja/training_data/funpacked_fits/telescope_g_UGC_5900_2024_03_15_03_07_56.fits'
    science = '/home/borderbenja/training_data/injected_fits/telescope_g_UGC_5900_2024_03_15_03_07_56.with_inserted_star0.fits'
    # print(reference[-4:])
    if reference[-4:] =='.cat':
        ref_cat = reference
    elif reference[-5:] == '.fits':
        fname = reference.replace('.fits', '.cat')
        fname= os.path.basename(fname)
        if not os.path.exists(f'{CAT_DIR}/{fname}'):
            os.system(f'sex {reference}     -c /home/borderbenja/anaconda3/envs/pipeline/share/sextractor/default.sex     -FILTER_NAME /home/borderbenja/anaconda3/envs/pipeline/share/sextractor/default.conv     -PARAMETERS_NAME /home/borderbenja/anaconda3/envs/pipeline/share/sextractor/funkytime.param     -CATALOG_NAME {CAT_DIR}/{fname} -PSF_NAME /home/borderbenja/anaconda3/envs/pipeline/share/sextractor/default.psf')
        refdata = read_cat_file(f'{CAT_DIR}/{fname}')
    if science[-4:] =='.cat':
        ref_cat = science
    elif science[-5:] == '.fits':
        fname = science.replace('.fits', '.cat')
        fname= os.path.basename(fname)
        if not os.path.exists(f'{CAT_DIR}/{fname}'):
            os.system(f'sex {science}     -c /home/borderbenja/anaconda3/envs/pipeline/share/sextractor/default.sex     -FILTER_NAME /home/borderbenja/anaconda3/envs/pipeline/share/sextractor/default.conv     -PARAMETERS_NAME /home/borderbenja/anaconda3/envs/pipeline/share/sextractor/funkytime.param     -CATALOG_NAME {CAT_DIR}/{fname} -PSF_NAME /home/borderbenja/anaconda3/envs/pipeline/share/sextractor/default.psf')
        scidata = read_cat_file(f'{CAT_DIR}/{fname}')



    new = check_for_matches(refdata, scidata)
    print(new)
    print(f'there are {len(new)} new objects')