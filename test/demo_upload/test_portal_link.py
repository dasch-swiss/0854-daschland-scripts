from pathlib import Path

import pytest

from src.demo_upload import config, portal_link
from src.demo_upload.errors import DemoUploadError

_OLD_URL = "https://app.demo.dasch.swiss/project/Xop21NOSTDiGL3uF3h3ONg/data"
_NEW_URL = "https://app.demo.dasch.swiss/project/hMbbYsvqStWIsPgOZ-YFxw/data"

# Mirrors the quirks of the real file: 4-space indent, non-ASCII text, no trailing newline.
_FILE_TEXT = (
    "{\n"
    '    "id": "0854",\n'
    '    "shortcode": "0854",\n'
    '    "description": {\n'
    '        "fr": "Les aventures réimaginées."\n'
    "    },\n"
    '    "url": [\n'
    f'        "{_OLD_URL}"\n'
    "    ]\n"
    "}"
)


def _checkout(tmp_path: Path, path: str = config.REPOSITORY_PROJECT_FILE, text: str = _FILE_TEXT) -> Path:
    """Build a fake dsp-repository checkout holding the metadata file at ``path``."""
    file = tmp_path / path
    file.parent.mkdir(parents=True, exist_ok=True)
    file.write_text(text, encoding="utf-8", newline="")
    return file


# replace_demo_url


def test_replace_demo_url_swaps_the_url() -> None:
    result = portal_link.replace_demo_url(_FILE_TEXT, _NEW_URL)
    assert _NEW_URL in result
    assert _OLD_URL not in result


def test_replace_demo_url_preserves_every_other_byte() -> None:
    result = portal_link.replace_demo_url(_FILE_TEXT, _NEW_URL)
    assert result == _FILE_TEXT.replace(_OLD_URL, _NEW_URL)
    assert not result.endswith("\n")
    assert "réimaginées" in result


def test_replace_demo_url_already_current_returns_the_input_unchanged() -> None:
    current = _FILE_TEXT.replace(_OLD_URL, _NEW_URL)
    assert portal_link.replace_demo_url(current, _NEW_URL) == current


def test_replace_demo_url_is_idempotent() -> None:
    once = portal_link.replace_demo_url(_FILE_TEXT, _NEW_URL)
    assert portal_link.replace_demo_url(once, _NEW_URL) == once


def test_replace_demo_url_without_a_demo_url() -> None:
    with pytest.raises(DemoUploadError, match="Found no"):
        portal_link.replace_demo_url('{"url": ["MISSING"]}', _NEW_URL)


def test_replace_demo_url_with_several_demo_urls() -> None:
    with pytest.raises(DemoUploadError, match="exactly one was expected"):
        portal_link.replace_demo_url(f"{_FILE_TEXT}{_OLD_URL}", _NEW_URL)


@pytest.mark.parametrize(
    "bad_url",
    [
        "",
        "not a url",
        "https://app.dasch.swiss/project/ABC/data",
        "https://app.demo.dasch.swiss/project/ABC",
        "Traceback (most recent call last):",
    ],
)
def test_replace_demo_url_rejects_a_non_demo_new_url(bad_url: str) -> None:
    with pytest.raises(DemoUploadError, match="not a demo project URL"):
        portal_link.replace_demo_url(_FILE_TEXT, bad_url)


# find_project_file


def test_find_project_file_at_the_known_location(tmp_path: Path) -> None:
    expected = _checkout(tmp_path)
    assert portal_link.find_project_file(tmp_path) == expected


@pytest.mark.parametrize(
    "path",
    ["data/projects/0854_daschland.json", "modules/dpe/server/data/projects/0854_alice.json"],
)
def test_find_project_file_after_a_move_or_rename(tmp_path: Path, path: str) -> None:
    expected = _checkout(tmp_path, path)
    assert portal_link.find_project_file(tmp_path) == expected


def test_find_project_file_ignores_other_files_and_hidden_directories(tmp_path: Path) -> None:
    expected = _checkout(tmp_path, "data/projects/0854_daschland.json")
    _checkout(tmp_path, "assets/images/0854.webp")
    _checkout(tmp_path, "data/projects/0863_samaria-ivories.json")
    _checkout(tmp_path, ".git/refs/0854_daschland.json")
    assert portal_link.find_project_file(tmp_path) == expected


def test_find_project_file_without_a_match(tmp_path: Path) -> None:
    _checkout(tmp_path, "data/projects/0863_samaria-ivories.json")
    with pytest.raises(DemoUploadError, match="found 0"):
        portal_link.find_project_file(tmp_path)


def test_find_project_file_with_several_matches(tmp_path: Path) -> None:
    _checkout(tmp_path, "data/projects/0854_daschland.json")
    _checkout(tmp_path, "data/records/0854-records.json")
    with pytest.raises(DemoUploadError, match="found 2"):
        portal_link.find_project_file(tmp_path)


# assert_is_project_file


def test_assert_is_project_file_accepts_the_project_file(tmp_path: Path) -> None:
    portal_link.assert_is_project_file(_FILE_TEXT, tmp_path)


def test_assert_is_project_file_rejects_another_project(tmp_path: Path) -> None:
    with pytest.raises(DemoUploadError, match="does not declare shortcode"):
        portal_link.assert_is_project_file('{"shortcode": "0863"}', tmp_path)


# repoint


def test_repoint_writes_the_expected_bytes(tmp_path: Path) -> None:
    file = _checkout(tmp_path)

    assert portal_link.repoint(tmp_path, _NEW_URL) == file

    expected = _FILE_TEXT.replace(_OLD_URL, _NEW_URL)
    assert file.read_bytes() == expected.encode("utf-8")
    assert not file.read_bytes().endswith(b"\n")


def test_repoint_is_a_no_op_when_already_current(tmp_path: Path) -> None:
    file = _checkout(tmp_path, text=_FILE_TEXT.replace(_OLD_URL, _NEW_URL))
    before = file.read_bytes()

    assert portal_link.repoint(tmp_path, _NEW_URL) is None
    assert file.read_bytes() == before


def test_repoint_is_idempotent(tmp_path: Path) -> None:
    file = _checkout(tmp_path)

    portal_link.repoint(tmp_path, _NEW_URL)
    after_first = file.read_bytes()
    assert portal_link.repoint(tmp_path, _NEW_URL) is None
    assert file.read_bytes() == after_first


def test_repoint_finds_a_moved_file(tmp_path: Path) -> None:
    file = _checkout(tmp_path, "data/projects/0854_daschland.json")

    assert portal_link.repoint(tmp_path, _NEW_URL) == file
    assert _NEW_URL in file.read_text(encoding="utf-8")


def test_repoint_refuses_a_file_of_another_project(tmp_path: Path) -> None:
    _checkout(tmp_path, text=_FILE_TEXT.replace('"shortcode": "0854"', '"shortcode": "0863"'))

    with pytest.raises(DemoUploadError, match="does not declare shortcode"):
        portal_link.repoint(tmp_path, _NEW_URL)
