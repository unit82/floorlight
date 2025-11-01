"""Utility helpers for the floorlight project.

Currently contains a small helper to load runtime configuration from
the project's `config/settings.json` file. The helper returns a dict
or an empty dict on error.
"""
from pathlib import Path
import yaml


def load_config(path):
    """Load runtime configuration from config/settings.json (project root).

    Returns:
        dict: Configuration dictionary or empty dict on error.
    """
    try:
        with open(path, 'r') as f:
            return yaml.safe_load(f)
    except Exception as e:
        print(f"Error loading configuration from {path}: {e}")
        return {}
