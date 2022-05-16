"""
Help text strings for the :mod:`brainprint.cli` module.
"""
CLI_DESCRIPTION: str = (
    "This program conducts a brainprint analysis of FreeSurfer output."
)


SID: str = (
    "Subject ID (FreeSurfer processed directory inside the subjects directory)"
)
SDIR: str = "FreeSurfer subjects directory"
OUTDIR: str = "Output directory (default: <sdir>/<sid>/brainprint)"
NUM: str = "Number of eigenvalues/vectors to compute (default: 50)"
EVEC: str = "Switch on eigenvector computation (default: off)"
SKIP_CORTEX: str = "Skip cortical surfaces (default: off)"
NORM: str = "Perform on eigenvalue normalization (default: none)"
RWT: str = "Switch on eigenvalue reweighting (default: off)"
ASYM: str = "Switch on additional asymmetry calculation (default: off)"
ASYM_DISTANCE: str = (
    "Distance measurement to use for asymmetry calculation (default: euc)"
)
HELP: str = "Display this help message and exit"
MORE_HELP: str = "Display extensive help message and exit"

HELPTEXT: str = """
brainprint.py
Author: Martin Reuter, 2015

=======
SUMMARY
=======

Computes the BrainPrint for a FreeSurfer subject.

The BrainPrint consists of the shape descriptors (Shape-DNA) [1]
of a selection of both cortical and subcortical structures [2].

Here is a list of structures and FreeSurfer aseg label ids:

CorpusCallosum                  [251, 252, 253, 254, 255]
Cerebellum                      [7, 8, 16, 46, 47]
Ventricles                      [4, 5, 14, 24, 31, 43, 44, 63]
3rd-Ventricle                   [14, 24]
4th-Ventricle                   15
Brain-Stem                      16
Left-Striatum                   [11, 12, 26]
Left-Lateral-Ventricle          [4, 5, 31]
Left-Cerebellum-White-Matter    7
Left-Cerebellum-Cortex          8
Left-Thalamus-Proper            10
Left-Caudate                    11
Left-Putamen                    12
Left-Pallidum                   13
Left-Hippocampus                17
Left-Amygdala                   18
Left-Accumbens-area             26
Left-VentralDC                  28
Right-Striatum                  [50, 51, 58]
Right-Lateral-Ventricle         [43, 44, 63]
Right-Cerebellum-White-Matter   46
Right-Cerebellum-Cortex         47
Right-Thalamus-Proper           49
Right-Caudate                   50
Right-Putamen                   51
Right-Pallidum                  52
Right-Hippocampus               53
Right-Amygdala                  54
Right-Accumbens-area            58
Right-VentralDC                 60

And the following cortical structures:

lh-white-2d    (left white matter surface triangles)
lh-pial-2d     (left pial surface triangles)
rh-white-2d    (same for right hemisphere ...)
rh-pial-2d

Processing of the cortical structures can be skipped (--skipcortex).

Implicit Inputs:
The mri/aseg.mgz and mri/norm.mgz should be available.
Also surf/?h.pial and surf/?h.white need to be
available unless --skipcortex is passed. norm.mgz is not
absolutely necessary but highly recommended to fix the labels
and obtain improved meshes.

Output:
The brainprint CSV table containing column headers for the
structures, a row of areas, a row of volumes and N rows of
the first N eigenvalues for each structure. An additional
output file will be created if the asymmetry calculation is
performed.

==================
COMMAND-LINE USAGE
==================

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

============
PYTHON USAGE
============

As an alternative to the command-line usage described above, individual
functions can also be called within a Python environment as follows:

import lapy
from brainprint import brainprint
brainprint.run_brainprint(subjects_dir="/my/subjects/directory", subject_id="my_subject_id")

Additional options are num=<int>, evec=<bool>, skipcortex=<bool>,
norm=<"surface"|"volume"|"geometry"|"none">, reweight=<bool>, and outdir=<string>.

=============
REQUIREMENTS
============

The script requires the lapy package, which can be installed from
https://github.com/Deep-MI/LaPy using
pip3 install --user git+https://github.com/Deep-MI/LaPy.git.

==========
REFERENCES
==========

If used for a publication, please cite both [1] for the shape
descriptor method and [2] for the application to brain MRI and
definiton of the BrainPrint.

[1] M. Reuter, F.-E. Wolter and N. Peinecke.
Laplace-Beltrami spectra as "Shape-DNA" of surfaces and solids.
Computer-Aided Design 38 (4), pp.342-366, 2006.
http://dx.doi.org/10.1016/j.cad.2005.10.011

[2] C. Wachinger, P. Golland, W. Kremen, B. Fischl, M. Reuter.
BrainPrint: A discriminative characterization of brain morphology.
NeuroImage Volume 109, pp.232-248, 2015.
http://dx.doi.org/10.1016/j.neuroimage.2015.01.032
"""

# flake8: noqa: E501
