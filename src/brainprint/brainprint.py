"""
Definition of the brainprint analysis execution functions.
"""
import warnings
from pathlib import Path
from typing import Dict, Tuple, Union

import numpy as np
from lapy import ShapeDNA, TriaMesh

from brainprint import configuration, messages
from brainprint.asymmetry import compute_asymmetry
from brainprint.surfaces import create_surfaces, read_vtk
from brainprint.utils import (
    create_output_paths,
    export_results,
    test_freesurfer,
    validate_environment,
    validate_subject_dir,
)

warnings.filterwarnings("ignore", ".*negative int.*")


def apply_eigenvalues_options(
    eigenvalues: np.ndarray,
    triangular_mesh: TriaMesh,
    norm: str = "none",
    reweight: bool = False,
) -> np.ndarray:
    """
    Applies BrainPrint analysis configuration options to the ShapeDNA
    eigenvalues.

    Parameters
    ----------
    eigenvalues : np.ndarray
        ShapeDNA derived eigenvalues
    triangular_mesh : TriaMesh
        Surface representation
    norm : str, optional
        Eigenvalues normalization method, by default "none"
    reweight : bool, optional
        Whether to reweight eigenvalues or not, by default False

    Returns
    -------
    np.ndarray
        Fixed eigenvalues
    """
    if not triangular_mesh.is_oriented():
        triangular_mesh.orient_()
    if norm != "none":
        eigenvalues = ShapeDNA.normalize_ev(
            geom=triangular_mesh,
            evals=eigenvalues,
            method=norm,
        )
    if reweight:
        eigenvalues = ShapeDNA.reweight_ev(eigenvalues)
    return eigenvalues


def compute_surface_brainprint(
    path: Path,
    return_eigenvectors: bool = True,
    num: int = 50,
    norm: str = "none",
    reweight: bool = False,
) -> Tuple[np.ndarray, Union[np.ndarray, None]]:
    """
    Returns the BrainPrint eigenvalues and eigenvectors for the given surface.

    Parameters
    ----------
    path : Path
        *.vtk* surface path
    return_eigenvectors : bool, optional
        Whether to store eigenvectors or not, by default True
    num : int, optional
        Number of eigenvalues to compute, by default 50
    norm : str, optional
        Eigenvalues normalization method, by default "none"
    reweight : bool, optional
        Whether to reweight eigenvalues or not, by default False

    Returns
    -------
    Tuple[np.ndarray, Union[np.ndarray, None]]
        Eigenvalues, eigenvectors (if returned)
    """
    triangular_mesh = read_vtk(path)
    shape_dna = ShapeDNA.compute_shapedna(
        triangular_mesh,
        k=num,
        **configuration.SHAPEDNA_KWARGS,
    )

    eigenvectors = None
    if return_eigenvectors:
        eigenvectors = shape_dna["Eigenvectors"]

    eigenvalues = shape_dna["Eigenvalues"]
    eigenvalues = apply_eigenvalues_options(
        eigenvalues, triangular_mesh, norm, reweight
    )
    eigenvalues = np.concatenate(
        (
            np.array(triangular_mesh.area(), ndmin=1),
            np.array(triangular_mesh.volume(), ndmin=1),
            eigenvalues,
        )
    )
    return eigenvalues, eigenvectors


def compute_brainprint(
    surfaces: Dict[str, Path],
    keep_eigenvectors: bool = False,
    num: int = 50,
    norm: str = "none",
    reweight: bool = False,
) -> Tuple[Dict[str, np.ndarray], Union[Dict[str, np.ndarray], None]]:
    """
    Computes ShapeDNA descriptors over several surfaces.

    Parameters
    ----------
    surfaces : Dict[str, Path]
        Dictionary mapping from labels to *.vtk* paths
    keep_eigenvectors : bool, optional
        Whether to also return eigenvectors or not, by default False
    num : int, optional
        Number of eigenvalues to compute, by default 50
    norm : str, optional
        Eigenvalues normalization method, by default "none"
    reweight : bool, optional
        Whether to reweight eigenvalues or not, by default False

    Returns
    -------
    Tuple[Dict[str, np.ndarray], Union[Dict[str, np.ndarray], None]]
        Surface label to eigenvalues, surface label to eigenvectors (if
        *keep_eigenvectors* is True)
    """
    eigenvalues = dict()
    eigenvectors = dict() if keep_eigenvectors else None
    for surface_label, surface_path in surfaces.items():
        try:
            (
                surface_eigenvalues,
                surface_eigenvectors,
            ) = compute_surface_brainprint(
                surface_path,
                num=num,
                norm=norm,
                reweight=reweight,
                return_eigenvectors=keep_eigenvectors,
            )
        except Exception as e:
            message = messages.GENERAL_EXECUTION_ERROR.format(exception=e)
            warnings.warn(message)
            eigenvalues[surface_label] = ["NaN"] * (num + 2)
        else:
            if len(eigenvalues[surface_label]) == 0:
                eigenvalues[surface_label] = ["NaN"] * (num + 2)
            eigenvalues[surface_label] = surface_eigenvalues
            if keep_eigenvectors:
                eigenvectors[surface_label] = surface_eigenvectors
    return eigenvalues, eigenvectors


def run_brainprint(
    subjects_dir: Path,
    subject_id: str,
    destination: Path = None,
    num: int = 50,
    skip_cortex: bool = False,
    keep_eigenvectors: bool = False,
    norm: str = "none",
    reweight: bool = False,
    asymmetry: bool = False,
    asymmetry_distance: str = "euc",
):
    """
    Runs the BrainPrint analysis.

    Parameters
    ----------
    subjects_dir : Path
        FreeSurfer's subjects directory
    subject_id : str
        The subject identifier, as defined within the FreeSurfer's subjects
        directory
    destination : Path, optional
        If provided, will use this path as the results root directory, by
        default None
    num : int, optional
        Number of eigenvalues to compute, by default 50
    norm : str, optional
        Eigenvalues normalization method, by default "none"
    reweight : bool, optional
        Whether to reweight eigenvalues or not, by default False
    skip_cortex : bool, optional
        _description_, by default False
    keep_eigenvectors : bool, optional
        Whether to also return eigenvectors or not, by default False
    asymmetry : bool, optional
        Whether to calculate asymmetry between lateral structures, by default
        False
    asymmetry_distance : str, optional
        Distance measurement to use if *asymmetry* is set to True, by default
        "euc"

    Returns
    -------
    Tuple[Dict[str, np.ndarray], Union[Dict[str, np.ndarray], None],
    Union[Dict[str, float], None]]
        Eigenvalues, eigenvectors, distances
    """
    validate_environment()
    test_freesurfer()
    subject_dir = validate_subject_dir(subjects_dir, subject_id)
    destination = create_output_paths(
        subject_dir=subject_dir,
        destination=destination,
    )

    surfaces = create_surfaces(
        subject_dir, destination, skip_cortex=skip_cortex
    )
    eigenvalues, eigenvectors = compute_brainprint(
        surfaces,
        num=num,
        norm=norm,
        reweight=reweight,
        keep_eigenvectors=keep_eigenvectors,
    )

    distances = None
    if asymmetry:
        distances = compute_asymmetry(
            eigenvalues,
            distance=asymmetry_distance,
            skip_cortex=skip_cortex,
        )

    csv_name = configuration.CSV_NAME_TEMPLATE.format(subject_id=subject_id)
    csv_path = destination / csv_name
    export_results(csv_path, eigenvalues, eigenvectors, distances)
    print(messages.RETURN_VALUES)
    return eigenvalues, eigenvectors, distances