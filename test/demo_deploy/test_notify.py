from typing import Any

import pytest

from src.demo_deploy import config, notify
from src.demo_deploy.errors import DemoDeployError


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, Any] | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = text

    def json(self) -> dict[str, Any]:
        return self._payload


_PROJECT_URL = "https://app.demo.dasch.swiss/project/ABC/data"
_SUCCESS_PAYLOAD = {"data": {"issueCreate": {"success": True, "issue": {"url": "https://linear.app/x/issue/RDU-1"}}}}


def test_build_issue_description_contains_urls() -> None:
    description = notify.build_issue_description(_PROJECT_URL)
    assert _PROJECT_URL in description
    assert config.REPOSITORY_PORTAL_URL in description


def test_build_issue_input_shape() -> None:
    issue_input = notify.build_issue_input(_PROJECT_URL)
    assert issue_input["teamId"] == config.LINEAR_TEAM_ID
    assert issue_input["assigneeId"] == config.LINEAR_ASSIGNEE_ID
    assert issue_input["title"]
    assert _PROJECT_URL in issue_input["description"]


def test_extract_issue_url_success() -> None:
    assert notify.extract_issue_url(_SUCCESS_PAYLOAD) == "https://linear.app/x/issue/RDU-1"


def test_extract_issue_url_graphql_errors() -> None:
    with pytest.raises(DemoDeployError, match="errors"):
        notify.extract_issue_url({"errors": [{"message": "bad"}]})


def test_extract_issue_url_unsuccessful() -> None:
    with pytest.raises(DemoDeployError, match="unsuccessful"):
        notify.extract_issue_url({"data": {"issueCreate": {"success": False, "issue": None}}})


def test_extract_issue_url_malformed() -> None:
    with pytest.raises(DemoDeployError, match="Unexpected"):
        notify.extract_issue_url({"data": {}})


def test_create_issue_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(200, _SUCCESS_PAYLOAD)

    monkeypatch.setattr("requests.post", fake_post)
    assert notify.create_issue("key", _PROJECT_URL) == "https://linear.app/x/issue/RDU-1"


def test_create_issue_http_error(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(500, text="boom")

    monkeypatch.setattr("requests.post", fake_post)
    with pytest.raises(DemoDeployError, match="Linear API call failed"):
        notify.create_issue("key", _PROJECT_URL)
