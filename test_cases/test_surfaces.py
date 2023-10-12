
from pathlib import Path


import pytest
from lapy import TriaMesh

# from brainprint.utils.utils import run_shell_command
from brainprint.surfaces import (
    create_aseg_surface,
    create_cortical_surfaces,
    read_vtk,
)


# Create a fixture for a sample subjects_dir
@pytest.fixture
def sample_subjects_dir():
    # Use a temporary directory for testing, replace this your local subject directory
    subject_dir = "../../brainprint_test_data/bert"
    return subject_dir


# Create a fixture for a sample subjects_dir
@pytest.fixture
def sample_destination_dir():
    # Use a temporary directory for testing, replace this your local subject directory
    destination = "../../brainprint_test_data/destination"
    return destination


def test_create_aseg_surfaces(sample_subjects_dir, sample_destination_dir):
    """
    Test the create_aseg_surfaces function.

    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.
    sample_destination_dir (str): Path to the sample destination directory.

    Raises:
    AssertionError: If the test fails due to unexpected results.

    Note:
    - Assumes the `create_aseg_surface` function is correctly implemented.
    - Checks the result for non-None, path type, and existence of the result file.
    - Verifies that the result file name matches the expected .vtk file name.
    """

    subject_dir = Path(sample_subjects_dir)
    destination = Path(sample_destination_dir)
    indices = ["label1", "label2"]
    result = create_aseg_surface(subject_dir, destination, indices)

    assert result is not None, "The result is not None"
    assert isinstance(result, Path), "The result is not a path"
    assert result.exists(), "The result file does not exist"

    expected_file_name = "aseg.final.label1_label2.vtk"
    assert result.name == expected_file_name, "The result file does not match .vtk file"


def test_create_cortical_surfaces(sample_subjects_dir, sample_destination_dir):
    """
    Test the create_cortical_surfaces function.

    Parameters:
    sample_subjects_dir (str): Path to the sample subjects directory.
    sample_destination_dir (str): Path to the sample destination directory.

    Raises:
    AssertionError: If the test fails due to unexpected results.

    Note:
    - Assumes the `create_cortical_surfaces` function is correctly implemented.
    - Validates the expected dictionary structure with label names as keys and Path objects.
    - Verifies specific key-value pairs in the result.
    """
    subject_dir = Path(sample_subjects_dir)
    destination = Path(sample_destination_dir)
    # Call the function
    result = create_cortical_surfaces(subject_dir, destination)

    assert isinstance(result, dict)
    assert all(isinstance(value, Path) for value in result.values())
    assert "lh-white-2d" in result
    assert result["lh-white-2d"] == destination / "surfaces" / "lh.white.vtk"
    assert "rh-white-2d" in result
    assert result["rh-white-2d"] == destination / "surfaces" / "rh.white.vtk"
    assert "lh-pial-2d" in result
    assert result["lh-pial-2d"] == destination / "surfaces" / "lh.pial.vtk"
    assert "rh-pial-2d" in result
    assert result["rh-pial-2d"] == destination / "surfaces" / "rh.pial.vtk"


def test_read_vtk():
    """
    Test the read_vtk function with a sample VTK file.

    Raises:
    AssertionError: If the test fails due to unexpected result type.

    Note: Assumes `read_vtk` is correctly implemented and validates TriaMesh result type.
    """
    sample_vtk_file = ("../../brainprint_test_data/destination/surfaces/aseg.final.label1_label2.vtk")

    # Call the function with the sample VTK file
    vtk_path = Path(sample_vtk_file)
    triangular_mesh = read_vtk(vtk_path)

    # Assert that the result is an instance of TriaMesh
    assert isinstance(triangular_mesh, TriaMesh)


def test_surf_to_vtk(sample_subjects_dir, sample_destination_dir):
    subject_dir = Path(sample_subjects_dir)
    sample_destination_dir = Path(sample_destination_dir)
    try:
        trimesh = TriaMesh.read_fssurf(subject_dir)
        if trimesh:
            trimesh.write_vtk(sample_destination_dir)
        else:
            print("Failed to read .surf file")
    except Exception as e:
        print(f"An error occurred: {e}")
