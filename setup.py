from setuptools import setup
from setuptools import find_packages

setup(name='modalMethods',
      description='Package to perform POD, DMD and Koopman analysis',
      author='Siddhesh Shinde',
      packages=find_packages(),
      entry_points = {
          'console_scripts':[
              'writePODmodes=modalMethods.bin.POD.write_pod_modes:main',
              'podBasicPlot=modalMethods.bin.POD.pod_basic_plot:main',
              'podQuiverPlot=modalMethods.bin.POD.pod_quiver_plot:main',
              'podEnergyPlot=modalMethods.bin.POD.pod_energy_plot:main'
              ]
          },
      install_requires=[
          'numpy',
          'scipy',
          'matplotlib',
          ],
      zip_safe=False)
