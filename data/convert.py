import glob
import os

import numpy as np
from PIL import Image


def JPGtoNPZ(configuration):
    for dataType in configuration.FEATS_PATH:
        imagePaths = glob.glob(f'{configuration.FEATS_PATH[dataType]}/*.jpg')
        for path in imagePaths:
            imageName = os.path.basename(path)
            image = Image.open(path)
            imageArray = np.array(image)
            np.savez_compressed(f'{path[:-4]}.npz', x=imageArray)
            os.remove(path)
