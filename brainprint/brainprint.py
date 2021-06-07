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
    brainprint.run_brainprint(sdir="/my/subjects/directory", sid="my_subject_id")

    Additional options are num=<int>, evec=<bool>, skipcortex=<bool>,
    norm=<"surface"|"volume"|"geometry"|"none">, reweight=<bool>, and outdir=<string>.

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
    h_sid = 'Subject ID (FreeSurfer processed directory inside the subjects directory)'
    h_sdir = 'FreeSurfer subjects directory'
    h_outdir = 'Output directory (default: <sdir>/<sid>/brainprint)'
    h_num = 'Number of eigenvalues/vectors to compute (default: 50)'
    h_evec = 'Switch on eigenvector computation (default: off)'
    h_skipcortex = 'Skip cortical surfaces (default: off)'
    h_norm = 'Perform on eigenvalue normalization (default: none)'
    h_rwt = 'Switch on eigenvalue reweighting (default: off)'
    h_asym = 'Switch on additional asymmetry calculation (default: off)'

    # required arguments
    required = parser.add_argument_group('Required arguments')

    required.add_argument('--sid', dest='sid', help=h_sid, default=None,
        metavar="<string>", required=False)
    required.add_argument('--sdir', dest="sdir", help=h_sdir, default=None,
        metavar="<directory>", required=False)

    # optional arguments
    optional = parser.add_argument_group('Processing directives')

    optional.add_argument('--num', dest='num', help=h_num, default=50,
        metavar="<num>", type=int, required=False)
    optional.add_argument('--evec', dest='evec', help=h_evec, default=False,
        action='store_true', required=False)
    optional.add_argument('--skipcortex', dest='skipcortex', help=h_skipcortex,
        default=False, action='store_true', required=False)
    optional.add_argument('--norm', dest='norm', help=h_norm, default="none",
        metavar=" <surface|volume|geometry|none>", required=False)
    optional.add_argument('--reweight', dest='rwt', help=h_rwt, default=False,
        action='store_true', required=False)
    optional.add_argument('--asymmetry', dest='asymmetry', help=h_asym,
        default=False, action='store_true', required=False)

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
        norm=args.norm, rwt=args.rwt, asymmetry=args.asymmetry)

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
        os.mkdir(os.path.join(options["outdir"], "eigenvectors"))
        os.mkdir(os.path.join(options["outdir"], "surfaces"))
        os.mkdir(os.path.join(options["outdir"], "temp"))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
        pass

    # return
    return options

# ------------------------------------------------------------------------------
# auxiliary functions

def _run_cmd(cmd, err_msg, expected_retcode=[0]):
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
    if (retcode in expected_retcode) is False:
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

