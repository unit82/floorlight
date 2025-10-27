"""Simple package initializer for the src package.

This module exposes a main() function from the package so the package
can be imported and used as a module: `from src import main`.
"""

from .main import main  # re-export main for convenience

__all__ = ["main"]
