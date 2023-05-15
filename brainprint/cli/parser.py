import argparse
import pathlib
import sys

from . import help_text


def parse_options():
    """
    Initiates the option parser and return the parsed object.
    """
    parser = argparse.ArgumentParser(
        description=help_text.CLI_DESCRIPTION, add_help=False
    )

    # Required arguments
    required = parser.add_argument_group(title="Required arguments")
    required.add_argument(
        "--sdir",
        dest="subjects_dir",
        help=help_text.SUBJECTS_DIR,
        default=None,
        metavar="<directory>",
        required=True,
        type=pathlib.Path,
    )
    required.add_argument(
        "--sid",
        dest="subject_id",
        help=help_text.SUBJECT_ID,
        default=None,
        metavar="<string>",
        required=True,
    )

    # Optional arguments
    optional = parser.add_argument_group(title="Processing directives")
    optional.add_argument(
        "--num",
        dest="num",
        help=help_text.NUM,
        default=50,
        metavar="<num>",
        type=int,
        required=False,
    )
    optional.add_argument(
        "--evec",
        dest="keep_eigenvectors",
        help=help_text.EVEC,
        default=False,
        action="store_true",
        required=False,
    )
    optional.add_argument(
        "--skipcortex",
        dest="skip_cortex",
        help=help_text.SKIP_CORTEX,
        default=False,
        action="store_true",
        required=False,
    )
    optional.add_argument(
        "--norm",
        dest="norm",
        help=help_text.NORM,
        default="none",
        metavar="<surface|volume|geometry|none>",
        choices=["surface", "volume", "geometry", "none"],
        required=False,
    )
    optional.add_argument(
        "--reweight",
        dest="reweight",
        help=help_text.REWEIGHT,
        default=False,
        action="store_true",
        required=False,
    )
    optional.add_argument(
        "--asymmetry",
        dest="asymmetry",
        help=help_text.ASYM,
        default=False,
        action="store_true",
        required=False,
    )
    optional.add_argument(
        "--asym-distance",
        dest="asymmetry_distance",
        help=help_text.ASYM_DISTANCE,
        default="euc",
        metavar="<euc>",
        choices=["euc"],
        required=False,
    )
    optional.add_argument(
        "--cholmod",
        dest="cholmod",
        help=help_text.CHOLMOD,
        default=False,
        action="store_true",
        required=False,
    )

    # Output options
    output = parser.add_argument_group(title="Output parameters")
    output.add_argument(
        "--outdir",
        dest="destination",
        help=help_text.OUTPUT_DIRECTORY,
        default=None,
        metavar="<directory>",
        required=False,
        type=pathlib.Path,
    )
    output.add_argument(
        "--keep-temp",
        dest="keep_temp",
        help=help_text.KEEP_TEMP,
        default=False,
        action="store_true",
        required=False,
    )

    # Help
    help = parser.add_argument_group(title="Getting help")
    help.add_argument("--help", help=help_text.HELP, action="help")
    help.add_argument(
        "--more-help",
        dest="more_help",
        help=help_text.MORE_HELP,
        default=False,
        action="store_true",
        required=False,
    )

    no_input = len(sys.argv) == 1
    more_help = "--more-help" in sys.argv
    if no_input:
        args = parser.parse_args(["--help"])
        return
    elif more_help:
        print(help_text.HELPTEXT)
        return
    else:
        args = vars(parser.parse_args())
        del args["more_help"]

    return args