def _write_ev(options, evMat, evecMat=None, dstMat=None):
    """
    writes EV files
    """

    # imports
    import os
    import numpy as np
    import pandas as pd

    # write final csv (keep in mind that evMat contains area and volume as
    # first two entries)
    df = pd.DataFrame(evMat).sort_index(axis=1)
    df.index =  [ "area",  "volume"] + [ "ev" + str(x) for x in np.arange(options["num"])]
    df.to_csv(options["brainprint"], index=True)

    # optionally write evec
    if options["evec"] is True and evecMat is not None:
        for i in evecMat.keys():
            pd.DataFrame(evecMat[i]).to_csv(os.path.join(
                os.path.dirname(options["brainprint"]), 'eigenvectors',
                os.path.basename(os.path.splitext(options["brainprint"])[0]) + ".evecs-" + i + ".csv"), index=True)

    # write distances
    if options["asymmetry"] is True and dstMat is not None:
        pd.DataFrame([dstMat]).to_csv(os.path.splitext(options["brainprint"])[0] + ".asymmetry.csv", index=False)

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
    segf = os.path.join(options["outdir"], 'temp', tmpname + '.mgz')
    segsurf = os.path.join(options["outdir"], 'temp', tmpname + '.surf')
    # binarize on selected labels (creates temp segf)
    # always binarize first, otherwise pretess may scale aseg if labels are
    # larger than 255 (e.g. aseg+aparc, bug in mri_pretess?)
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
            # cp segf if not exist yet (it exists already if we combined labels
            # above)
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
    from lapy import TriaMesh, TriaIO, ShapeDNA, read_geometry

    # define aseg labels

    # combined and individual aseg labels:
    # - Left  Striatum: left  Caudate + Putamen + Accumbens
    # - Right Striatum: right Caudate + Putamen + Accumbens
    # - CorpusCallosum: 5 subregions combined
    # - Cerebellum: brainstem + (left+right) cerebellum WM and GM
    # - Ventricles: (left+right) lat.vent + inf.lat.vent + choroidplexus + 3rdVent + CSF
    # - Lateral-Ventricle: lat.vent + inf.lat.vent + choroidplexus
    # - 3rd-Ventricle: 3rd-Ventricle + CSF

    aseg_labels = {
        'CorpusCallosum' : ['251', '252', '253', '254', '255'],
        'Cerebellum' : ['7', '8', '16', '46', '47'],
        'Ventricles' : ['4', '5', '14', '24', '31', '43', '44', '63'],
        '3rd-Ventricle' : ['14', '24'],
        '4th-Ventricle' : ['15'],
        'Brain-Stem' : ['16'],
        'Left-Striatum' : ['11', '12', '26'],
        'Left-Lateral-Ventricle' : ['4', '5', '31'],
        'Left-Cerebellum-White-Matter' : ['7'],
        'Left-Cerebellum-Cortex' : ['8'],
        'Left-Thalamus-Proper' : ['10'],
        'Left-Caudate' : ['11'],
        'Left-Putamen' : ['12'],
        'Left-Pallidum' : ['13'],
        'Left-Hippocampus' : ['17'],
        'Left-Amygdala' : ['18'],
        'Left-Accumbens-area' : ['26'],
        'Left-VentralDC' : ['28'],
        'Right-Striatum' : ['50', '51', '58'],
        'Right-Lateral-Ventricle' : ['43', '44', '63'],
        'Right-Cerebellum-White-Matter' : ['46'],
        'Right-Cerebellum-Cortex' : ['47'],
        'Right-Thalamus-Proper' : ['49'],
        'Right-Caudate' : ['50'],
        'Right-Putamen' : ['51'],
        'Right-Pallidum' : ['52'],
        'Right-Hippocampus' : ['53'],
        'Right-Amygdala' : ['54'],
        'Right-Accumbens-area' : ['58'],
        'Right-VentralDC' : ['60']
        }

    # generate surfaces from aseg labels

    surfaces = dict()

    for aseg_labels_i in aseg_labels:

        # message
        print("\n\n===========================================================")
        print("Aseg label id str " + '_'.join(aseg_labels[aseg_labels_i]) + "\n")

        #
        options['asegid'] = aseg_labels[aseg_labels_i]
        options['outsurf'] = os.path.join(options["outdir"], 'surfaces', 'aseg.final.' + '_'.join(aseg_labels[aseg_labels_i]) + '.vtk')

        # generate surfaces
        surfaces[aseg_labels_i] = _get_aseg_surf(options)

    # define cortical labels

    if options["skipcortex"] is False:

        cortical_labels = {
            'lh-white-2d' : 'lh.white',
            'rh-white-2d': 'rh.white',
            'lh-pial-2d' : 'lh.pial',
            'rh-pial-2d': 'rh.pial',
            }

    # generate surfaces for lh/rh white/pial

    if options["skipcortex"] is False:

        for cortical_labels_i in cortical_labels:

                # message
                print("\n\n===========================================================")
                print("2D Cortical Surface " + cortical_labels[cortical_labels_i] + "\n")

                # convert to vtk and append to list of structures
                surf = read_geometry.read_geometry(os.path.join(options["sdir"], options["sid"], 'surf', cortical_labels[cortical_labels_i]))
                TriaIO.export_vtk(TriaMesh(v=surf[0], t=surf[1]), os.path.join(options["outdir"], 'surfaces', cortical_labels[cortical_labels_i] + '.vtk'))
                surfaces[cortical_labels_i] = os.path.join(options["outdir"], 'surfaces', cortical_labels[cortical_labels_i] + '.vtk')

    # compute shape dna

    failed = False
    evMat = dict()
    evecMat = dict()

    for surfaces_i in surfaces:

        try:

            # read surface
            tria = TriaIO.import_vtk(surfaces[surfaces_i])

            # run ShapeDNA
            evDict = ShapeDNA.compute_shapedna(tria,
                k=options["num"], lump=options["lump"],
                aniso=options["aniso"],
                aniso_smooth=options["aniso_smooth"])

            evMat[surfaces_i] = evDict["Eigenvalues"]
            evecMat[surfaces_i] = evDict["Eigenvectors"]

            # normalize
            if options["norm"] == "surface":
                evMat[surfaces_i] = ShapeDNA.normalize_ev(geom=tria, evals=evMat[surfaces_i], method="surface")
            elif options["norm"] == "volume":
                evMat[surfaces_i] = ShapeDNA.normalize_ev(geom=tria, evals=evMat[surfaces_i], method="volume")
            elif options["norm"] == "geometry":
                evMat[surfaces_i] = ShapeDNA.normalize_ev(geom=tria, evals=evMat[surfaces_i], method="geometry")

            # reweight
            if options["rwt"] is True:
                evMat[surfaces_i] = ShapeDNA.reweight_ev(evMat[surfaces_i])

            # prepend area, volume to evals
            evMat[surfaces_i] = np.concatenate((np.array(tria.area(), ndmin=1), np.array(tria.volume(), ndmin=1), evMat[surfaces_i]))

        except subprocess.CalledProcessError as e:
            print('Error occured, skipping label ' + surfaces_i)
            failed = True

        if len(evMat[surfaces_i])==0 or failed:
            evMat[surfaces_i] = ['NaN'] * (options["num"] + 2)

    return evMat, evecMat

