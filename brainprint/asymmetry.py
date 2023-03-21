"""
Contains asymmetry estimation functionality.
"""
from typing import Dict

import numpy as np
from lapy import ShapeDNA

import configuration, messages


def compute_asymmetry(
    eigenvalues, distance: str = "euc", skip_cortex: bool = False
) -> Dict[str, float]:
    """
    Computes lateral shape distances from BrainPrint analysis results.

    Parameters
    ----------
    eigenvalues : _type_
        BrainPrint analysis results
    distance : str, optional
        ShapeDNA distance, by default "euc"
    skip_cortex : bool, optional
        Whether to skip white matter and pial surfaces, by default False

    Returns
    -------
    Dict[str, float]
        {left_label}_{right_label}, distance
    """
    structures = configuration.LATERAL_STRUCTURES
    if not skip_cortex:
        structures += configuration.LATERAL_STRUCTURES_2D

    distances = dict()
    for left_label, right_label in structures:
        left_eigenvalues, right_eigenvalues = (
            eigenvalues[left_label][2:],
            eigenvalues[right_label][2:],
        )
        has_nan = (
            np.isnan(left_eigenvalues).any()
            or np.isnan(right_eigenvalues).any()
        )
        key = f"{left_label}_{right_label}"
        if has_nan:
            message = messages.ASYMMETRY_NAN.format(
                left_label=left_label, right_label=right_label
            )
            print(message)
            distances[key] = np.nan
        else:
            distances[key] = ShapeDNA.compute_distance(
                left_eigenvalues,
                right_eigenvalues,
                distance=distance,
            )
    return distances
