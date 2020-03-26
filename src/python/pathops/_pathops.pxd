from ._skia.core cimport (
    SkLineCap,
    SkLineJoin,
    SkPath,
    SkPathFillType,
    SkPoint,
    SkScalar,
    kMove_Verb,
    kLine_Verb,
    kQuad_Verb,
    kConic_Verb,
    kCubic_Verb,
    kClose_Verb,
    kDone_Verb,
    kSmall_ArcSize,
    kLarge_ArcSize,
    SkPathDirection,
    SkMatrix,
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
from libc.stdint cimport uint8_t, int32_t, uint32_t


cpdef enum PathOp:
    DIFFERENCE = kDifference_SkPathOp
    INTERSECTION = kIntersect_SkPathOp
    UNION = kUnion_SkPathOp
    XOR = kXOR_SkPathOp
    REVERSE_DIFFERENCE = kReverseDifference_SkPathOp


cpdef enum FillType:
    WINDING = <uint32_t>SkPathFillType.kWinding
    EVEN_ODD = <uint32_t>SkPathFillType.kEvenOdd
    INVERSE_WINDING = <uint32_t>SkPathFillType.kInverseWinding
    INVERSE_EVEN_ODD = <uint32_t>SkPathFillType.kInverseEvenOdd


cpdef enum LineCap:
    BUTT_CAP = <uint32_t>SkLineCap.kButt_Cap,
    ROUND_CAP = <uint32_t>SkLineCap.kRound_Cap,
    SQUARE_CAP =  <uint32_t>SkLineCap.kSquare_Cap

cpdef enum LineJoin:
    MITER_JOIN = <uint32_t>SkLineJoin.kMiter_Join,
    ROUND_JOIN = <uint32_t>SkLineJoin.kRound_Join,
    BEVEL_JOIN = <uint32_t>SkLineJoin.kBevel_Join


cpdef enum ArcSize:
    SMALL = kSmall_ArcSize
    LARGE = kLarge_ArcSize


cpdef enum Direction:
    CW = <uint32_t>SkPathDirection.kCW
    CCW = <uint32_t>SkPathDirection.kCCW


cdef union FloatIntUnion:
    float Float
    int32_t SignBitInt


cdef int32_t _float2bits(float x)


cdef float _bits2float(int32_t float_as_bits)


cdef float SCALAR_NEARLY_ZERO_SQD


cdef bint can_normalize(SkScalar dx, SkScalar dy)


cdef bint points_almost_equal(const SkPoint& p1, const SkPoint& p2)


cdef bint is_middle_point(
    const SkPoint& p1, const SkPoint& p2, const SkPoint& p3
)


cdef bint collinear(
    const SkPoint& p1, const SkPoint& p2, const SkPoint& p3
)


cdef class Path:

    cdef SkPath path

    @staticmethod
    cdef Path create(const SkPath& path)

    cpdef PathPen getPen(self, bint allow_open_paths=*)

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

    cpdef void arcTo(
        self,
        SkScalar rx,
        SkScalar ry,
        SkScalar xAxisRotate,
        ArcSize largeArc,
        Direction sweep,
        SkScalar x,
        SkScalar y,
    )

    cpdef void close(self)

    cpdef void reset(self)

    cpdef void rewind(self)

    cpdef draw(self, pen)

    cpdef addPath(self, Path path)

    cpdef reverse(self)

    cpdef simplify(self, bint fix_winding=*, keep_starting_points=*)

    cpdef convertConicsToQuads(self, float tolerance=*)

    cpdef stroke(self, SkScalar width, LineCap cap, LineJoin join, SkScalar miter_limit)

    cdef list getVerbs(self)

    cdef list getPoints(self)

    cdef int countContours(self) except -1

    cdef int getFirstPoints(self, SkPoint **pp, int *count) except -1

    cpdef Path transform(
        self,
        SkScalar scaleX=*,
        SkScalar skewY=*,
        SkScalar skewX=*,
        SkScalar scaleY=*,
        SkScalar translateX=*,
        SkScalar translateY=*,
        SkScalar perspectiveX=*,
        SkScalar perspectiveY=*,
        SkScalar perspectiveBias=*,
    )


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


cdef class RawPathIterator:

    cdef Path path
    cdef SkPath.RawIter iterator


cdef class SegmentPenIterator:

    cdef _SkPointArray pa
    cdef SkPoint *pts
    cdef _VerbArray va
    cdef uint8_t *verbs
    cdef uint8_t *verb_stop
    cdef SkPoint move_pt
    cdef bint closed

    cdef uint8_t peek(self)

    cdef tuple _join_quadratic_segments(self)


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


cdef double get_path_area(const SkPath& path) except? -1234567


cdef class _VerbArray:

    cdef uint8_t *data
    cdef int count

    @staticmethod
    cdef _VerbArray create(const SkPath& path)


cdef class _SkPointArray:

    cdef SkPoint *data
    cdef int count

    @staticmethod
    cdef _SkPointArray create(const SkPath& path)


cdef int pts_in_verb(unsigned v) except -1


cdef bint reverse_contour(SkPath& path) except False


cdef int path_is_inside(const SkPath& self, const SkPath& other) except -1


cpdef int restore_starting_points(Path path, list points) except -1


cpdef bint winding_from_even_odd(Path path, bint truetype=*) except False


cdef list _decompose_quadratic_segment(tuple points)


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


cdef int set_contour_start_point(SkPath& path, SkScalar x, SkScalar y) except -1


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
