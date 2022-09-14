import glob
import os
from concurrent.futures import ThreadPoolExecutor

import numpy as np
from PIL import Image


COUNT = 0
def imageToNPZ(configuration, type):
    print(f':: Converting {type.upper()} to NPZ files')
    def convert(path):
        global COUNT
        image = Image.open(path)
        imageArray = np.array(image)
        np.savez_compressed(f'{path[:-4]}.npz', x=imageArray)
        os.remove(path)
        COUNT+=1

    for dataType in configuration.FEATS_PATH:
        global COUNT
        COUNT = 0
        imagePaths = glob.glob(f'{configuration.FEATS_PATH[dataType]}/*.{type}')
        total = len(imagePaths)

        if total == 0:
            print(f'!! No {type.upper()} images found for {dataType}')
        else:
            with ThreadPoolExecutor(max_workers=10) as e:
                for _ in e.map(convert, imagePaths):
                    print(f'>> {dataType} : {COUNT}/{total}', end='\r')
            print()

    print(':: Finished Conversion')