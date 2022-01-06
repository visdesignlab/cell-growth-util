from io import BytesIO
import os, io, math, random
from functools import wraps
from typing import Dict, Tuple, List, Union, Set
import array
import uuid
from datetime import datetime

# working with matlab (.mat) files, especially images
import h5py
from scipy.io import loadmat
from PIL import Image
from PIL import ImageFilter
from PIL import ImageChops
import numpy as np

# for doing preprocessing on tracks array
import pandas as pd;

# for generating pb files
import pbCurveList_pb2

# for saving metadata
import json

# my util functions for dealing with matlab junk
import util_common as util

def makeMassOverTimePb(inFolder: str, outFolder: str, quietMode: bool) -> None:
    util.msg_header('Processing file: (' + inFolder + '/data_allframes.mat' + ')')
    matlabFilename = os.path.join(inFolder, 'data_allframes.mat')
    data_allframes = util.openAnyMatlabFile(matlabFilename)
    # generate data
    colHeaders = getColTracksHeader(data_allframes)
    if colHeaders is None:
        util.warn('"tracksColHeaders" not found, using default column headers:', quietMode)
        util.msg('\tX,Y,Mass (pg),Time (h),id,Mean Value,Shape Factor,Location ID,Frame ID,xShift,yShift,segmentLabel', quietMode)
        colHeaderList = ['X', 'Y', 'Mass (pg)', 'Time (h)', 'id', 'Mean Value', 'Shape Factor', 'Location ID', 'Frame ID', 'xShift', 'yShift', 'segmentLabel']
        areaIndex = -1
        massIndex = 2
        timeIndex = 3
        idIndex = 4
    else:
        colHeaders = colHeaders[0]
        if type(colHeaders[0]) is h5py.h5r.Reference:
            # strings are stored as h5 references
            # You have to dereference to get the value, which is then a list of char ints..
            charLists = [data_allframes[ref] for ref in colHeaders]
            colHeaders = [''.join([chr(c[0]) for c in charList[:]]) for charList in charLists]
        else:
            # nd array of srtrings, just get the only string in the nested arrays
            colHeaders = [x[0] for x in colHeaders]

        try:
            areaIndex = colHeaders.index('Area')
        except:
            areaIndex = -1
        massIndex = colHeaders.index('Mass (pg)')
        timeIndex = colHeaders.index('Time (h)')
        idIndex = colHeaders.index('id')
        colHeaderList = [x for x in colHeaders]

    massOverTime = getMassOverTimeArray(data_allframes)

    if massOverTime is None:
        util.err('Cannot find "tracks" array. Skipping file.')
        return

    locIncluded =  colHeaders is not None and 'Location ID' in colHeaders
    frameIncluded = colHeaders is not None and 'Frame ID' in colHeaders
    xShiftIncluded = colHeaders is not None and 'xShift' in colHeaders
    yShiftIncluded = colHeaders is not None and 'yShift' in colHeaders
    segLabelIncluded = colHeaders is not None and 'segmentLabel' in colHeaders
    meanIntensityIncluded = colHeaders is not None and 'Mean Intensity' in colHeaders
    allIncluded = locIncluded and frameIncluded and xShiftIncluded and yShiftIncluded and segLabelIncluded

    if not meanIntensityIncluded and areaIndex >= 0:
        pixelSize = getPixelSize(data_allframes)[0][0]
        if colHeaders is not None:
            util.info('Will add "Mean Intensity" to tracks array.', quietMode)
            colHeaderList.append('Mean Intensity')
    if not locIncluded:
        locationArray = getLocationArray(data_allframes)
        if colHeaders is not None:
            util.info('Will add "Location ID" to tracks array.', quietMode)
            colHeaderList.append('Location ID')
    if not frameIncluded:
        frameArray = getFrameArray(data_allframes)
        if colHeaders is not None:
            util.info('Will add "Frame ID" to tracks array.', quietMode)
            colHeaderList.append('Frame ID')
    if not xShiftIncluded:
        xShiftArray = getXShiftArray(data_allframes)
        if colHeaders is not None:
            util.info('Will add "xShift" to tracks array.', quietMode)
            colHeaderList.append('xShift')
    if not yShiftIncluded:
        yShiftArray = getYShiftArray(data_allframes)
        if colHeaders is not None:
            util.info('Will add "yShift" to tracks array.', quietMode)
            colHeaderList.append('yShift')
    if not segLabelIncluded and colHeaders is not None:
        util.info('Will add "segmentLabel" to tracks array.', quietMode)
        colHeaderList.append('segmentLabel')
    
    if not allIncluded:
        timeArray = getTimeIndexArray(data_allframes)
        if timeArray is None:
            util.err('Cannot find "t_stored" array. Skipping file.')
            return

    if not allIncluded:
        util.msg('Adding extra necessary columns...', quietMode)
        timeToIndex = {}
        uniqueLocationList = set()
        for index, time in enumerate(timeArray):
            # weird [0] indexing here is a result of weird
            # array structure that has nested arrays at 
            # surprising places
            time = time[0]
            if not locIncluded:
                locId = locationArray[0][index]
                uniqueLocationList.add(locId)
            else:
                locId = None
            if not frameIncluded:
                frameId = frameArray[index, 0]
            else:
                frameId = None

            if not xShiftIncluded:
                xShift = xShiftArray[index][0]
            else:
                xShift = None

            if not yShiftIncluded:
                yShift = yShiftArray[index][0]
            else:
                yShift = yShift = None
            timeToIndex[time] = (locId, frameId, xShift, yShift)

    if not segLabelIncluded:
        # to handle this buildLabelLookup from loon app.py server code
        # must be refactored to calculate the labels
        util.err('"segmentLabel" is not in original data. Skipping file.')
        return

    dataRowList = []
    step = max(1, round(len(massOverTime) * util.LOADING_BAR_CONSTANT))
    for index, row in enumerate(massOverTime):
        if index % step == 0 or index == len(massOverTime) -1:
            loadingBar = util.loadingBar(index + 1, len(massOverTime))
            util.msg('{} rows.'.format(loadingBar), quietMode, True)
        dataRow = [x for x in row] # convert to vanilla python array
        if not allIncluded:
            if not meanIntensityIncluded and areaIndex >= 0:
                miConstant = 5555 + (5/9) # Cite: Eddie's email.
                # 1000 * 1/(10000)**3/100/0.0018*1e12
                mass = dataRow[massIndex]
                area = dataRow[areaIndex]
                meanIntensity = mass / (area * (pixelSize**2) * miConstant)
                dataRow.append(meanIntensity)
            time = dataRow[timeIndex]
            if not (locIncluded and frameIncluded and xShiftIncluded and yShiftIncluded):
                locationId, frameId, xShift, yShift = timeToIndex[time]
            # this corrects the xShift/yShift problem.
            # row[0] += xShift
            # row[1] += yShift
            if not locIncluded:
                dataRow.append(locationId)
            if not frameIncluded:
                dataRow.append(frameId)
            if not xShiftIncluded:
                dataRow.append(xShift)
            if not yShiftIncluded:
                dataRow.append(yShift)
            if not segLabelIncluded:
                cellId = row[idIndex]
                label = labelLookup.get(cellId, {}).get(frameId, -1)
                dataRow.append(label)
        dataRowList.append(dataRow)
    
    util.msg_header('', quietMode)

    util.msg('Building location maps...', quietMode)
    locationMaps = buildLocationMaps(colHeaderList, dataRowList)

    curveNames = {'Location ID', 'xShift', 'yShift'}
    for key in colHeaderList:
        if key.startswith('condition_'):
            curveNames.add(key)

    curveAttrNames = [x for x in colHeaderList if x in curveNames]
    curveNames.add('id')
    pointAttrNames = [x for x in colHeaderList if x not in curveNames]
    pbCurveList = pbCurveList_pb2.PbCurveList()
    pbCurveList.pointAttrNames.extend(pointAttrNames)
    pbCurveList.curveAttrNames.extend(curveAttrNames)

    util.msg('Building "CurveList" data structure...', quietMode)
    tKey = colHeaderList[timeIndex]
    idKey = colHeaderList[idIndex]
    df = pd.DataFrame(data=dataRowList, columns=colHeaderList)
    curveList = df.groupby(idKey)
    numberOfTracks = curveList.ngroups

    step = max(1, round(numberOfTracks * util.LOADING_BAR_CONSTANT))
    for curveId, curve in curveList:
        if curveId % step == 0 or curveId == numberOfTracks - 1:
            top = int(curveId)
            loadingBar = util.loadingBar(top, numberOfTracks)
            util.msg('{} cells.'.format(loadingBar), quietMode, True)
        curve.sort_values(tKey)
        pbCurve = pbCurveList.curveList.add()
        pbCurve.id = int(curveId)
        for key in curveAttrNames:
            val = curve.head(1)[key]
            pbCurve.valueList.extend([val])
        for _idx, point in curve.iterrows():
            pbPoint = pbCurve.pointList.add()
            for key in pointAttrNames:
                val = point[key]
                pbPoint.valueList.extend([val])
    util.msg_header('', quietMode) # return so you can see the last Cell ID
    util.msg('Serializing ProtoBuf (peanut butter)...', quietMode)

    pbString = pbCurveList.SerializeToString()

    util.msg('Saving data to files...', quietMode) 
    saveTracksData(outFolder, pbString)
    saveExperimentMetaData(outFolder, locationMaps)
    util.msg('Done!', quietMode) 
    return


