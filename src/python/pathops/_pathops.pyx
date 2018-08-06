from ._skia.core cimport (
    SkPath,
    SkPoint,
    SkScalar,
    SkRect,
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
from libc.stdint cimport uint8_t
from libc.stdlib cimport malloc, free
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


cdef Path new_path(SkPath skpath):
    cdef Path p = Path()
    p.path = SkPath(skpath)
    return p


cdef class Path:

    cdef SkPath path
    cdef PathPen pen

    def __init__(self, other=None, fillType=None):
        if fillType is not None:
            self.fillType = fillType
        if other is None:
            return
        if not isinstance(other, Path):
            other.draw(self.getPen())
            return
        cdef Path static_path = other
        self.path = SkPath(static_path.path)

    cpdef PathPen getPen(self, bint allow_open_paths=True):
        return PathPen(self, allow_open_paths=allow_open_paths)

    def __iter__(self):
        return PathIterator(self)

    cpdef draw(self, pen):
        cdef tuple pts
        cdef bint closed = True

        for verb, pts in self:
            method = getattr(pen, PEN_METHODS[verb.value])
            if verb is PathVerb.MOVE:
                if not closed:
                    # skia contours starting with "moveTo" are implicitly
                    # open, unless they end with a "close" verb
                    pen.endPath()
                method(*pts)
                closed = False
            elif verb is PathVerb.CLOSE:
                method()
                closed = True
            else:
                method(*pts)

        if not closed:
            pen.endPath()

    def dump(self):
        # prints a text repesentation of SkPath to stdout
        self.path.dump()

    cpdef addPath(self, Path path):
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

    def contains(self, tuple pt):
        return self.path.contains(pt[0], pt[1])

    @property
    def bounds(self):
        cdef SkRect r = self.path.getBounds()
        return (r.left(), r.top(), r.right(), r.bottom())

    cpdef simplify(self, fix_winding=True):
        if not Simplify(self.path, &self.path):
            raise PathOpsError("simplify operation did not succeed")
        if fix_winding:
            self.fix_winding()

    cpdef fix_winding(self):
        if not SkOpBuilder.FixWinding(&self.path):
            raise PathOpsError("failed to fix winding direction")

    cdef list getVerbs(self):
        cdef int i, count
        cdef uint8_t *verbs
        count = self.path.countVerbs()
        verbs = <uint8_t *> malloc(count)
        if not verbs:
            raise MemoryError()
        try:
            assert self.path.getVerbs(verbs, count) == count
            return [PathVerb(verbs[i]) for i in range(count)]
        finally:
            free(verbs)

    @property
    def verbs(self):
        return self.getVerbs()

    cdef list getPoints(self):
        cdef int i, count
        cdef SkPoint *pts
        count = self.path.countPoints()
        pts = <SkPoint *> malloc(count * sizeof(SkPoint))
        if not pts:
            raise MemoryError()
        try:
            assert self.path.getPoints(pts, count) == count
            return [(pts[i].x(), pts[i].y()) for i in range(count)]
        finally:
            free(pts)

    @property
    def points(self):
        return self.getPoints()

    @property
    def contours(self):
        cdef SkPath temp
        temp.setFillType(self.path.getFillType())

        cdef SkPath.Verb verb
        cdef SkPoint p[4]
        cdef SkPath.Iter iterator = SkPath.Iter(self.path, False)

        while True:
            verb = iterator.next(p, False)
            if verb == kMove_Verb:
                if not temp.isEmpty():
                    yield new_path(temp)
                    temp.rewind()
                temp.moveTo(p[0])
            elif verb == kLine_Verb:
                temp.lineTo(p[1])
            elif verb == kQuad_Verb:
                temp.quadTo(p[1], p[2])
            elif verb == kConic_Verb:
                temp.conicTo(p[1], p[2], iterator.conicWeight())
            elif verb == kCubic_Verb:
                temp.cubicTo(p[1], p[2], p[3])
            elif verb == kClose_Verb:
                temp.close()
                yield new_path(temp)
                temp.rewind()
            elif verb == kDone_Verb:
                if not temp.isEmpty():
                    yield new_path(temp)
                    temp.reset()
                break
            else:
                raise AssertionError(verb)


class PathVerb(IntEnum):
    MOVE = kMove_Verb
    LINE = kLine_Verb
    QUAD = kQuad_Verb
    CONIC = kConic_Verb  # unsupported
    CUBIC = kCubic_Verb
    CLOSE = kClose_Verb
    DONE = kDone_Verb  # unused; we raise StopIteration instead


cdef dict PEN_METHODS = {
    kMove_Verb: "moveTo",
    kLine_Verb: "lineTo",
    kQuad_Verb: "qCurveTo",
    kCubic_Verb: "curveTo",
    kClose_Verb: "closePath",
}


cdef class PathIterator:

    cdef Path path
    cdef SkPath.Iter iterator
    cdef bint doConsumeDegenerates
    cdef bint exact

    def __cinit__(
        self,
        Path path,
        bint forceClose=False,
        bint doConsumeDegenerates=False,
        bint exact=False,
    ):
        self.path = path
        self.iterator = SkPath.Iter(self.path.path, forceClose)
        self.doConsumeDegenerates = doConsumeDegenerates
        self.exact = exact

    def __iter__(self):
        return self

    def __next__(self):
        cdef tuple pts
        cdef SkPath.Verb verb
        cdef SkPoint p[4]

        verb = self.iterator.next(p, self.doConsumeDegenerates, self.exact)

        if verb == kMove_Verb:
            pts = ((p[0].x(), p[0].y()),)
        elif verb == kLine_Verb:
            pts = ((p[1].x(), p[1].y()),)
        elif verb == kQuad_Verb:
            pts = ((p[1].x(), p[1].y()),
                   (p[2].x(), p[2].y()))
        elif verb == kConic_Verb:
            pts = ((p[1].x(), p[1].y()),
                   (p[2].x(), p[2].y()),
                   self.iterator.conicWeight())
        elif verb == kCubic_Verb:
            pts = ((p[1].x(), p[1].y()),
                   (p[2].x(), p[2].y()),
                   (p[3].x(), p[3].y()))
        elif verb == kClose_Verb:
            pts = ()
        elif verb == kDone_Verb:
            raise StopIteration()
        else:
            raise UnsupportedVerbError(verb)

        return (PathVerb(verb), pts)


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


cpdef Path op(Path one, Path two, SkPathOp operator, fix_winding=True):
    cdef Path result = Path()
    if not Op(one.path, two.path, operator, &result.path):
        raise PathOpsError("operation did not succeed")
    if fix_winding:
        result.fix_winding()
    return result


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


cpdef Path fix_winding(Path path):
    cdef Path copy = Path(path)
    if not SkOpBuilder.FixWinding(&copy.path):
        raise PathOpsError("failed to fix winding direction")
    return copy


cpdef bint bounds_intersect(Path self, Path other):
    return SkRect.Intersects(
        self.path.getBounds(),
        other.path.getBounds(),
    )
