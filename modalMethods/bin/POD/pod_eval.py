import numpy as np
import os
from modalMethods.readers.reader_support_functions import *
from modalMethods.readers.reader import *

__all__=["get_modes", "get_normal_phi"]

def get_modes(configFile):
    '''
    Input
    -----
        configFile: path of configuration file

    Output
    ------
        phi1: POD modes in direction 1
        phi2: POD modes in direction 2
        singVals: singular values
    '''

    [configDict, modes, points] = config_to_dict(configFile)

    # read data from configDict:
    filePath  = os.getcwd()
    filePath  = filePath + '/postProcessing/cuttingPlane'
    patchName = configDict["patchName"]
    nSnaps    = int( configDict["nSnaps"] )
    dir1      = configDict["direction1"]     
    dir2      = configDict["direction2"]     
    x1min     = float( configDict["x1min"] ) 
    x1max     = float( configDict["x1max"] ) 
    x2min     = float( configDict["x2min"] ) 
    x2max     = float( configDict["x2max"] ) 
    h         = float( configDict['h'] )

    # columns to read based on POD window:
    cols = get_columns(dir1, dir2)

    [x1, x2, indices, nPts] = read_points_from_foamFile(filePath, cols, nSnaps, patchName,
                                                        x1min, x1max, x2min, x2max, h)

    [u1, u2] = read_velocity_from_foamFile(filePath, patchName, cols, indices, nSnaps, nPts)
    
    c1 = np.dot(u1.T, u1)
    c2 = np.dot(u2.T, u2)
    c = np.add(c1, c2)/nSnaps

    print('\n performing SVD ...')
    eigVect, singVals, _ = np.linalg.svd(c)

    phi1, phi2 = get_normal_phi(u1, u2, eigVect, nSnaps, nPts)

    return x1, x2, phi1, phi2, singVals, nSnaps


def get_normal_phi(u1, u2, eigVect, nSnaps, nPts):
    '''
    Input
    -----
        u1, u2: velocity snapshots in directions 1, 2
        eigVect: eigenVectors from SVD of c
        nSnaps: # of snapshots used
        nPts: # of points in each snapshot window

    Output
    ------
        phi1, phi2: normalized POD modes in direction 1, 2
    '''

    phi1 = np.dot(u1, eigVect)
    phi2 = np.dot(u2, eigVect)

    phiNorm = np.sum( np.square(phi1) + np.square(phi2), axis=0)
    phiNorm = np.sqrt( phiNorm )

    for j in range(nSnaps):
        phi1[:, j] = np.divide(phi1[:, j], phiNorm[j])
        phi2[:, j] = np.divide(phi2[:, j], phiNorm[j])

    return phi1, phi2









