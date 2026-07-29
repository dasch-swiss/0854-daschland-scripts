"""Automation helpers for re-uploading the Alice project to the DSP demo server.

Provides the raw HTTP operations that ``dsp-tools`` does not expose: erasing the
project, deriving its (post-upload) DSP-APP URL, and filing a Linear reminder.
Used by the ``recreate-on-demo`` GitHub Actions workflow.
"""
