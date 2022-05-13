import argparse
import sys

from cli import help_text
from cli.utils import get_help


def _parse_options():
    """
    Initiates the option parser and return the parsed object.
    """

    # setup parser
    parser = argparse.ArgumentParser(
        description=help_text.CLI_DESCRIPTION, add_help=False
    )

    # required arguments
    required = parser.add_argument_group(title="Required arguments")

    required.add_argument(
        "--sid",
        dest="sid",
        help=help_text.SID,
        default=None,
        metavar="<string>",
    )
    required.add_argument(
        "--sdir",
        dest="sdir",
        help=help_text.SDIR,
        default=None,
        metavar="<directory>",
    )

    # optional arguments
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
        dest="skipcortex",
        help=help_text.SKIPCORTEX,
        default=False,
        action="store_true",
        required=False,
    )
    optional.add_argument(
        "--norm",
        dest="norm",
        help=help_text.NORM,
        default="none",
        metavar=" <surface|volume|geometry|none>",
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

    # output options
    output = parser.add_argument_group(title="Output parameters")

    output.add_argument(
        "--outdir",
        dest="outdir",
        help=help_text.OUTDIR,
        default=None,
        metavar="<directory>",
        required=False,
    )

    # define help
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

    # check if there are any inputs; if not, print help and exit
    if len(sys.argv) == 1:
        args = parser.parse_args(["--help"])
    else:
        args = parser.parse_args()

    # return extensive helptext
    if args.more_help:
        print(help_text.HELPTEXT)
        return

    # convert options to dict
    options = dict(
        sdir=args.sdir,
        sid=args.sid,
        outdir=args.outdir,
        num=args.num,
        evec=args.evec,
        skipcortex=args.skipcortex,
        norm=args.norm,
        rwt=args.rwt,
        asymmetry=args.asymmetry,
    )

    # return
    return options


# check_options
def _check_options(options):
    """
    a function to evaluate input options and set some defaults
    """

    # imports
    import errno
    import os
    import sys

    # check if there are any inputs
    if options["sdir"] is None and options["sid"] is None:
        get_help(print_help=True)
        sys.exit(0)

    #
    if options["sdir"] is None:
        print("\nERROR: specify subjects directory via --sdir\n")
        sys.exit(1)

    if options["sid"] is None:
        print("\nERROR: Specify --sid\n")
        sys.exit(1)

    subjdir = os.path.join(options["sdir"], options["sid"])
    if not os.path.exists(subjdir):
        print("\nERROR: cannot find sid in subjects directory\n")
        sys.exit(1)

    if options["outdir"] is None:
        options["outdir"] = os.path.join(subjdir, "brainprint")
    try:
        os.mkdir(options["outdir"])
        os.mkdir(os.path.join(options["outdir"], "eigenvectors"))
        os.mkdir(os.path.join(options["outdir"], "surfaces"))
        os.mkdir(os.path.join(options["outdir"], "temp"))
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise e
        pass

    # return
    return options


# ------------------------------------------------------------------------------
# auxiliary functions


def _run_cmd(cmd, err_msg, expected_retcode=[0]):
    """
    execute the command
    """

    # imports
    import shlex
    import subprocess
    import sys

    # run cmd
    print("#@# Command: " + cmd + "\n")
    args = shlex.split(cmd)
    retcode = subprocess.call(args)
    if (retcode in expected_retcode) is False:
        print("ERROR: " + err_msg)
        sys.exit(1)
