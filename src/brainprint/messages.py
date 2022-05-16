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
SURFACE_READ_ERROR: str = (
    "Failed to read {label} VTK from the following path: {path}!"
)
ASYMMETRY_NAN: str = "NaNs found for {left_label} or {right_label}, skipping asymmetry computation..."
MISSING_OUTPUT_BASE: str = (
    "One of *subject_dir* or *output_dir* must be provided!"
)
SHELL_EXECUTION_FAILURE: str = "Failed to execute the following command:\n{command}\nThe following exception was raised:\n{exception}"
SHELL_EXECUTION_RETURN: str = "Execution of the following command:\n{command}\nReturned non-zero exit code!"
