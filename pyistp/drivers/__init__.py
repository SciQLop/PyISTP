import logging, os
import importlib
from typing import Callable, ByteString
from ._driver import Driver

log = logging.getLogger(__name__)


def _load_cdf_lib() -> Callable[[str or ByteString], Driver]:
    available_libs = ["pycdfpp", "spacepy"]
    try_first_lib = os.environ.get("PYISTP_CDFLIB", "pycdfpp")
    available_libs.remove(try_first_lib)
    available_libs.insert(0, try_first_lib)

    for driver in available_libs:
        try:
            mod = importlib.import_module(f"pyistp.drivers.{driver}", "*")
            log.info(f"Using {driver}")
            return mod.Driver
        except ImportError:
            log.info(f"Failed to load {driver}, trying next available driver")
    raise ImportError("Can't import any compatible CDF library")


current_driver = _load_cdf_lib()