def saveTracksData(outFolder: str, pbString) -> None:
    if not os.path.exists(outFolder):
        os.mkdir(outFolder)
    outFilename = os.path.join(outFolder, 'massOverTime.pb')
    outFile = open(outFilename, 'wb')
    outFile.write(pbString)
    outFile.close()
    return

def saveExperimentMetaData(outFolder: str, locationMaps: Dict[str, Dict[str, List[List[int]]]]) -> None:
    if not os.path.exists(outFolder):
        os.mkdir(outFolder)
    metaDataDict = dict()

    metaDataDict['displayName'] = ''
    metaDataDict['author'] = ''
    metaDataDict['folder'] = ''
    metaDataDict['locationMaps'] = locationMaps
    jsonString = json.dumps(metaDataDict)
    outFilename = os.path.join(outFolder, 'experimentMetaData.json')
    outFile = open(outFilename, 'w')
    outFile.write(jsonString)
    outFile.close()
    return

def getColTracksHeader(matlabDict):
    return util.getNormalizedMatlabObjectFromKey(matlabDict, 'tracksColHeaders')

def getMassOverTimeArray(matlabDict):
    return util.getNormalizedMatlabObjectFromKey(matlabDict, 'tracks')
    
def getTimeIndexArray(matlabDict):
    return util.getNormalizedMatlabObjectFromKey(matlabDict, 't_stored')
    
