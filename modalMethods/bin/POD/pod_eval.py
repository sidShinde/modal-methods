import numpy as np
import os
from modalMethods.readers.reader_support_functions import *
from modalMethods.readers.reader import *

__all__=["get_modes", "get_normal_phi"]

def get_modes(configFile, comm):
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

    rank = comm.Get_rank()

    # root process begins execution:
    if rank == 0:

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

        # a container for velocity vectors:
        uDict = dict()

        if nDim == 2:
            # columns to read based on POD window:
            cols = get_columns(dir1, dir2)

            [x1, x2, indices, nPts] = read_points_from_foamFile(filePath, nSnaps, 
                                                                patchName, minX, maxX, h, 
                                                                nDim, cols)
            [u1, u2] = read_velocity_from_foamFile(filePath, patchName, indices, 
                                                   nSnaps, nPts, nDim, cols)
        
            c1 = np.dot(u1.T, u1)
            c2 = np.dot(u2.T, u2)
            c = np.add(c1, c2)/nSnaps

            print('\n performing SVD ...')
            eigVect, singVals, _ = np.linalg.svd(c)

            uDict['u1'], uDict['u2'] = u1, u2
            phi1, phi2 = get_normal_phi(uDict, eigVect, nSnaps, nPts)

            singVals = np.delete(singVals, np.s_[nModes::])
            phi1     = np.delete(phi1, np.s_[nModes::], 1)
            phi2     = np.delete(phi2, np.s_[nModes::], 1)

            return x1, x2, phi1, phi2, singVals, patchName, nSnaps

        elif nDim == 3:
            [x1, x2, x3, indices, nPts] = read_points_from_foamFile(filePath, nSnaps, 
                                                                    patchName, minX, maxX, 
                                                                    h, nDim)

            [u1, u2, u3] = read_velocity_from_foamFile(filePath, patchName, indices, 
                                                       nSnaps, nPts, nDim)

            c1 = np.dot(u1.T, u1)
            c2 = np.dot(u2.T, u2)
            c3 = np.dot(u3.T, u3)
            c = np.add(np.add(c1, c2), c3)/nSnaps

            print('\n performing SVD ...')
            eigVect, singVals, _ = np.linalg.svd(c)
            
            uDict['u1'], uDict['u2'], uDict['u3'] = u1, u2, u3
            phi1, phi2, phi3 = get_normal_phi(uDict, eigVect, nSnaps, nPts)
            
            singVals = np.delete(singVals, np.s_[nModes::])
            phi1     = np.delete(phi1, np.s_[nModes::], 1)
            phi2     = np.delete(phi2, np.s_[nModes::], 1)
            phi3     = np.delete(phi3, np.s_[nModes::], 1)

            return x1, x2, x3, phi1, phi2, phi3, singVals, patchName, nSnaps

        else:
            raise ValueError('Oops! Number of dimensions not defined ...')


def get_normal_phi(uDict, eigVect, nSnaps, nPts):
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

    u1, u2 = uDict['u1'], uDict['u2']
    phi1   = np.dot(u1, eigVect)
    phi2   = np.dot(u2, eigVect)
    
    if len(uDict) == 2:
        phiNorm = np.sum( np.square(phi1) + np.square(phi2), axis=0)

    elif len(uDict) == 3:
        u3   = uDict['u3']
        phi3 = np.dot(u3, eigVect)
        phiNorm = np.sum( np.square(phi1) + np.square(phi2) + np.square(phi3), axis=0)

    phiNorm = np.sqrt( phiNorm )

    if len(uDict) == 2:
        for j in range(nSnaps):
            phi1[:, j] = np.divide(phi1[:, j], phiNorm[j])
            phi2[:, j] = np.divide(phi2[:, j], phiNorm[j])

            return phi1, phi2
            
    elif len(uDict) == 3:
        for j in range(nSnaps):
            phi1[:, j] = np.divide(phi1[:, j], phiNorm[j])
            phi2[:, j] = np.divide(phi2[:, j], phiNorm[j])
            phi3[:, j] = np.divide(phi3[:, j], phiNorm[j])

            return phi1, phi2, phi3

