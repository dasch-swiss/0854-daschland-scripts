"""Repoint the portal link in a checkout of dsp-repository.

The DaSCH portal page of "Alice in DaSCHland" links to the project on the demo
server. Every re-upload assigns the project a new IRI, so that link has to be
repointed afterwards. This module rewrites the URL in the project's metadata
file; the workflow turns the result into a pull request.

The file is edited as text, not as parsed JSON: a ``json.load``/``json.dump``
round-trip would change the indentation, escape the non-ASCII characters and add
the trailing newline the file deliberately lacks, turning a one-line change into
a diff over the whole file.
"""

import re
from pathlib import Path

from loguru import logger

from src.demo_upload import config
from src.demo_upload.errors import DemoUploadError

_DEMO_URL_PATTERN = re.compile(re.escape(f"{config.DEMO_APP_URL}/project/") + r"[A-Za-z0-9_-]+" + re.escape("/data"))
# Directories that hold no metadata but plenty of files, so they are skipped when searching
_SKIPPED_DIRS = frozenset({"target", "node_modules"})


def replace_demo_url(file_text: str, new_url: str) -> str:
    """Swap the demo project URL in the file text, leaving every other byte untouched.

    Returns the text unchanged when it already carries ``new_url``, which is the
    expected outcome of a re-run rather than an error.
    """
    if not _DEMO_URL_PATTERN.fullmatch(new_url):
        raise DemoUploadError(f"Refusing to write {new_url!r} into {config.REPOSITORY_REPO}: not a demo project URL.")
    matches = list(_DEMO_URL_PATTERN.finditer(file_text))
    if not matches:
        raise DemoUploadError(
            f"Found no {config.DEMO_APP_URL} project URL to replace. The metadata file no longer links to the "
            f"demo server, so it has to be updated by hand."
        )
    if len(matches) > 1:
        raise DemoUploadError(
            f"Found {len(matches)} demo project URLs where exactly one was expected "
            f"({', '.join(match.group() for match in matches)}), so it is unclear which one to replace."
        )
    match = matches[0]
    return file_text[: match.start()] + new_url + file_text[match.end() :]


def find_project_file(repo_dir: Path) -> Path:
    """Locate the project's metadata file in a checkout of dsp-repository.

    Falls back to searching by file name, so the file is still found after
    dsp-repository moves it to another directory or renames its descriptive part.
    """
    known = repo_dir / config.REPOSITORY_PROJECT_FILE
    if known.is_file():
        return known
    logger.warning("{} does not exist; searching the checkout for the metadata file.", known)
    candidates = sorted(p for p in repo_dir.rglob(f"*{config.PROJECT_SHORTCODE}*.json") if _is_searchable(p, repo_dir))
    if len(candidates) != 1:
        raise DemoUploadError(
            f"Expected exactly one metadata file for project {config.PROJECT_SHORTCODE} in "
            f"{config.REPOSITORY_REPO}, but found {len(candidates)}: {candidates}. "
            f"Point REPOSITORY_PROJECT_FILE in src/demo_upload/config.py at the right file."
        )
    logger.warning("Found the metadata file at {}. Please update REPOSITORY_PROJECT_FILE in config.py.", candidates[0])
    return candidates[0]


def _is_searchable(path: Path, repo_dir: Path) -> bool:
    parts = path.relative_to(repo_dir).parts[:-1]
    return not any(part.startswith(".") or part in _SKIPPED_DIRS for part in parts)


def assert_is_project_file(file_text: str, path: Path) -> None:
    """Guard that the file really is this project's metadata file."""
    if f'"shortcode": "{config.PROJECT_SHORTCODE}"' not in file_text:
        raise DemoUploadError(
            f"{path} does not declare shortcode {config.PROJECT_SHORTCODE}, so it is not the file to edit."
        )


def repoint(repo_dir: Path, new_url: str) -> Path | None:
    """Point the portal link at ``new_url``.

    Returns the file that was edited, or ``None`` when the link was already current.
    """
    path = find_project_file(repo_dir)
    text = path.read_text(encoding="utf-8")
    assert_is_project_file(text, path)
    new_text = replace_demo_url(text, new_url)
    if new_text == text:
        logger.info("{} already points at {}; nothing to do.", path, new_url)
        return None
    # newline="" keeps the file's line endings, and its missing final newline, exactly as they are
    path.write_text(new_text, encoding="utf-8", newline="")
    logger.info("Pointed {} at {}.", path, new_url)
    return path
