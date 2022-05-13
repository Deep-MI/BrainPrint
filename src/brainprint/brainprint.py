"""
Script entry point.
"""
import importlib
import os
import subprocess
import sys
import uuid
import warnings

from cli.parser import _check_options, _parse_options, _run_cmd

warnings.filterwarnings("ignore", ".*negative int.*")


def _get_ev(evfile):
    """
    returns string list of area, volume and evals
    """
    if not os.path.isfile(evfile):
        return
    area = ""
    volume = ""
    with open(evfile, "r") as inF:
        for line in inF:
            if "Area:" in line:
                strlst = line.split()
                area = strlst[1]
            if "Volume:" in line:
                strlst = line.split()
                volume = strlst[1]
            if "Eigenvalues:" in line:
                evline = next(inF)
                evstr = ""
                while (evline is not None) and ("}" not in evline):
                    evstr = evstr + evline
                    evline = next(inF)
                evstr = evstr + evline
                evstr = (
                    evstr.replace("{", "")
                    .replace("}", "")
                    .replace(" ", "")
                    .replace("\n", "")
                )
                evals = evstr.split(";")
                if abs(float(evals[0])) < 10e-16:
                    evals[0] = "0"
                evals.insert(0, volume)
                evals.insert(0, area)
                return evals


def _write_ev(options, evMat, evecMat=None, dstMat=None):
    """
    writes EV files
    """
    import numpy as np
    import pandas as pd

    # write final csv (keep in mind that evMat contains area and volume as
    # first two entries)
    df = pd.DataFrame(evMat).sort_index(axis=1)
    df.index = ["area", "volume"] + [
        "ev" + str(x) for x in np.arange(options["num"])
    ]
    df.to_csv(options["brainprint"], index=True, na_rep="NaN")

    # optionally write evec
    if options["evec"] is True and evecMat is not None:
        for i in evecMat.keys():
            pd.DataFrame(evecMat[i]).to_csv(
                os.path.join(
                    os.path.dirname(options["brainprint"]),
                    "eigenvectors",
                    os.path.basename(
                        os.path.splitext(options["brainprint"])[0]
                    )
                    + ".evecs-"
                    + i
                    + ".csv",
                ),
                index=True,
                na_rep="NaN",
            )

    # write distances
    if options["asymmetry"] is True and dstMat is not None:
        pd.DataFrame([dstMat]).to_csv(
            os.path.splitext(options["brainprint"])[0] + ".asymmetry.csv",
            index=False,
            na_rep="NaN",
        )


# ------------------------------------------------------------------------------
# image and surface processing functions

# creates a surface from the aseg and label info and writes it to the outdir
def _get_aseg_surf(options):
    """
    a function to create a surface from the aseg and label files
    """
    astring = " ".join(options["asegid"])
    subjdir = os.path.join(options["sdir"], options["sid"])
    aseg = os.path.join(subjdir, "mri", "aseg.mgz")
    norm = os.path.join(subjdir, "mri", "norm.mgz")
    tmpname = "aseg." + str(uuid.uuid4())
    segf = os.path.join(options["outdir"], "temp", tmpname + ".mgz")
    segsurf = os.path.join(options["outdir"], "temp", tmpname + ".surf")
    # binarize on selected labels (creates temp segf)
    # always binarize first, otherwise pretess may scale aseg if labels are
    # larger than 255 (e.g. aseg+aparc, bug in mri_pretess?)
    cmd = "mri_binarize --i " + aseg + " --match " + astring + " --o " + segf
    _run_cmd(cmd, "mri_binarize failed.")
    ptinput = segf
    ptlabel = "1"
    # if norm exist, fix label (pretess)
    if os.path.isfile(norm):
        cmd = (
            "mri_pretess " + ptinput + " " + ptlabel + " " + norm + " " + segf
        )
        _run_cmd(cmd, "mri_pretess failed.")
    else:
        if not os.path.isfile(segf):
            # cp segf if not exist yet (it exists already if we combined labels
            # above)
            cmd = "cp " + ptinput + " " + segf
            _run_cmd(cmd, "cp segmentation file failed.")
    # runs marching cube to extract surface
    cmd = "mri_mc " + segf + " " + ptlabel + " " + segsurf
    _run_cmd(cmd, "mri_mc failed?")
    # convert to vtk
    cmd = "mris_convert " + segsurf + " " + options["outsurf"]
    _run_cmd(cmd, "mris_convert failed.")
    # return surf name
    return options["outsurf"]


