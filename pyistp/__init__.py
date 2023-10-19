"""Top-level package for Python ISTP loader."""

__author__ = """Alexis Jeandet"""
__email__ = 'alexis.jeandet@member.fsf.org'
__version__ = '0.4.0'

from .loader import ISTPLoader as _ISTPLoader


def load(file=None, buffer=None) -> _ISTPLoader:
    return _ISTPLoader(file=file, buffer=buffer)
