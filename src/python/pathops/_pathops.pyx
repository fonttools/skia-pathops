from ._skia.core cimport (
    SkPath,
    SkPoint,
    SkScalar,
    kMove_Verb,
    kLine_Verb,
    kQuad_Verb,
    kConic_Verb,
    kCubic_Verb,
    kClose_Verb,
    kDone_Verb,
    kWinding_FillType,
    kEvenOdd_FillType,
    kInverseWinding_FillType,
    kInverseEvenOdd_FillType,
)
from ._skia.pathops cimport (
    Op,
    Simplify,
    SkOpBuilder,
    SkPathOp,
    kDifference_SkPathOp,
    kIntersect_SkPathOp,
    kUnion_SkPathOp,
    kXOR_SkPathOp,
    kReverseDifference_SkPathOp,
)
from .errors import (
    PathOpsError,
    UnsupportedVerbError,
    OpenPathError,
)
from enum import IntEnum


class PathOp(IntEnum):
    DIFFERENCE = kDifference_SkPathOp
    INTERSECTION = kIntersect_SkPathOp
    UNION = kUnion_SkPathOp
    XOR = kXOR_SkPathOp
    REVERSE_DIFFERENCE = kReverseDifference_SkPathOp


class FillType(IntEnum):
    WINDING = kWinding_FillType
    EVEN_ODD = kEvenOdd_FillType
    INVERSE_WINDING = kInverseWinding_FillType
    INVERSE_EVEN_ODD = kInverseEvenOdd_FillType


cdef class Path:

    cdef SkPath path
    cdef PathPen pen

    def __init__(self, other=None):
        if other is None:
            return
        if not isinstance(other, Path):
            other.draw(self.getPen())
            return
        cdef Path static_path = other
        self.path = SkPath(static_path.path)

    def getPen(self, allow_open_paths=True):
        return PathPen(self, allow_open_paths=allow_open_paths)

    def draw(self, pen):
        cdef SkPoint p[4]
        cdef SkPath.Verb verb
        cdef SkPath.Iter iterator = SkPath.Iter(self.path, False)
        cdef bint closed = False

        verb = iterator.next(p, False)
        if verb == kDone_Verb:
            return  # empty path
        assert verb == kMove_Verb
        pen.moveTo((p[0].x(), p[0].y()))

        verb = iterator.next(p, False)
        while verb != kDone_Verb:

            if verb == kMove_Verb:
                if not closed:
                    # skia contours starting with "moveTo" are implicitly
                    # open, unless they end with a "close" verb
                    pen.endPath()
                pen.moveTo((p[0].x(), p[0].y()))
                closed = False

            elif verb == kLine_Verb:
                pen.lineTo((p[1].x(), p[1].y()))

            elif verb == kCubic_Verb:
                pen.curveTo(
                    (p[1].x(), p[1].y()),
                    (p[2].x(), p[2].y()),
                    (p[3].x(), p[3].y()))

            elif verb == kQuad_Verb:
                pen.qCurveTo(
                    (p[1].x(), p[1].y()),
                    (p[2].x(), p[2].y()))

            elif verb == kConic_Verb:
                raise UnsupportedVerbError("conicTo")

            elif verb == kClose_Verb:
                pen.closePath()
                closed = True

            verb = iterator.next(p, False)

        if not closed:
            pen.endPath()

    def dump(self):
        # prints a text repesentation of SkPath to stdout
        self.path.dump()

    def addPath(self, Path path):
        self.path.addPath(path.path)

    @property
    def fillType(self):
        return FillType(self.path.getFillType())

    @fillType.setter
    def fillType(self, value):
        self.path.setFillType(FillType(value))

    @property
    def isConvex(self):
        return self.path.isConvex()


cdef class PathPen:

    cdef Path path
    cdef SkPath *path_ptr
    cdef bint allow_open_paths

    def __cinit__(self, Path path, bint allow_open_paths=True):
        # need to keep a reference to the parent Path object in case it's
        # garbage-collected before us and later we attempt to deref the
        # pointer to the wrapped SkPath instance
        self.path = path
        self.path_ptr = &path.path
        self.allow_open_paths = allow_open_paths

    cpdef moveTo(self, pt):
        self.path_ptr.moveTo(pt[0], pt[1])

    cpdef lineTo(self, pt):
        self.path_ptr.lineTo(pt[0], pt[1])

    cpdef curveTo(self, pt1, pt2, pt3):
        # support BasePen "super-beziers"? Nah.
        self.path_ptr.cubicTo(
            pt1[0], pt1[1],
            pt2[0], pt2[1],
            pt3[0], pt3[1])

    def qCurveTo(self, *points):
        for pt1, pt2 in decompose_quadratic_segment(points):
            self._qCurveToOne(pt1, pt2)

    cdef _qCurveToOne(self, pt1, pt2):
        self.path_ptr.quadTo(pt1[0], pt1[1], pt2[0], pt2[1])

    cpdef closePath(self):
        self.path_ptr.close()

    cpdef endPath(self):
        if not self.allow_open_paths:
            raise OpenPathError()

    cpdef addComponent(self, glyphName, transformation):
        pass


cdef list decompose_quadratic_segment(tuple points):
    cdef:
        int i, n = len(points) - 1
        list quad_segments = []
        SkScalar x, y, nx, ny
        tuple implied_pt

    assert n > 0
    for i in range(n - 1):
        x, y = points[i]
        nx, ny = points[i+1]
        implied_pt = (0.5 * (x + nx), 0.5 * (y + ny))
        quad_segments.append((points[i], implied_pt))
    quad_segments.append((points[-2], points[-1]))
    return quad_segments


cpdef Path op(Path one, Path two, SkPathOp operator):
    cdef Path result = Path()
    if Op(one.path, two.path, operator, &result.path):
        return result
    raise PathOpsError("operation did not succeed")


cpdef Path simplify(Path path):
    cdef Path result = Path()
    if Simplify(path.path, &result.path):
        return result
    raise PathOpsError("operation did not succeed")


cdef class OpBuilder:

    cdef SkOpBuilder builder

    cpdef add(self, Path path, SkPathOp operator):
        self.builder.add(path.path, operator)

    cpdef Path resolve(self):
        cdef Path result = Path()
        if self.builder.resolve(&result.path):
            return result
        raise PathOpsError("operation did not succeed")


cpdef fix_winding(Path path):
    cdef SkPath *skpath = &path.path
    if not SkOpBuilder.FixWinding(skpath):
        raise PathOpsError("failed to fix winding direction")
