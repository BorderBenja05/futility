try:
    import sewpy
except ImportError:
    sewpy = None
from astropy.io import ascii
from astropy.table import QTable, Table
import numpy as np
import sys
import os
from pathlib import Path

def get_catalog(fits_file):
    if sewpy is None:
        raise ImportError("sewpy is required for rotation_finder but is not installed")
    params=["NUMBER", "X_IMAGE", "Y_IMAGE", "MAG_AUTO"] # the params we want sewpy to include in its catalog
    sew = sewpy.SEW(params=params,     # make a function to find all the stars and catalog them
        config={"DETECT_MINAREA": 5, 
                "THRESH_TYPE": "RELATIVE", 
                "DETECT_THRESH": 40,
                "FILTER": "Y"})
                
    out = sew(fits_file)
    table = QTable(out['table']) 
    
    
    return table



def pixel_separation(table):
    table.sort("MAG_AUTO") # sort by auto magnitude

    star1 = table[0]
    star2 = table[1]
    star1= [star1[1].value, star1[2].value]
    star2= [star2[1].value, star2[2].value]

    diffx = star2[0]-star1[0]
    diffy = star2[1]- star1[1]
    diff = np.hypot(diffx,diffy)

    return diff, [diffx, diffy]


def get_pixelscale(inpath, source1, source2):
    source1dec_rads =(source1[1][0] + (source1[1][1]/60))*(np.pi/180)
    # print(np.rad2deg(source1dec_rads))


    
    source1_coord_for_dif=[0,0]
    source1_coord_for_dif[0] = float((source1[0][1]*15*60) + (source1[0][2]*15))
    source1_coord_for_dif[1] =float((source1[1][1]*60) + (source1[1][2]))
    # print("source1",source1_coord_for_dif)


    source2_coord_for_dif=[0,0]
    source2_coord_for_dif[0] = float((source2[0][1]*15*60) + (source2[0][2]*15))
    source2_coord_for_dif[1] =float((source2[1][1]*60) + (source2[1][2]))
    # print("source2",source2_coord_for_dif)


    # print(source1_coord_for_dif, source2_coord_for_dif)
    diffx_physical=(source2_coord_for_dif[0] - source1_coord_for_dif[0])*np.cos(source1dec_rads)
    diffy_physical=(source2_coord_for_dif[1]- source1_coord_for_dif[1])

    diff_physical = np.hypot(diffx_physical,diffy_physical)


    
    table = get_catalog(inpath)
    # print(f'found: {len(table)} sources')
    pic_diff, Vector_pic_diff = pixel_separation(table)

    
    pix_scale = diff_physical/pic_diff 



    return pix_scale
# def get_cam_angles(inpath, source1, source2, scale, pos):


def get_cam_angle(inpath,source1, source2, scale=False, pos=False):
    # if os.path.isdir('inpath'):
    #     paths = 

    source1dec_rads =(source1[1][0] + (source1[1][1]/60))*(np.pi/180)
    # print(np.rad2deg(source1dec_rads))




    
    source1_coord_for_dif=[0,0]
    source1_coord_for_dif[0] = float((source1[0][1]*15*60) + (source1[0][2]*15))
    source1_coord_for_dif[1] =float((source1[1][1]*60) + (source1[1][2]))
    # print("source1",source1_coord_for_dif)


    source2_coord_for_dif=[0,0]
    source2_coord_for_dif[0] = float((source2[0][1]*15*60) + (source2[0][2]*15))
    source2_coord_for_dif[1] =float((source2[1][1]*60) + (source2[1][2]))
    # print("source2",source2_coord_for_dif)


    # print(source1_coord_for_dif, source2_coord_for_dif)
    diffx_physical=(source2_coord_for_dif[0] - source1_coord_for_dif[0])*np.cos(source1dec_rads)
    diffy_physical=(source2_coord_for_dif[1]- source1_coord_for_dif[1])

    modifier = 0
    if diffx_physical<0:
        modifier= 180

    real_angle = -1*(np.rad2deg(np.arctan(diffy_physical/diffx_physical))  + modifier)
    # print('physical vector difference:',diffx_physical, diffy_physical)
    diff_physical = np.hypot(diffx_physical,diffy_physical)
    # print('angular separation',diff_physical)
    # print("real angle between sources:",real_angle)

    
    table = get_catalog(inpath)
    # print(f'found: {len(table)} sources')
    pic_diff, Vector_pic_diff = pixel_separation(table)
    pic_angle = np.rad2deg(np.arctan2(Vector_pic_diff[1], Vector_pic_diff[0]))
    
    pix_scale = diff_physical/pic_diff 
    
    # print(pic_angle)


    cam_angle =  real_angle - pic_angle# + np.pi


    if cam_angle > 180:
        cam_angle = cam_angle-360
    elif cam_angle < -180:
        cam_angle = cam_angle+360

    if scale and not pos:
        return cam_angle, pix_scale
    elif pos and scale:
        return cam_angle, pix_scale, table
    return cam_angle



# if len(sys.argv) ==2:
#     inpath = sys.argv[1]



if __name__ == "__main__":
    source1 = [[19, 30, 43.288], [27, 57, 34.73]]
    source2 = [[19, 30, 45.3962],[27, 57, 54.989]]



    inpath = "/home/borderbenja/futility/Alberion_20_minute/alberion_3sec_1_1_8_of_20.fits"
    # pixscale = get_pixelscale(inpath, source1, source2)
    # print(pixscale)

    cam_angle =get_cam_angle(inpath, source1, source2)
    print(cam_angle)
    
