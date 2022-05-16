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
    """
    Tests FreeSurfer binarize are accessible and executable.

    Raises
    ------
    RuntimeError
        Failed to execute test FreeSurfer command
    """
    command = configuration.COMMAND_TEMPLATES["test"]
    try:
        run_shell_command(command)
    except FileNotFoundError:
        raise RuntimeError(messages.NO_FREESURFER_BINARIES)


def run_shell_command(command: str):
    """
    Execute shell command.

    Parameters
    ----------
    command : str
        Shell command to be executed

    Raises
    ------
    RuntimeError
        Shell command execution failure
    """
    print(f"Executing command:\t{command}", end="\n")
    args = shlex.split(command)
    try:
        return_code = subprocess.call(args)
    except Exception as e:
        message = messages.SHELL_EXECUTION_FAILURE.format(
            command=command, exception=e
        )
        print(message)
        raise
    if return_code != 0:
        message = messages.SHELL_EXECUTION_RETURN.format(command=command)
        raise RuntimeError(message)


def validate_subject_dir(subjects_dir: Path, subject_id: str) -> None:
    """
    Checks the input FreeSurfer preprocessing results directory exists.

    Parameters
    ----------
    subjects_dir : Path
        FreeSurfer's subjects directory
    subject_id : str
        The subject identifier, as defined within the FreeSurfer's subjects
        directory

    Raises
    ------
    FileNotFoundError
        Subject results directory does not exist
    """
    subject_dir = subjects_dir / subject_id
    if not subject_dir.is_dir():
        message = messages.MISSING_SUBJECT_DIRECTORY.format(path=subject_dir)
        raise FileNotFoundError(message)
    return subject_dir


def create_output_paths(
    subject_dir: Path = None, output_dir: Path = None
) -> None:
    """
    Creates the output directories in which the BrainPrint analysis derivatives
    will be created. One of *subject_dir* or *output_dir* must be
    provided.

    Parameters
    ----------
    subject_dir : Path, optional
        If provided, will simply nest results in the provided directory, by
        default None
    output_dir : Path, optional
        If provided, will use this path as the results root directory, by
        default None

    Raises
    ------
    ValueError
        No *subject_dir* or *output_dir* provided
    """
    if subject_dir is None and output_dir is None:
        raise ValueError(messages.MISSING_OUTPUT_BASE)
    elif output_dir is None:
        destination = Path(subject_dir) / configuration.BRAINPRINT_RESULTS_DIR
    else:
        destination = output_dir
    destination.mkdir(parents=True, exist_ok=True)
    (destination / configuration.EIGENVECTORS_DIR).mkdir(
        parents=True, exist_ok=True
    )
    (destination / configuration.SURFACES_DIR).mkdir(
        parents=True, exist_ok=True
    )
    (destination / configuration.TEMP_DIR).mkdir(parents=True, exist_ok=True)
    return destination


def export_results(
    destination: Path,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray = None,
    distances: np.ndarray = None,
):
    """
    Writes the BrainPrint analysis results to CSV files.

    Parameters
    ----------
    destination : Path
        Eigenvalues CSV file destination
    eigenvalues : np.ndarray
        Eigenvalues
    eigenvectors : np.ndarray, optional
        Eigenvectors, by default None
    distances : np.ndarray, optional
        Distances, by default None
    """
    df = pd.DataFrame(eigenvalues).sort_index(axis=1)
    ev_indices = [f"ev{i}" for i in range(len(df) - 2)]
    df.index = ["area", "volume"] + ev_indices
    df.to_csv(destination, index=True, na_rep="NaN")

    if eigenvectors is not None:
        eigenvectors_dir = destination.parent / configuration.EIGENVECTORS_DIR
        for key, value in eigenvectors.items():
            suffix = configuration.EIGENVECTORS_SUFFIX_TEMPLATE.format(key=key)
            name = destination.with_suffix(suffix).name
            vectors_destination = eigenvectors_dir / name
            pd.DataFrame(value).to_csv(
                vectors_destination,
                index=True,
                na_rep="NaN",
            )

    if distances is not None:
        distances_destination = destination.with_suffix(".asymmetry.csv")
        pd.DataFrame([distances]).to_csv(
            distances_destination,
            index=False,
            na_rep="NaN",
        )


def surf_to_vtk(source: Path, destination: Path) -> Path:
    """
    Converted a FreeSurfer *.surf* file to *.vtk*.

    Parameters
    ----------
    source : Path
        FreeSurfer *.surf* file
    destination : Path
        Equivalent *.vtk* file

    Returns
    -------
    Path
        Resulting *.vtk* file
    """
    surface = read_geometry(source)
    TriaIO.export_vtk(TriaMesh(v=surface[0], t=surface[1]), destination)
    return destination
