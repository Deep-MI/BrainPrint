"""
Utilities for the :mod:`brainprint` module.
"""
import os
import shlex
import subprocess
from pathlib import Path
from typing import Dict

import numpy as np
import pandas as pd


def validate_environment() -> None:
    """
    Checks whether required environment variables are set.
    """
    if not os.getenv("FREESURFER_HOME"):
        raise RuntimeError(
            "FreeSurfer root directory must be set as the $FREESURFER_HOME "
            "environment variable!"
        )


def test_freesurfer() -> None:
    """
    Tests FreeSurfer binarize are accessible and executable.

    Raises
    ------
    RuntimeError
        Failed to execute test FreeSurfer command
    """
    command = "mri_binarize -version"
    try:
        run_shell_command(command)
    except FileNotFoundError:
        raise RuntimeError(
            "Failed to run FreeSurfer command, please check the required binaries "
            "are included in your $PATH."
        )


def run_shell_command(command: str, verbose: bool = False):
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
    if verbose:
        print(f"Executing command:\t{command}", end="\n")
    args = shlex.split(command)
    try:
        return_code = subprocess.call(args)
    except Exception as e:
        message = (
            "Failed to execute the following command:\n{command}\n"
            "The following exception was raised:\n{exception}".format(
                command=command, exception=e
            )
        )
        print(message)
        raise
    if return_code != 0:
        message = (
            "Execution of the following command:\n{command}\n"
            "Returned non-zero exit code!".format(command=command)
        )
        raise RuntimeError(message)


def validate_subject_dir(subjects_dir: Path, subject_id: str) -> Path:
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
    subject_dir = Path(subjects_dir) / subject_id
    if not subject_dir.is_dir():
        message = "FreeSurfer results directory at {path} does not exist!".format(
            path=subject_dir
        )
        raise FileNotFoundError(message)
    return subject_dir


def resolve_destination(subject_dir: Path, destination: Path = None) -> Path:
    if destination is None:
        return Path(subject_dir) / "brainprint"
    return destination


def create_output_paths(subject_dir: Path = None, destination: Path = None) -> None:
    """
    Creates the output directories in which the BrainPrint analysis derivatives
    will be created. One of *subject_dir* or *destination* must be
    provided.

    Parameters
    ----------
    subject_dir : Path, optional
        If provided, will simply nest results in the provided directory, by
        default None
    destination : Path, optional
        If provided, will use this path as the results root directory, by
        default None

    Raises
    ------
    ValueError
        No *subject_dir* or *destination* provided
    """
    destination = resolve_destination(subject_dir, destination)
    destination.mkdir(parents=True, exist_ok=True)
    (destination / "surfaces").mkdir(parents=True, exist_ok=True)
    (destination / "temp").mkdir(parents=True, exist_ok=True)
    return destination


def export_brainprint_results(
    destination: Path,
    eigenvalues: np.ndarray,
    eigenvectors: np.ndarray = None,
    distances: np.ndarray = None,
) -> Dict[str, Path]:
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
    files = {}
    df = pd.DataFrame(eigenvalues).sort_index(axis=1)
    ev_indices = [f"ev{i}" for i in range(len(df) - 2)]
    df.index = ["area", "volume"] + ev_indices
    df.to_csv(destination, index=True, na_rep="NaN")
    files["eigenvalues"] = destination

    if eigenvectors is not None:
        eigenvectors_dir = destination.parent / "eigenvectors"
        eigenvectors_dir.mkdir(parents=True, exist_ok=True)
        for key, value in eigenvectors.items():
            suffix = ".evecs-{key}.csv".format(key=key)
            name = destination.with_suffix(suffix).name
            vectors_destination = eigenvectors_dir / name
            pd.DataFrame(value).to_csv(
                vectors_destination,
                index=True,
                na_rep="NaN",
            )
        files["eigenvectors"] = eigenvectors_dir

    if distances is not None:
        distances_destination = destination.with_suffix(".asymmetry.csv")
        pd.DataFrame([distances]).to_csv(
            distances_destination,
            index=False,
            na_rep="NaN",
        )
        files["distances"] = distances_destination
    return files
