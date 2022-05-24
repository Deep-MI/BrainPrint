# BrainPrint

This is the `brainprint` python package, a derivative of the original
[BrainPrint-legacy](https://github.com/Deep-MI/BrainPrint-legacy) scripts,
with the primary goal to provide a Python-only version (except some FreeSurfer dependencies), to integrate the [LaPy](https://github.com/Deep-MI/LaPy) package, and to remove dependencies on third-party software (shapeDNA-* binaries, gmsh, meshfix). As a result, some functionality of the
original BrainPrint-legacy scripts is no longer maintained (currently no
support of tetrahedral meshes and no support of cortical parcellations or
label files).

## Installation

Use the following code to download, build and install a package from this
repository into your local Python package directory:

`pip3 install --user git+https://github.com/Deep-MI/BrainPrint-python.git`

This will also install the necessary dependencies, e.g. the [LaPy](https://github.com/Deep-MI/LaPy)
package. You may need to add your local Python package directory to your $PATH
in order to run the scripts.

## Usage
### Command Line Interface (CLI)

Once installed, the package provides a `brainprint` executable which can be run from the command line.

The `brainprint` CLI enables per-subject computation of the individual brainprint descriptors. Its usage and options are summarized below;
detailed info is available by calling the script without any arguments from the command line.

```sh
brainprint --sdir <directory> --sid <SubjectID>  [--num <num>] [--evec] [--skipcortex] [--norm <surface|volume|geometry|none> ] [--reweight] [--asymmetry] [--outdir <directory>] [--help] [--more-help]

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
  --keep-temp      Whether to keep the temporary files directory or not
                   by default False
```

### Python Package

`brainprint` can also be run within a pure Python environment, i.e. installed and imported as a Python package. E.g.:

```python
>>> from brainprint import Brainprint

>>> subjects_dir = "/path/to/freesurfer/subjects_dir/"
>>> subject_id = "42"

>>> bp = Brainprint(subjects_dir=subjects_dir, asymmetry=True, keep_eigenvectors=True)
>>> results = bp.run(subject_id=subject_id)
>>> results
{"eigenvalues": PosixPath("/path/to/freesurfer/subjects_dir/subject_id/brainprint/subject_id.brainprint.csv"), "eigenvectors": PosixPath("/path/to/freesurfer/subjects_dir/subject_id/brainprint/eigenvectors"), "distances": PosixPath("/path/to/freesurfer/subjects_dir/subject_id/brainprint/subject_id.brainprint.asymmetry.csv")}
```

## Output

The script will create an output directory that contains a CSV table with
values (in that order) for the area, volume, and first n eigenvalues per each
FreeSurfer structure. An additional output file will be created if the
asymmetry calculation is performed and/or for the eigenvectors (CLI `--evecs` flag or `keep_eigenvectors` on class initialization).

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
