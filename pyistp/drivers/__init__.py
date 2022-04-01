try:
    import pycdfpp
    from .pycdfpp import Driver as current_driver
except ImportError:
    try:
        import spacepy.pycdf as cdf
        from .spacepy import Driver as current_driver
    except ImportError:
        pass
