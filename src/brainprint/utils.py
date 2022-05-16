"""
Utilities for the :mod:`brainprint` module.
"""
import os
import shlex
import subprocess
from pathlib import Path

import numpy as np
import pandas as pd
from lapy import TriaIO, TriaMesh
from lapy.read_geometry import read_geometry

from brainprint import configuration, messages


def validate_environment() -> None:
    """
    Checks whether required environment variables are set.
    """
    if not os.getenv("FREESURFER_HOME"):
        raise RuntimeError(messages.NO_FREESURFER_HOME)


def test_freesurfer() -> None:
    command = configuration.COMMAND_TEMPLATES["test"]
    try:
        run_shell_command(command, "mri_binarize failed.")
    except FileNotFoundError:
        raise RuntimeError(messages.NO_FREESURFER_BINARIES)


def run_shell_command(command: str, error_message: str):
    """
    Execute shell command.
    """
    print(f"Executing command:\t{command}", end="\n")
    args = shlex.split(command)
    return_code = subprocess.call(args)
    if return_code != 0:
        raise RuntimeError(error_message)


def validate_subject_dir(subjects_dir: Path, subject_id: str) -> None:
    """
    a function to validate input options and set some defaults.
    """
    subject_dir = subjects_dir / subject_id
    if not subject_dir.is_dir():
        message = messages.MISSING_SUBJECT_DIRECTORY.format(path=subject_dir)
        raise FileNotFoundError(message)
    return subject_dir


def create_output_paths(
    subject_dir: Path = None, output_directory: Path = None
) -> None:
    if subject_dir is None and output_directory is None:
        raise ValueError(messages.MISSING_OUTPUT_BASE)
    elif output_directory is None:
        destination = Path(subject_dir) / configuration.BRAINPRINT_RESULTS_DIR
    else:
        destination = output_directory
    destination.mkdir(parents=True, exist_ok=True)
    eigenvectors_path = destination / configuration.EIGENVECTORS_DIR
    surfaces_path = destination / configuration.SURFACES_DIR
    temp_path = destination / configuration.TEMP_DIR
    eigenvectors_path.mkdir(parents=True, exist_ok=True)
    surfaces_path.mkdir(parents=True, exist_ok=True)
    temp_path.mkdir(parents=True, exist_ok=True)
    return destination


def export_results(
    options,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray = None,
    distances: np.ndarray = None,
):
    """
    Writes the BrainPrint analysis results to CSV files.
    """
    df = pd.DataFrame(eigenvalues).sort_index(axis=1)
    ev_indices = [f"ev{i}" for i in range(len(df) - 2)]
    df.index = ["area", "volume"] + ev_indices
    eigenvalues_csv = options["csv_path"]
    df.to_csv(eigenvalues_csv, index=True, na_rep="NaN")

    if eigenvectors is not None:
        eigenvectors_dir = (
            eigenvalues_csv.parent / configuration.EIGENVECTORS_DIR
        )
        for key, value in eigenvectors.items():
            suffix = configuration.EIGENVECTORS_SUFFIX_TEMPLATE.format(key=key)
            name = eigenvalues_csv.with_suffix(suffix).name
            destination = eigenvectors_dir / name
            pd.DataFrame(value).to_csv(
                destination,
                index=True,
                na_rep="NaN",
            )

    if distances is not None:
        destination = eigenvalues_csv.with_suffix(".asymmetry.csv")
        pd.DataFrame([distances]).to_csv(
            destination,
            index=False,
            na_rep="NaN",
        )


def surf_to_vtk(source: Path, destination: Path) -> Path:
    surface = read_geometry(source)
    TriaIO.export_vtk(TriaMesh(v=surface[0], t=surface[1]), destination)
    return destination
