import os
from subprocess import call
import numpy as np
import time
from tqdm import tqdm 
from .reader_support_functions import *

__all__=["config_to_dict", "read_points_from_foamFile", "read_velocity_from_foamFile"]

def read_velocity_from_foamFile(filePath, patchName, indices, nSnaps, nPts, nDim, cols=0):
    '''
    Input
    -----
        filePath: path of the velocity files directory
        planeName: name of the sampled surface 
        cols: list of cols to read from the file
        indices: list of indices to read from the velocity file
        n_snaps: # of snapshots to use for POD
        npts: # of points in the snapshot window

    Output
    ------
        u1, u2: velocity vectors in the snapshot window
    '''
    
    timeDirs = get_time_dirs(filePath, nSnaps)

    u1 = np.zeros((nPts, nSnaps))
    u2 = np.zeros((nPts, nSnaps))
    if nDim == 3:
        u3 = np.zeros((nPts, nSnaps))

    print('\n importing velocity snapshots ...')

    # 2d problem:
    if nDim == 2:
        for i in tqdm( range(nSnaps), ncols=100 ):
            fname = filePath + '/' + str(timeDirs[i]) + '/' + patchName + '/' \
                'vectorField/U'
            data = read_data(fname, cols)
        
            temp1 = data[0]
            temp2 = data[1]
        
            u1[:, i] = temp1[indices]
            u2[:, i] = temp2[indices]
            
        return u1, u2
    # 3d problem:
    elif nDim == 3:
        for i in tqdm( range(nSnaps), ncols=100 ):
            fname = filePath + '/' + str(timeDirs[i]) + '/' + \
                    'U'
            data = get_internal_field(fname, skiprows=22)

            u1[:, i] = data[indices, 0]
            u2[:, i] = data[indices, 1]
            u3[:, i] = data[indices, 2]

        return u1, u2, u3
        
    else:
        raise ValueError('Oops! Number of dimensions not defined ...')


def read_points_from_foamFile(filePath, nSnaps, patchName,
                              minX, maxX, h, nDim, cols=0):
    '''
    Input
    -----
        filePath: path of the file to read
        cols: column numbers to read from the data files
        x1min, x2min: lower bound of the POD window
        x1max, x2max: upper bound of the POD window
        h: non-dimensionalization length

    Output
    ------
        x1, x2: array of x1, x2 coordinates in the POD window
    '''
    
    timeDirs = get_time_dirs(filePath, nSnaps)

    if nDim == 2:
        filePath = filePath + '/' + str(timeDirs[0]) + '/' \
                   + patchName + '/points'

        coordData = read_data(filePath, cols)
        coordData /= h

        indices, nPts = get_indices_npts(coordData, minX, maxX, nDim)

        x1 = coordData[indices, 0]
        x2 = coordData[indices, 1]
    
        return x1, x2, indices, nPts

    elif nDim == 3:
        cellCentres = filePath + '/' + str(timeDirs[0]) + '/' \
                      + 'cellCentres'

        if os.path.exists(cellCentres):
            coordData = get_internal_field(cellCentres, skiprows=22)

        # if cellCentres file does not exists then, run the "myWriteCellCentres"
        # command in the case directory
        else:
            fnull = open(os.devnull, 'w')
            out = call(['myWriteCellCentres', '-time', str(timeDirs[0])],
                       stdout=fnull)
            if out != 0:
                raise RuntimeError('Oops! Something went wrong with' + 
                                   ' myWriteCellCentres ...')

            coordData = get_internal_field(cellCentres, skiprows=22)
            
        indices, nPts = get_indices_npts(coordData, minX, maxX, nDim)
        
        x1 = coordData[indices, 0]
        x2 = coordData[indices, 1]
        x3 = coordData[indices, 2]
    
        return x1, x2, x3, indices, nPts
        
    else:
        raise ValueError('Oops! Number of dimensions not defined ...')

    
def config_to_dict(configFile):
    """Parse a config file to dictionary"""
    
    configDict = {}
    points = []
    for line in configFile:
        if (line[0] == '#') or (line == '\n'):
            continue

        elif (line.startswith('modes')):
            str = line.partition('(')[2]
            str = str[:-2]
            modes = [int(x) for x in str.split(',')]

        elif (line.startswith('point')):
            str = line.partition('(')[2]
            str = str[:-2]
            temp = [float(x) for x in str.split(',')]
            points.append(temp)

        else:
            configDict[line.split()[0]] = line.split()[1]

    modes = np.array(modes)

    return configDict, modes, points

