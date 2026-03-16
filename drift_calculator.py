try:
    from .rotation_finder import get_catalog, get_cam_angle
except ImportError:
    from rotation_finder import get_catalog, get_cam_angle
import os
from astropy.io import fits
import numpy as np
from datetime import datetime
from astropy.table import QTable, Table


def drift_calculator(inpath, source1, source2):
    
    files = os.listdir(inpath)
    
    # Rename .fits files to .fz
    pic_times = []
    
    for file in files:
        if file.endswith('.fits'):
            with fits.open(f'{inpath}/{file}') as hdul:
                header = hdul[0].header
                pic_times.append(header['DATE-OBS'][11:-1])
    time_objects = [datetime.strptime(time, '%H:%M:%S.%f') for time in pic_times]
    sorted_filetimes =sorted(zip(files, time_objects), key=lambda x: x[1])

    
    

    pics_info = []
    angles = []
    pix_scales = []
    xAvgs = []
    yAvgs = []
    Vxs = []
    Vys = []


    for i, filetime in enumerate(sorted_filetimes):
        angle, pix_scale, table = get_cam_angle(f'{inpath}/{filetime[0]}', source1, source2, scale=True, pos=True)
        table = QTable(table)
        table.sort('MAG_AUTO')
        star1 = table[0]
        star2 = table[1]
        xAvg = (star1[0] + star2[0])/2
        yAvg = (star1[1] + star2[1])/2
        angles.append(angle)
        pix_scales.append(pix_scale)
        xAvgs.append(xAvg)
        yAvgs.append(yAvg)


        if i>0:
            timedif = filetime[1] - sorted_filetimes[i-1][1]
            xdif = xAvg - xAvgs[i-1]
            ydif = yAvg - yAvgs[i-1]
            Vx = xdif/float(timedif.total_seconds())
            Vy = ydif/float(timedif.total_seconds())
        else:
            Vx=0
            Vy=0
        Vxs.append(Vx)
        Vys.append(Vy)

    pixscale_real = np.average(pix_scales)
    angle_real = np.average(angles)
    print(angle_real)


    for i, Vx in enumerate(Vxs):
        # print(i)
        Vxs[i] = Vx*pixscale_real
        Vys[i] = Vys[i]*pixscale_real
        # print(Vxs[i])

    return Vxs, Vys, angle_real, pixscale_real

    







    


if __name__ == "__main__":
    source1 = [[19, 30, 43.288], [27, 57, 34.73]]
    source2 = [[19, 30, 45.3962],[27, 57, 54.989]]



    inpath = "/home/borderbenja/futility/Alberion_20_minute"
    drift_calculator(inpath, source1, source2)
    # pixscale = get_pixelscale(inpath, source1, source2)
    # print(pixscale)

    # cam_angle =get_cam_angle(inpath, source1, source2)
    # print(cam_angle)
    