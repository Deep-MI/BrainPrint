"""
BrainPrint analysis CLI.
"""
from brainprint import run_brainprint

from cli.parser import parse_options


def main():
    options = parse_options()
    if options is not None:
        return run_brainprint(**options)
