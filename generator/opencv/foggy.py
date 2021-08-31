import cv2, math
import numpy as np
from numba import jit
import time

@jit(nopython=True)
def foggy(img=None,p=5,big=0.25,bit=0.5):
    img=img.copy();
    img_f = img / 255.0
    (row, col, chs) = img.shape
    img_f=np.asarray(img_f)

    A = 1  # light
    beta = bit  # density of fog
    size = math.sqrt(max(row, col))  # size of fog
    # 9 positions
    pm={1:(row//6,col//6*5),4:(row//6*3,col//6*5),7:(row//6*5,col//6*5),
        2:(row//6,col//6*3),5:(row//6*3,col//6*3),8:(row//6*5,col//6*3),
        3:(row//6,col//6),6:(row//6*3,col//6),9:(row//6*5,col//6)}
    center = pm[p] # center of fog
    for j in range(row):
        for l in range(col):
            d = -0.02 * math.sqrt((j - center[0]) ** 2 + (l - center[1]) ** 2) + size * big
            td = math.exp(-beta * d)
            img_f[j][l][:] = img_f[j][l][:] * td + A * (1 - td)
            gray1 = 0.2989 * img_f[j][l][0] * 255 + 0.5870 * img_f[j][l][1] * 255 + 0.1140 * img_f[j][l][2] * 255
            gray2 = 0.2989 * img[j][l][0] + 0.5870 * img[j][l][1] + 0.1140 * img[j][l][2]
            if gray1 >= gray2:
                img[j][l][0] = img_f[j][l][0] * 255
                img[j][l][1] = img_f[j][l][1] * 255
                img[j][l][2] = img_f[j][l][2] * 255
    return img
import os

densities={'light':0.1,'heavy':0.2,'dense':0.3,'strong':0.4,'extra':0.45} #density

directions={'D1':1,'D2':2,'D3':3,'D4':4,'D5':5,'D6':6,'D7':7,'D8':8,'D9':9} #direction

def create_dir(path):
    """
    Creates a path recursively if it doesn't exist
    :param path: The specified path
    :return: None
    """
    if path is None or path == '':
        return
    import os
    if not os.path.exists(path):
        os.makedirs(path)
    if not os.path.isdir(path):
        raise Exception("Not a valid path: {}".format(path))
# create fog images
def create_img(srcpath,dstpath,direction='D5',size=1/3,density='dense'):
    for root, dirs, files in os.walk(srcpath):
        for file in files:
            print(file)
            img=cv2.imread(srcpath+"/"+file)
            time1 = time.time()
            position=directions[direction]
            bit=densities[density]
            imgs = foggy(img, position, size, bit)
            create_dir(dstpath+"/"+direction+"/"+density)
            print(dstpath+"/"+direction+"/"+density+"/"+file)
            cv2.imwrite(dstpath+"/"+direction+"/"+density+"/"+file,imgs)
            time2 = time.time()
            print(time2 - time1)
            # break


def create_density():
    for d in densities:
        create_img(clear_input,intensity_path,density=d)

def create_direction():
    for d in directions:
        create_img(clear_input,intensity_path,direction=d)

intensity_path='/common/ahy/dataset/metdata/opencv'
clear_input="/common/ahy/dataset/udas"

if __name__ == '__main__':
    create_density()

