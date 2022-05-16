"""
Script entry point.
"""
import subprocess
import warnings
from pathlib import Path

import numpy as np
from lapy import ShapeDNA, TriaIO

from brainprint import configuration, messages
from brainprint.surfaces import create_aseg_surfaces, create_cortical_surfaces
from brainprint.utils import (
    create_output_paths,
    export_results,
    test_freesurfer,
    validate_environment,
    validate_subject_dir,
)

warnings.filterwarnings("ignore", ".*negative int.*")


def compute_brainprint(
    subject_dir: Path,
    options,
):
    """
    Computes shapeDNA descriptors for several structures.
    """
    destination = options["output_directory"]
    surfaces = create_aseg_surfaces(subject_dir, options["output_directory"])

    if not options["skip_cortex"]:
        cortical_surfaces = create_cortical_surfaces(subject_dir, destination)
        surfaces.update(cortical_surfaces)

    # Compute shape DNA.
    failed = False
    eigenvalues = dict()
    eigenvectors = dict()

    for surface_label, surface_path in surfaces.items():
        try:
            triangular_mesh = TriaIO.import_vtk(surface_path)
        except Exception:
            message = messages.SURFACE_READ_ERROR.format(
                label=surface_label, path=surface_path
            )
            raise RuntimeError(message)
        else:
            if triangular_mesh is None:
                message = messages.SURFACE_READ_ERROR.format(
                    label=surface_label, path=surface_path
                )
                raise RuntimeError(message)
        try:
            shape_dna = ShapeDNA.compute_shapedna(
                triangular_mesh,
                k=options["num"],
                **configuration.SHAPEDNA_KWARGS,
            )

            eigenvalues[surface_label] = shape_dna["Eigenvalues"]
            eigenvectors[surface_label] = shape_dna["Eigenvectors"]

            if not triangular_mesh.is_oriented():
                triangular_mesh.orient_()

            if options["norm"] != "none":
                eigenvalues[surface_label] = ShapeDNA.normalize_ev(
                    geom=triangular_mesh,
                    evals=eigenvalues[surface_label],
                    method=options["norm"],
                )

            if options["rwt"]:
                eigenvalues[surface_label] = ShapeDNA.reweight_ev(
                    eigenvalues[surface_label]
                )

            # Prepend area and volume to eigenvalues.
            eigenvalues[surface_label] = np.concatenate(
                (
                    np.array(triangular_mesh.area(), ndmin=1),
                    np.array(triangular_mesh.volume(), ndmin=1),
                    eigenvalues[surface_label],
                )
            )

        except subprocess.CalledProcessError:
            print("Error occured, skipping label " + surface_label)
            failed = True

        if len(eigenvalues[surface_label]) == 0 or failed:
            eigenvalues[surface_label] = ["NaN"] * (options["num"] + 2)

    return eigenvalues, eigenvectors


def compute_asymmetry(
    eigenvalues, distance: str = "euc", skip_cortex: bool = False
):
    """
    a function to compute lateral shape analysis using the brainprint.
    """
    structures = configuration.LATERAL_STRUCTURES.copy()
    if not skip_cortex:
        structures += configuration.LATERAL_STRUCTURES_2D

    distances = dict()
    for lateral_structure in structures:
        left_label, right_label = (
            lateral_structure["left"],
            lateral_structure["right"],
        )
        left_eigenvalues, right_eigenvalues = (
            eigenvalues[left_label][2:],
            eigenvalues[right_label][2:],
        )
        has_nan = (
            np.isnan(left_eigenvalues).any()
            or np.isnan(right_eigenvalues).any()
        )
        key = f"{left_label}_{right_label}"
        if has_nan:
            message = messages.ASYMMETRY_NAN.format(
                left_label=left_label, right_label=right_label
            )
            print(message)
            distances[key] = np.nan
        else:
            distances[key] = ShapeDNA.compute_distance(
                left_eigenvalues,
                right_eigenvalues,
                dist=distance,
            )
    return distances


def run_brainprint(subjects_dir: Path, subject_id: str, **kwargs):
    """
    Runs the BrainPrint analysis.
    """
    subject_dir = validate_subject_dir(subjects_dir, subject_id)
    validate_environment()
    test_freesurfer()
    kwargs["output_directory"] = create_output_paths(
        subject_dir=subject_dir,
        output_directory=kwargs.get("output_directory"),
    )
    kwargs["csv_path"] = (
        kwargs["output_directory"] / f"{subject_id}.brainprint.csv"
    )

    eigenvalues, eigenvectors = compute_brainprint(subject_dir, kwargs)

    distances = None
    if kwargs["asymmetry"]:
        distances = compute_asymmetry(
            eigenvalues,
            distance=kwargs["asymmetry_distance"],
            skip_cortex=kwargs["skip_cortex"],
        )

    export_results(kwargs, eigenvalues, eigenvectors, distances)
    print(messages.RETURN_VALUES)
    return eigenvalues, eigenvectors, distances
