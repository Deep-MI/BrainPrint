"""
Utilities for the :mod:`brainprint` module.
"""
import os
import shlex
import subprocess
from pathlib import Path
from typing import Any, Dict

from brainprint import configuration, messages

FREESURFER_TEST_COMMAND: str = "mri_binarize -version"
ASEG_LABELS = {
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
CORTICAL_LABELS = {
    "lh-white-2d": "lh.white",
    "rh-white-2d": "rh.white",
    "lh-pial-2d": "lh.pial",
    "rh-pial-2d": "rh.pial",
}

EXECUTION_DEFAULTS = {
    "bcond": 1,
    "lump": False,
    "aniso": None,
    "aniso_smooth": 10,
    "distance": "euc",
}


def validate_environment() -> None:
    """
    Checks whether required environment variables are set.
    """
    if not os.getenv("FREESURFER_HOME"):
        raise RuntimeError(messages.NO_FREESURFER_HOME)


def test_freesurfer() -> None:
    try:
        run_shell_command(FREESURFER_TEST_COMMAND, "mri_binarize failed.")
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


def create_output_paths(subject_dir: Path, options: Dict[str, Any]) -> None:
    try:
        destination = Path(options["outdir"])
    except (KeyError, ValueError, TypeError):
        destination = Path(subject_dir) / configuration.BRAINPRINT_RESULTS_DIR
    destination.mkdir(parents=True, exist_ok=True)
    eigenvectors_path = destination / configuration.EIGENVECTORS_DIR
    surfaces_path = destination / configuration.SURFACES_DIR
    temp_path = destination / configuration.TEMP_DIR
    eigenvectors_path.mkdir(parents=True, exist_ok=True)
    surfaces_path.mkdir(parents=True, exist_ok=True)
    temp_path.mkdir(parents=True, exist_ok=True)
    return destination
