import os
from pathlib import Path

import numpy as np
import pytest
from lapy import TriaMesh

from brainprint import Brainprint
from brainprint.brainprint import (
    apply_eigenvalues_options,
    compute_brainprint,
    compute_surface_brainprint,
    run_brainprint,
)
from brainprint.surfaces import create_surfaces
from brainprint.utils.utils import create_output_paths, validate_subject_dir


# Create a fixture for a sample subjects_dir
@pytest.fixture
def sample_subjects_dir():
    # Use a temporary directory for testing
    subjects_dir = os.environ["SUBJECTS_DIR"]
    return subjects_dir


@pytest.fixture
def sample_subject_id():
    # Use a temporary subject id for testing
    subject_id = os.environ["SUBJECT_ID"]
    return subject_id


# Create a fixture for a sample vtk_file
@pytest.fixture
def sample_vtk_file(sample_subjects_dir, sample_subject_id):
    # Use a temporary file for testing
    source = Path(sample_subjects_dir) / sample_subject_id / "surf" / "lh.pial"
    destination = Path(sample_subjects_dir) / sample_subject_id / "surf" / "lh.pial.vtk"
    TriaMesh.read_fssurf(source).write_vtk(str(destination))
    return str(destination)


# Test the initialization of the Brainprint class
def test_brainprint_initialization(sample_subjects_dir, sample_subject_id):
    """
    Test the initialization and run of the Brainprint class.

    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.
    sample_subject_id (str): Sample subject ID.

    Raises:
    AssertionError: If the test fails due to incorrect attribute initialization.

    Note:
    - Assumes Brainprint class is correctly implemented.
    - Checks if Brainprint instance attributes are initialized as expected.
    """
    # Create an instance of Brainprint
    brainprint = Brainprint(sample_subjects_dir)

    # Check if the attributes are initialized correctly
    assert brainprint.subjects_dir == sample_subjects_dir
    assert brainprint.num == 50
    assert brainprint.norm == "none"
    assert not brainprint.skip_cortex
    assert not brainprint.reweight
    assert not brainprint.keep_eigenvectors
    assert not brainprint.asymmetry
    assert brainprint.asymmetry_distance == "euc"
    assert not brainprint.keep_temp
    assert not brainprint.use_cholmod

    #
    result = brainprint.run(sample_subject_id)
    assert isinstance(result, dict)

    # Check if the values in the dict are of type Dict[str, Path]
    for key, value in result.items():
        assert isinstance(value, Path)


def test_apply_eigenvalues_options(sample_vtk_file, norm="none", reweight=False):
    """
    Test the apply_eigenvalues_options function.

    Parameters:
    sample_vtk_file (str): Path to sample vtk file.
    norm (str): eigenvalues normalization method.
    reweight (bool): eigenvalues reweighting.

    Raises:
    AssertionError: For unexpected eigenvalues normalization failures.

    Note:
    - Assumes the `apply_eigenvalues_options` function is correctly implemented.
    - Checks type of 'eigenvalues' for successful normalization.
    """

    tria_mesh = TriaMesh.read_vtk(sample_vtk_file)

    eigenvalues = np.random.rand(50)

    new_eigenvalues = apply_eigenvalues_options(
        eigenvalues, triangular_mesh=tria_mesh, norm=norm, reweight=reweight
    )

    assert isinstance(new_eigenvalues, np.ndarray)


def test_compute_surface_brainprint(sample_vtk_file):
    """
    Test the compute_surface_brainprint function.

    This test validates compute_surface_brainprint with a sample VTK path.

    Parameters:
    sample_vtk_file (str): Path to sample vtk file.

    Raises:
    AssertionError: If the test fails due to unexpected return types.

    Note:
    - Assumes the `compute_surface_brainprint` function is correctly implemented.
    - Test checks tuple result, unpacks 'eigenvalues' & 'eigenvectors', verifies types.
    """

    eigenvalues, eigenvectors = compute_surface_brainprint(sample_vtk_file, num=50)
    assert isinstance(eigenvalues, np.ndarray), "Eigenvalues is not a numpyarray"
    assert len(eigenvalues) == 52, "Eigenvalues has an incorrect length"
    assert eigenvectors is None or isinstance(
        eigenvectors, np.ndarray
    ), "Eigenvectors is not None or a NumPy array"


def test_compute_brainprint(sample_subjects_dir, sample_subject_id):
    """
    Test the compute_brainprint function.

    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.
    sample_subject_id (str): Sample subject ID.

    Raises:
    AssertionError: If the test fails due to unexpected return types.

    Note:
    Assumes validate_subject_dir, create_output_paths, create_surfaces & compute_BP.
    """

    subject_dir = validate_subject_dir(sample_subjects_dir, sample_subject_id)
    destination = create_output_paths(subject_dir=subject_dir, destination=None)
    surfaces = create_surfaces(subject_dir, destination, skip_cortex=False)
    result = compute_brainprint(surfaces)
    eigenvalues, eigenvectors = result
    assert isinstance(result, tuple), "result is not a tuple"
    assert isinstance(eigenvalues, dict), "eigenvalues are not dict type"
    assert eigenvectors is None or isinstance(
        eigenvectors, dict
    ), "eigenvectors are not none or dict type"


def test_run_brainprint(sample_subjects_dir, sample_subject_id):
    """
    Test the run_brainprint function.

    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.
    sample_subject_id (str): Sample subject ID.

    Raises:
    AssertionError: For unexpected return types or eigenvalue matrix properties.

    Note:
    - Assumes run_brainprint is correctly implemented and available.
    - Checks:
    - Result is a tuple.
    - 'eigenvalues' is a dict.
    - 'eigenvectors' is None or a dict.
    - 'distances' is None or a dict.
    - If 'eigenvalues' not None and subject found, further checks eigenvalue matrix.
    """

    result = run_brainprint(sample_subjects_dir, sample_subject_id)
    eigenvalues, eigenvectors, distances = result

    assert isinstance(result, tuple), "result is not tuple"
    assert isinstance(eigenvalues, dict), "eigenvalues are not dict type"
    assert eigenvectors is None or isinstance(
        eigenvectors, dict
    ), "eigenvector is not none or dict type"
    assert distances is None or isinstance(eigenvectors, dict)

    # Check if "area" and "volume" are the first two rows in the eigenvalue matrix
    if eigenvalues is not None and sample_subject_id in eigenvalues:
        eigenvalue_matrix = eigenvalues[sample_subject_id]
        assert eigenvalue_matrix.shape[0] >= 2  # Ensure there are at least two rows

        # Check the values of the first two rows are non-zero
        assert np.all(
            eigenvalue_matrix[:2] >= 0
        )  # Assuming "area" and "volume" are positive values
