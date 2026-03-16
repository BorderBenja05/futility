import os
import numpy as np
import sys
import matplotlib.pyplot as plt
from astropy.io import fits
from mpl_toolkits.mplot3d import Axes3D
import argparse
import time
from fim_scripts.paths import FUTILITY_DIR, OUTSIDE_DIR
from pathlib import Path
from fim_scripts.image_analysis import analyze_poisson_noise


def get_all_directories(root_folder):
    root = Path(root_folder)
    return [str(path) for path in root.rglob('*') if path.is_dir()]
def get_all_files(root_folder):
    root = Path(root_folder)
    return [str(path) for path in root.rglob('*') if path.is_file()]

def get_files_in_directory(folder_path):
    return [os.path.join(folder_path, f) for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]


def filefinder(filename_chunk):
    files = get_all_files(FUTILITY_DIR) # + get_files_in_directory(OUTSIDE_DIR)
    # print(files[-1][-5:-1])
    matches = []
    for file in files:
        if filename_chunk in file and file[-5:-1]=='.fit':
            matches.append(file)
            if len(matches) > 10:
                print("too many matches, narrow it down")
                return 
    return matches



def filetrier(args):
    inpath = args['inpath']
    elev = int(args['elev'])
    azim = int(args['azim'])
    chunks = bool(args['chunks'])
    ortho = bool(args['ortho'])
    outpath = args['outpath']

    if not outpath:
        try:
            analyze_poisson_noise(inpath, elev, azim, chunks, ortho ,plots=True)
        except FileNotFoundError:
            inpath = Path(inpath)
            subdirs = get_all_directories(FUTILITY_DIR) + [OUTSIDE_DIR]
            for directory in subdirs:
                try:
                    analyze_poisson_noise(f'{directory}/{inpath}', elev, azim, chunks, ortho ,plots=True)
                    exit()
                except:
                    pass
            print("The file was not found under that filepath, its parent path or any recursive directories from it")
            inpath = input("please provide another filepath or chunk of filename: ")
            if len(inpath)>4:
                if inpath[-5:-1] == '.fit'  and not inpath==None:
                    analyze_poisson_noise(inpath, elev, azim, chunks, ortho, plots=True)
            if len(inpath)<5 or not inpath[-5:-1] == '.fit' :
                matches = filefinder(inpath)
                if matches == None:
                    return
                if not len(matches) == 1 and not len(matches) == 0:
                    yorn =input(f"there are {len(matches)} matches, would you like to pick one? (Y/N): ")
                    if yorn == 'y' or yorn =='yes' or yorn=='Y' or yorn=="Yes" or yorn =="YES":
                        for i, match in enumerate(matches):
                            print(f'{i}: {match}')
                        choice =input("which number match do you want to try?: ")
                        try:
                            choice=int(choice)
                            analyze_poisson_noise(matches[choice], elev, azim, chunks, ortho , plots=True)
                        except:
                            exit()
                if len(matches) == 1:
                    analyze_poisson_noise(matches[0], elev, azim, chunks, ortho , plots=True)

                
                    

        except Exception as e:
            # This will catch all other exceptions
            print(f"An error occurred: {e}")
        return None
    else:
        try:
            analyze_poisson_noise(inpath, elev, azim, chunks, ortho ,plots=True)
        except FileNotFoundError:
            subdirs = get_all_directories(FUTILITY_DIR) + [OUTSIDE_DIR]
            for directory in subdirs:
                try:
                    analyze_poisson_noise(f'{directory}/{inpath}', elev, azim, chunks, ortho ,plots=True, output_dir=outpath)
                    exit()
                except:
                    pass
            print("The file was not found under that filepath, its parent path or any recursive directories from it")
            inpath = input("please provide another filepath or chunk of filename: ")
            if len(inpath)>4:
                if inpath[-5:-1] == '.fit'  and not inpath==None:
                    analyze_poisson_noise(inpath, elev, azim, chunks, ortho ,plots=True, output_dir=outpath)
            if len(inpath)<5 or not inpath[-5:-1] == '.fit' :
                matches = filefinder(inpath)
                if matches == None:
                    print('no matches')
                    return
                if not len(matches) == 1 and not len(matches) == 0:
                    yorn =input(f"there are {len(matches)} matches, would you like to pick one? (Y/N): ")
                    if yorn == 'y' or yorn =='yes' or yorn=='Y' or yorn=="Yes" or yorn =="YES":
                        for i, match in enumerate(matches):
                            print(f'{i}: {match}')
                        choice =input("which number match do you want to try?: ")
                        try:
                            choice=int(choice)
                            analyze_poisson_noise(inpath, elev, azim, chunks, ortho ,plots=True, output_dir=outpath)
                        except:
                            exit()
                if len(matches) == 1:
                    analyze_poisson_noise(inpath, elev, azim, chunks, ortho ,plots=True, output_dir=outpath)


if __name__ == "__main__":
    elev = 40
    azim = 40
    if len(sys.argv) ==2:
        inpath = sys.argv[1]
        filetrier(inpath)

    elif len(sys.argv) == 3:
        outpath = sys.argv[2]
        inpath = sys.argv[1]
        filetrier(inpath,outpath)
    else:
        # inpath =input('please provide filepath: ')
        inpath = '/home/borderbenja/futility/funpacked_fits/telescope_g_UGC_5900_2024_03_15_03_07_56.fits'
        if not len(inpath)==0 and not inpath==None:
            filetrier(inpath)
        else:
            exit()