"""
brainprint - a script to compute ShapeDNA of FreeSurfer structures

type 'brainprint.get_help()' for info.
"""

# ==============================================================================
# FUNCTIONS

# ------------------------------------------------------------------------------
# help function

def get_help(print_help=True):
    """
    a function to retrieve a help message
    """

    HELPTEXT = """

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
    the first N eigenvalues for each structure.

    ==================
    COMMAND-LINE USAGE
    ==================

    python3 brainprint.py --sdir <directory> --subjects SubjectID  [--num=<int>]
                          [--evec] [--skipcortex] [--norm] [--reweight]
                          [--outdir <directory>] [--help] [--more-help]

    Options:
      --help           show this help message and exit

    Required options:
      --sid=SID        Subject ID (FreeSurfer-processed directory inside the
                       subjects directory)
      --sdir=SDIR      FreeSurfer subjects directory

    Processing directives:
      --num=NUM        Number of eigenvalues/vectors to compute (default: 50)
      --evec           Switch on eigenvector computation (default: off)
      --skipcortex     Skip cortical surfaces (default: off)
      --norm           Switch on eigenvalue normalization (default: off)
      --reweight       Switch on eigenvalue reweighting (default: off)

    Output parameters:
      --outdir=OUTDIR  Output directory (default: <sdir>/<sid>/brainprint)

    ============
    PYTHON USAGE
    ============

    As an alternative to the command-line usage described above, individual
    functions can also be called within a Python environment as follows:

    import lapy
    from brainprint import brainprint
    brainprint.run_brainprint(sdir="/my/subjects/directory", sid="my_subject_id")

    Additional options are num=<int>, evec=<bool>, skipcortex=<bool>,
    norm=<bool>, reweight=<bool>, and outdir=<string>.

    See `help(brainprint)` and `brainprint.get_help()` for further usage info
    and additional options.

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

    if print_help is True:
        print(HELPTEXT)
    else:
        return HELPTEXT

# ------------------------------------------------------------------------------
# parse options

# parse_options
def _parse_options():
    """
    command line options parser: initiate the option parser and return the parsed object
    """

    # imports
    import sys
    import argparse

    # setup parser
    parser = argparse.ArgumentParser(description="This program conducts a brainprint analysis of FreeSurfer output.",
        add_help=False)

    # help text
    h_sid = '(REQUIRED) subject ID (FS processed directory inside the subjects directory)'
    h_sdir = '(REQUIRED) FS subjects directory'
    h_outdir = 'Output directory (default: <sdir>/<sid>/brainprint)'
    h_num = 'Number of eigenvalues/vectors to compute (default: 50)'
    h_evec = 'Switch on eigenvector computation (default: off)'
    h_skipcortex = 'Skip cortical surfaces (default: off)'
    h_norm = 'Switch on eigenvalue normalization (default: off)'
    h_rwt = 'Switch on eigenvalue reweighting (default: off)'


    # required arguments
    required = parser.add_argument_group('Required arguments')

    required.add_argument('--sid', dest='sid', help=h_sid, default=None,
        metavar="<string>", required=False)
    required.add_argument('--sdir', dest="sdir", help=h_sdir, default=None,
        metavar="<directory>", required=False)

    # optional arguments
    optional = parser.add_argument_group('Processing directives')

    optional.add_argument('--outputdir', dest="outputdir", help="Directory where the results will be written. If not given, a subfolder within each subject's directory will be created.",
        default=None, metavar="<directory>", required=False)


    optional.add_argument('--num', dest='num', help=h_num, default=50,
        metavar="<num>", type=int, required=False)
    optional.add_argument('--evec', dest='evec', help=h_evec, default=False,
        action='store_true', required=False)
    optional.add_argument('--skipcortex', dest='skipcortex', help=h_skipcortex,
        default=False, action='store_true', required=False)
    optional.add_argument('--norm', dest='norm', help=h_norm, default=False,
        action='store_true', required=False)
    optional.add_argument('--reweight', dest='rwt', help=h_rwt, default=False,
        action='store_true', required=False)


    # output options
    output = parser.add_argument_group("Output parameters")

    output.add_argument('--outdir', dest='outdir', help=h_outdir, default=None,
        metavar="<directory>", required=False)

    # define help
    help = parser.add_argument_group('Getting help')

    help.add_argument('--help', help="Display this help message and exit",
        action='help')
    help.add_argument('--more-help', dest='more_help', help="Display extensive help message and exit",
        default=False, action="store_true", required=False)

    # --------------------------------------------------------------------------
    #

    # check if there are any inputs; if not, print help and exit
    if len(sys.argv) == 1:
        args = parser.parse_args(['--help'])
    else:
        args = parser.parse_args()

    # return extensive helptext
    if args.more_help is True:
        get_help()
        sys.exit(0)

    # check for required arguments print help and exit
    if args.sid is None:
        print("ERROR: the --sid argument is required, exiting. Use --help to see details.")
        sys.exit(1)

    if args.sdir is None:
        print("ERROR: the --sdir argument is required, exiting. Use --help to see details.")
        sys.exit(1)

    # convert options to dict
    options = dict(sdir=args.sdir, sid=args.sid, outdir=args.outdir,
        num=args.num, evec=args.evec, skipcortex=args.skipcortex,
        norm=args.norm, rwt=args.rwt)

    # return
    return options

# check_options
def _check_options(options):
    """
    a function to evaluate input options and set some defaults
    """

    # imports
    import os
    import sys
    import errno

    # check if there are any inputs
    if options["sdir"] is None and options["sid"] is None:
        get_help(print_help=True)
        sys.exit(0)

    #
    if options["sdir"] is None:
        print('\nERROR: specify subjects directory via --sdir\n')
        sys.exit(1)

    if options["sid"] is None:
        print('\nERROR: Specify --sid\n')
        sys.exit(1)

    subjdir = os.path.join(options["sdir"], options["sid"])
    if not os.path.exists(subjdir):
        print('\nERROR: cannot find sid in subjects directory\n')
        sys.exit(1)

    if options["outdir"] is None:
        options["outdir"] = os.path.join(subjdir, 'brainprint')
    try:
        os.mkdir(options["outdir"])
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
        pass

    # return
    return options

# ------------------------------------------------------------------------------
# auxiliary functions

def _run_cmd(cmd, err_msg):
    """
    execute the command
    """

    # imports
    import sys
    import shlex
    import subprocess

    # run cmd
    print('#@# Command: ' + cmd + '\n')
    args = shlex.split(cmd)
    retcode = subprocess.call(args)
    if retcode != 0:
        print('ERROR: ' + err_msg)
        sys.exit(1)

def _get_ev(evfile):
    """
    returns string list of area, volume and evals
    """

    # imports
    import os

    #
    if not os.path.isfile(evfile):
        return
    area = ''
    volume = ''
    with open(evfile, 'r') as inF:
        for line in inF:
            if 'Area:' in line:
                strlst = line.split()
                area = strlst[1]
            if 'Volume:' in line:
                strlst = line.split()
                volume = strlst[1]
            if 'Eigenvalues:' in line:
                evline = next(inF)
                evstr = ''
                while (evline is not None) and (not '}' in evline):
                    evstr = evstr + evline
                    evline = next(inF)
                evstr = evstr + evline
                evstr = evstr.replace("{", "").replace("}", "").replace(" ", "").replace("\n", "")
                evals = evstr.split(';')
                if abs(float(evals[0])) < 10e-16:
                    evals[0] = "0"
                evals.insert(0, volume)
                evals.insert(0, area)
                return evals

def _write_ev(options, structures, evmat):
    """
    writes EV files
    """

    # write final csv
    outfile = options["brainprint"]
    text_file = open(outfile, "w")
    text_file.write((','.join(structures)) + '\n')
    evstrans = list(zip(*evmat))
    for item in evstrans:
        text_file.write("%s\n" % ','.join(["%.8e" % it for it in item]))
    text_file.close()

# ------------------------------------------------------------------------------
# image and surface processing functions

# creates a surface from the aseg and label info and writes it to the outdir
def _get_aseg_surf(options):
    """
    a function to create a surface from the aseg and label files
    """

    # imports
    import os
    import uuid

    #
    astring = ' '.join(options["asegid"])
    subjdir = os.path.join(options["sdir"], options["sid"])
    aseg = os.path.join(subjdir, 'mri', 'aseg.mgz')
    norm = os.path.join(subjdir, 'mri', 'norm.mgz')
    tmpname = 'aseg.' + str(uuid.uuid4())
    segf = os.path.join(options["outdir"], tmpname + '.mgz')
    segsurf = os.path.join(options["outdir"], tmpname + '.surf')
    # binarize on selected labels (creates temp segf)
    # always binarize first, otherwise pretess may scale aseg if labels are larger than 255 (e.g. aseg+aparc, bug in mri_pretess?)
    cmd = 'mri_binarize --i ' + aseg + ' --match ' + astring + ' --o ' + segf
    _run_cmd(cmd, 'mri_binarize failed.')
    ptinput = segf
    ptlabel = '1'
    # if norm exist, fix label (pretess)
    if os.path.isfile(norm):
        cmd = 'mri_pretess ' + ptinput + ' ' + ptlabel + ' ' + norm + ' ' + segf
        _run_cmd(cmd, 'mri_pretess failed.')
    else:
        if not os.path.isfile(segf):
            # cp segf if not exist yet (it exists already if we combined labels above)
            cmd = 'cp ' + ptinput + ' ' + segf
            _run_cmd(cmd, 'cp segmentation file failed.')
    # runs marching cube to extract surface
    cmd = 'mri_mc ' + segf + ' ' + ptlabel + ' ' + segsurf
    _run_cmd(cmd, 'mri_mc failed?')
    # convert to vtk
    cmd = 'mris_convert ' + segsurf + ' ' + options["outsurf"]
    _run_cmd(cmd, 'mris_convert failed.')
    # return surf name
    return options["outsurf"]

# ------------------------------------------------------------------------------
# compute brainprint

def _compute_brainprint(options):
    """
    a function to compute shapeDNA descriptors for several structures
    """

    # imports
    import os
    import subprocess
    import numpy as np
    from lapy import ShapeDNA, TriaIO

    # define structures

    # combined and individual aseg labels:
    # - Left  Striatum: left  Caudate + Putamen + Accumbens
    # - Right Striatum: right Caudate + Putamen + Accumbens
    # - CorpusCallosum: 5 subregions combined
    # - Cerebellum: brainstem + (left+right) cerebellum WM and GM
    # - Ventricles: (left+right) lat.vent + inf.lat.vent + choroidplexus + 3rdVent + CSF
    # - Lateral-Ventricle: lat.vent + inf.lat.vent + choroidplexus
    # - 3rd-Ventricle: 3rd-Ventricle + CSF

    structures = ['CorpusCallosum', 'Cerebellum', 'Ventricles',
                  '3rd-Ventricle', '4th-Ventricle', 'Brain-Stem',
                  'Left-Striatum', 'Left-Lateral-Ventricle',
                  'Left-Cerebellum-White-Matter', 'Left-Cerebellum-Cortex',
                  'Left-Thalamus-Proper', 'Left-Caudate', 'Left-Putamen',
                  'Left-Pallidum', 'Left-Hippocampus', 'Left-Amygdala',
                  'Left-Accumbens-area', 'Left-VentralDC',
                  'Right-Striatum', 'Right-Lateral-Ventricle',
                  'Right-Cerebellum-White-Matter', 'Right-Cerebellum-Cortex',
                  'Right-Thalamus-Proper', 'Right-Caudate', 'Right-Putamen',
                  'Right-Pallidum', 'Right-Hippocampus', 'Right-Amygdala',
                  'Right-Accumbens-area', 'Right-VentralDC']

    cortex_2d = ['lh-white-2d', 'lh-pial-2d', 'rh-white-2d', 'rh-pial-2d']

    if not options["skipcortex"]:
        structures = structures + cortex_2d

    labels = [[251, 252, 253, 254, 255], [7, 8, 16, 46, 47], [4, 5, 14, 24, 31, 43, 44, 63],
              [14, 24], 15, 16,
              [11, 12, 26], [4, 5, 31],
              7, 8,
              10, 11, 12,
              13, 17, 18,
              26, 28,
              [50, 51, 58], [43, 44, 63],
              46, 47,
              49, 50, 51,
              52, 53, 54,
              58, 60]

    # process aseg labels

    evmat = list()

    for lab in labels:

        if type(lab) == list:
            astring = '_'.join(str(x) for x in lab)
        else:
            astring = str(lab)

        print("\n\n===========================================================")
        print("Aseg label id str " + astring + "\n")

        surfnameo = 'aseg.final.' + astring + '.vtk'
        asegsurfo = os.path.join(options["outdir"], surfnameo)
        failed = False

        evals = list()
        options['asegid'] = astring.split('_')
        options['outsurf'] = asegsurfo

        try:
            # convert to string
            options['asegid'] = [ str(i) for i in options['asegid'] ]

            # generate surfaces
            procsurf = _get_aseg_surf(options)

            # read surface
            tria = TriaIO.import_vtk(procsurf)

            # run ShapeDNA
            evDict = ShapeDNA.compute_shapedna(tria,
                k=options["num"], lump=options["lump"],
                aniso=options["aniso"],
                aniso_smooth=options["aniso_smooth"],
                norm=options["norm"], rwt=options["rwt"])

            # prepend area, volume to evals
            evals = np.concatenate((np.array(tria.area(), ndmin=1), np.array(tria.volume(), ndmin=1), evDict["Eigenvalues"]))

        except subprocess.CalledProcessError as e:
            print('Error occured, skipping label ' + astring)
            failed = True

        if len(evals)==0 or failed:
            evals = ['NaN'] * (options["num"] + 2)

        evmat.append(evals)

    # if skip cortex, return here

    if options["skipcortex"] is False:

        # process 2D Surfaces

        for hem in ['lh', 'rh']:
            for typeSurf in ['white', 'pial']:

                surfname = hem + '.' + typeSurf
                print("\n\n===========================================================")
                print("2D Cortical Surface " + surfname + "\n")

                outsurf = os.path.join(options["sdir"], options["sid"], 'surf', surfname)
                failed = False

                evals = list()
                options['surf'] = outsurf
                options['outsurf'] = outsurf + '.vtk'

                try:
                    # convert to string
                    options['asegid'] = [ str(i) for i in options['asegid'] ]

                    # generate surfaces
                    procsurf = _get_aseg_surf(options)

                    # read surface
                    tria = TriaIO.import_vtk(procsurf)

                    # run ShapeDNA
                    evDict = ShapeDNA.compute_shapedna(tria,
                        k=options["num"], lump=options["lump"],
                        aniso=options["aniso"],
                        aniso_smooth=options["aniso_smooth"],
                        norm=options["norm"], rwt=options["rwt"])

                    # prepend area, volume to evals
                    evals = np.concatenate((np.array(tria.area(), ndmin=1), np.array(tria.volume(), ndmin=1), evDict["Eigenvalues"]))

                except subprocess.CalledProcessError as e:
                    print('Error occured, skipping 2D surface ' + surfname)
                    failed = True

                if len(evals)==0 or failed:
                    evals = ['NaN'] * (options["num"] + 2)

                evmat.append(evals)

    return structures, evmat

# ------------------------------------------------------------------------------
# run brainprint (as a function)

def run_brainprint(options=None, sdir=None, sid=None, outdir=None, num=50, evec=False, skipcortex=False, norm=False, reweight=False):
    """
    a function to run a BrainPrint analysis
    """

    # imports
    import os
    import sys
    import importlib

    # get options
    if options is None:

        options = { "sdir" : sdir, "sid" : sid, "outdir" : outdir, "num" : num,
            "evec" : evec, "skipcortex" : skipcortex, "norm" : norm,
            "rwt" : reweight }

    # check options
    options = _check_options(options)

    # check dependencies
    if importlib.util.find_spec("lapy") is None:
        print("ERROR: could not find the lapy package, exiting.")
        sys.exit(1)

    # check Freesurfer
    if os.getenv('FREESURFER_HOME') is None:
        print('ERROR: Environment variable FREESURFER_HOME not set.')
        sys.exit(1)

    # set non-changeable default options
    options["bcond"] = 1
    options["lump"] = False
    options["aniso"] = None
    options["aniso_smooth"] = 10
    options["brainprint"] = os.path.join(options["outdir"], options["sid"] + '.brainprint.csv')

    # run shapeDNA
    structures, evmat = _compute_brainprint(options)

    # write EVs
    _write_ev(options, structures, evmat)

# ------------------------------------------------------------------------------
# main function

if __name__ == "__main__":

    # imports
    import warnings

    # settings
    warnings.filterwarnings('ignore', '.*negative int.*')

    # parse command line options
    options = _parse_options()

    # run brainprint
    run_brainprint(options)
