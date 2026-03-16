import numpy as np
import time
try:
    from .get_sources import getcenter
    from . import gaussian as ga
    from .paths import FUTILITY_DIR, FUNPACKED_FITS, INJECTED_FITS, CAT_DIR
    from .flats_noise import noise_maker1
except ImportError:
    from get_sources import getcenter
    import gaussian as ga
    from paths import FUTILITY_DIR, FUNPACKED_FITS, INJECTED_FITS, CAT_DIR
    from flats_noise import noise_maker1
import xml.etree.ElementTree as ET
from os import listdir
from os.path import isfile, join, splitext, split
fits_path = FUNPACKED_FITS
out_path = INJECTED_FITS



# put all files in need of injections in fits_path
files = [f for f in listdir(fits_path) if isfile(join(fits_path, f))]




import xml.etree.ElementTree as ET
from xml.dom import minidom

def append_to_xml(filename, data):
    # Create the root element with the filename as its tag
    root = ET.Element(filename)

    # Iterate through each inner list in the data
    for i, item in enumerate(data):
        # Create a new element for each set of x, y, sigma, amp
        entry = ET.SubElement(root, f'injection{i}')
        x, y, sigma, amp = item
        ET.SubElement(entry, 'x').text = str(x)
        ET.SubElement(entry, 'y').text = str(y)
        ET.SubElement(entry, 'sigma').text = str(sigma)
        ET.SubElement(entry, 'amp').text = str(amp)

    # Convert the ElementTree to a string
    rough_string = ET.tostring(root, 'utf-8')
    
    # Use minidom to prettify the XML
    reparsed = minidom.parseString(rough_string)
    pretty_xml_as_string = reparsed.toprettyxml(indent="    ")

    # Write the prettified XML to a file
    with open(f"starcoords.xml", "a", encoding="utf-8") as f:
        f.write(pretty_xml_as_string)

# filename = "example"
# data = [
#     [1.0, 2.0, 0.5, 100.0],
#     [2.0, 3.0, 0.6, 200.0],
#     [3.0, 4.0, 0.7, 300.0]
# ]

# append_to_xml(filename, data)



def convert_to_integers(data):

    result = []
    for sublist in data:
        converted_sublist = [int(element) for element in sublist]
        result.append(converted_sublist)
    return result

def galsplitter(centers, num_tables, max_centers):
    tables = [[] for _ in range(num_tables)]

    for i, row in enumerate(centers):
        if i < (max_centers -1):
            table_index = i % num_tables
            tables[table_index].append(row)
        else:
            break
    return tables

def make_trainer(infile,out_path):
    tstart =time.time()
    clones = np.random.randint(8,10)
    insertions_per_file = np.random.randint(30,50)


    # print(gal_num)
    centers = getcenter(infile)
    centers = convert_to_integers(centers)
    max_centers = insertions_per_file * clones
    if len(centers) < max_centers:
        for a in range(max_centers - len(centers)):
            centers.append([np.random.randint(80, 9495), np.random.randint(80, 6307)])
    gals_table = galsplitter(centers, clones, max_centers)


    for i, gals in enumerate(gals_table):
        
        outname, injections = ga.insert_gaussians(infile,out_path, .5, 1.3,gals, i)
        outname = splitext(outname)[0]
        outname = outname.split('/')[-1]
        append_to_xml(outname, injections)

# make_trainer(fits_path,out_path)
# a = [[371.0277, 683.0317], [2750.0183, 4621.0913], [5333.3682, 401.3629], [321.5137, 6080.3301], [1981.4419, 3747.2944], [3825.5391, 3066.0383], [5183.811, 1717.7922], [1115.8502, 6071.7964]]
# print(convert_to_integers(a))
tstart =time.time()
for file in files:
    print(fits_path.joinpath(file))
    make_trainer(f'{fits_path.joinpath(file)}',out_path)
print(time.time()-tstart)
