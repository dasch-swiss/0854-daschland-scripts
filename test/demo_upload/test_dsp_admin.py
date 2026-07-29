from typing import Any

import pytest

from src.demo_upload import config, dsp_admin
from src.demo_upload.dsp_admin import EraseOutcome
from src.demo_upload.errors import AuthenticationError, DemoUploadError, EraseError


class _FakeResponse:
    def __init__(self, status_code: int, payload: dict[str, Any] | None = None, text: str = "") -> None:
        self.status_code = status_code
        self._payload = payload if payload is not None else {}
        self.text = text

    def json(self) -> dict[str, Any]:
        return self._payload


def test_interpret_erase_status_erased() -> None:
    assert dsp_admin.interpret_erase_status(200, "") is EraseOutcome.ERASED


def test_interpret_erase_status_already_absent() -> None:
    assert dsp_admin.interpret_erase_status(404, "") is EraseOutcome.ALREADY_ABSENT


@pytest.mark.parametrize("status_code", [401, 403])
def test_interpret_erase_status_refused(status_code: int) -> None:
    with pytest.raises(EraseError, match="ALLOW_ERASE_PROJECTS"):
        dsp_admin.interpret_erase_status(status_code, "body")


def test_interpret_erase_status_unexpected() -> None:
    with pytest.raises(EraseError, match="Unexpected"):
        dsp_admin.interpret_erase_status(500, "body")


def test_build_app_url() -> None:
    iri = "http://rdfh.ch/projects/Xop21NOSTDiGL3uF3h3ONg"
    assert dsp_admin.build_app_url(iri) == f"{config.DEMO_APP_URL}/project/Xop21NOSTDiGL3uF3h3ONg/data"


def test_build_app_url_trailing_slash() -> None:
    iri = "http://rdfh.ch/projects/Xop21NOSTDiGL3uF3h3ONg/"
    assert dsp_admin.build_app_url(iri) == f"{config.DEMO_APP_URL}/project/Xop21NOSTDiGL3uF3h3ONg/data"


def test_build_app_url_empty_segment() -> None:
    with pytest.raises(ValueError, match="Cannot derive"):
        dsp_admin.build_app_url("/")


def test_extract_project_iri() -> None:
    payload = {"project": {"id": "http://rdfh.ch/projects/ABC", "shortcode": "0854"}}
    assert dsp_admin.extract_project_iri(payload) == "http://rdfh.ch/projects/ABC"


def test_extract_project_iri_malformed() -> None:
    with pytest.raises(ValueError, match="Unexpected project payload"):
        dsp_admin.extract_project_iri({"nope": {}})


def test_authenticate_returns_token(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(200, {"token": "tok-123"})

    monkeypatch.setattr("requests.post", fake_post)
    assert dsp_admin.authenticate("pw") == "tok-123"


def test_authenticate_bad_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(401, text="unauthorized")

    monkeypatch.setattr("requests.post", fake_post)
    with pytest.raises(AuthenticationError):
        dsp_admin.authenticate("pw")


def test_authenticate_no_token(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(200, {})

    monkeypatch.setattr("requests.post", fake_post)
    with pytest.raises(AuthenticationError, match="no token"):
        dsp_admin.authenticate("pw")


def test_erase_project_erased(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_delete(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(200)

    monkeypatch.setattr("requests.delete", fake_delete)
    assert dsp_admin.erase_project("tok") is EraseOutcome.ERASED


def test_erase_project_already_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_delete(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(404)

    monkeypatch.setattr("requests.delete", fake_delete)
    assert dsp_admin.erase_project("tok") is EraseOutcome.ALREADY_ABSENT


def test_erase_project_forbidden(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_delete(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(403, text="forbidden")

    monkeypatch.setattr("requests.delete", fake_delete)
    with pytest.raises(EraseError):
        dsp_admin.erase_project("tok")


def test_fetch_project_url(monkeypatch: pytest.MonkeyPatch) -> None:
    payload = {"project": {"id": "http://rdfh.ch/projects/ABC"}}

    def fake_get(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(200, payload)

    monkeypatch.setattr("requests.get", fake_get)
    assert dsp_admin.fetch_project_url() == f"{config.DEMO_APP_URL}/project/ABC/data"


def test_fetch_project_url_not_found(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_get(*_args: Any, **_kwargs: Any) -> _FakeResponse:
        return _FakeResponse(404, text="not found")

    monkeypatch.setattr("requests.get", fake_get)
    with pytest.raises(DemoUploadError):
        dsp_admin.fetch_project_url()
