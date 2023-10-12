from pathlib import Path

import numpy as np
import pytest
from lapy import TriaMesh, shapedna

from brainprint import Brainprint
from brainprint.brainprint import (
    compute_brainprint,
    compute_surface_brainprint,
    run_brainprint,
)
from brainprint.surfaces import create_surfaces
from brainprint.utils.utils import create_output_paths, validate_subject_dir

"""
Don't forget to source Freesurfer
export FREESURFER_HOME=/groups/ag-reuter/software-centos/fs72
source $FREESURFER_HOME/SetUpFreeSurfer.sh 
"""


# Create a fixture for a sample subjects_dir
@pytest.fixture
def sample_subjects_dir():
    # Use a temporary directory for testing, replace this your local subject directory
    subjects_dir = "../../brainprint_test_data/subjects"
    return subjects_dir


@pytest.fixture
def tria_mesh_fixture():
    """
    Create a triangular mesh fixture with predefined points and triangles.

    Returns:
    TriaMesh: An instance of the TriaMesh class with predefined data.
    """
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [0, 1, 0],
            [1, 1, 0],
            [1, 0, 0],
            [0, 0, 1],
            [0, 1, 1],
            [1, 1, 1],
            [1, 0, 1],
        ]
    )
    trias = np.array(
        [
            [0, 1, 2],
            [2, 3, 0],
            [4, 5, 6],
            [6, 7, 4],
            [0, 4, 7],
            [7, 3, 0],
            [0, 4, 5],
            [5, 1, 0],
            [1, 5, 6],
            [6, 2, 1],
            [3, 7, 6],
            [6, 2, 3],
        ]
    )
    return TriaMesh(points, trias)


# Test the initialization of the Brainprint class
def test_brainprint_initialization(sample_subjects_dir):
    """
    Test the initialization and run of the Brainprint class.

    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.

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

    # Change subject id if requried
    subject_id = "bert"
    result = brainprint.run(subject_id=subject_id)
    assert isinstance(result, dict)

    # Check if the values in the dict are of type Dict[str, Path]
    for key, value in result.items():
        assert isinstance(value, Path)


def test_apply_eigenvalues_options(tria_mesh_fixture):
    """
    Test the apply_eigenvalues_options function.

    Parameters:
    tria_mesh_fixture: Fixture providing a triangular mesh for testing.

    Raises:
    AssertionError: For unexpected eigenvalues normalization failures.
    Note:
    - Assumes the `apply_eigenvalues_options` function is correctly implemented.
    - The 'norm' variable specifies the eigenvalues normalization method for testing.
    - Test verifies 'eigenvalues' result as None for successful normalization.
    """
    norm = "none"

    eigenvalues = shapedna.normalize_ev(
        geom=tria_mesh_fixture,
        evals=np.array([10, 2, 33]),
        method=norm,
    )
    assert eigenvalues is None


def test_compute_surface_brainprint():
    """
    Test the compute_surface_brainprint function.

    This test validates compute_surface_brainprint with a sample VTK path.

    Raises:
    AssertionError: If the test fails due to unexpected return types.

    Note:
    - Assumes the `compute_surface_brainprint` function is correctly implemented.
    - Replace 'path' with the actual path to a VTK file for meaningful testing.
    - Test checks tuple result, unpacks 'eigenvalues' & 'eigenvectors', verifies types.
    """

    path = "/home/ashrafo/LaPy/data/cubeTria.vtk"
    # This path must be replace with the actival .vtk path
    result = compute_surface_brainprint(path, num=50)
    eigenvalues, eigenvectors = result
    assert isinstance(result, tuple), "Return value is not a tuple"
    assert isinstance(eigenvalues, np.ndarray), "Eigenvalues is not a numpyarray"
    assert len(eigenvalues) == 52, "Eigenvalues has an incorrect length"
    assert eigenvectors is None or isinstance(
        eigenvectors, np.ndarray
    ), "Eigenvectors is not None or a NumPy array"


# def test_run_brainprint(sample_subjects_dir):
#     """
#     Test the run_brainprint function.


