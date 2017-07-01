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
    patchName = configDict["patchName"]
    nSnaps    = int( configDict["nSnaps"] )
    nModes    = int( configDict["nModes"] )
    nDim      = int( configDict['nDim'] ) 

    if nDim == 2:
        filePath  = filePath + '/postProcessing/cuttingPlane'
        dir1      = configDict["direction1"]
        dir2      = configDict["direction2"]

    # region of interest:
    minX, maxX = dict(), dict()
    minX['x1'] = float( configDict["x1min"] )
    minX['x2'] = float( configDict["x2min"] )

    maxX['x1'] = float( configDict["x1max"] )
    maxX['x2'] = float( configDict["x2max"] )

    if nDim == 3:
        minX['x3'] = float( configDict['x3min'] )
        maxX['x3'] = float( configDict['x3max'] )

    # non-dim parameter:
    h = float( configDict['h'] )

    if nDim == 2:
        # columns to read based on POD window:
        cols = get_columns(dir1, dir2)

        [x1, x2, indices, nPts] = read_points_from_foamFile(filePath, cols, nSnaps, 
                                                            patchName, minX, maxX, h, 
                                                            nDim)

        [u1, u2] = read_velocity_from_foamFile(filePath, patchName, cols, indices, 
                                               nSnaps, nPts, nDim)

        c1 = np.dot(u1.T, u1)
        c2 = np.dot(u2.T, u2)
        c = np.add(c1, c2)/nSnaps

        print('\n performing SVD ...')
        eigVect, singVals, _ = np.linalg.svd(c)

        phi1, phi2 = get_normal_phi(u1, u2, 0, eigVect, nSnaps, nPts)

        singVals = np.delete(singVals, np.s_[nModes::])
        phi1     = np.delete(phi1, np.s_[nModes::], 1)
        phi2     = np.delete(phi2, np.s_[nModes::], 1)

        return x1, x2, phi1, phi2, singVals, patchName, nSnaps

    elif nDim == 3:
         [x1, x2, x3, indices, nPts] = read_points_from_foamFile(filePath, cols, nSnaps, 
                                                                 patchName, minX, maxX, 
                                                                 h, nDim)

        [u1, u2, u3] = read_velocity_from_foamFile(filePath, patchName, cols, indices, 
                                                   nSnaps, nPts, nDim)

        c1 = np.dot(u1.T, u1)
        c2 = np.dot(u2.T, u2)
        c3 = np.dot(u3.T, u3)
        c = np.add(np.add(c1, c2), c3)/nSnaps

        print('\n performing SVD ...')
        eigVect, singVals, _ = np.linalg.svd(c)

        phi1, phi2, phi3 = get_normal_phi(u1, u2, u3, eigVect, nSnaps, nPts)

        singVals = np.delete(singVals, np.s_[nModes::])
        phi1     = np.delete(phi1, np.s_[nModes::], 1)
        phi2     = np.delete(phi2, np.s_[nModes::], 1)
        phi3     = np.delete(phi3, np.s_[nModes::], 1)

        return x1, x2, x3, phi1, phi2, phi3, singVals, patchName, nSnaps

    else:
        raise ValueError('Oops! Number of dimensions not defined ...')


def get_normal_phi(u1, u2, u3=0, eigVect, nSnaps, nPts):
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

    if u3 != 0:
        phi3 = np.dot(u3, eigVect)
        phiNorm = np.sum( np.square(phi1) + np.square(phi2) + np.square(phi3), axis=0)

    phiNorm = np.sqrt( phiNorm )

    if u3 == 0:
        for j in range(nSnaps):
            phi1[:, j] = np.divide(phi1[:, j], phiNorm[j])
            phi2[:, j] = np.divide(phi2[:, j], phiNorm[j])

            return phi1, phi2
            
    else:
        for j in range(nSnaps):
            phi1[:, j] = np.divide(phi1[:, j], phiNorm[j])
            phi2[:, j] = np.divide(phi2[:, j], phiNorm[j])
            phi3[:, j] = np.divide(phi3[:, j], phiNorm[j])

            return phi1, phi2, phi3

