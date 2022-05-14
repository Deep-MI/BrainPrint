"""
String messages for the :mod:`brainprint` package.
"""
RETURN_VALUES: str = """Returning matrices for eigenvalues, eigenvectors, and (optionally) distances.
The eigenvalue matrix contains area and volume as first two rows."""
NO_FREESURFER_HOME: str = "FreeSurfer root directory must be set as the $FREESURFER_HOME environment variable!"
NO_FREESURFER_BINARIES: str = "Failed to run FreeSurfer command, please check the required binaries are included in your $PATH."
MISSING_SUBJECT_DIRECTORY: str = (
    "FreeSurfer results directory at {path} does not exist!"
)
