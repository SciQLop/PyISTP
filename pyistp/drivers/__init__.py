import logging

log = logging.getLogger(__name__)

try:
    import pycdfpp
    from .pycdfpp import Driver as current_driver
    log.info("Using pycdfpp")
except ImportError:
    try:
        import spacepy.pycdf as cdf
        from .spacepy import Driver as current_driver
        log.info("Using spacepy.pycdf")
    except ImportError:
        raise ImportError("can't import any compatible CDF library")
