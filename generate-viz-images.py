import math
import os
import json
import sys
import fnmatch
from typing import Tuple, Dict

# image/data modules
import numpy as np
from PIL import Image
from PIL import ImageOps

# data structure
import RLE_pb2

# my util functions for dealing with matlab junk
import util_common
import util_tracks


def main(baseFolder: str) -> None:
    pattern = 'data*.mat'
    outName = '_LoonData'
    for root, _, files in os.walk(baseFolder):
        for name in fnmatch.filter(files, pattern):
            outFolderRoot = os.path.join(root, outName)
            if not os.path.exists(outFolderRoot):
                os.mkdir(outFolderRoot)
            if name == 'data_allframes.mat':
                handleDataAllFrames(root, outFolderRoot)
            else:
                handleImageData(root, outFolderRoot, name)

    return

def handleDataAllFrames(inFolderRoot, outFolderRoot) -> None:
    outFolder = os.path.join(outFolderRoot, '.vizMetaData')
    util_tracks.makeMassOverTimePb(inFolderRoot, outFolder)
    return

def handleImageData(inFolderRoot, outFolderRoot, name) -> None:
    outFolderSub = os.path.join(outFolderRoot, name)[:-4]
    if not os.path.exists(outFolderSub):
        os.mkdir(outFolderSub)

    outFolderSub += '/'

    matlabFilename = os.path.join(inFolderRoot, name)
    if shouldMakeFiles(matlabFilename, outFolderSub):
        makeFiles(matlabFilename, outFolderSub, outFolderRoot)
    return

def shouldMakeFiles(matlabFilename: str, outFolderName: str) -> bool:
    if matlabFilename.endswith('data_allframes.mat'):
        return False
    if FORCE_ALL:
        return True
    # Returns in seconds since epoch
    matlabTime = os.path.getmtime(matlabFilename)
    generatedTime = 0
    for root, _, files in os.walk(outFolderName):
        for name in files:
            outFilename = os.path.join(root, name)
            generatedTime = max(generatedTime, os.path.getmtime(outFilename))
    return matlabTime > generatedTime

def makeFiles(matlabFilename: str, outFolderName: str, rootFolder: str) -> None:
    print('Processing file: (' + matlabFilename + ')')
    matlabObject = util_common.openAnyMatlabFile(matlabFilename)
    imageData = util_common.getNormalizedMatlabObjectFromKey(matlabObject, 'D_stored')
    labelData = util_common.getNormalizedMatlabObjectFromKey(matlabObject, 'L_stored')
    scaleFactor = getScaleFactor(imageData.shape[:2])
    metadata = makeImageFiles(imageData, labelData, outFolderName, scaleFactor)

    metadataFolder = os.path.join(rootFolder, '.vizMetaData')
    if shouldMakeFiles(matlabFilename, metadataFolder):
        makeMetaDataFile(metadata, metadataFolder)

    if DELETE_MAT_DATA:
        deleteMatlabFile(matlabFilename)
    return

def getScaleFactor(size: Tuple[int, int], maxDim = 600.0) -> int:
    larger = max(size)
    scaleFactor = math.ceil(larger / maxDim)
    return scaleFactor

def makeMetaDataFile(data: Dict, folderName: str) -> None:
    if not os.path.exists(folderName):
        os.mkdir(folderName)
    fullPath = os.path.join(folderName, 'imageMetaData.json')
    with open(fullPath, 'w') as fileObject:
        json.dump(data, fileObject)
    return

def makeImageFiles(imageStackArray: np.array, imageLabelStackArray: np.array, folderPath: str, scaleFactor: int = 1) -> Dict:
    maxPerBundle = 100
    numberOfColumns = 10
    height, width, frames = imageStackArray.shape
    numBundles = math.ceil(frames / maxPerBundle)
    metadata = {'tileWidth': int(width / scaleFactor), 'tileHeight': int(height / scaleFactor), 'numberOfColumns': numberOfColumns, 'tilesPerFile': maxPerBundle, 'scaleFactor': scaleFactor}
    for i in range(numBundles):
        if not QUIET_MODE:
            print('\t--- Bundle {} of {} ---'.format(i+1, numBundles))
        start = i * maxPerBundle
        framesInBundle = min(maxPerBundle,  frames - start)
        filename = folderPath + 'D{}.jpg'.format(i)
        getTiledImage(imageStackArray, (start, framesInBundle), filename, numberOfColumns, scaleFactor)
        filename = folderPath + 'L{}.pb'.format(i)
        getTiledLabelImage(imageLabelStackArray, (start, framesInBundle), filename, scaleFactor)

    return metadata

