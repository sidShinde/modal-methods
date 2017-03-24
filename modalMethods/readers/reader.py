import os
import numpy as np
import time
from progressbar import ProgressBar, Percentage, Bar
from .reader_support_functions import *

__all__=["config_to_dict", "read_points_from_foamFile", "read_velocity_from_foamFile"]

def read_velocity_from_foamFile(filePath, patchName, cols, indices, nSnaps, nPts):
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

    print('\n importing velocity snapshots ...')

    for i in range(nSnaps):
        fname = filePath + '/' + str(timeDirs[i]) + '/' + patchName + '/' \
                'vectorField/U'
        data = read_data(fname, cols)
        
        temp1 = data[0]
        temp2 = data[1]
        
        u1[:, i] = temp1[indices]
        u2[:, i] = temp2[indices]
            
        time.sleep(0.001)
        update_progress((i+1)/nSnaps)

    return u1, u2


def read_points_from_foamFile(filePath, cols, nSnaps, patchName,
                              x1min, x1max, x2min, x2max, h):
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

    filePath = filePath + '/' + str(timeDirs[0]) + '/' \
               + patchName + '/faceCentres'

    data = read_data(filePath, cols)
    x1 = data[0]/h
    x2 = data[1]/h

    indices, nPts = get_indices_npts(x1, x2, x1min, x2min, x1max, x2max)

    x1 = x1[indices]
    x2 = x2[indices]
    
    return x1, x2, indices, nPts
    
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

