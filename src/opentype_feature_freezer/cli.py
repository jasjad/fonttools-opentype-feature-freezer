from argparse import ArgumentParser
import logging
import os
import sys
from typing import List, Optional, Callable

import opentype_feature_freezer


def parseOptions(args=None):
    parser = ArgumentParser(
        description=(
            'With %(prog)s you can "freeze" some OpenType features into a font. '
            'These features are then "on by default", even in apps that don\'t '
            'support OpenType features. Internally, the tool remaps the "cmap" '
            "table of the font by applying the specified GSUB features. Only "
            "single and alternate substitutions are supported."
        ),
        epilog=(
            "Examples: "
            "%(prog)s -f 'c2sc,smcp' -S -U SC OpenSans.ttf OpenSansSC.ttf "
            "%(prog)s -R 'Lato/Otal' Lato-Regular.ttf Otal-Regular.ttf"
        ),
    )

    parser.add_argument(
        "inpath",
        help="input .otf or .ttf font file"
    )
    parser.add_argument(
        "outpath",
        nargs="?",
        default=None,
        help="output .otf or .ttf font file (optional)",
    )

    group_freezing = parser.add_argument_group("options to control feature freezing")
    group_freezing.add_argument(
        "-f",
        "--features",
        action="store",
        dest="features",
        type=str,
        default="",
        help="comma-separated list of OpenType feature tags, e.g. 'smcp,c2sc,onum'",
    )
    group_freezing.add_argument(
        "-s",
        "--script",
        action="store",
        dest="script",
        type=str,
        default="latn",
        help="OpenType script tag, e.g. 'cyrl' (default: 'latn')",
    )
    group_freezing.add_argument(
        "-l",
        "--lang",
        action="store",
        dest="lang",
        type=str,
        default=None,
        help="OpenType language tag, e.g. 'SRB ' (optional)",
    )
    group_freezing.add_argument(
        "-z",
        "--zapnames",
        action="store_true",
        dest="zapnames",
        help="zap glyphnames from the font ('post' table version 3, .ttf only)",
    )

    group_renaming = parser.add_argument_group("options to control font renaming")
    group_renaming.add_argument(
        "-S",
        "--suffix",
        action="store_true",
        dest="suffix",
        help="add a suffix to the font family name (by default, the suffix will be constructed from the OpenType feature tags)",
    )
    group_renaming.add_argument(
        "-U",
        "--usesuffix",
        action="store",
        dest="usesuffix",
        default="",
        help="use a custom suffix when --suffix is provided",
    )
    group_renaming.add_argument(
        "-R",
        "--replacenames",
        action="store",
        dest="replacenames",
        default="",
        help="search for strings in the font naming tables and replace them, format is 'search1/replace1,search2/replace2,...'",
    )
    group_renaming.add_argument(
        "-i",
        "--info",
        action="store_true",
        dest="info",
        help="update font version string",
    )

    group_reporting = parser.add_argument_group("reporting options")
    group_reporting.add_argument(
        "-r",
        "--report",
        action="store_true",
        dest="report",
        help="report languages, scripts and features in font",
    )
    group_reporting.add_argument(
        "-n",
        "--names",
        action="store_true",
        dest="names",
        help="output names of remapped glyphs during processing",
    )
    group_reporting.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        dest="verbose",
        help="print additional information during processing",
    )
    group_reporting.add_argument(
        "-V",
        "--version",
        action="version",
        version=opentype_feature_freezer.__version__,
    )

    return parser.parse_args(args)


def main(args: Optional[List[str]] = None, parser: Optional[Callable[[list], ArgumentParser]] = None) -> int:
    logging.basicConfig(format="%(levelname)s: %(message)s")
    if not parser:
        parser = parseOptions
    args_parsed = parser(args)
    if not os.path.exists(args_parsed.inpath):
        logging.error("Input file does not exist.")
        return 1

    if args_parsed.verbose:
        logging.getLogger().setLevel(logging.INFO)

    p = opentype_feature_freezer.RemapByOTL(args_parsed)
    try:
        p.run()
    except RuntimeError as e:
        logging.error(e)
        return 1
    if p.success:
        logging.info("Finished processing.")
        return 0

    logging.warning("Errors during processing.")
    return 1


if __name__ == "__main__":
    sys.exit(main())

