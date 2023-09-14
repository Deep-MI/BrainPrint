from brainprint import Brainprint
import pytest
from brainprint.surfaces import create_surfaces
import numpy as np 

from lapy import TriaMesh, shapedna
from pathlib import Path

from brainprint.brainprint import compute_surface_brainprint, compute_brainprint, run_brainprint


from brainprint.utils.utils import (
    create_output_paths,
    export_brainprint_results,
    test_freesurfer,
    validate_environment,
    validate_subject_dir,
)

'''
In order to run the tests, please export the directory of freesurfer in your virtual environment
export FREESURFER_HOME=/groups/ag-reuter/software-centos/fs72
source $FREESURFER_HOME/SetUpFreeSurfer.sh 
'''

subjects_dir = "/home/ashrafo/brainprint_test_data/subjects"
subject_id = "bert"

# bp = Brainprint(subjects_dir=subjects_dir, asymmetry=True, keep_eigenvectors=True)
# results = bp.run(subject_id=subject_id)
# results

# Create a fixture for a sample subjects_dir
@pytest.fixture
def sample_subjects_dir():
    # Use a temporary directory for testing, replace this your local subject directory
    subjects_dir = "/home/ashrafo/brainprint_test_data/subjects"
    return subjects_dir

@pytest.fixture
def tria_mesh_fixture():
    """
    fixture is a method to parse parameters to the class
    only once so that it is not required in each test case
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

    This test case validates the initialization of the Brainprint class by creating
    an instance and checking the values of its attributes.

    Parameters:
    sample_subjects_dir (str): The path to the sample subjects directory.

    Raises:
    AssertionError: If the test fails due to incorrect attribute initialization.

    Note:
    - This test assumes that the Brainprint class is correctly implemented and
      available in the test environment.
    - The test checks if the attributes of the Brainprint instance are initialized
      to the expected values.

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
    for key , value in result.items():
        assert isinstance(value, Path)


def test_apply_eigenvalues_options(tria_mesh_fixture):
    """
    Test the apply_eigenvalues_options function.

    This test case validates the behavior of the apply_eigenvalues_options function
    by applying eigenvalues normalization and checking the result.

    Parameters:
    tria_mesh_fixture: A fixture providing a triangular mesh for testing.

    Raises:
    AssertionError: If the test fails due to unexpected eigenvalues normalization results.

    Note:
    - This test assumes that the function `apply_eigenvalues_options` is correctly
      implemented and available in the test environment.
    - The 'norm' variable specifies the eigenvalues normalization method, which can
      be customized for different test scenarios.
    - The test checks if the result 'eigenvalues' is None, indicating successful
      eigenvalues normalization.

    """
    norm = "none"

    eigenvalues = shapedna.normalize_ev(
        geom=tria_mesh_fixture,
        evals=np.array([10,2,33]),
        method=norm,
    )
    assert eigenvalues == None 



def test_compute_surface_brainprint():

    """
    Test the compute_surface_brainprint function.

    This test case validates the behavior of the compute_surface_brainprint function
    by providing it with a sample VTK path and checking the types of its return values.

    Raises:
    AssertionError: If the test fails due to unexpected return types.

    Note:
    - This test assumes that the function `compute_surface_brainprint` is correctly
      implemented and available in the test environment.
    - The 'path' variable should be replaced with the actual path to a VTK file for
      meaningful testing.
    - The test checks that the result is a tuple, and if so, unpacks it into
      'eigenvalues' and 'eigenvectors' and checks their types.

    """
    path = "/home/ashrafo/LaPy/data/cubeTria.vtk" 
    # This path must be replace with the actival .vtk path
    result = compute_surface_brainprint(path, num = 50)
    
    # Assert that the result is a tuple
    assert isinstance(result, tuple)

    # If it's a tuple, unpack it into eigenvalues and eigenvectors
    eigenvalues, eigenvectors = result

    # Assert the types of eigenvalues and eigenvectors
    assert isinstance(eigenvalues, np.ndarray)
    assert isinstance(eigenvectors, (np.ndarray, type(None)))



def test_compute_brainprint(sample_subjects_dir):
    """
    Test the compute_brainprint function.

    This test case validates the behavior of the compute_brainprint function
    by providing it with sample data and checking the types of its return values.

    Parameters:
    sample_subjects_dir (str): The path to the sample subjects directory.

    Raises:
    AssertionError: If the test fails due to unexpected return types.

    Note:
    This test assumes that the functions `validate_subject_dir`, `create_output_paths`,
    `create_surfaces`, and `compute_brainprint` are correctly implemented and available
    in the test environment.

    """
    subject_id = "bert"
    subject_dir = validate_subject_dir(sample_subjects_dir, subject_id)
    destination = create_output_paths(subject_dir=subject_dir,destination=None)
    surfaces = create_surfaces(subject_dir, destination, skip_cortex=False)
    result = compute_brainprint(surfaces)
    eigenvalues, eigenvectors = result
    assert isinstance(result, tuple)
    assert isinstance(eigenvalues, dict)
    assert eigenvectors is None or isinstance(eigenvectors, dict)



def test_run_brainprint(sample_subjects_dir):
    """
    Test the run_brainprint function.

    This test case validates the behavior of the run_brainprint function by running it
    with sample data and checking the properties of the results, including the types of
    the returned values and the structure of the eigenvalue matrix.

    Parameters:
    sample_subjects_dir (str): The path to the sample subjects directory.

    Raises:
    AssertionError: If the test fails due to unexpected return types or eigenvalue matrix properties.

    Note:
    - This test assumes that the run_brainprint function is correctly implemented and
      available in the test environment.
    - The test checks the following:
      - The result is a tuple.
      - 'eigenvalues' is a dictionary.
      - 'eigenvectors' is either None or a dictionary.
      - 'distances' is either None or a dictionary.
      - If 'eigenvalues' is not None and the subject is found in it, it further checks
        that the eigenvalue matrix contains at least two rows and that the values in
        the first two rows are assumed to be non-negative.

    """
    subject_id = "bert"
    result = run_brainprint(subjects_dir=sample_subjects_dir, subject_id=subject_id)
    eigenvalues, eigenvectors, distances = result 
    assert isinstance(result, tuple)
    assert isinstance(eigenvalues, dict)
    assert  eigenvectors is None or isinstance(eigenvectors, dict)
    assert  distances is None or isinstance(eigenvectors, dict)

    # Check if "area" and "volume" are the first two rows in the eigenvalue matrix
    if eigenvalues is not None and subject_id in eigenvalues:
        eigenvalue_matrix = eigenvalues[subject_id]
        assert eigenvalue_matrix.shape[0] >= 2  # Ensure there are at least two rows

        # Check the values of the first two rows are non-zero
        assert np.all(eigenvalue_matrix[:2] >= 0)  # Assuming "area" and "volume" are positive values