# ------------------------------------------------------------------------------
# compute asymmetry

def _compute_asymmetry(options, evMat):
    """
    a function to compute lateral shape analysis using the brainprint
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

    structures_left_right = [
        {'left': 'Left-Striatum', 'right': 'Right-Striatum'},
        {'left': 'Left-Lateral-Ventricle', 'right': 'Right-Lateral-Ventricle'},
        {'left': 'Left-Cerebellum-White-Matter', 'right': 'Right-Cerebellum-White-Matter'},
        {'left': 'Left-Cerebellum-Cortex', 'right': 'Right-Cerebellum-Cortex'},
        {'left': 'Left-Thalamus-Proper', 'right': 'Right-Thalamus-Proper'},
        {'left': 'Left-Caudate', 'right': 'Right-Caudate'},
        {'left': 'Left-Putamen', 'right': 'Right-Putamen'},
        {'left': 'Left-Pallidum', 'right': 'Right-Pallidum'},
        {'left': 'Left-Hippocampus', 'right': 'Right-Hippocampus'},
        {'left': 'Left-Amygdala', 'right': 'Right-Amygdala'},
        {'left': 'Left-Accumbens-area', 'right': 'Right-Accumbens-area'},
        {'left': 'Left-VentralDC', 'right': 'Right-VentralDC'}
        ]

    cortex_2d_left_right = [
        {'left': 'lh-white-2d', 'right': 'rh-white-2d'},
        {'left': 'lh-pial-2d', 'right': 'rh-pial-2d'}
        ]

    if options["skipcortex"] is False:
        structures_left_right = structures_left_right + cortex_2d_left_right

    # keep in mind that evMat contains area and volume as first two entries,
    # hence [2:]

    dst = dict()

    for i in range(len(structures_left_right)):
        dst[structures_left_right[i]["left"] + "_" +
            structures_left_right[i]["right"]] = ShapeDNA.compute_distance(
                evMat[structures_left_right[i]["left"]][2:],
                evMat[structures_left_right[i]["right"]][2:],
                dist=options["distance"])

    #
    return dst

# ------------------------------------------------------------------------------
# run brainprint (as a function)

def run_brainprint(options=None, sdir=None, sid=None, outdir=None, num=50, evec=False, skipcortex=False, norm="none", reweight=False, asymmetry=False):
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
            "rwt" : reweight, "asymmetry" : asymmetry }

    # check options
    options = _check_options(options)

    # check dependencies
    if importlib.util.find_spec("lapy") is None:
        print("ERROR: could not find the lapy package, exiting.")
        sys.exit(1)

    # check FreeSurfer
    if os.getenv('FREESURFER_HOME') is None:
        print('ERROR: Environment variable FREESURFER_HOME not set.')
        sys.exit(1)

    # check FreeSurfer
    try:
        cmd = 'mri_binarize -version'
        _run_cmd(cmd, 'mri_binarize failed.', expected_retcode=[0])
    except:
        print('ERROR: could not find / run FreeSurfer binaries.')
        sys.exit(1)

    # set non-changeable default options
    options["bcond"] = 1
    options["lump"] = False
    options["aniso"] = None
    options["aniso_smooth"] = 10
    options["brainprint"] = os.path.join(options["outdir"], options["sid"] + '.brainprint.csv')
    options["distance"] = "euc"

    # compute brainprint (keep in mind that evMat contains area and volume as
    # first two entries)
    evMat, evecMat = _compute_brainprint(options)

    # compute asymmetry
    if options["asymmetry"] is True:
        dstMat = _compute_asymmetry(options, evMat)
    else:
        dstMat = None

    # write EVs
    _write_ev(options, evMat, evecMat, dstMat)

    # return
    print("Returning matrices for eigenvalues, eigenvectors, and (optionally) distances.")
    print("The eigenvalue matrix contains area and volume as first two rows.")
    return evMat, evecMat, dstMat

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
