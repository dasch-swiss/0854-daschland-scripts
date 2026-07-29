"""DSP-API admin operations that dsp-tools does not expose.

Covers the SystemAdmin login, the (undocumented) hard-erase endpoint, and
deriving the project's DSP-APP data URL from its IRI.
"""

import enum
from http import HTTPStatus
from typing import Any

import requests
from loguru import logger

from src.demo_deploy import config
from src.demo_deploy.errors import AuthenticationError, DemoDeployError, EraseError


class EraseOutcome(enum.Enum):
    """Result of an erase attempt that did not fail."""

    ERASED = "erased"
    ALREADY_ABSENT = "already absent"


def interpret_erase_status(status_code: int, body: str) -> EraseOutcome:
    """Map an HTTP status from the erase endpoint to an outcome.

    A ``404`` means the project is already gone, which satisfies the goal of the
    erase step, so it is treated as a no-op rather than an error.
    """
    if status_code == HTTPStatus.OK:
        return EraseOutcome.ERASED
    if status_code == HTTPStatus.NOT_FOUND:
        return EraseOutcome.ALREADY_ABSENT
    if status_code in {HTTPStatus.UNAUTHORIZED, HTTPStatus.FORBIDDEN}:
        raise EraseError(
            f"Erase was refused (HTTP {status_code}). Either the SystemAdmin login is not valid on this "
            f"server, or the 'ALLOW_ERASE_PROJECTS' feature is disabled on it. Response body: {body}"
        )
    raise EraseError(f"Unexpected response from the erase endpoint (HTTP {status_code}). Response body: {body}")


def build_app_url(project_iri: str) -> str:
    """Turn a project IRI (``.../projects/<segment>``) into the DSP-APP data URL."""
    segment = project_iri.rstrip("/").rsplit("/", 1)[-1]
    if not segment:
        raise ValueError(f"Cannot derive a project URL from IRI: {project_iri!r}")
    return f"{config.DEMO_APP_URL}/project/{segment}/data"


def extract_project_iri(payload: dict[str, Any]) -> str:
    """Extract the project IRI from an admin 'get project' response."""
    try:
        return str(payload["project"]["id"])
    except (KeyError, TypeError) as exc:
        raise ValueError(f"Unexpected project payload: {payload!r}") from exc


def authenticate(password: str, *, api_url: str = config.DEMO_API_URL, email: str = config.SYSADMIN_EMAIL) -> str:
    """Log in to DSP-API and return a bearer token."""
    response = requests.post(
        f"{api_url}/v2/authentication",
        json={"email": email, "password": password},
        timeout=config.HTTP_TIMEOUT,
    )
    if response.status_code != HTTPStatus.OK:
        raise AuthenticationError(
            f"Login as {email} on {api_url} failed (HTTP {response.status_code}). Response body: {response.text}"
        )
    token = response.json().get("token")
    if not token:
        raise AuthenticationError(f"Login succeeded but the response contained no token: {response.text}")
    return str(token)


def erase_project(
    token: str, *, api_url: str = config.DEMO_API_URL, shortcode: str = config.PROJECT_SHORTCODE
) -> EraseOutcome:
    """Permanently erase the project with the given shortcode, including its assets."""
    response = requests.delete(
        f"{api_url}/admin/projects/shortcode/{shortcode}/erase",
        headers={"Authorization": f"Bearer {token}"},
        timeout=config.HTTP_TIMEOUT,
    )
    outcome = interpret_erase_status(response.status_code, response.text)
    logger.info("Erase of project {} on {}: {}.", shortcode, api_url, outcome.value)
    return outcome


def fetch_project_url(*, api_url: str = config.DEMO_API_URL, shortcode: str = config.PROJECT_SHORTCODE) -> str:
    """Return the DSP-APP data URL of the project currently registered under the shortcode."""
    response = requests.get(f"{api_url}/admin/projects/shortcode/{shortcode}", timeout=config.HTTP_TIMEOUT)
    if response.status_code != HTTPStatus.OK:
        raise DemoDeployError(
            f"Could not read project {shortcode} from {api_url} (HTTP {response.status_code}). "
            f"Response body: {response.text}"
        )
    return build_app_url(extract_project_iri(response.json()))
