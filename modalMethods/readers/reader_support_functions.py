import numpy as np
import os
import re
import time, sys

__all__=["update_progress", "get_columns", "read_data", "get_indices_npts", "get_time_dirs"]


# update_progress() : Displays or updates a console progress bar
## Accepts a float between 0 and 1. Any int will be converted to a float.
## A value under 0 represents a 'halt'.
## A value at 1 or bigger represents 100%
def update_progress(progress):
    barLength = 20 # Modify this to change the length of the progress bar
    status = ""
    if isinstance(progress, int):
        progress = float(progress)
    if not isinstance(progress, float):
        progress = 0
        status = "error: progress var must be float\r\n"
    if progress < 0:
        progress = 0
        status = "Halt...\r\n"
    if progress >= 1:
        progress = 1
        status = "Done...\r\n"
    block = int(round(barLength*progress))
    text = "\rPercent: [{0}] {1}% {2}".format( "#"*block + "-"*(barLength-block), 
                                               round(progress*100, 1), status )
    sys.stdout.write(text)
    sys.stdout.flush()


def get_columns(dir1, dir2):
    '''return the column numbers of the POD directions'''

    if (dir1 == 'x' and dir2 == 'y') or (dir1 == 'y' and dir2 == 'x'):
        cols = [0, 1]
    elif (dir1 == 'y' and dir2 == 'z') or (dir1 == 'z' and dir2 == 'y'):
        cols = [1, 2]
    elif (dir1 == 'x' and dir2 == 'z') or (dir1 == 'z' and dir2 == 'x'):
        cols = [0, 2]
    else:
        raise ValueError('\n wrong set of dimensions ...')

    return cols


def read_data(filePath, cols):
    '''
    Input
    -----
        filePath: path of the file to read
        cols: array of columns to read 

    Output
    ------
        data: array of data read from the file
    '''

    data = [[] for i in range(len(cols))]
    
    with open(filePath) as f:
        for line in f:
            line = re.split(r'[(|)|\s]', line)
            try:
                for i in range(len(cols)):
                    data[i].append(float(line[1+cols[i]]))
            except:
                continue
                
    return np.array(data)


def get_indices_npts(x1, x2, x1min, x2min, x1max, x2max):
    '''
    Input
    -----
        x1, x2: coordinates of the snapshot window
        x1min, x2min: lower bound of the POD window
        x1max, x2max: upper bound of the POD window

    Output
    ------
        indices: list of indices in the snapshot window
        npts: number of points in the snapshot window
    '''

    indices = []
    npts = x1.shape[0]

    for i in range(npts):
        if ( (x1min <= x1[i]) and (x1[i] <= x1max) and
             (x2min <= x2[i]) and (x2[i] <= x2max) ):
            indices.append(i)

    indices = np.array(indices)
    nPts = indices.size

    return indices, nPts


def get_time_dirs(filePath, nSnaps):
    '''
    Returns list of time directories in the folder
    '''

    dirs = os.listdir(filePath)
    dirs = np.sort( np.asarray(dirs) )

    nFiles = dirs.size

    timeDirs = dirs[nFiles - nSnaps:]

    return timeDirs