# ------------------------------------------------------------------------------
# compute brainprint


def _compute_brainprint(options):
    """
    a function to compute shapeDNA descriptors for several structures
    """
    import numpy as np
    from lapy import ShapeDNA, TriaIO, TriaMesh, read_geometry

    # define aseg labels
    # combined and individual aseg labels:
    # - Left  Striatum: left  Caudate + Putamen + Accumbens
    # - Right Striatum: right Caudate + Putamen + Accumbens
    # - CorpusCallosum: 5 subregions combined
    # - Cerebellum: brainstem + (left+right) cerebellum WM and GM
    # - Ventricles: (left+right) lat.vent + inf.lat.vent + choroidplexus
    # + 3rdVent + CSF
    # - Lateral-Ventricle: lat.vent + inf.lat.vent + choroidplexus
    # - 3rd-Ventricle: 3rd-Ventricle + CSF

    aseg_labels = {
        "CorpusCallosum": ["251", "252", "253", "254", "255"],
        "Cerebellum": ["7", "8", "16", "46", "47"],
        "Ventricles": ["4", "5", "14", "24", "31", "43", "44", "63"],
        "3rd-Ventricle": ["14", "24"],
        "4th-Ventricle": ["15"],
        "Brain-Stem": ["16"],
        "Left-Striatum": ["11", "12", "26"],
        "Left-Lateral-Ventricle": ["4", "5", "31"],
        "Left-Cerebellum-White-Matter": ["7"],
        "Left-Cerebellum-Cortex": ["8"],
        "Left-Thalamus-Proper": ["10"],
        "Left-Caudate": ["11"],
        "Left-Putamen": ["12"],
        "Left-Pallidum": ["13"],
        "Left-Hippocampus": ["17"],
        "Left-Amygdala": ["18"],
        "Left-Accumbens-area": ["26"],
        "Left-VentralDC": ["28"],
        "Right-Striatum": ["50", "51", "58"],
        "Right-Lateral-Ventricle": ["43", "44", "63"],
        "Right-Cerebellum-White-Matter": ["46"],
        "Right-Cerebellum-Cortex": ["47"],
        "Right-Thalamus-Proper": ["49"],
        "Right-Caudate": ["50"],
        "Right-Putamen": ["51"],
        "Right-Pallidum": ["52"],
        "Right-Hippocampus": ["53"],
        "Right-Amygdala": ["54"],
        "Right-Accumbens-area": ["58"],
        "Right-VentralDC": ["60"],
    }

    # generate surfaces from aseg labels

    surfaces = dict()

    for aseg_labels_i in aseg_labels:

        # message
        print(
            "\n\n==========================================================="
        )
        print(
            "Aseg label id str " + "_".join(aseg_labels[aseg_labels_i]) + "\n"
        )

        #
        options["asegid"] = aseg_labels[aseg_labels_i]
        options["outsurf"] = os.path.join(
            options["outdir"],
            "surfaces",
            "aseg.final." + "_".join(aseg_labels[aseg_labels_i]) + ".vtk",
        )

        # generate surfaces
        surfaces[aseg_labels_i] = _get_aseg_surf(options)

    # define cortical labels

    if options["skipcortex"] is False:

        cortical_labels = {
            "lh-white-2d": "lh.white",
            "rh-white-2d": "rh.white",
            "lh-pial-2d": "lh.pial",
            "rh-pial-2d": "rh.pial",
        }

    # generate surfaces for lh/rh white/pial

    if options["skipcortex"] is False:

        for cortical_labels_i in cortical_labels:

            # message
            print(
                "\n\n========================================================="
            )
            print(
                "2D Cortical Surface "
                + cortical_labels[cortical_labels_i]
                + "\n"
            )

            # convert to vtk and append to list of structures
            surf = read_geometry.read_geometry(
                os.path.join(
                    options["sdir"],
                    options["sid"],
                    "surf",
                    cortical_labels[cortical_labels_i],
                )
            )
            TriaIO.export_vtk(
                TriaMesh(v=surf[0], t=surf[1]),
                os.path.join(
                    options["outdir"],
                    "surfaces",
                    cortical_labels[cortical_labels_i] + ".vtk",
                ),
            )
            surfaces[cortical_labels_i] = os.path.join(
                options["outdir"],
                "surfaces",
                cortical_labels[cortical_labels_i] + ".vtk",
            )

    # compute shape dna

    failed = False
    evMat = dict()
    evecMat = dict()

    for surfaces_i in surfaces:

        try:

            # read surface
            tria = TriaIO.import_vtk(surfaces[surfaces_i])

            # run ShapeDNA
            evDict = ShapeDNA.compute_shapedna(
                tria,
                k=options["num"],
                lump=options["lump"],
                aniso=options["aniso"],
                aniso_smooth=options["aniso_smooth"],
            )

            evMat[surfaces_i] = evDict["Eigenvalues"]
            evecMat[surfaces_i] = evDict["Eigenvectors"]

            # orient if necessary
            if not tria.is_oriented():
                tria.orient_()

            # normalize
            if options["norm"] == "surface":
                evMat[surfaces_i] = ShapeDNA.normalize_ev(
                    geom=tria, evals=evMat[surfaces_i], method="surface"
                )
            elif options["norm"] == "volume":
                evMat[surfaces_i] = ShapeDNA.normalize_ev(
                    geom=tria, evals=evMat[surfaces_i], method="volume"
                )
            elif options["norm"] == "geometry":
                evMat[surfaces_i] = ShapeDNA.normalize_ev(
                    geom=tria, evals=evMat[surfaces_i], method="geometry"
                )

            # reweight
            if options["rwt"] is True:
                evMat[surfaces_i] = ShapeDNA.reweight_ev(evMat[surfaces_i])

            # prepend area, volume to evals
            evMat[surfaces_i] = np.concatenate(
                (
                    np.array(tria.area(), ndmin=1),
                    np.array(tria.volume(), ndmin=1),
                    evMat[surfaces_i],
                )
            )

        except subprocess.CalledProcessError:
            print("Error occured, skipping label " + surfaces_i)
            failed = True

        if len(evMat[surfaces_i]) == 0 or failed:
            evMat[surfaces_i] = ["NaN"] * (options["num"] + 2)

    return evMat, evecMat