def getPixelSize(matlabDict):
    return util.getNormalizedMatlabObjectFromKey(matlabDict, 'pxlsize')
    
def getLocationArray(matlabDict):
    return util.getNormalizedMatlabObjectFromKey(matlabDict, 'Loc_stored')
    
def getFrameArray(matlabDict):
    return util.getNormalizedMatlabObjectFromKey(matlabDict, 'ii_stored')
    
def getXShiftArray(matlabDict):
    return util.getNormalizedMatlabObjectFromKey(matlabDict, 'xshift_store')
  
def getYShiftArray(matlabDict):
    return util.getNormalizedMatlabObjectFromKey(matlabDict, 'yshift_store')

def buildLocationMaps(columnHeaderArray: List[str], dataRowArray: List[List[float]]) -> Dict[str, Dict[str, List[List[int]]]]:
    locationMaps = {}
    locationIndex = columnHeaderArray.index('Location ID')
    conditionIndices = []
    # Find conditions
    for index, header in enumerate(columnHeaderArray):
        if header.startswith('condition_'):
            conditionName = header.split('_')[1]
            conditionIndices.append((index, conditionName))

    # init conditions
    for colIdx, conditionName in conditionIndices:
        locationMaps[conditionName] = {}

    # populate from data
    for dataRow in dataRowArray:
        locationId = dataRow[locationIndex]
        for colIdx, conditionName in conditionIndices:
            conditionValue = str(dataRow[colIdx])
            thisMap = locationMaps[conditionName]
            if conditionValue not in thisMap:
                thisMap[conditionValue] = set()
            thisMap[conditionValue].add(locationId)

    # turn sets of locationIDs to list of locationID ranges
    for _, conditionName in conditionIndices:
        thisMap = locationMaps[conditionName]
        for conditionValue, locationSet in thisMap.items():
            locationRanges = buildRangesFromSet(locationSet)
            thisMap[conditionValue] = locationRanges

    return locationMaps

def buildRangesFromSet(numberSet: Set[int]) -> List[List[int]]:
    sortedList = list(numberSet)
    sortedList.sort()

    rangeListFlat = []
    for i, val in enumerate(sortedList):
        if i == 0:
            prevVal = -math.inf
        else:
            prevVal = sortedList[i-1]

        if i == len(sortedList) - 1:
            nextVal = math.inf
        else:
            nextVal = sortedList[i+1]

        # it is intended that val could be added twice here
        if val - prevVal > 1:
            rangeListFlat.append(val)
        if nextVal - val > 1:
            rangeListFlat.append(val)

    nestedArray = [[rangeListFlat[j], rangeListFlat[j+1]] for j in range(0, len(rangeListFlat), 2)]

    return nestedArray