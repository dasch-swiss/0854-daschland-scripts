import json
from pathlib import Path
from typing import Any

from dsp_tools.commands.excel2json.project import excel2json

EXCEL_FOLDER = Path("data/daschland_ontology")
JSON_FILE = Path("data/output/daschland.json")

# The order of list nodes is shown to users, so it has meaning.
ORDERED_KEYS = {"nodes"}


def test_committed_json_matches_excel(tmp_path: Path) -> None:
    generated_file = tmp_path / JSON_FILE.name
    excel2json(str(EXCEL_FOLDER), str(generated_file))
    generated = normalize(json.loads(generated_file.read_text(encoding="utf-8")))
    committed = normalize(json.loads(JSON_FILE.read_text(encoding="utf-8")))
    assert generated == committed, (
        f"{JSON_FILE} does not match the Excel files in {EXCEL_FOLDER}. "
        "Make the change in the Excel files, then run 'just daschland-excel2json'."
    )


def normalize(obj: Any, key: str | None = None) -> Any:
    """Sort all arrays where the order has no meaning, so that only content differences remain."""
    if isinstance(obj, dict):
        return {k: normalize(v, k) for k, v in obj.items()}
    if isinstance(obj, list):
        items = [normalize(x) for x in obj]
        if key in ORDERED_KEYS:
            return items
        return sorted(items, key=lambda x: json.dumps(x, sort_keys=True))
    return obj


def test_dict_key_order_is_ignored() -> None:
    assert normalize({"a": 1, "b": 2}) == normalize({"b": 2, "a": 1})


def test_resource_order_is_ignored() -> None:
    first = {"resources": [{"name": "Book"}, {"name": "Audio"}]}
    second = {"resources": [{"name": "Audio"}, {"name": "Book"}]}
    assert normalize(first) == normalize(second)


def test_list_node_order_is_kept() -> None:
    first = {"nodes": [{"name": "a"}, {"name": "b"}]}
    second = {"nodes": [{"name": "b"}, {"name": "a"}]}
    assert normalize(first) != normalize(second)


def test_nested_list_node_order_is_kept() -> None:
    first = {"lists": [{"name": "l", "nodes": [{"name": "n", "nodes": [{"name": "a"}, {"name": "b"}]}]}]}
    second = {"lists": [{"name": "l", "nodes": [{"name": "n", "nodes": [{"name": "b"}, {"name": "a"}]}]}]}
    assert normalize(first) != normalize(second)