# ------------------------------------------------------------------------------
# compute asymmetry


def _compute_asymmetry(options, evMat):
    """
    a function to compute lateral shape analysis using the brainprint
    """

    import numpy as np
    from lapy import ShapeDNA

    # define structures
    # combined and individual aseg labels:
    # - Left  Striatum: left  Caudate + Putamen + Accumbens
    # - Right Striatum: right Caudate + Putamen + Accumbens
    # - CorpusCallosum: 5 subregions combined
    # - Cerebellum: brainstem + (left+right) cerebellum WM and GM
    # - Ventricles: (left+right) lat.vent + inf.lat.vent + choroidplexus
    # + 3rdVent + CSF
    # - Lateral-Ventricle: lat.vent + inf.lat.vent + choroidplexus
    # - 3rd-Ventricle: 3rd-Ventricle + CSF

    structures_left_right = [
        {"left": "Left-Striatum", "right": "Right-Striatum"},
        {"left": "Left-Lateral-Ventricle", "right": "Right-Lateral-Ventricle"},
        {
            "left": "Left-Cerebellum-White-Matter",
            "right": "Right-Cerebellum-White-Matter",
        },
        {"left": "Left-Cerebellum-Cortex", "right": "Right-Cerebellum-Cortex"},
        {"left": "Left-Thalamus-Proper", "right": "Right-Thalamus-Proper"},
        {"left": "Left-Caudate", "right": "Right-Caudate"},
        {"left": "Left-Putamen", "right": "Right-Putamen"},
        {"left": "Left-Pallidum", "right": "Right-Pallidum"},
        {"left": "Left-Hippocampus", "right": "Right-Hippocampus"},
        {"left": "Left-Amygdala", "right": "Right-Amygdala"},
        {"left": "Left-Accumbens-area", "right": "Right-Accumbens-area"},
        {"left": "Left-VentralDC", "right": "Right-VentralDC"},
    ]

    cortex_2d_left_right = [
        {"left": "lh-white-2d", "right": "rh-white-2d"},
        {"left": "lh-pial-2d", "right": "rh-pial-2d"},
    ]

    if options["skipcortex"] is False:
        structures_left_right = structures_left_right + cortex_2d_left_right

    # keep in mind that evMat contains area and volume as first two entries,
    # hence [2:]

    dst = dict()

    for i in range(len(structures_left_right)):
        if (
            np.isnan(evMat[structures_left_right[i]["left"]][2:]).any()
            or np.isnan(evMat[structures_left_right[i]["right"]][2:]).any()
        ):
            print(
                "NaNs found for "
                + structures_left_right[i]["left"]
                + " or "
                + structures_left_right[i]["right"]
                + ". Not computing asymmetry, returning NaN."
            )
            dst[
                structures_left_right[i]["left"]
                + "_"
                + structures_left_right[i]["right"]
            ] = np.nan
        else:
            dst[
                structures_left_right[i]["left"]
                + "_"
                + structures_left_right[i]["right"]
            ] = ShapeDNA.compute_distance(
                evMat[structures_left_right[i]["left"]][2:],
                evMat[structures_left_right[i]["right"]][2:],
                dist=options["distance"],
            )

    #
    return dst


