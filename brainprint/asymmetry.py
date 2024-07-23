"""
Contains asymmetry estimation functionality.
"""
import numpy as np
from lapy import shapedna


def compute_asymmetry(
    eigenvalues, distance: str = "euc", skip_cortex: bool = False
) -> dict[str, float]:
    """
    Compute lateral shape distances from BrainPrint analysis results.

    Parameters
    ----------
    eigenvalues : _type_
        BrainPrint analysis results.
    distance : str, optional
        ShapeDNA distance, by default "euc".
    skip_cortex : bool, optional
        Whether to skip white matter and pial surfaces, by default False.

    Returns
    -------
    dict[str, float]
        {left_label}_{right_label}, distance.
    """

    structures_left_right = [
        ("Left-Lateral-Ventricle", "Right-Lateral-Ventricle"),
        ("Left-Cerebellum", "Right-Cerebellum"),
        ("Left-Thalamus-Proper", "Right-Thalamus-Proper"),
        ("Left-Caudate", "Right-Caudate"),
        ("Left-Putamen", "Right-Putamen"),
        ("Left-Pallidum", "Right-Pallidum"),
        ("Left-Hippocampus", "Right-Hippocampus"),
        ("Left-Amygdala", "Right-Amygdala"),
        ("Left-Accumbens-area", "Right-Accumbens-area"),
        ("Left-VentralDC", "Right-VentralDC"),
    ]

    cortex_2d_left_right = [
        ("lh-white-2d", "rh-white-2d"),
        ("lh-pial-2d", "rh-pial-2d"),
    ]

    structures = structures_left_right
    if not skip_cortex:
        structures += cortex_2d_left_right

    distances = dict()
    for left_label, right_label in structures:
        left_eigenvalues, right_eigenvalues = (
            eigenvalues[left_label][2:],
            eigenvalues[right_label][2:],
        )
        has_nan = np.isnan(left_eigenvalues).any() or np.isnan(right_eigenvalues).any()
        key = f"{left_label}_{right_label}"
        if has_nan:
            message = (
                f"NaNs found for {left_label} or {right_label}, "
                "skipping asymmetry computation..."
            )
            print(message)
            distances[key] = np.nan
        else:
            distances[key] = shapedna.compute_distance(
                left_eigenvalues,
                right_eigenvalues,
                dist=distance,
            )
    return distances
