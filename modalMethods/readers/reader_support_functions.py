import numpy as np
import os
import re
import time, sys

__all__=["update_progress", "get_columns", "read_data", "get_indices_npts", "get_time_dirs"]


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


def get_internal_field(fname, skiprows=0):
    nCols = get_number_of_cols(fname, skiprows)
    data = [[] for i in range(nCols)]

    count = 0                   # line counter
    pointsInternalField = 0     # number of points in the internal field

    with open(fname) as f:
        for line in f:
            count += 1

            if count == (skiprows-1):
                line = re.split(r'[\s]', line)

                # remove whitespaces from the line
                while '' in line:
                    line.remove('')

                pointsInternalField = int( line[0] )

            elif (count > skiprows) and (count <= pointsInternalField + skiprows):
                line = re.split(r'[(|)|\s]', line)

                # remove whitespaces from the line
                while '' in line:
                    line.remove('')

                try:
                    for i in range( nCols ):
                        data[i].append( float( line[i] ) )

                except:
                    continue

            elif count > pointsInternalField + skiprows:
                break

            # skip rows
            else: continue

    return np.array(data).T


def get_indices_npts(coordData, minX, maxX, nDim):
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
    npts = coordData.shape[0]

    for i in range(npts):

        if nDim == 2:
            if ( (minX['x1'] <= coordData[i, 0]) and (coordData[i, 0] <= maxX['x1']) and
                 (minX['x2'] <= coordData[i, 1]) and (coordData[i, 1] <= maxX['x2'] ):
                indices.append(i)

        elif nDim == 3:
            if ( (minX['x1'] <= coordData[i, 0]) and (coordData[i, 0] <= maxX['x1']) and
                 (minX['x2'] <= coordData[i, 1]) and (coordData[i, 1] <= maxX['x2']) and
                 (minX['x3'] <= coordData[i, 2]) and (coordData[i, 2] <= maxX['x3'] ):
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
