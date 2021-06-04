# BrainPrint

This is the `brainprint` python package, a derivative of the original
[BrainPrint-legacy](https://github.com/Deep-MI/BrainPrint-legacy) scripts,
with the primary goal to provide a Python-only version (except some Freesurfer
dependencies), to integrate the [LaPy](https://github.com/Deep-MI/LaPy)
package, and to remove dependencies on third-party software
(shapeDNA-* binaries, gmsh, meshfix). As a result, some functionality of the
original BrainPrint-legacy scripts is no longer maintained (currently no
support of tetrahedral meshes and no support of cortical parcellations or
label files).

**Note that this branch is the development version that is under active development.**

## Usage

### Usage from the command line

The toolbox consists of the `brainprint.py` Python script, which can be run
from the command line as well as from within a Python environment.

The `brainprint.py` script is used for the per-subject computation of the
individual brainprint descriptor. Its usage and options are summarized below;
detailed info is available by calling the script without any arguments from the
command line.

```
python3 brainprint.py --sdir <directory> --sid <SubjectID>  [--num <num>]
                    [--evec] [--skipcortex] [--norm <surface|volume|geometry|none> ]
                    [--reweight] [--asymmetry] [--outdir <directory>] [--help]
                    [--more-help]

Options:
  --help           Show this help message and exit
  --more-help      Show extensive help message and exit

Required options:
  --sid <SubjectID>
                   Subject ID (FreeSurfer-processed directory inside the
                   subjects directory)
  --sdir <directory>
                   FreeSurfer subjects directory

Processing directives:
  --num <num>      Number of eigenvalues/vectors to compute (default: 50)
  --evec           Switch on eigenvector computation (default: off)
  --skipcortex     Skip cortical surfaces (default: off)
  --norm <surface|volume|geometry|none>
                   Switch on eigenvalue normalization; will be either surface,
                   volume, or determined by the geometry of the object. Use
                   "none" or leave out entirely to skip normalization.
  --reweight       Switch on eigenvalue reweighting (default: off)
  --asymmetry      Perform left-right asymmetry calculation (default: off)

Output parameters:
  --outdir=OUTDIR  Output directory (default: <sdir>/<sid>/brainprint)
```

### Usage as a Python package

As an alternative to their command-line usage, the BrainPrint scripts can also
be run within a pure Python environment, i.e. installed and imported as a
Python package.

Use `import brainprint` (or sth. equivalent) to import the package within
a Python environment.

Use the `run_brainprint` function from the `brainprint` module to run an
analysis:

```
import lapy
from brainprint import brainprint
brainprint.run_brainprint(sdir="/my/subjects/directory", sid="my_subject_id")
```

Additional options are `num=<int>`, `evec=<bool>`, `skipcortex=<bool>`,
`norm=<"surface"|"volume"|"geometry"|"none">`, `reweight=<bool>`, and
`outdir=<string>`.

See `help(brainprint)` and `brainprint.get_help()` for further usage info and
additional options.

## Output

The script will create an output directory that contains a csv table with
values for the area, volume, and first n eigenvalues per each FreeSurfer
structure. An additional output file will be created if the asymmetry
calculation is performed.

## Installation

**Note that this installs the development version.**

Use the following code to download, build and install a package from this
repository into your local Python package directory:

`pip3 install --user git+https://github.com/Deep-MI/BrainPrint-python.git@dev`

This will also install the necessary dependencies, e.g. the [LaPy](https://github.com/Deep-MI/LaPy)
package. You may need to add your local Python package directory to your $PATH
in order to run the scripts.

## Requirements

- The [LaPy](https://github.com/Deep-MI/LaPy) package must be installed.
- A working installation of Freesurfer 6.0 must be sourced.
- At least one structural MR image that was processed with Freesurfer 6.0.

## Changes

There are some changes in functionality in comparison to the original [BrainPrint](https://github.com/Deep-MI/BrainPrint-legacy)
scripts:

- currently no support for tetrahedral meshes
- currently no support for analyses of cortical parcellation or label files
- no more Python 2.x compatibility

## References

If you use this software for a publication please cite:

[1] BrainPrint: a discriminative characterization of brain morphology. Wachinger C, Golland P, Kremen W, Fischl B, Reuter M. Neuroimage. 2015;109:232-48. http://dx.doi.org/10.1016/j.neuroimage.2015.01.032 http://www.ncbi.nlm.nih.gov/pubmed/25613439

[2] Laplace-Beltrami spectra as 'Shape-DNA' of surfaces and solids. Reuter M, Wolter F-E, Peinecke N Computer-Aided Design. 2006;38:342-366. http://dx.doi.org/10.1016/j.cad.2005.10.011
