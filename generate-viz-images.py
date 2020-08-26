import math
import os
import sys
import fnmatch
from typing import Union, Tuple
# Matlab modules
import h5py
from scipy.io import loadmat
import numpy as np
from PIL import Image


def main(baseFolder: str) -> None:
    pattern = 'data*.mat'
    for root, _, files in os.walk(baseFolder):
        for name in fnmatch.filter(files, pattern):
            matlabFilename = os.path.join(root, name)
            outFolderName = matlabFilename[:-4]
            if not os.path.exists(outFolderName):
                os.mkdir(outFolderName)

            outFolderName += '/'

            if shouldMakeFiles(matlabFilename, outFolderName):
                makeFiles(matlabFilename, outFolderName)
    return


def shouldMakeFiles(matlabFilename: str, outFolderName: str) -> bool:
    # TODO
    return True

def makeFiles(matlabFilename: str, outFolderName: str) -> None:
    matlabObject = openAnyMatlabFile(matlabFilename)
    imageData = getNormalizedMatlabObjectFromKey(matlabObject, 'D_stored')
    labelData = getNormalizedMatlabObjectFromKey(matlabObject, 'L_stored')
    scaleFactor = getScaleFactor(imageData.shape[:2])
    makeImageFiles(imageData, outFolderName, scaleFactor)


    return

def openAnyMatlabFile(matlabFilename: str) -> Union[dict, h5py.File]:
    try:
        outputDict = h5py.File(matlabFilename, 'r')
    except:
        outputDict = loadmat(matlabFilename)
    return outputDict

def getNormalizedMatlabObjectFromKey(matlabDict: Union[dict, h5py.File], key: str):
    if key not in matlabDict:
        return None
    if type(matlabDict) == dict:
        return matlabDict[key]
    # else it is an h5py file, which has to be transposed
    # (https://www.mathworks.com/matlabcentral/answers/308303-why-does-matlab-transpose-hdf5-data)
    return np.array(matlabDict[key]).T

def getScaleFactor(size: Tuple[int, int], maxDim = 600.0) -> int:
    larger = max(size)
    scaleFactor = math.ceil(larger / maxDim)
    return scaleFactor

def makeMetaDataFile() -> None:
    # TODO
    return

def makeImageFiles(imageStackArray: np.array, folderPath: str, scaleFactor: int = 1) -> None:
    maxPerBundle = 100
    _, _, frames = imageStackArray.shape
    numBundles = math.ceil(frames / maxPerBundle)
    for i in range(numBundles):
        start = i * maxPerBundle
        framesInBundle = min(maxPerBundle,  frames - start)
        filename = folderPath + 'F{}.jpeg'.format(i)
        getTiledImage(imageStackArray, (start, framesInBundle), filename, scaleFactor)

    return

def getTiledImage(imageStackArray: np.array, indexStartCount: Tuple[int, int], filename: str, scaleFactor: int = 1) -> None:
    h, w, totalImages = imageStackArray.shape
    first, numImages = indexStartCount
    numberOfColumns = 10
    smallW = int(w / scaleFactor)
    smallH = int(h / scaleFactor)
    newSize = (smallW, smallH)

    numRows = math.ceil(numImages / float(numberOfColumns))

    (bigWidth, bigHeight) = (numberOfColumns * smallW, numRows * smallH)    

    imageType = 'F'
    bigImageType = 'RGB'

    bigImg = Image.new(bigImageType, (bigWidth, bigHeight))

    for frameIndex in range(first, first + numImages):
        smallImg = imageStackArray[:, :, frameIndex]
        smallImg = Image.fromarray(smallImg, imageType)
        # TODO - color map smallImg
        smallImg = smallImg.resize(newSize)
        # smallImg = smallImg.convert('RGB')
        tileIndex = frameIndex - first
        x = tileIndex % numberOfColumns
        y = math.floor(tileIndex / numberOfColumns)
        top = y * smallH
        left = x * smallW
        bigImg.paste(smallImg, (left, top))

    bigImg.save(filename, 'JPEG')

    return

def makeLabelFiles() -> None:
    # TODO
    return

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Error: no input folder received. Quitting.')
        sys.exit(1)

    main(sys.argv[1])