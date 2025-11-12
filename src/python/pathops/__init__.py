from ._pathops import (
    PathPen,
    Path,
    PathVerb,
    PathOp,
    FillType,
    LineCap,
    LineJoin,
    ArcSize,
    Direction,
    op,
    simplify,
    OpBuilder,
    PathOpsError,
    UnsupportedVerbError,
    OpenPathError,
    NumberOfPointsError,
    bits2float,
    float2bits,
    decompose_quadratic_segment,
)

# Cython generates cpdef enums as IntFlag. Starting in Python 3.11, IntFlag
# only includes "canonical" members when iterating: that is, only powers of
# two (1, 2, 4, 8...). Non-powers of two members ("aliases") are excluded
# from _member_names_ which controls iteration, even though they're still
# in __members__. This breaks would code that iterates over the enum
# expecting all members to be listed (just like our operations.py does).
# Cython added a workaround that sets _member_names_ to bypass this filtering,
# but it only applies when compiling with Python 3.11+ (controlled by a
# compile-time PY_VERSION_HEX check). If we build the abi3 wheels with Python
# 3.10, that workaround doesn't get applied, causing enum iteration to fail
# when the wheel is installed and run on Python 3.11+.
# We fix this by manually setting _member_names_ here, just like Cython does,
# ensuring wheels built with 3.10 will also work on 3.11+. See:
# https://github.com/cython/cython/pull/4877
# https://github.com/cython/cython/issues/5109
for _enum_class in [PathOp, FillType, LineCap, LineJoin, ArcSize, Direction, PathVerb]:
    _enum_class._member_names_ = list(_enum_class.__members__.keys())
del _enum_class

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
