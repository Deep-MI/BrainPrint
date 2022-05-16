"""
BrainPrint analysis CLI.
"""
from brainprint import run_brainprint

from cli.parser import _parse_options


def main():
    options = _parse_options()
    return run_brainprint(**options)
