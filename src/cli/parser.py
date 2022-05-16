import argparse
import pathlib
import sys

from cli import help_text


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
        help=help_text.SDIR,
        default=None,
        metavar="<directory>",
        required=True,
        type=pathlib.Path,
    )
    required.add_argument(
        "--sid",
        dest="subject_id",
        help=help_text.SID,
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
        dest="evec",
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
        dest="rwt",
        help=help_text.RWT,
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

    # Output options
    output = parser.add_argument_group(title="Output parameters")
    output.add_argument(
        "--outdir",
        dest="output_dir",
        help=help_text.OUTDIR,
        default=None,
        metavar="<directory>",
        required=False,
        type=pathlib.Path,
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
    elif more_help:
        print(help_text.HELPTEXT)
        sys.exit(0)
    else:
        args = parser.parse_args()

    return vars(args)
