import os
import argparse
import numpy as np
import matplotlib
matplotlib.use('PDF')
from matplotlib import pyplot as plt
from modalMethods.readers.reader import *


def pod_energy_plot(configFile):
    '''
    Input
    -----
        configFile: file with input details
    Output
    ------
        saves a plot of energy v/s modes
    '''

    configDict, _, _ = config_to_dict(configFile)

    # read data from configDict:
    patchName = configDict['patchName']
    nSnaps    = int( configDict['nSnaps'] )

    caseDir = os.getcwd();
    fname = caseDir + '/postProcessing/POD/singVals_' + patchName + '_' + \
            str( nSnaps ) + '.csv'
    singVals = np.loadtxt(fname)

    totalEnergy = np.sum( singVals[1:] )
    perEnergy = singVals[1:]*(100/totalEnergy)

    modes = np.linspace(1, nSnaps-1, nSnaps-1)
    modes.astype(int)

    print('\n plotting energy ...')

    fig = plt.figure(figsize=(5,5))

    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    plt.plot(modes, perEnergy, '-ok', lw=2.0)

    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)
    plt.xlim(0, 30)
    plt.ylim(0, int(perEnergy.max() + 5))
    plt.xlabel(r'$n^{th}$ POD mode', fontsize=16)
    plt.ylabel(r'Energy ratio $(\%)$', fontsize=16)

    fname = caseDir + '/postProcessing/POD/energy_' + \
            patchName + '_' + str( nSnaps ) + '.pdf'
    plt.savefig(fname)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(
            description="Save energy v/s modes plot in postProcessing/POD.")

    parser.add_argument('-config',
                        type=str,
                        help='The config file',
                        required=True)

    args = parser.parse_args()

    # Parse the config
    configFile = open(args.config, mode='r')

    pod_energy_plot(configFile)
