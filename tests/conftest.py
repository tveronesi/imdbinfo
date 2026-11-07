import sys
from types import SimpleNamespace

import pytest

# Provide a minimal stub for the 'niquests' module so that the package can be imported
# in environments where the real dependency is unavailable.
sys.modules.setdefault("niquests", SimpleNamespace(get=lambda *args, **kwargs: None))


@pytest.fixture(autouse=True)
def reset_library_config():
    from imdbinfo.config import reset_config

    reset_config()
    yield
    reset_config()