#     Parameters:
#     sample_subjects_dir (str): Path to the sample subjects directory.

#     Raises:
#     AssertionError: For unexpected return types or eigenvalue matrix properties.

#     Note:
#     - Assumes the `run_brainprint` function is correctly implemented.
#     - The test checks:
#       - The result is a tuple.
#       - 'eigenvalues' is a dictionary.
#       - 'eigenvectors' is either None or a dictionary.
#       - 'distances' is either None or a dictionary.
#       - If 'eigenvalues' not None and subject found, more eigenvalue matrix checks.
#       - It verifies that the matrix contains at least two rows.
#       - It ensures that the values in the first two rows are non-negative.
#     """
#     subject_id = "bert"
#     result = run_brainprint(subjects_dir=sample_subjects_dir, subject_id=subject_id)
#     eigenvalues, eigenvectors, distances = result
#     assert isinstance(result, tuple), "Return value is not a tuple"
#     assert isinstance(eigenvalues, dict), "Return value is not a dictionary"
#     assert eigenvectors is None or isinstance(
#         eigenvectors, dict
#     ), "Eigenvectors is not None or a NumPy array"
#     assert distances is None or isinstance(
#         eigenvectors, dict
#     ), "Distacnces is not None or a dictionary"

#     # Check if "area" and "volume" are the first two rows in the eigenvalue matrix
#     if eigenvalues is not None and subject_id in eigenvalues:
#         eigenvalue_matrix = eigenvalues[subject_id]
#         assert (
#             eigenvalue_matrix.shape[0] >= 2
#         ), "Eigenvalue matrix has fewer than two rows"

#         # Check the values of the first two rows are non-zero
#         assert np.all(
#             eigenvalue_matrix[:2] >= 0
#         ), "Area and volume values are not non-negative"


def test_compute_brainprint(sample_subjects_dir):
    """
    Test the compute_brainprint function.


    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.

    Raises:
    AssertionError: If the test fails due to unexpected return types.

    Note:
    Assumes validate_subject_dir, create_output_paths, create_surfaces & compute_BP.
    """
    subject_id = "bert"
    subject_dir = validate_subject_dir(sample_subjects_dir, subject_id)
    destination = create_output_paths(subject_dir=subject_dir, destination=None)
    surfaces = create_surfaces(subject_dir, destination, skip_cortex=False)
    result = compute_brainprint(surfaces)
    eigenvalues, eigenvectors = result
    assert isinstance(result, tuple), "result is not a tuple"
    assert isinstance(eigenvalues, dict), "eigenvalues are not dict type"
    assert eigenvectors is None or isinstance(
        eigenvectors, dict
    ), "eigenvectors are not none or dict type"


def test_run_brainprint(sample_subjects_dir):
    """
    Test the run_brainprint function.

    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.

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
    subject_id = "bert"
    result = run_brainprint(subjects_dir=sample_subjects_dir, subject_id=subject_id)
    eigenvalues, eigenvectors, distances = result
    assert isinstance(result, tuple), "result is not tuple"
    assert isinstance(eigenvalues, dict), "eigenvalues are not dict type"
    assert eigenvectors is None or isinstance(
        eigenvectors, dict
    ), "eigenvector is not none or dict type"
    assert distances is None or isinstance(eigenvectors, dict)

    # Check if "area" and "volume" are the first two rows in the eigenvalue matrix
    if eigenvalues is not None and subject_id in eigenvalues:
        eigenvalue_matrix = eigenvalues[subject_id]
        assert eigenvalue_matrix.shape[0] >= 2  # Ensure there are at least two rows

        # Check the values of the first two rows are non-zero
        assert np.all(
            eigenvalue_matrix[:2] >= 0
        )  # Assuming "area" and "volume" are positive values
