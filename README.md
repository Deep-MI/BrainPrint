# BrainPrint-python

This is the `brainprintpython` package, a derivative of the original
[BrainPrint](https://github.com/Deep-MI/BrainPrint) scripts, with the primary
goal to provide a Python-only version of the BrainPrint scripts (except some
Freesurfer dependencies), to integrate of the `lapy` package, and to remove
dependencies on third-party software (shapeDNA binaries, gmsh, meshfix).

## Usage

### Usage from the command line

The toolbox consists of two Python scripts, `brainPrint.py` and `brainPrintPostProc.py`.
Both scripts can be run directly from the command line as well as from within
a Python environment.

The `brainPrint.py` script is used for the per-subject computation of the
individual BrainPrint descriptor. Its usage and options are summarized below;
detailed info is available by calling the script without any arguments from the
command line.

```
python3 brainPrint.py --sdir <directory> --subjects SubjectID  [--num=<int>]
                    [--evec] [--skipcortex] [--outdir <directory>] [-h]

Options:
  -h, --help         show this help message and exit

Required options:
  --sid=SID        (REQUIRED) subject ID (FS processed directory inside the
                   subjects directory)
  --sdir=SDIR      (REQUIRED) FS subjects directory

Processing directives:
  --num=NUM        Number of eigenvalues/vectors to compute (default: 50)
  --evec           Switch on eigenvector computation (default: off)
  --skipcortex     Skip cortical surfaces (default: off)

Output parameters:
  --outdir=OUTDIR  Output directory (default: <sdir>/<sid>/brainprint)
```

The `brainPrintPostProc.py` script is used for post-processing of a set of
individual BrainPrint results. Its usage and options are summarized below;
detailed info is available by calling the script without any arguments from the
command line.

```
python3 brainPrintPostProc.py --file <file> OR --list <file> [--vol=<int>] [--lin]
                    [--asy=<euc|mah|mcd>] [--covfile=<file>] [--out=<directory>]
                    [--outcov=<directory>] [-h] [--help]

Options:
  -h, --help           show this help message and exit

  Required options::
    use EITHER --file OR --list (but not both)

    --file=FILE        a csv file that was produced by the pyBrainPrint.py
                       script
    --list=LIST        a text file with a list of csv files that were produced
                       by the pyBrainPrint.py script

  Processing options::
    use --help for details

    --vol=VOL          perform default (VOL=1), surface (VOL=2), or volume
                       (VOL=3) normalization
    --lin              perform linear reweighting
    --asy=ASY          compute lateral shape asymmetries using euclidean
                       (ASY=euc), mahalanobis (ASY=mah), or robust (ASY=mcd)
                       distances
    --covfile=COVFILE  a csv file with covariance matrices (in conjunction
                       with --file and mahalanobis or robust distances)
    --out=OUT          common output directory; will be created if necessary
    --outcov=OUTCOV    covariance output directory; will be created if
                       necessary
```

### Usage as a Python package

As an alternative to their command-line usage, the BrainPrint scripts can also
be run within a pure Python environment, i.e. installed and imported as a
Python package.

Use `import brainprintpython` (or sth. equivalent) to import the package within
a Python environment.

Use the `run_brainprint` function from the `brainprint` module to run an
analysis:

```
import lapy
from brainprintpython import brainPrint
brainPrint.run_brainprint(sdir="/my/subjects/directory", sid="my_subject_id")
```

See `help(brainPrint)` and `brainPrint.get_help()` for further usage info and
additional options.

Use the `run_postproc` function from the `brainPrintPostProc` module to do the
post-processing:

```
import lapy
from brainprintpython import brainPrintPostProc
brainPrintPostProc.run_postproc(file="/my/brainprint/output") # for a single subject
brainPrintPostProc.run_postproc(list="/my/list/of/brainprint/outputs") # for multiple subjects
```

See `help(brainPrintPostProc)` and `brainPrintPostProc.get_help()` for
further usage info and additional options.

## Installation

Use the following code to download, build and install a package from this
repository into your local Python package directory:

`pip3 install --user git+https://github.com/reuter-lab/BrainPrint-python.git@freesurfer-module#egg=brainprintpython`

Use the following code to install the package in editable mode to a location of
your choice:

`pip3 install --user --src /my/preferred/location --editable git+https://github.com/reuter-lab/BrainPrint-python.git@freesurfer-module#egg=brainprintpython`

You may need to add your local Python package directory to your $PATH in order
to run the scripts.

## Requirements

- The [LaPy](https://github.com/Deep-MI/LaPy) package must be installed.

- A working installation of Freesurfer 6.0 must be sourced.

- At least one structural MR image that was processed with Freesurfer 6.0.

## Changes

There are some changes in functionality in comparison to the original [BrainPrint](https://github.com/Deep-MI/BrainPrint)
scripts:

- currently no support for tetrahedral meshes
- currently no support for analyses of cortical parcellation or label files
- no more Python 2.x compatibility

## References

If you use this software for a publication please cite:

[1] BrainPrint: a discriminative characterization of brain morphology. Wachinger C, Golland P, Kremen W, Fischl B, Reuter M. Neuroimage. 2015;109:232-48. http://dx.doi.org/10.1016/j.neuroimage.2015.01.032 http://www.ncbi.nlm.nih.gov/pubmed/25613439
