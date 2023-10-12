from typing import Dict

import numpy as np
import pytest
from lapy import shapedna

from brainprint import asymmetry
from brainprint.asymmetry import compute_asymmetry
from brainprint.brainprint import run_brainprint


@pytest.fixture
def sample_subjects_dir():
    # Use a temporary directory for testing, replace this your local subject directory
    subjects_dir = "../../brainprint_test_data/subjects"
    return subjects_dir


def test_run_brainprint(sample_subjects_dir):
    """
    Test the run_brainprint function with sample data.

    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.

    Raises:
    AssertionError: If the test fails due to unexpected results.

    Note: Assumes the `run_brainprint` function is correctly implemented and checks result types and eigenvalue matrix properties.
    """
    subject_id = "bert"
    result = run_brainprint(subjects_dir=sample_subjects_dir, subject_id=subject_id)
    eigenvalues, eigenvectors, distances = result

    # Computed eigen values from run_brainprint
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
