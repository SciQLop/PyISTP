"""Top-level package for Python ISTP loader."""

__author__ = """Alexis Jeandet"""
__email__ = 'alexis.jeandet@member.fsf.org'
__version__ = '0.1.0'

from .drivers import current_driver


class ISTPLoader:
    cdf = None

    def __init__(self, file=None, buffer=None):
        if file:
            self.cdf = current_driver.load(file)
        if buffer:
            self.cdf = current_driver.load(buffer)
