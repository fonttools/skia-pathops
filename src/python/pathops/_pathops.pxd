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
    SkOpBuilder,
    SkPathOp,
    kDifference_SkPathOp,
    kIntersect_SkPathOp,
    kUnion_SkPathOp,
    kXOR_SkPathOp,
    kReverseDifference_SkPathOp,
)
from libc.stdint cimport uint8_t
from libc.float cimport FLT_EPSILON


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


cdef Path new_path(SkPath skpath)


cdef class Path:

    cdef SkPath path

    cpdef PathPen getPen(self, bint allow_open_paths=*)

    cpdef bint add(self, PathVerb verb, tuple pts) except False

    cpdef void moveTo(self, SkScalar x, SkScalar y)

    cpdef void lineTo(self, SkScalar x, SkScalar y)

    cpdef void quadTo(
        self,
        SkScalar x1,
        SkScalar y1,
        SkScalar x2,
        SkScalar y2
    )

    cpdef void conicTo(
        self,
        SkScalar x1,
        SkScalar y1,
        SkScalar x2,
        SkScalar y2,
        SkScalar w
    )

    cpdef void cubicTo(
        self,
        SkScalar x1,
        SkScalar y1,
        SkScalar x2,
        SkScalar y2,
        SkScalar x3,
        SkScalar y3,
    )

    cpdef void close(self)

    cpdef void reset(self)

    cpdef void rewind(self)

    cpdef draw(self, pen)

    cpdef addPath(self, Path path)

    cpdef reverse(self)

    cpdef simplify(self, bint fix_winding=*, keep_starting_points=*)

    cdef list getVerbs(self)

    cdef list getPoints(self)

    cdef int countContours(self) except -1

    cdef int getFirstPoints(self, SkPoint **pp, int *count) except -1


cpdef enum PathVerb:
    MOVE = kMove_Verb
    LINE = kLine_Verb
    QUAD = kQuad_Verb
    CONIC = kConic_Verb  # unsupported
    CUBIC = kCubic_Verb
    CLOSE = kClose_Verb
    DONE = kDone_Verb  # unused; we raise StopIteration instead


cdef uint8_t *POINTS_IN_VERB

cpdef dict VERB_METHODS

cpdef dict PEN_METHODS


cdef class PathIterator:

    cdef Path path
    cdef SkPath.RawIter iterator

    cpdef PathVerb peek(self)


cdef class PathPen:

    cdef Path path
    cdef bint allow_open_paths

    cpdef moveTo(self, pt)

    cpdef lineTo(self, pt)

    cpdef curveTo(self, pt1, pt2, pt3)

    # def qCurveTo(self, *points)

    cdef _qCurveToOne(self, pt1, pt2)

    cpdef closePath(self)

    cpdef endPath(self)

    cpdef addComponent(self, glyphName, transformation)


cdef double get_path_area(const SkPath& path) except? FLT_EPSILON


cdef class _VerbArray:

    cdef uint8_t *data
    cdef int count


cdef class _SkPointArray:

    cdef SkPoint *data
    cdef int count


cdef int pts_in_verb(unsigned v) except -1


cdef bint reverse_contour(Path path) except False


cdef int path_is_inside(const SkPath& self, const SkPath& other) except -1


cpdef int restore_starting_points(Path path, list points) except -1


cpdef bint winding_from_even_odd(Path path, bint truetype=*) except False


cdef list decompose_quadratic_segment(tuple points)


cdef double ROUGH_EPSILON


cdef bint almost_equal(SkScalar v1, SkScalar v2)


cdef list join_quadratic_segments(list quad_segments)


cdef int find_oncurve_point(
    SkScalar x,
    SkScalar y,
    const SkPoint *pts,
    int pt_count,
    const uint8_t *verbs,
    int verb_count,
    int *pt_index,
    int *verb_index,
) except -1


cdef int contour_is_closed(const uint8_t *verbs, int verb_count) except -1


cpdef int set_contour_start_point(Path path, SkScalar x, SkScalar y) except -1


cpdef Path op(
    Path one,
    Path two,
    SkPathOp operator,
    fix_winding=*,
    keep_starting_points=*,
)


cpdef Path simplify(Path path, fix_winding=*, keep_starting_points=*)


cdef class OpBuilder:

    cdef SkOpBuilder builder
    cdef bint fix_winding
    cdef bint keep_starting_points
    cdef list first_points

    cpdef add(self, Path path, SkPathOp operator)

    cpdef Path resolve(self)
