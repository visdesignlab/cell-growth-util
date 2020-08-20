import os
import sys
import fnmatch
# Matlab modules
import h5py
from scipy.io import loadmat


def main(baseFolder: str) -> None:
    pattern = 'data*.mat'
    for root, _, files in os.walk(baseFolder):
        for name in fnmatch.filter(files, pattern):
            matlabFilename = os.path.join(root, name)
            outFolderName = matlabFilename[:-4]
            if not os.path.exists(outFolderName):
                os.mkdir(outFolderName)

            if shouldMakeFiles(matlabFilename, outFolderName):
                makeFiles(matlabFilename, outFolderName)
    return


def shouldMakeFiles(matlabFilename: str, outFolderName: str) -> bool:
    # TODO
    return False

def makeFiles(matlabFilename: str, outFolderName: str) -> None:
    # TODO
    return

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print('Error: no input folder received. Quitting.')
        sys.exit(1)

    main(sys.argv[1])