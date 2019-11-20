#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
pyBrainPrint - a script to compute ShapeDNA of FreeSurfer structures

"""

# ==============================================================================
# FUNCTIONS

# ------------------------------------------------------------------------------
# help function

def get_help():
    """
    a function to retrieve a help message
    """

    HELPTEXT = """
    
    fs_brainprint.py V2.0
    Author: Martin Reuter, 2015
    
    SUMMARY
    
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

    return HELPTEXT

# ------------------------------------------------------------------------------
# parse options

def parse_options():
    """
    command line options parser: initiate the option parser and return the parsed object
    """

    # imports
    import optparse

    # parse
    parser = optparse.OptionParser(usage=get_help())

    # help text
    h_sid = '(REQUIRED) subject ID (FS processed directory inside the subjects directory)'
    h_sdir = '(REQUIRED) FS subjects directory'
    h_outdir = 'Output directory (default: <sdir>/<sid>/brainprint/ )'
    h_num = 'Number of eigenvalues/vectors to compute (default: 50)'
    h_evec = 'Switch on eigenvector computation (default: off)'
    h_skipcortex = 'Skip cortical surfaces (default: off)'

    # required options
    group = optparse.OptionGroup(parser, "Required options")
    group.add_option('--sid', dest='sid', help=h_sid)
    group.add_option('--sdir', dest='sdir', help=h_sdir)
    parser.add_option_group(group)

    # processing directives
    group = optparse.OptionGroup(parser, "Processing directives")
    group.add_option('--num', dest='num', help=h_num, default=50, type='int')
    group.add_option('--evec', dest='evec', help=h_evec, default=False, action='store_true')
    group.add_option('--skipcortex', dest='skipcortex', help=h_skipcortex, default=False, action='store_true')
    parser.add_option_group(group)

    # output options
    group = optparse.OptionGroup(parser, "Output parameters")
    group.add_option('--outdir', dest='outdir', help=h_outdir)
    parser.add_option_group(group)

    options, args = parser.parse_args()

    return parser, options


def check_options(parser, options):
    """
    a function to evaluate input options and set some defaults
    """

    # imports
    import os
    import sys

    # WITHOUT FREESURFER DO NOTHING
    fshome = os.getenv('FREESURFER_HOME')
    if fshome is None:
        parser.print_help()
        print('\nERROR: Environment variable FREESURFER_HOME not set.', flush=True)
        print('        You need to source FreeSurfer 6.0 or newer.\n', flush=True)
        sys.exit(1)

    if options.sdir is None:
        parser.print_help()
        print('\nERROR: specify subjects directory via --sdir\n', flush=True)
        sys.exit(1)

    if options.sid is None:
        parser.print_help()
        print('\nERROR: Specify --sid\n', flush=True)
        sys.exit(1)

    subjdir = os.path.join(options.sdir, options.sid)
    if not os.path.exists(subjdir):
        parser.print_help()
        print('\nERROR: cannot find sid in subjects directory\n', flush=True)
        sys.exit(1)

    if options.outdir is None:
        options.outdir = os.path.join(subjdir, 'brainprint')
    try:
        os.mkdir(options.outdir)
    except OSError as e:
        if e.errno != os.errno.EEXIST:
            raise e
        pass

    return options


# ------------------------------------------------------------------------------
# auxiliary functions

def run_cmd(cmd, err_msg):
    """
    execute the command
    """

    # imports
    import sys
    import shlex
    import subprocess

    # run cmd
    print('#@# Command: ' + cmd + '\n', flush=True)
    args = shlex.split(cmd)
    retcode = subprocess.call(args)
    if retcode != 0:
        print('ERROR: ' + err_msg, flush=True)
        sys.exit(1)


def get_ev(evfile):
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


def write_ev(options, structures, evmat):
    """
    writes EV files
    """

    # write final csv
    outfile = options.brainprint
    text_file = open(outfile, "w")
    text_file.write((','.join(structures)) + '\n')
    evstrans = list(zip(*evmat))
    for item in evstrans:
        text_file.write("%s\n" % ','.join(["%.8e" % it for it in item]))
    text_file.close()


# ------------------------------------------------------------------------------
# compute shapeDNA

def compute_brainprint(options):
    """
    a function to compute shapeDNA descriptors for several structures
    """

    # imports
    import os
    import subprocess
    from brainprintpython import pyShapeDNA

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

    if not options.skipcortex:
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

        print("\n\n===========================================================", flush=True)
        print("Aseg label id str " + astring + "\n", flush=True)

        surfnameo = 'aseg.final.' + astring + '.vtk'
        asegsurfo = os.path.join(options.outdir, surfnameo)
        failed = False

        ev = list()
        options.asegid = astring.split('_')
        options.outsurf = asegsurfo

        try:
            procsurf = pyShapeDNA.get_aseg_surf(options)
            v, t, ev, evec = pyShapeDNA.compute_shapeDNA_tria(procsurf, options)
            pyShapeDNA.write_ev(v, t, ev, evec, options)
        except subprocess.CalledProcessError as e:
            print('Error occured, skipping label ' + astring, flush=True)
            failed = True

        if len(ev)==0 or failed:
            ev = ['NaN'] * (options.num + 2)

        evmat.append(ev)

    # if skip cortex, return here

    if options.skipcortex:
        return structures, evmat

    # process 2D Surfaces

    for hem in ['lh', 'rh']:
        for typeSurf in ['white', 'pial']:

            surfname = hem + '.' + typeSurf
            print("\n\n===========================================================", flush=True)
            print("2D Cortical Surface " + surfname + "\n", flush=True)

            outsurf = os.path.join(options.sdir, options.sid, 'surf', surfname)
            failed = False

            ev = list()
            options.surf = outsurf
            options.outsurf = outsurf+'.vtk'

            try:
                procsurf = pyShapeDNA.get_surf_surf(options)
                v, t, ev, evec = pyShapeDNA.compute_shapeDNA_tria(procsurf, options)
                pyShapeDNA.write_ev(v, t, ev, evec, options)
            except subprocess.CalledProcessError as e:
                print('Error occured, skipping 2D surface ' + surfname, flush=True)
                failed = True

            if len(ev)==0 or failed:
                ev = ['NaN'] * (options.num + 2)

            evmat.append(ev)

    return structures, evmat


# ------------------------------------------------------------------------------
# main function

if __name__ == "__main__":

    # imports
    import os
    import warnings

    # settings
    warnings.filterwarnings('ignore', '.*negative int.*')

    # parse command line options
    parser, options = parse_options()

    # check options
    options = check_options(parser, options)

    # set options
    options.bcond = 1
    options.brainprint = os.path.join(options.outdir, options.sid+'.brainprint.csv')

    # run shapeDNA
    structures, evmat = compute_brainprint(options)

    # write EVs
    write_ev(options, structures, evmat)