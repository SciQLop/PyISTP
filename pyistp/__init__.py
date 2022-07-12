"""Top-level package for Python ISTP loader."""

__author__ = """Alexis Jeandet"""
__email__ = 'alexis.jeandet@member.fsf.org'
__version__ = '0.1.0'


def load(file=None, buffer=None):
    from .loader import ISTPLoader
    return ISTPLoader(file=file, buffer=buffer)
