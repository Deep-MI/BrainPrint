"""
Utility functions for the :mod:`brainprint.cli` module.
"""
import help_text


def get_help(print_help: bool = True):
    """
    Returns a detailed help message.
    """
    if print_help:
        print(help_text.HELPTEXT)
    else:
        return help_text.HELPTEXT