# ------------------------------------------------------------------------------
# run brainprint (as a function)


def run_brainprint(
    options=None,
    sdir=None,
    sid=None,
    outdir=None,
    num=50,
    evec=False,
    skipcortex=False,
    norm="none",
    reweight=False,
    asymmetry=False,
):
    """
    a function to run a BrainPrint analysis
    """
    from brainprint import messages

    if options is None:
        options = _parse_options()

    # get options
    if options is None:

        options = {
            "sdir": sdir,
            "sid": sid,
            "outdir": outdir,
            "num": num,
            "evec": evec,
            "skipcortex": skipcortex,
            "norm": norm,
            "rwt": reweight,
            "asymmetry": asymmetry,
        }

    # check options
    options = _check_options(options)

    # check dependencies
    if importlib.util.find_spec("lapy") is None:
        print("ERROR: could not find the lapy package, exiting.")
        sys.exit(1)

    # check FreeSurfer
    if os.getenv("FREESURFER_HOME") is None:
        print("ERROR: Environment variable FREESURFER_HOME not set.")
        sys.exit(1)

    # check FreeSurfer
    try:
        cmd = "mri_binarize -version"
        _run_cmd(cmd, "mri_binarize failed.", expected_retcode=[0])
    except Exception:
        print("ERROR: could not find / run FreeSurfer binaries.")
        sys.exit(1)

    # set non-changeable default options
    options["bcond"] = 1
    options["lump"] = False
    options["aniso"] = None
    options["aniso_smooth"] = 10
    options["brainprint"] = os.path.join(
        options["outdir"], options["sid"] + ".brainprint.csv"
    )
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

    print(messages.RETURN_VALUES)
    return evMat, evecMat, dstMat
