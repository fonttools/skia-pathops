from ._skia.core cimport (
    SkPath,
    SkPoint,
    kMove_Verb,
    kLine_Verb,
    kQuad_Verb,
    kConic_Verb,
    kCubic_Verb,
    kClose_Verb,
    kDone_Verb
)
from ._skia.pathops cimport SkOpBuilder, kUnion_SkPathOp


cdef class Path:

    cdef SkPath path
    cdef PathPen pen

    def __cinit__(self):
        self.pen = PathPen(self)

    def __init__(self, other_path=None):
        if other_path is None:
            return
        cdef Path static_path = other_path
        self.path = SkPath(static_path.path)

    def getPen(self):
        return self.pen

    def draw(self, pen):
        cdef SkPoint p[4]
        cdef SkPath.Verb verb
        cdef SkPath.Iter iterator = SkPath.Iter(self.path, False)

        verb = iterator.next(p, False)
        while verb != kDone_Verb:
            if verb == kMove_Verb:
                pen.moveTo((p[0].x(), p[0].y()))
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
                raise ValueError("conic is unsupported")
            elif verb == kClose_Verb:
                pen.closePath()
            verb = iterator.next(p, False)

    def dump(self):
        # prints a text repesentation of SkPath to stdout
        self.path.dump()


cdef class PathPen:

    cdef SkPath *path_ptr

    def __cinit__(self, Path path):
        self.path_ptr = &path.path

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

    cpdef qCurveTo(self, pt1, pt2):
        # TODO TrueType spline can have multiple offcurves, split
        # into atomic quadratic curves
        self.path_ptr.quadTo(pt1[0], pt1[1], pt2[0], pt2[1])

    cpdef closePath(self):
        self.path_ptr.close()

    cpdef endPath(self):
        # XXX can a SkPath be "open"? How does SkOpBuilder handles them?
        pass

    cpdef addComponent(self, glyphName, transformation):
        pass


cpdef int demo():
    cdef SkOpBuilder builder
    cdef SkPath path1, path2, result
    cdef SkPath.Iter iterator
    cdef SkPoint p[4]
    cdef SkPath.Verb verb
    cdef bint ok = 0

    path1.moveTo(5, -225)
    path1.lineTo(-225, 7425)
    path1.lineTo(7425, 7425)
    path1.lineTo(7425, -225)
    path1.lineTo(-225, -225)
    path1.lineTo(5, -225)
    path1.close()

    path2.moveTo(5940, 2790)
    path2.lineTo(5940, 2160)
    path2.lineTo(5970, 1980)
    path2.lineTo(5688, 773669888)
    path2.lineTo(5688, 2160)
    path2.lineTo(5688, 2430)
    path2.lineTo(5400, 4590)
    path2.lineTo(5220, 4590)
    path2.lineTo(5220, 4920)
    path2.cubicTo(5182.22900390625, 4948.328125, 5160,
                  4992.78662109375, 5160, 5040.00048828125)
    path2.lineTo(5940, 2790)
    path2.close()

    builder.add(path1, kUnion_SkPathOp)
    builder.add(path2, kUnion_SkPathOp)
    ok = builder.resolve(&result)

    iterator = SkPath.Iter(result, False)

    if ok:
        verb = iterator.next(p, False)
        while verb != kDone_Verb:
            if verb == kMove_Verb:
                print("moveTo (%g, %g)" % (p[0].x(), p[0].y()))
            elif verb == kLine_Verb:
                print("lineTo (%g, %g)" % (p[1].x(), p[1].y()))
            elif verb == kCubic_Verb:
                print("cubicTo (%g, %g) (%g, %g) (%g, %g)" % (
                    p[1].x(), p[1].y(),
                    p[2].x(), p[2].y(),
                    p[3].x(), p[3].y()))
            elif verb == kQuad_Verb:
                print("quadTo (%g, %g) (%g, %g)" % (
                    p[1].x(), p[1].y(), p[2].x(), p[2].y()))
            elif verb == kConic_Verb:
                print("conicTo (%g, %g) (%g, %g) (%g)" % (
                    p[1].x(), p[1].y(), p[2].x(), p[2].y(),
                    iterator.conicWeight()))
            elif verb == kClose_Verb:
                print("close")
            elif verb == kDone_Verb:
                pass
            else:
                raise RuntimeError("unknown verb: %d" % int(verb))
            verb = iterator.next(p, False)

    return ok
