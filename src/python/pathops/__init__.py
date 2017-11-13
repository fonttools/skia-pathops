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
