"""CLI entry point for the demo-deploy automation.

Usage (from the repo root):

    uv run python -m src.demo_deploy erase
    uv run python -m src.demo_deploy project-url
    uv run python -m src.demo_deploy notify --url <project-url>

Logs go to stderr; ``project-url`` prints the resulting URL to stdout so the
workflow can capture it. Any expected failure exits non-zero with one log line.
"""

import argparse
import os
import sys

from loguru import logger

from src.demo_deploy import dsp_admin, notify
from src.demo_deploy.errors import DemoDeployError


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise DemoDeployError(f"Required environment variable {name} is not set.")
    return value


def _run_erase() -> None:
    password = _require_env("DASCH_USER_PW_PROD")
    token = dsp_admin.authenticate(password)
    dsp_admin.erase_project(token)


def _run_project_url() -> None:
    url = dsp_admin.fetch_project_url()
    logger.info("Current demo project URL: {}", url)
    print(url)  # stdout, consumed by the workflow


def _run_notify(project_url: str) -> None:
    api_key = _require_env("LINEAR_API_KEY")
    issue_url = notify.create_issue(api_key, project_url)
    logger.info("Created Linear reminder issue: {}", issue_url)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="demo_deploy", description="Recreate the Alice project on the demo server.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("erase", help="Erase the Alice project from the demo server.")
    subparsers.add_parser("project-url", help="Print the current demo project's DSP-APP URL.")
    notify_parser = subparsers.add_parser("notify", help="File a Linear reminder to update the portal link.")
    notify_parser.add_argument("--url", required=True, help="The new project URL to put in the reminder.")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    try:
        if args.command == "erase":
            _run_erase()
        elif args.command == "project-url":
            _run_project_url()
        elif args.command == "notify":
            _run_notify(args.url)
    except DemoDeployError as exc:
        logger.error(str(exc))
        sys.exit(1)


if __name__ == "__main__":
    main()
