
import RLE_pb2

inFolder = './in/_loonData/data7/'
outFolder = './out/'


def main():
    # Open file
    testFile = inFolder + 'L0.pb'
    f = open(testFile, 'rb')
    pbDataString = f.read()
    f.close()
    
    # parse protobuf structure
    rleLabelData = RLE_pb2.ImageLabels()
    rleLabelData.ParseFromString(pbDataString)

    # Use RLE structure
    # print(rleLabelData)
    rowIndex = 0
    for row in rleLabelData.rowList:
        print('Row:', rowIndex)
        rowIndex += 1
        for labelRun in row.row:
            print('\tL:', labelRun.label, '[{}, {}]'.format(labelRun.start, labelRun.start + labelRun.length))
        if rowIndex >= 300:
            break
    return

if __name__ == '__main__':
    main()