#!/usr/bin/env python3
"""Render referenced PDF figures to sibling PNGs without silent replacement.

Each invocation selects one 1-based page for all its inputs. An existing PNG is
reused only when its decoded pixels match this page at the requested DPI.
A different page or resolution is a conflict unless --overwrite is given.
"""

from __future__ import annotations

import argparse
import importlib
import os
from pathlib import Path
import sys
import tempfile

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class ConversionError(Exception):
    """An expected input, rendering, or output failure."""


def positive_int(value: str) -> int:
    try:
        parsed = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return parsed


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description=__doc__)
    result.add_argument("pdf", nargs="+", type=Path, help="PDF figure path(s)")
    result.add_argument("--page", type=positive_int, default=1,
                        help="1-based page for every input (default: 1)")
    result.add_argument("--dpi", type=positive_int, default=300,
                        help="render resolution (default: 300 DPI)")
    result.add_argument("--overwrite", action="store_true",
                        help="explicitly replace an existing differing or damaged PNG")
    return result


def load_renderer():
    try:
        return importlib.import_module("pymupdf")
    except ImportError as exc:
        raise ConversionError(
            "PyMuPDF is unavailable in this Python environment. Use the skill's "
            ".venv interpreter or install its requirements.txt in an isolated environment."
        ) from exc


def prepare_inputs(paths: list[Path], page_number: int, renderer) -> list[Path]:
    """Validate every source before creating outputs; deduplicate aliases."""
    sources: list[Path] = []
    seen: set[str] = set()
    destinations: set[str] = set()
    for supplied in paths:
        try:
            source = supplied.expanduser().resolve(strict=True)
        except (OSError, RuntimeError) as exc:
            raise ConversionError(f"{supplied}: cannot read PDF: {exc}") from exc
        if not source.is_file() or source.suffix.lower() != ".pdf":
            raise ConversionError(f"{supplied}: expected a regular .pdf file")
        key = os.path.normcase(str(source))
        if key in seen:
            continue
        seen.add(key)
        destination = source.with_suffix(".png")
        destination_key = os.path.normcase(str(destination))
        if destination_key in destinations:
            raise ConversionError(f"{destination}: multiple PDFs map to the same output")
        destinations.add(destination_key)
        if destination.is_symlink():
            raise ConversionError(f"{destination}: refusing a symbolic-link output")
        if destination.exists() and not destination.is_file():
            raise ConversionError(f"{destination}: output is not a regular file")
        try:
            with renderer.open(str(source)) as document:
                if not document.is_pdf:
                    raise ConversionError(f"{source}: content is not a PDF")
                if document.needs_pass:
                    raise ConversionError(f"{source}: PDF requires a password")
                if not 1 <= page_number <= document.page_count:
                    raise ConversionError(
                        f"{source}: page {page_number} is out of range "
                        f"(PDF has {document.page_count} page(s))"
                    )
        except ConversionError:
            raise
        except Exception as exc:
            raise ConversionError(f"{source}: cannot open PDF: {exc}") from exc
        sources.append(source)
    return sources


def same_pixels(destination: Path, rendered, renderer) -> bool:
    """Compare decoded RGB pixels, not compression metadata or timestamps."""
    try:
        with destination.open("rb") as stream:
            if stream.read(8) != PNG_SIGNATURE:
                raise ConversionError(
                    f"{destination}: existing file is not a PNG; it was preserved. "
                    "Use --overwrite only if replacement is intended."
                )
        existing = renderer.Pixmap(str(destination))
        if existing.alpha or existing.colorspace is None:
            return False
        if existing.colorspace.n != 3:
            existing = renderer.Pixmap(renderer.csRGB, existing)
        return (
            existing.width == rendered.width
            and existing.height == rendered.height
            and existing.n == rendered.n
            and existing.samples == rendered.samples
        )
    except ConversionError:
        raise
    except Exception as exc:
        raise ConversionError(
            f"{destination}: cannot decode existing PNG: {exc}. "
            "It was preserved; use --overwrite only if replacement is intended."
        ) from exc


def write_png(destination: Path, png: bytes, overwrite: bool) -> None:
    if not overwrite:
        # Exclusive creation also protects a file created after the reuse check.
        created = False
        try:
            with destination.open("xb") as stream:
                created = True
                stream.write(png)
        except BaseException:
            if created:
                destination.unlink(missing_ok=True)
            raise
        return
    # Commit a replacement only after the new PNG has been fully written.
    descriptor, temporary_name = tempfile.mkstemp(
        dir=destination.parent, prefix=f".{destination.stem}.", suffix=".png.tmp"
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            stream.write(png)
        os.replace(temporary, destination)
    finally:
        temporary.unlink(missing_ok=True)


def convert(source: Path, page_number: int, dpi: int, overwrite: bool, renderer):
    destination = source.with_suffix(".png")
    try:
        with renderer.open(str(source)) as document:
            page = document.load_page(page_number - 1)
            rendered = page.get_pixmap(dpi=dpi, colorspace=renderer.csRGB, alpha=False)
        if destination.is_symlink():
            raise ConversionError(f"{destination}: refusing a symbolic-link output")
        existed = destination.exists()
        if existed and not overwrite:
            if same_pixels(destination, rendered, renderer):
                return "REUSED", destination
            raise ConversionError(
                f"{destination}: existing PNG differs from page {page_number} "
                f"at {dpi} DPI (content, resolution, or transparency conflict). "
                "It was preserved. Check the requested page and existing asset; "
                "use --overwrite only if replacement is intended."
            )
        write_png(destination, rendered.tobytes("png"), overwrite)
        return "UPDATED" if existed else "CREATED", destination
    except ConversionError:
        raise
    except Exception as exc:
        raise ConversionError(f"{source}: conversion failed: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        renderer = load_renderer()
    except ConversionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    try:
        sources = prepare_inputs(args.pdf, args.page, renderer)
    except ConversionError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    failures = 0
    for source in sources:
        try:
            status, destination = convert(
                source, args.page, args.dpi, args.overwrite, renderer
            )
            print(f"{status}: {destination} (page {args.page}, {args.dpi} DPI)")
        except ConversionError as exc:
            failures += 1
            print(f"ERROR: {exc}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
