from __future__ import annotations

import argparse
import sys
import tempfile
from pathlib import Path

from pc2bs import __version__
from pc2bs.convert import pointcloud_to_ballstick, resolve_stdio_path
from pc2bs.launch import DEFAULT_SPACEWALK_URL, launch_in_spacewalk


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="pc2bs",
        description="Convert a point-cloud Spacewalk .sw file to ball-and-stick (one-way).",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    p.add_argument(
        "-q",
        "--quiet",
        action="store_true",
        help="Suppress non-error messages on stderr.",
    )
    p.add_argument(
        "input",
        metavar="INPUT",
        help="Point-cloud .sw path, or '-' to read from standard input.",
    )
    p.add_argument(
        "output",
        metavar="OUTPUT",
        help="Output ball-and-stick .sw path, or '-' to write to standard output.",
    )
    p.add_argument(
        "--open",
        action="store_true",
        help="After writing OUTPUT, open it in Spacewalk via the default browser.",
    )
    p.add_argument(
        "--no-index",
        dest="index",
        action="store_false",
        help="Do not append an hdf5-indexer _index dataset to OUTPUT.",
    )
    p.set_defaults(index=True)
    p.add_argument(
        "--spacewalk-url",
        default=DEFAULT_SPACEWALK_URL,
        metavar="URL",
        help=f"Spacewalk URL to open (default: {DEFAULT_SPACEWALK_URL}).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    args = _build_parser().parse_args(argv)

    quiet = args.quiet
    if args.open and args.output == "-":
        print("pc2bs: error: --open is incompatible with OUTPUT='-'", file=sys.stderr)
        return 2

    tmp_in: tempfile.TemporaryDirectory | None = None
    tmp_out: tempfile.TemporaryDirectory | None = None
    try:
        in_path, tmp_in = resolve_stdio_path(args.input, is_input=True)
        out_is_dash = args.output == "-"
        if out_is_dash:
            tmp_out = tempfile.TemporaryDirectory(prefix="pc2bs-out-")
            out_path = str(Path(tmp_out.name) / "out.sw")
        else:
            out_path = args.output

        pointcloud_to_ballstick(in_path, out_path, index=args.index)

        if out_is_dash:
            sys.stdout.buffer.write(Path(out_path).read_bytes())
        elif not quiet:
            print(f"wrote {out_path}", file=sys.stderr)

        if args.open:
            if not quiet:
                print("pc2bs: opening in Spacewalk\u2026", file=sys.stderr)
            ok = launch_in_spacewalk(Path(out_path), spacewalk_url=args.spacewalk_url)
            if not ok and not quiet:
                print("pc2bs: warning: Spacewalk handoff timed out", file=sys.stderr)

        return 0
    except BrokenPipeError:
        return 0
    except Exception as e:
        print(f"pc2bs: error: {e}", file=sys.stderr)
        return 1
    finally:
        for t in (tmp_in, tmp_out):
            if t is not None:
                t.cleanup()
