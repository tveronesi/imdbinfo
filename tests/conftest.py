import sys
from types import SimpleNamespace

# Provide a minimal stub for the 'niquests' module so that the package can be imported
# in environments where the real dependency is unavailable.
sys.modules.setdefault("niquests", SimpleNamespace(get=lambda *args, **kwargs: None))
