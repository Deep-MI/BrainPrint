import pytest

from brainprint.asymmetry import compute_asymmetry
from brainprint.brainprint import run_brainprint


@pytest.fixture
def sample_subjects_dir():
    # Use a temporary directory for testing
    subjects_dir = "data"
    return subjects_dir

@pytest.fixture
def sample_subject_id():
    # Use a temporary subject id for testing
    subject_id = "bert"
    return subject_id

def test_compute_asymmetry(sample_subjects_dir, sample_subject_id):
    """
    Test the compute_asymmetry function with sample data.

    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.
    sample_subject_id (str): Sampple subject id.

    Raises:
    AssertionError: If the test fails due to unexpected results.

    Note:
    Assumes run_brainprint checks result types and eigenvalue matrix properties.
    """

    # Run brainprint
    eigenvalues, eigenvectors, distances = run_brainprint(subjects_dir=sample_subjects_dir, subject_id=sample_subject_id)

    # Compute asymmetry
    distances = compute_asymmetry(eigenvalues, distance="euc", skip_cortex=False)

    # Assert that distances is a dictionary
    assert isinstance(
        distances, dict
    ), "Distances is not a dictionary with string keys and float values"
    assert all(
        value >= 0 for value in distances.values()
    ), "Negative distance values found"
    distances_with_cortex = compute_asymmetry(
        eigenvalues, distance="euc", skip_cortex=False
    )
    distances_without_cortex = compute_asymmetry(
        eigenvalues, distance="euc", skip_cortex=True
    )
    # Assert that the results differ when skip_cortex is True and False
    assert (
        distances_with_cortex != distances_without_cortex
    ), "Distances are the same with and without cortex"
