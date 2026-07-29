"""Create a Linear reminder issue after a successful re-upload.

Because the demo project URL changes on every upload, someone has to update the
"Discover Project Data" link on the DaSCH portal by hand. This files an issue
assigned to Daniela to prompt that.
"""

from http import HTTPStatus
from typing import Any

import requests

from src.demo_deploy import config
from src.demo_deploy.errors import DemoDeployError

_ISSUE_MUTATION = """
mutation IssueCreate($input: IssueCreateInput!) {
  issueCreate(input: $input) {
    success
    issue { identifier url }
  }
}
"""


def build_issue_title() -> str:
    """Title of the reminder issue."""
    return "Update the 'Discover Project Data' link for Alice in DaSCHland (demo)"


def build_issue_description(project_url: str) -> str:
    """Body of the reminder issue, pointing at the new URL and the portal link to edit."""
    lines = [
        "The 'Alice in DaSCHland' project was re-uploaded to the demo server, so its URL changed.",
        "",
        f"Please update the 'Discover Project Data' link on {config.REPOSITORY_PORTAL_URL} to point to:",
        "",
        project_url,
        "",
        "This reminder was created automatically by the `recreate-on-demo` GitHub Actions workflow.",
    ]
    return "\n".join(lines)


def build_issue_input(project_url: str) -> dict[str, str]:
    """Assemble the ``IssueCreateInput`` for the GraphQL mutation."""
    return {
        "teamId": config.LINEAR_TEAM_ID,
        "assigneeId": config.LINEAR_ASSIGNEE_ID,
        "title": build_issue_title(),
        "description": build_issue_description(project_url),
    }


def extract_issue_url(payload: dict[str, Any]) -> str:
    """Extract the created issue's URL from a Linear GraphQL response."""
    if payload.get("errors"):
        raise DemoDeployError(f"Linear API returned errors: {payload['errors']}")
    try:
        result = payload["data"]["issueCreate"]
        if not result["success"]:
            raise DemoDeployError(f"Linear reported the issue creation as unsuccessful: {payload}")
        return str(result["issue"]["url"])
    except (KeyError, TypeError) as exc:
        raise DemoDeployError(f"Unexpected Linear response: {payload!r}") from exc


def create_issue(api_key: str, project_url: str, *, api_url: str = config.LINEAR_API_URL) -> str:
    """Create the reminder issue and return its URL."""
    response = requests.post(
        api_url,
        json={"query": _ISSUE_MUTATION, "variables": {"input": build_issue_input(project_url)}},
        # Linear personal API keys go in the Authorization header verbatim (no "Bearer" prefix).
        headers={"Authorization": api_key, "Content-Type": "application/json"},
        timeout=config.HTTP_TIMEOUT,
    )
    if response.status_code != HTTPStatus.OK:
        raise DemoDeployError(f"Linear API call failed (HTTP {response.status_code}). Response body: {response.text}")
    return extract_issue_url(response.json())
