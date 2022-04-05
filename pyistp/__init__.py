"""Top-level package for Python ISTP loader."""

__author__ = """Alexis Jeandet"""
__email__ = 'alexis.jeandet@member.fsf.org'
__version__ = '0.1.0'

from ._impl import ISTPLoaderImpl
from typing import List


class ISTPLoader:
    cdf = None

    def __init__(self, file=None, buffer=None):
        self._impl = ISTPLoaderImpl(file=file, buffer=buffer)

    def data_variables(self) -> List[str]:
        return self._impl.data_variables