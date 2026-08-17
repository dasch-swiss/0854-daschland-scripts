"""CLI entry point for the demo-upload automation.

Usage (from the repo root):

    uv run python -m src.demo_upload erase
    uv run python -m src.demo_upload project-url
    uv run python -m src.demo_upload edit-metadata --url <project-url> --repo-dir <checkout>

Logs go to stderr; ``project-url`` prints the resulting URL to stdout so the
workflow can capture it. Any expected failure exits non-zero with one log line.
"""

import argparse
import os
import sys
from pathlib import Path

from loguru import logger

from src.demo_upload import config, dsp_admin, portal_link
from src.demo_upload.errors import DemoUploadError


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise DemoUploadError(f"Required environment variable {name} is not set.")
    return value


def _run_erase() -> None:
    password = _require_env("DASCH_USER_PW_PROD")
    token = dsp_admin.authenticate(password)
    dsp_admin.erase_project(token)


def _run_project_url() -> None:
    url = dsp_admin.fetch_project_url()
    logger.info("Current demo project URL: {}", url)
    print(url)  # stdout, consumed by the workflow


def _emit_output(name: str, value: str) -> None:
    """Hand a single-line value to the later workflow steps, when running inside GitHub Actions."""
    output_file = os.environ.get("GITHUB_OUTPUT")
    if not output_file:
        return
    with Path(output_file).open("a", encoding="utf-8") as handle:
        handle.write(f"{name}={value}\n")


def _run_edit_metadata(project_url: str, repo_dir: Path) -> None:
    edited = portal_link.repoint(repo_dir, project_url)
    note = ""
    if edited is not None and edited != repo_dir / config.REPOSITORY_PROJECT_FILE:
        note = (
            f"> Note: the metadata file now lives at `{edited.relative_to(repo_dir)}`, not at "
            f"`{config.REPOSITORY_PROJECT_FILE}`. Please update REPOSITORY_PROJECT_FILE in "
            f"src/demo_upload/config.py of 0854-daschland-scripts."
        )
    # Underscore, not hyphen: GitHub Actions expressions cannot dereference a hyphenated output name
    _emit_output("moved_note", note)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="demo_upload", description="Re-upload the Alice project to the demo server.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("erase", help="Erase the Alice project from the demo server.")
    subparsers.add_parser("project-url", help="Print the current demo project's DSP-APP URL.")
    edit_parser = subparsers.add_parser(
        "edit-metadata", help="Repoint the portal link in a checkout of dsp-repository."
    )
    edit_parser.add_argument("--url", required=True, help="The new project URL to put on the portal.")
    edit_parser.add_argument("--repo-dir", required=True, type=Path, help="Path to the dsp-repository checkout.")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    try:
        if args.command == "erase":
            _run_erase()
        elif args.command == "project-url":
            _run_project_url()
        elif args.command == "edit-metadata":
            _run_edit_metadata(args.url, args.repo_dir)
    except DemoUploadError as exc:
        logger.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
