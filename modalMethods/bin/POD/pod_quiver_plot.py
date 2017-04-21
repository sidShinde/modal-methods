import numpy as np
import os
import argparse
from scipy.interpolate import griddata
import matplotlib
matplotlib.use('PDF')
from matplotlib import pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches
from modalMethods.readers.reader_support_functions import *
from modalMethods.readers.reader import *
from modalMethods.bin.POD.pod_basic_plot import *


def pod_quiver_plot(configFile):
    '''
    Input
    -----
        configFile: configuration file from "/constant/"
    Output
    ------
        saves plots generated in /postProcessing/POD/"
    '''

    [configDict, modes, points] = config_to_dict(configFile)

    # read data from configDict:
    patchName = configDict["patchName"]
    nSnaps    = int( configDict["nSnaps"] )
    dir1      = configDict["direction1"]
    dir2      = configDict["direction2"]
    x1min     = float( configDict["x1min"] )
    x1max     = float( configDict["x1max"] )
    x2min     = float( configDict["x2min"] )
    x2max     = float( configDict["x2max"] )
    nPltPts   = int( configDict["nPltPts"] )

    # import data from postProcessing/POD
    caseDir = os.getcwd()

    # getting plotting info from configFile:
    x1, x2, samplePts, nPltPts, phi1, phi2, geometry = \
    plot_setup(caseDir, x1min, x1max, x2min, x2max, nPltPts, patchName, nSnaps, points)

    x1Plt = samplePts[:, 0].reshape(nPltPts, nPltPts)
    x2Plt = samplePts[:, 1].reshape(nPltPts, nPltPts)

    print('\n plotting data ...')
    for i in range( len( modes ) ):
        # interpolate data on a regular mesh:
        phi1Temp = griddata( (x1, x2), phi1[:, modes[i]],
                           samplePts, method='linear')
        phi1Plt = phi1Temp.reshape(nPltPts, nPltPts)
        phi2Temp = griddata( (x1, x2), phi2[:, modes[i]],
                           samplePts, method='linear')
        phi2Plt = phi2Temp.reshape(nPltPts, nPltPts)

        # generate plot:
        fig = plt.figure(figsize=(12, 4))
        ax = fig.add_axes([0.08, 0.25, 0.85, 0.6])

        patch = patches.PathPatch(geometry, facecolor='black', lw=1)
        ax.add_patch(patch)

        plt.rc('text', usetex=True)
        plt.rc('font', family='serif')

        nAltPts = 18
        Q = plt.quiver(x1Plt[::nAltPts, ::nAltPts], x2Plt[::nAltPts, ::nAltPts],
        phi1Plt[::nAltPts, ::nAltPts], phi2Plt[::nAltPts, ::nAltPts],
        scale_units='width', scale=0.22)

        qk = plt.quiverkey(Q, 0.9, 0.9, 0.01, r'$0.01 \frac{m}{s}$', labelpos='E',
             coordinates='figure', fontproperties={'size': 20})

        plt.xlim(x1min, x1max)
        plt.ylim(x2min, x2max)
        plt.xticks(list( range(int(x1min), int(x1max)+1) ), fontsize=26)
        plt.yticks(list( range(int(x2min), int(x2max)+1) ), fontsize=26)

        plt.xlabel(r'$x/H_{\rm{cube}}$', fontsize=24)
        plt.ylabel(r'$y/H_{\rm{cube}}$', fontsize=24)

        pltName = caseDir + '/postProcessing/POD/quiver'  + \
                  '_mode_' + str( modes[i] ) + '_' + patchName + '_' + str( nSnaps ) + \
                  '.pdf'

        plt.savefig(pltName)
        plt.close(fig)

def main():
    # Parse the command-line arguments
    parser = argparse.ArgumentParser(
            description="Save POD mode plots in postProcessing/POD.")

    parser.add_argument('-config',
                        type=str,
                        help='The config file',
                        required=True)

    args = parser.parse_args()

    # Parse the config
    configFile = open(args.config, mode='r')

    pod_quiver_plot(configFile)
