import os

import pytest


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


def test_files_exist_in_directory(sample_subjects_dir, sample_subject_id):
    subject_directory = os.path.join(sample_subjects_dir, sample_subject_id)
    output_directory = os.path.join(subject_directory, "brainprint")
    output_files = [
        sample_subject_id + ".brainprint.csv"
    ]  # replace with your expected files

    surface_directory = os.path.join(output_directory, "surfaces")
    surface_files = [
        "aseg.final.10.vtk",
        "aseg.final.49.vtk",
        "aseg.final.11.vtk",
        "aseg.final.12.vtk",
        "aseg.final.50.vtk",
        "aseg.final.13.vtk",
        "aseg.final.51.vtk",
        "aseg.final.14_24.vtk",
        "aseg.final.52.vtk",
        "aseg.final.15.vtk",
        "aseg.final.53.vtk",
        "aseg.final.16.vtk",
        "aseg.final.54.vtk",
        "aseg.final.17.vtk",
        "aseg.final.58.vtk",
        "aseg.final.18.vtk",
        "aseg.final.60.vtk",
        "aseg.final.251_252_253_254_255.vtk",
        "aseg.final.7_8_16_46_47.vtk",
        "aseg.final.26.vtk",
        "aseg.final.7_8.vtk",
        "aseg.final.28.vtk",
        "aseg.final.43_44_63.vtk",
        "lh.pial.vtk",
        "lh.white.vtk",
        "aseg.final.4_5_31.vtk",
        "rh.pial.vtk",
        "aseg.final.46_47.vtk",
        "rh.white.vtk",
    ]

    for file in output_files:
        assert os.path.isfile(
            os.path.join(output_directory, file)
        ), f"{file} does not exist in the directory"

    for file in surface_files:
        assert os.path.isfile(
            os.path.join(surface_directory, file)
        ), f"{file} does not exist in the directory"
