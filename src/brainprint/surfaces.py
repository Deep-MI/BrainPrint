"""
Utilty module holding surface generation related functions.
"""
import uuid
from pathlib import Path
from typing import Dict, List

from lapy import TriaIO, TriaMesh
from lapy.read_geometry import read_geometry

from brainprint import configuration, messages
from brainprint.utils import run_shell_command


def create_aseg_surface(
    subject_dir: Path, destination: Path, indices: List[int]
) -> Path:
    """
    Creates a surface from the aseg and label files.
    """
    aseg_path = subject_dir / configuration.RELATIVE_ASEG_MGZ_PATH
    norm_path = subject_dir / configuration.RELATIVE_NORM_MGZ_PATH
    temp_name = configuration.TEMP_ASEG_TEMPLATE.format(uid=uuid.uuid4())
    indices_mask = destination / f"{temp_name}.mgz"
    # binarize on selected labels (creates temp indices_mask)
    # always binarize first, otherwise pretess may scale aseg if labels are
    # larger than 255 (e.g. aseg+aparc, bug in mri_pretess?)
    binarize_template = configuration.COMMAND_TEMPLATES["mri_binarize"]
    binarize_command = binarize_template.format(
        source=aseg_path, match=" ".join(indices), destination=indices_mask
    )
    run_shell_command(binarize_command)

    label_value = "1"
    # if norm exist, fix label (pretess)
    if norm_path.is_file():
        pretess_template = configuration.COMMAND_TEMPLATES["mri_pretess"]
        pretess_command = pretess_template.format(
            source=indices_mask,
            label_value=label_value,
            norm_path=norm_path,
            destination=indices_mask,
        )
        run_shell_command(pretess_command)

    # runs marching cube to extract surface
    surface_name = configuration.SURFACE_NAME_TEMPLATE.format(name=temp_name)
    surface_path = destination / surface_name
    extraction_template = configuration.COMMAND_TEMPLATES["mri_mc"]
    extraction_command = extraction_template.format(
        source=indices_mask, label_value=label_value, destination=surface_path
    )
    run_shell_command(extraction_command)

    # convert to vtk
    relative_path = configuration.RELATIVE_SURFACE_TEMPLATE.format(
        indices="_".join(indices)
    )
    conversion_destination = destination / relative_path
    conversion_template = configuration.COMMAND_TEMPLATES["mris_convert"]
    conversion_command = conversion_template.format(
        source=surface_path, destination=conversion_destination
    )
    run_shell_command(conversion_command)

    return conversion_destination


def create_aseg_surfaces(
    subject_dir: Path, destination: Path
) -> Dict[str, Path]:
    return {
        label: create_aseg_surface(subject_dir, destination, indices)
        for label, indices in configuration.ASEG_LABELS.items()
    }


def create_cortical_surfaces(
    subject_dir: Path, destination: Path
) -> Dict[str, Path]:
    return {
        label: surf_to_vtk(
            subject_dir / "surf" / name,
            destination / "surfaces" / f"{name}.vtk",
        )
        for label, name in configuration.CORTICAL_LABELS.items()
    }


def create_surfaces(
    subject_dir: Path, destination: Path, skip_cortex: bool = False
) -> Dict[str, Path]:
    surfaces = create_aseg_surfaces(subject_dir, destination)
    if not skip_cortex:
        cortical_surfaces = create_cortical_surfaces(subject_dir, destination)
        surfaces.update(cortical_surfaces)
    return surfaces


def read_vtk(path: Path):
    try:
        triangular_mesh = TriaIO.import_vtk(path)
    except Exception:
        message = messages.SURFACE_READ_ERROR.format(path=path)
        raise RuntimeError(message)
    else:
        if triangular_mesh is None:
            message = messages.SURFACE_READ_ERROR.format(path=path)
            raise RuntimeError(message)
        return triangular_mesh


def surf_to_vtk(source: Path, destination: Path) -> Path:
    """
    Converted a FreeSurfer *.surf* file to *.vtk*.

    Parameters
    ----------
    source : Path
        FreeSurfer *.surf* file
    destination : Path
        Equivalent *.vtk* file

    Returns
    -------
    Path
        Resulting *.vtk* file
    """
    surface = read_geometry(source)
    TriaIO.export_vtk(TriaMesh(v=surface[0], t=surface[1]), destination)
    return destination
