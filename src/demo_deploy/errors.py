"""Exceptions raised by the demo-deploy automation.

All inherit from ``DemoDeployError`` so the CLI can turn any expected failure
into a single, actionable log line and a non-zero exit code.
"""


class DemoDeployError(RuntimeError):
    """Base class for all expected demo-deploy failures."""


class AuthenticationError(DemoDeployError):
    """Raised when logging in to the DSP server fails."""


class EraseError(DemoDeployError):
    """Raised when the project could not be erased (e.g. feature disabled, no permission)."""
