"""Exceptions raised by the demo-upload automation.

All inherit from ``DemoUploadError`` so the CLI can turn any expected failure
into a single, actionable log line and a non-zero exit code.
"""


class DemoUploadError(RuntimeError):
    """Base class for all expected demo-upload failures."""


class AuthenticationError(DemoUploadError):
    """Raised when logging in to the DSP server fails."""


class EraseError(DemoUploadError):
    """Raised when the project could not be erased (e.g. feature disabled, no permission)."""