def deleteMatlabFile(matlabFilename: str) -> None:
    print('🗑 ❌❌❌ DELETING FILE ❌❌❌🗑 : ({})'.format(matlabFilename))
    os.remove(matlabFilename)
    return


def getTiledImage(imageStackArray: np.array, indexStartCount: Tuple[int, int], filename: str, numberOfColumns: int, scaleFactor: int = 1) -> None:
    h, w, totalImages = imageStackArray.shape
    first, numImages = indexStartCount
    smallW = int(w / scaleFactor)
    smallH = int(h / scaleFactor)
    newSize = (smallW, smallH)

    numRows = math.ceil(numImages / float(numberOfColumns))

    (bigWidth, bigHeight) = (numberOfColumns * smallW, numRows * smallH)    

    bigImageType = 'RGB'

    bigImg = Image.new(bigImageType, (bigWidth, bigHeight))

    for frameIndex in range(first, first + numImages):
        if not QUIET_MODE:
            print('\tGenerating JPEG: ' + str(frameIndex+1), end='\r')
        smallImg = imageStackArray[:, :, frameIndex]
        if smallImg.dtype == np.int16:
            smallImg = smallImg.astype('float32')
            smallImg *= ((624*2*math.pi)/65536)
        smallImg = Image.fromarray(smallImg)        
        # TODO - color map smallImg
        smallImg = smallImg.resize(newSize)
        tileIndex = frameIndex - first
        x = tileIndex % numberOfColumns
        y = math.floor(tileIndex / numberOfColumns)
        top = y * smallH
        left = x * smallW
        bigImg.paste(smallImg, (left, top))
    if not QUIET_MODE:
        print()
    bigImg = ImageOps.autocontrast(bigImg)
    bigImg.save(filename, 'JPEG', quality=50)
    return

def getTiledLabelImage(labeledImageStackArray: np.array, indexStartCount: Tuple[int, int], filename: str, scaleFactor: int = 1) -> None:

    first, numImages = indexStartCount

    labeledImageStackArray = downSample(labeledImageStackArray, scaleFactor)
    h, w, totalImages = labeledImageStackArray.shape

    labeledImageStackArray = labeledImageStackArray.astype(np.int32)

    # Compress with run length encoding
    rows = []
    for t in range(first, first + numImages):
        if not QUIET_MODE:
            print('\tCompressing Labels: ' + str(t+1), end='\r')
        for y in range(h):
            encodedRow = []
            firstLabel = labeledImageStackArray[y, 0, t]
            currentRun = (0, 0, firstLabel)
            for x in range(w):
                start, length, lastLabel = currentRun
                thisLabel = labeledImageStackArray[y, x, t]
                if thisLabel == lastLabel:
                    currentRun = (start, length + 1, thisLabel)

                else:
                    if lastLabel != 0:
                        encodedRow.append(currentRun)
                    currentRun = (x, 1, thisLabel)

                if x == w - 1 and thisLabel != 0:
                    encodedRow.append(currentRun)

            rows.append(encodedRow)
    if not QUIET_MODE:
        print()
    # Store in protobuf object
    pbImageLabels = RLE_pb2.ImageLabels()
    for row in rows:
        pbRow = pbImageLabels.rowList.add()
        for start, length, label in row:
            pbRun = pbRow.row.add()
            pbRun.start = start
            pbRun.length = length
            pbRun.label = label        

    # Save file
    if not QUIET_MODE:
        print('\tSerializing to ProtoBuf file')
    serialString = pbImageLabels.SerializeToString()
    fileObject = open(filename, 'wb')
    fileObject.write(serialString)
    fileObject.close()

    return

def downSample(imageStackArray, factor = 3):
    return imageStackArray[::factor,::factor,:]

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Error: no input folder received. Quitting.')
        sys.exit(1)
    
    baseFolder = sys.argv[1]
    global FORCE_ALL
    FORCE_ALL = '-f' in sys.argv or '-force' in sys.argv
    global QUIET_MODE
    QUIET_MODE = '-q' in sys.argv or '-quiet' in sys.argv
    global DELETE_MAT_DATA
    DELETE_MAT_DATA = '-delete' in sys.argv

    main(baseFolder)