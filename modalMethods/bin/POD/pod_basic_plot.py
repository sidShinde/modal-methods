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

__all__ = ['plot_setup']

def plot_setup(caseDir, x1min, x1max, x2min, x2max, nPltPts, patchName, nSnaps, points):
    '''
    Input
    -----
        caseDir: case directory path
        x1min, x2min, x1max, x2max: coordinates of the snap-shot window
        nPltPts: # of plotting points in the smaller direction
        nSnaps: # of snap-shots to consider
        points: list of geometry coordinates
    Output
    ------
        x1, x2: coordinates of the snap-shot window
        samplePts: coordinates of the uniform mesh used of plotting
        nx1, nx2: # of points in each direction used for plotting
        phi1, phi2: POD modes
        geometry: Path defining the geometry
    '''

    print('\n importing data ...')

    fname = caseDir + '/postProcessing/POD/x1_coord_' + patchName + '_' + \
            str(nSnaps) + '.csv'
    x1 = np.loadtxt(fname, delimiter=',')

    fname = caseDir + '/postProcessing/POD/x2_coord_' + patchName + '_' + \
            str(nSnaps) + '.csv'
    x2 = np.loadtxt(fname, delimiter=',')

    fname = caseDir + '/postProcessing/POD/phi1_' + patchName + '_' + \
            str(nSnaps) + '.csv'
    phi1 = np.loadtxt(fname, delimiter=',')

    fname = caseDir + '/postProcessing/POD/phi2_' + patchName + '_' + \
            str(nSnaps) + '.csv'
    phi2 = np.loadtxt(fname, delimiter=',')

    x1Plt = np.linspace(x1min, x1max, nPltPts)
    x2Plt = np.linspace(x2min, x2max, nPltPts)

    samplePts = np.zeros((nPltPts*nPltPts, 2))
    count = 0

    for i in range(nPltPts):
        for j in range(nPltPts):
            samplePts[count, 0] = x1Plt[j]
            samplePts[count, 1] = x2Plt[i]
            count += 1

    # create the plot path:
    plotPath = [Path.MOVETO]
    for i in range( len(points)-2 ):
        plotPath.append(Path.LINETO)

    plotPath.append(Path.CLOSEPOLY)

    # geometry of the plot:
    geometry = Path(points, plotPath)

    return x1, x2, samplePts, nPltPts, phi1, phi2, geometry


def pod_basic_plot(configFile):
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

    # directions to plot for:
    direction = [dir1, dir2]

    print('\n plotting data ...')
    for i in range( len( modes ) ):
        for j in range( len( direction ) ):

            if direction[j] == dir1:
                phi = phi1
            else:
                phi = phi2

            # interpolate data on a regular mesh:
            phiTemp = griddata( (x1, x2), phi[:, modes[i]],
                               samplePts, method='linear')
            phiPlt = phiTemp.reshape(nPltPts, nPltPts)

            # generate plot:
            fig = plt.figure(figsize=(13, 6))
            ax = plt.gca()

            patch = patches.PathPatch(geometry, facecolor='black', lw=1)
            ax.add_patch(patch)

            plt.rc('text', usetex=True)
            plt.rc('font', family='serif')

            im = plt.imshow(phiPlt, extent=(x1min, x1max, x2min, x2max),
                            origin='lower', cmap='coolwarm', aspect=1)

            plt.xlim(x1min, x1max)
            plt.ylim(x2min, x2max)
            plt.xticks(list( range(int(x1min), int(x1max)+1) ), fontsize=26)
            plt.yticks(list( range(int(x2min), int(x2max)+1) ), fontsize=26)

            cbar = plt.colorbar(im, fraction=0.03, pad=0.03, aspect=8.8)
            cbar.set_label(r'$\phi_{' + direction[j] + '}^{(' + str(modes[i]) +
                           ')}$', fontsize=20)
            cbar.ax.tick_params(labelsize=18)
            cbar.formatter.set_powerlimits((0,0))
            cbar.ax.yaxis.set_offset_position('left')
            cbar.ax.yaxis.get_offset_text().set(size=20)
            cbar.update_ticks()

            plt.xlabel(r'$x/H_{\rm{ramp}}$', fontsize=24)
            plt.ylabel(r'$y/H_{\rm{ramp}}$', fontsize=24)

            pltName = caseDir + '/postProcessing/POD/' + direction[j] + \
                      '_mode_' + str( modes[i] ) + '_' + patchName + '_' + \
                      str( nSnaps ) + '.pdf'
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

    pod_basic_plot(configFile)
