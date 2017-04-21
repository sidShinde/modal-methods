import os
import numpy as np
import argparse
from modalMethods.readers.reader_support_functions import *
from modalMethods.readers.reader import *
from .pod_eval import *

def main():
    '''
    Writes the POD modes in the postProcessing directory
    '''
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(
            description="Write POD modes and singular values in the postProcessing/POD. \
                         Modes are arranged in decreasing singular value order.")

    parser.add_argument('-config',
                        type=str,
                        help='The config file',
                        required=True)

    args = parser.parse_args()

    # Parse the config
    configFile = open(args.config, mode='r')


    [x1, x2, phi1, phi2, singVals, patchName, nSnaps] = get_modes(configFile)

    # make POD directory in postProcessing:
    podDir = './postProcessing/POD'
    if not os.path.exists(podDir):
        os.mkdir(podDir)

    # write the files:
    print('\n writing POD modes ...')
    fname = podDir + '/x1_coord_' + patchName + '_' + str(nSnaps) + '.csv'
    np.savetxt(fname, x1, delimiter = ',', fmt='%1.4e')

    fname = podDir + '/x2_coord_' + patchName + '_' + str(nSnaps) + '.csv'
    np.savetxt(fname, x2, delimiter = ',', fmt='%1.4e')

    fname = podDir + '/phi1_' + patchName + '_' + str(nSnaps) + '.csv'
    np.savetxt(fname, phi1, delimiter = ',', fmt='%1.4e')

    fname = podDir + '/phi2_' + patchName + '_' + str(nSnaps) + '.csv'
    np.savetxt(fname, phi2, delimiter = ',', fmt='%1.4e')

    fname = podDir + '/singVals_' + patchName + '_' + str(nSnaps) + '.csv'
    np.savetxt(fname, singVals, delimiter = ',', fmt='%1.4e')

if __name__ == "__main__":
    main()
