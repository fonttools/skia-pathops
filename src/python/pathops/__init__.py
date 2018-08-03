from ._pathops import (
    PathPen,
    Path,
    op,
    OpBuilder,
    DIFFERENCE,
    INTERSECTION,
    UNION,
    XOR,
    REVERSE_DIFFERENCE,
    fix_winding,
)

from .errors import (
    PathOpsError,
    UnsupportedVerbError,
    OpenPathError,
)

from .operations import (
    union,
    difference,
    intersection,
    xor,
)

try:
    from ._version import version as __version__
except ImportError:
    __version__ = "0.0.0+unknown"
