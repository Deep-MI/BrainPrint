# BrainPrint-python

This is the `brainprintpython` package, an experimental derivative of the 
original BrainPrint scripts, with the following goals and changes:

## Goals

- provide a Python-only version of the BrainPrint scripts (except some 
  Freesurfer dependencies)
- remove dependencies on third-party software (shapeDNA binaries, gmsh, meshfix)
- provide a light-weight version of the original scripts that contains only the
  most frequently used submodules
- integrate the post-processing module (for computing distances etc.)
- create a fully modularized package whose functions can be called from other
  python scripts without the need of spawning subprocesses, while still
  maintaining the command-line interface of the scripts
- provide additional files (setup.py, LICENSE, README) so that it can be 
  packaged and distributed as a stand-alone Python package
- revision, and, where possible, simplification and reduction of the original 
  code base for easier maintainability
- allow for future integration of code from the `lapy` package

## Changes

- no more support for analyses of cortical parcellation or label files
- no more Python 2.x compatibility
- currently no more support for tetrahedral meshes

## Installation

Use the following code to download, build and install a package from this 
repository into your local Python package directory:

`pip3 install --user git+https://github.com/reuter-lab/BrainPrint-python.git@freesurfer-module#egg=brainprintpython`

Use the following code to install the package in editable mode to a location of
your choice:

`pip3 install --user --src /my/preferred/location --editable git+https://github.com/reuter-lab/BrainPrint-python.git@freesurfer-module#egg=brainprintpython`
