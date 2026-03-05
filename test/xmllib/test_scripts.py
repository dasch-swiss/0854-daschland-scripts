import filecmp
import os
import re
import shutil
import warnings
from difflib import context_diff
from pathlib import Path

import pytest
from dsp_tools.xmllib.internal.xmllib_warnings import XmllibInputInfo

from src.xmllib.xmllib_main import main

XML_FILE = Path("data/output/data_daschland.xml")
ENV_VARS = ["XMLLIB_SORT_RESOURCES", "XMLLIB_SORT_PROPERTIES", "XMLLIB_AUTHORSHIP_ID_WITH_INTEGERS"]


@pytest.fixture
def stashed_original_xml(tmp_path: Path) -> Path:
    dst = tmp_path / XML_FILE.name
    shutil.copy(XML_FILE, dst)
    return dst


@pytest.fixture
def regenerate_xml_file(stashed_original_xml: Path) -> None:  # noqa: ARG001 (unused argument)
    for env_var in ENV_VARS:
        os.environ[env_var] = "true"
    with warnings.catch_warnings():
        warnings.simplefilter(action="ignore", category=XmllibInputInfo)
        main()


@pytest.mark.usefixtures("regenerate_xml_file")
def test_xml_has_not_changed(stashed_original_xml: Path) -> None:
    if filecmp.cmp(XML_FILE, stashed_original_xml, shallow=False):
        return
    diff = _get_diff(stashed_original_xml)
    if not _is_diff_legitimate(diff):
        _fail_on_diff(diff)


def _get_diff(stashed_original_xml: Path) -> list[str]:
    orig = Path(stashed_original_xml).read_text().splitlines(keepends=True)
    generated = Path(XML_FILE).read_text().splitlines(keepends=True)
    return list(context_diff(orig, generated))


def _is_diff_legitimate(diff: list[str]) -> bool:
    """
    For automated testing, the MP4 is not downloaded via Git LFS.
    The xmllib scripts read the file size and write it into the XML as ":hasFileSize" property.
    If the generated XML file differs only in this property from the checked-in version, this is not a problem.
    """
    num_of_diff_lines_if_only_video_size_changed = 19
    num_of_changed_lines = 2
    result = all(
        (
            len(diff) == num_of_diff_lines_if_only_video_size_changed,
            sum([1 if re.search(r"! +<decimal>\d+\.\d+</decimal>", x) else 0 for x in diff]) == num_of_changed_lines,
        )
    )
    return result


def _fail_on_diff(diff: list[str]) -> None:
    fail_msg = (
        "The XML file freshly generated with xmllib is not identical to the original. "
        "To fix this, run the xmllib scripts and commit the resulting XML file. "
        "Make sure that your .env file contains the following environment variables:\n"
        + "\n".join([f"{x}=true" for x in ENV_VARS])
    )
    fail_msg += "".join(diff)
    pytest.fail(fail_msg)
