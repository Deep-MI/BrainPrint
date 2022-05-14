"""
Script entry point.
"""
import os
import subprocess
import uuid
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
from cli.parser import _parse_options
from lapy import ShapeDNA, TriaIO, TriaMesh, read_geometry

from brainprint import messages
from brainprint.utils import (
    ASEG_LABELS,
    CORTICAL_LABELS,
    EXECUTION_DEFAULTS,
    create_output_paths,
    run_shell_command,
    test_freesurfer,
    validate_environment,
    validate_subject_dir,
)

warnings.filterwarnings("ignore", ".*negative int.*")


def _write_ev(options, evMat, evecMat=None, dstMat=None):
    """
    Writes eigenvalue (EV) files.
    """
    df = pd.DataFrame(evMat).sort_index(axis=1)
    df.index = ["area", "volume"] + [
        "ev" + str(x) for x in np.arange(options["num"])
    ]
    df.to_csv(options["csv_path"], index=True, na_rep="NaN")

    # optionally write evec
    if options["evec"] is True and evecMat is not None:
        for key, value in evecMat.items():
            pd.DataFrame(value).to_csv(
                os.path.join(
                    os.path.dirname(options["csv_path"]),
                    "eigenvectors",
                    os.path.basename(os.path.splitext(options["csv_path"])[0])
                    + ".evecs-"
                    + key
                    + ".csv",
                ),
                index=True,
                na_rep="NaN",
            )

    # write distances
    if options["asymmetry"] is True and dstMat is not None:
        pd.DataFrame([dstMat]).to_csv(
            os.path.splitext(options["csv_path"])[0] + ".asymmetry.csv",
            index=False,
            na_rep="NaN",
        )


def _get_aseg_surf(subject_dir: Path, options):
    """
    Creates a surface from the aseg and label files.
    """
    astring = " ".join(options["asegid"])

    aseg = subject_dir / "mri" / "aseg.mgz"
    norm = subject_dir / "mri" / "norm.mgz"
    tmpname = f"aseg.{str(uuid.uuid4())}"
    segf = options["outdir"] / "temp" / f"{tmpname}.mgz"
    segsurf = options["outdir"] / "temp" / "{tmpname}.surf"
    # binarize on selected labels (creates temp segf)
    # always binarize first, otherwise pretess may scale aseg if labels are
    # larger than 255 (e.g. aseg+aparc, bug in mri_pretess?)
    cmd = f"mri_binarize --i {aseg} --match {astring} --o {segf}"
    run_shell_command(cmd, "mri_binarize failed.")
    ptinput = segf
    ptlabel = "1"
    # if norm exist, fix label (pretess)
    if norm.is_file():
        cmd = f"mri_pretess {ptinput} {ptlabel} {norm} {segf}"
        run_shell_command(cmd, "mri_pretess failed.")
    else:
        if not segf.is_file():
            # cp segf if not exist yet (it exists already if we combined labels
            # above)
            cmd = f"cp {ptinput} {segf}"
            run_shell_command(cmd, "cp segmentation file failed.")
    # runs marching cube to extract surface
    cmd = f"mri_mc {segf} {ptlabel} {segsurf}"
    run_shell_command(cmd, "mri_mc failed?")
    # convert to vtk
    cmd = f"mris_convert {segsurf} {options['outsurf']}"
    run_shell_command(cmd, "mris_convert failed.")
    # return surf name
    return options["outsurf"]


def compute_brainprint(subject_dir: Path, options):
    """
    Computes shapeDNA descriptors for several structures.
    """

    # generate surfaces from aseg labels

    surfaces = dict()

    for label, indices in ASEG_LABELS.items():
        options["asegid"] = indices
        index_string = "_".join(indices)
        options["outsurf"] = (
            options["outdir"] / "surfaces" / f"aseg.final.{index_string}.vtk"
        )
        surfaces[label] = _get_aseg_surf(subject_dir, options)

    if not options["skipcortex"]:
        for label, file_name in CORTICAL_LABELS.items():
            # Convert to vtk and append to list of structures.
            surface_path = subject_dir / "surf" / file_name
            surface = read_geometry.read_geometry(surface_path)
            destination = options["outdir"] / "surfaces" / f"{file_name}.vtk"
            TriaIO.export_vtk(
                TriaMesh(v=surface[0], t=surface[1]), destination
            ),
            surfaces[label] = destination

    # Compute shape DNA.
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


def run_brainprint(subjects_dir: Path, subject_id: str, **kwargs):
    """
    Runs the BrainPrint analysis.
    """
    subject_dir = validate_subject_dir(subjects_dir, subject_id)
    validate_environment()
    test_freesurfer()
    options = {**kwargs, **EXECUTION_DEFAULTS}
    options["outdir"] = create_output_paths(subject_dir, kwargs)
    options["csv_path"] = options["outdir"] / f"{subject_id}.brainprint.csv"

    evMat, evecMat = compute_brainprint(subject_dir, options)

    dstMat = None
    if options["asymmetry"]:
        dstMat = _compute_asymmetry(options, evMat)

    # write EVs
    _write_ev(options, evMat, evecMat, dstMat)

    print(messages.RETURN_VALUES)
    return evMat, evecMat, dstMat


def main():
    options = _parse_options()
    return run_brainprint(**options)
