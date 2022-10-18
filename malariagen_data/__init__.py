# flake8: noqa
from .af1 import Af1
from .ag3 import Ag3
from .amin1 import Amin1
from .anopheles import Anopheles, Region
from .util import SiteClass

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata


# this will read version from pyproject.toml
__version__ = importlib_metadata.version(__name__)
