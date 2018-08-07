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


cpdef enum PathOp:
    DIFFERENCE = kDifference_SkPathOp
    INTERSECTION = kIntersect_SkPathOp
    UNION = kUnion_SkPathOp
    XOR = kXOR_SkPathOp
    REVERSE_DIFFERENCE = kReverseDifference_SkPathOp


cpdef enum FillType:
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

    cpdef bint add(self, PathVerb verb, tuple pts) except False:
        if verb is PathVerb.MOVE:
            self.path.moveTo(pts[0][0], pts[0][1])
        elif verb is PathVerb.LINE:
            self.path.lineTo(pts[0][0], pts[0][1])
        elif verb is PathVerb.QUAD:
            self.path.quadTo(pts[0][0], pts[0][1],
                             pts[1][0], pts[1][1])
        elif verb is PathVerb.CONIC:
            self.path.conicTo(pts[0][0], pts[0][1],
                              pts[1][0], pts[1][1], pts[2])
        elif verb is PathVerb.CUBIC:
            self.path.cubicTo(pts[0][0], pts[0][1],
                              pts[1][0], pts[1][1],
                              pts[2][0], pts[2][1])
        elif verb is PathVerb.CLOSE:
            self.path.close()
        else:
            raise AssertionError(verb)
        return True

    cpdef void moveTo(self, SkScalar x, SkScalar y):
        self.path.moveTo(x, y)

    cpdef void lineTo(self, SkScalar x, SkScalar y):
        self.path.lineTo(x, y)

    cpdef void quadTo(
        self,
        SkScalar x1,
        SkScalar y1,
        SkScalar x2,
        SkScalar y2
    ):
        self.path.quadTo(x1, y1, x2, y2)

    cpdef void conicTo(
        self,
        SkScalar x1,
        SkScalar y1,
        SkScalar x2,
        SkScalar y2,
        SkScalar w
    ):
        self.path.conicTo(x1, y2, x2, y2, w)

    cpdef void cubicTo(
        self,
        SkScalar x1,
        SkScalar y1,
        SkScalar x2,
        SkScalar y2,
        SkScalar x3,
        SkScalar y3,
    ):
        self.path.cubicTo(x1, y1, x2, y2, x3, y3)

    cpdef void close(self):
        self.path.close()

    cpdef void reset(self):
        self.path.reset()

    cpdef void rewind(self):
        self.path.rewind()

    cpdef draw(self, pen):
        cdef PathVerb verb
        cdef tuple pts
        cdef bint closed = True
        cdef PathIterator iterator = iter(self)

        for verb, pts in iterator:
            try:
                method = getattr(pen, PEN_METHODS[verb])
            except KeyError:
                raise UnsupportedVerbError(PathVerb(verb).name)
            if verb is PathVerb.MOVE:
                if not closed:
                    # skia contours starting with "moveTo" are implicitly
                    # open, unless they end with a "close" verb
                    pen.endPath()
                closed = False
            elif verb is PathVerb.CLOSE:
                closed = True
            # TODO: join quadratic curve segments using TrueType implied
            # on-curve points, reversing the `decompose_quadratic_segment`
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
        cdef SkPath.RawIter iterator = SkPath.RawIter(self.path)

        while True:
            verb = iterator.next(p)
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


cpdef enum PathVerb:
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
    cdef SkPath.RawIter iterator

    def __cinit__(self, Path path):
        self.path = path
        self.iterator = SkPath.RawIter(self.path.path)

    def __iter__(self):
        return self

    def __next__(self):
        cdef tuple pts
        cdef SkPath.Verb verb
        cdef SkPoint p[4]

        verb = self.iterator.next(p)

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

    cpdef PathVerb peek(self):
        return PathVerb(self.iterator.peek())


cdef class PathPen:

    cdef Path path
    cdef bint allow_open_paths

    def __cinit__(self, Path path, bint allow_open_paths=True):
        self.path = path
        self.allow_open_paths = allow_open_paths

    cpdef moveTo(self, pt):
        self.path.moveTo(pt[0], pt[1])

    cpdef lineTo(self, pt):
        self.path.lineTo(pt[0], pt[1])

    cpdef curveTo(self, pt1, pt2, pt3):
        # support BasePen "super-beziers"? Nah.
        self.path.cubicTo(
            pt1[0], pt1[1],
            pt2[0], pt2[1],
            pt3[0], pt3[1])

    def qCurveTo(self, *points):
        for pt1, pt2 in decompose_quadratic_segment(points):
            self._qCurveToOne(pt1, pt2)

    cdef _qCurveToOne(self, pt1, pt2):
        self.path.quadTo(pt1[0], pt1[1], pt2[0], pt2[1])

    cpdef closePath(self):
        self.path.close()

    cpdef endPath(self):
        if not self.allow_open_paths:
            raise OpenPathError()

    cpdef addComponent(self, glyphName, transformation):
        pass


cpdef Path reverse_contour(Path path):
    cdef:
        Path result
        PathVerb firstType, secondType, lastType, v, curType
        tuple firstPts, lastPts, firstOnCurve, lastOnCurve, secondPts
        tuple curPts, nextPts
        bint closed
        int i, j
        list contour, revPts

    result = Path()
    contour = list(path)
    if not contour:
        return result  # empty, nothing to reverse

    firstType, firstPts = contour.pop(0)
    assert firstType == PathVerb.MOVE
    for i in range(1, len(contour)):
        v = contour[i][0]
        if v == PathVerb.MOVE:
            raise ValueError("cannot reverse multiple-contour paths")
        elif v == PathVerb.CONIC:
            raise UnsupportedVerbError("CONIC")

    if not contour:
        closed = False
    else:
        closed = contour[-1][0] == PathVerb.CLOSE
        if closed:
            del contour[-1]

    firstOnCurve = firstPts[-1]
    if not contour:
        # contour contains only one segment, nothing to reverse
        result.add(firstType, firstPts)
    else:
        lastType, lastPts = contour[-1]
        lastOnCurve = lastPts[-1]
        if closed:
            # for closed paths, we keep the starting point
            result.add(firstType, firstPts)
            if firstOnCurve != lastOnCurve:
                # emit an implied line between the last and first points
                result.add(PathVerb.LINE, (lastOnCurve,))
                contour[-1] = (lastType, tuple(lastPts[:-1]) + (firstOnCurve,))

            if len(contour) > 1:
                secondType, secondPts = contour[0]
            else:
                # contour has only two points, the second and last are the same
                secondType, secondPts = lastType, lastPts
            # if a lineTo follows the initial moveTo, after reversing it
            # will be implied by the closePath, so we don't emit one;
            # unless the lineTo and moveTo overlap, in which case we keep the
            # duplicate points
            if secondType == PathVerb.LINE and firstPts != secondPts:
                del contour[0]
                if contour:
                    contour[-1] = (lastType, tuple(lastPts[:-1]) + secondPts)
        else:
            # for open paths, the last point will become the first
            result.add(firstType, (lastOnCurve,))
            contour[-1] = (lastType, tuple(lastPts[:-1]) + (firstOnCurve,))

        # we iterate over all segment pairs in reverse order, and add
        # each one with the off-curve points reversed (if any), and
        # with the on-curve point of the following segment
        for i in range(len(contour)-1, -1, -1):
            curType, curPts = contour[i]
            nextPts = contour[i-1][1]
            revPts = []
            for j in range(len(curPts)-2, -1, -1):
                revPts.append(curPts[j])
            revPts.append(nextPts[-1])
            result.add(curType, tuple(revPts))

    if closed:
        result.add(PathVerb.CLOSE, ())

    return result


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
