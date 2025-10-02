"""Test package initialisation hacks for shared fixtures."""

import importlib
import sys
import time as _time_module

_PERFORMANCE_MODULE = "tests.test_calendar_performance"

if _PERFORMANCE_MODULE in sys.modules:
    sys.modules[_PERFORMANCE_MODULE].time = _time_module
else:
    module = importlib.import_module(
        f".{_PERFORMANCE_MODULE.split('.', 1)[1]}", package=__name__
    )
    module.time = _time_module

__all__ = []
