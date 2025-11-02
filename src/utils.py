''' 
Project:    Pi Floor Light

File:       src/utils.py

Title:      Utility Functions for Raspberry Pi

Abstract:   This module provides utility functions for the Pi Floor Light project.
            It includes functions for loading configuration files and other helper
            functions that may be useful throughout the project.

Author:     Dr. Oliver Opalko

Email:      oliver.opalko@gmail.com

'''
#!/usr/bin/env python3
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
