"""
Utility module holding surface generation related functions.
"""
import uuid
import nibabel as nb
import numpy as np
from pathlib import Path

from lapy import TriaMesh

from skimage.measure import marching_cubes

def create_aseg_surface(
    subject_dir: Path, destination: Path, indices: list[int]
) -> Path:
    """
    Generate a surface from the aseg and label files.

    Parameters
    ----------
    subject_dir : Path
        Path to the subject's directory.
    destination : Path
        Path to the destination directory where the surface will be saved.
    indices : list[int]
        List of label indices to include in the surface generation.

    Returns
    -------
    Path
        Path to the generated surface in VTK format
    """
    aseg_path = subject_dir / "mri/aseg.mgz"
    temp_name = "temp/aseg.{uid}".format(uid=uuid.uuid4())
    indices_mask = destination / f"{temp_name}.mgz"

    # binarize on selected labels (creates temp indices_mask)
    aseg = nb.load(aseg_path)
    indices_num = [ int(x) for x in indices ]
    aseg_data_bin = np.isin(aseg.get_fdata(), indices_num).astype(np.float32)
    aseg_bin = nb.MGHImage(dataobj=aseg_data_bin, affine=aseg.affine)
    nb.save(img=aseg_bin, filename=indices_mask)

    # runs marching cube to extract surface
    vertices, trias, _, _ = marching_cubes(volume=aseg_data_bin, level=0.5)

    # convert to vtk
    relative_path = "surfaces/aseg.final.{indices}.vtk".format(
        indices="_".join(indices)
    )
    conversion_destination = destination / relative_path
    TriaMesh(v=vertices, t=trias).write_vtk(filename=conversion_destination)

    return conversion_destination


def create_aseg_surfaces(subject_dir: Path, destination: Path) -> dict[str, Path]:
    """
    Create surfaces from FreeSurfer aseg labels.

    Parameters
    ----------
    subject_dir : Path
        Path to the subject's FreeSurfer directory.
    destination : Path
        Path to the destination directory for saving surfaces.

    Returns
    -------
    dict[str, Path]
        Dictionary of label names mapped to corresponding surface Path objects.
    """
    # Define aseg labels

    # combined and individual aseg labels:
    # - Left  Striatum: left  Caudate + Putamen + Accumbens
    # - Right Striatum: right Caudate + Putamen + Accumbens
    # - CorpusCallosum: 5 subregions combined
    # - Cerebellum: brainstem + (left+right) cerebellum WM and GM
    # - Ventricles: (left+right) lat.vent + inf.lat.vent + choroidplexus + 3rdVent + CSF
    # - Lateral-Ventricle: lat.vent + inf.lat.vent + choroidplexus
    # - 3rd-Ventricle: 3rd-Ventricle + CSF

    aseg_labels = {
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
    return {
        label: create_aseg_surface(subject_dir, destination, indices)
        for label, indices in aseg_labels.items()
    }


def create_cortical_surfaces(subject_dir: Path, destination: Path) -> dict[str, Path]:
    """
    Create cortical surfaces from FreeSurfer labels.

    Parameters
    ----------
    subject_dir : Path
        Path to the subject's FreeSurfer directory.
    destination : Path
        Path to the destination directory where the surfaces will be saved.

    Returns
    -------
    dict[str, Path]
        Dictionary mapping label names to associated surface Paths.
    """
    cortical_labels = {
        "lh-white-2d": "lh.white",
        "rh-white-2d": "rh.white",
        "lh-pial-2d": "lh.pial",
        "rh-pial-2d": "rh.pial",
    }
    return {
        label: surf_to_vtk(
            subject_dir / "surf" / name,
            destination / "surfaces" / f"{name}.vtk",
        )
        for label, name in cortical_labels.items()
    }


def create_surfaces(
    subject_dir: Path, destination: Path, skip_cortex: bool = False
) -> dict[str, Path]:
    """
    Create surfaces based on FreeSurfer labels.

    Parameters
    ----------
    subject_dir : Path
        Path to the subject's FreeSurfer directory.
    destination : Path
        Path to the destination directory where the surfaces will be saved.
    skip_cortex : bool, optional
        If True, cortical surfaces will not be created (default is False).

    Returns
    -------
    dict[str, Path]
        Dict mapping label names to the corresponding Path objects of created surfaces.
    """
    surfaces = create_aseg_surfaces(subject_dir, destination)
    if not skip_cortex:
        cortical_surfaces = create_cortical_surfaces(subject_dir, destination)
        surfaces.update(cortical_surfaces)
    return surfaces


def read_vtk(path: Path):
    """
    Read a VTK file and return a triangular mesh.

    Parameters
    ----------
    path : Path
        Path to the VTK file to be read.

    Returns
    -------
    TriaMesh
        A triangular mesh object representing the contents of the VTK file.

    Raises
    ------
    RuntimeError
        If there is an issue reading the VTK file or if the file is empty.
    """
    try:
        triangular_mesh = TriaMesh.read_vtk(path)
    except Exception:
        message = f"Failed to read VTK from the following path: {path}!"
        raise RuntimeError(message) from None
    else:
        if triangular_mesh is None:
            message = f"Failed to read VTK from the following path: {path}!"
            raise RuntimeError(message)
        return triangular_mesh


def surf_to_vtk(source: Path, destination: Path) -> Path:
    """
    Converted a FreeSurfer *.surf* file to *.vtk*.

    Parameters
    ----------
    source : Path
        FreeSurfer *.surf* file.
    destination : Path
        Equivalent *.vtk* file.

    Returns
    -------
    Path
        Resulting *.vtk* file.
    """
    TriaMesh.read_fssurf(source).write_vtk(destination)
    return destination
