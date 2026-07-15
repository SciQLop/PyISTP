"""NetCDF4 driver implementing the PyISTP Driver protocol.

netCDF4/HDF5 is not thread-safe (see pyistp.drivers._netcdf_worker for
why a lock cannot fix this), so this module is a thin IPC client: the
real netCDF4 calls run in a single dedicated subprocess and are reached
over a pipe, matching Unidata's own recommendation to use process-based
rather than thread-based parallelism around netCDF4.
"""

import atexit
import multiprocessing
import threading

_CTX = multiprocessing.get_context("spawn")
_process = None
_conn = None
_start_lock = threading.Lock()
_call_lock = threading.Lock()


def _ensure_worker():
    global _process, _conn
    if _process is not None and _process.is_alive():
        return
    with _start_lock:
        if _process is not None and _process.is_alive():
            return
        from ._netcdf_worker import worker_main
        parent_conn, child_conn = _CTX.Pipe()
        process = _CTX.Process(
            target=worker_main, args=(child_conn,), daemon=True,
            name="pyistp-netcdf-worker",
        )
        process.start()
        child_conn.close()
        _process = process
        _conn = parent_conn


def _shutdown_worker():
    global _process, _conn
    if _process is None:
        return
    with _call_lock:
        if _process is not None and _process.is_alive():
            try:
                _conn.send(('shutdown',))
            except (BrokenPipeError, OSError):
                pass
            _process.join(timeout=5)
            if _process.is_alive():
                _process.terminate()
        _process = None
        _conn = None


atexit.register(_shutdown_worker)


def _request(op, *payload):
    """Send one request to the worker and return its result, spawning
    the worker on first use (or respawning it if a previous one died)."""
    _ensure_worker()
    with _call_lock:
        try:
            _conn.send((op, *payload))
            status, result = _conn.recv()
        except (BrokenPipeError, EOFError, OSError) as exc:
            raise RuntimeError(
                "netCDF4 worker process is unavailable"
            ) from exc
    if status == 'err':
        raise result
    return result


class Driver:
    """NetCDF4 driver implementing the PyISTP Driver protocol."""

    def __init__(self, file):
        self._handle = _request('open', file)

    def __del__(self):
        handle = getattr(self, '_handle', None)
        # Skip if the worker was never started or already shut down —
        # avoids spawning a fresh worker during interpreter teardown
        # just to close a handle nobody cares about anymore.
        if handle is not None and _process is not None:
            try:
                _request('close', handle)
            except Exception:
                pass

    def _call(self, method, *args, **kwargs):
        return _request('call', self._handle, method, args, kwargs)

    def variables(self):
        return self._call('variables')

    def has_variable(self, name):
        return self._call('has_variable', name)

    def variable_attributes(self, var):
        return self._call('variable_attributes', var)

    def variable_attribute_value(self, var, attr):
        return self._call('variable_attribute_value', var, attr)

    def is_char(self, var):
        return self._call('is_char', var)

    def is_nrv(self, var):  # NOSONAR
        # NRV concept does not exist in NetCDF4 — no need to ask the
        # worker.
        return False

    def shape(self, var):
        return self._call('shape', var)

    def attributes(self):
        return self._call('attributes')

    def attribute(self, key):
        return self._call('attribute', key)

    def values(self, var, is_metadata_variable=False):  # NOSONAR
        return self._call(
            'values', var, is_metadata_variable=is_metadata_variable)

    def cdf_type(self, var):
        return self._call('cdf_type', var)
