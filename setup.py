from setuptools import setup
from setuptools import find_packages

setup(name='modalMethods',
      description='Package to perform POD, DMD and Koopman analysis',
      author='Siddhesh Shinde',
      packages=find_packages(),
      entry_points = {
          'console_scripts':[
              'writePODmodes=modalMethods.bin.POD.write_pod_modes:main', 
              'plotPODmodes=modalMethods.bin.POD.plot_pod_modes:main',
              'plotPODenergy=modalMethods.bin.POD.plot_pod_energy:main'
              ]
          },
      install_requires=[
          'numpy',
          'scipy',
          'matplotlib',
          ],
      zip_safe=False)

