from ._skia.core cimport (
    SkArcSize,
    SkLineCap,
    SkLineJoin,
    SkPath,
    SkPathBuilder,
    SkPathFillType,
    SkPathIter,
    SkPathVerb,
    SkPoint,
    SkScalar,
    SkSpan,
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
from libcpp.optional cimport optional


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
    SMALL = <uint32_t>SkArcSize.kSmall_ArcSize
    LARGE = <uint32_t>SkArcSize.kLarge_ArcSize


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

    cdef SkPathBuilder path

    @staticmethod
    cdef Path create(const SkPathBuilder& path)

    cpdef PathPen getPen(self, object glyphSet=*, bint allow_open_paths=*)

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

    cpdef simplify(
        self,
        bint fix_winding=*,
        bint keep_starting_points=*,
        bint clockwise=*,
    )

    cpdef convertConicsToQuads(self, float tolerance=*)

    cpdef stroke(
        self,
        SkScalar width,
        LineCap cap,
        LineJoin join,
        SkScalar miter_limit,
        object dash_array=*,
        SkScalar dash_offset=*,
    )

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
    MOVE = <uint8_t>SkPathVerb.kMove
    LINE = <uint8_t>SkPathVerb.kLine
    QUAD = <uint8_t>SkPathVerb.kQuad
    CONIC = <uint8_t>SkPathVerb.kConic  # unsupported
    CUBIC = <uint8_t>SkPathVerb.kCubic
    CLOSE = <uint8_t>SkPathVerb.kClose


cdef uint8_t *POINTS_IN_VERB

cdef dict VERB_METHODS

cdef dict PEN_METHODS


cdef class RawPathIterator:

    cdef Path path
    cdef optional[SkPathIter] iterator


cdef class SegmentPenIterator:

    cdef Path path
    cdef const SkPoint *pts
    cdef const SkPathVerb *verbs
    cdef const SkPathVerb *verb_stop
    cdef SkPoint move_pt
    cdef bint closed

    cdef bint nextIsClose(self)

    cdef tuple _join_quadratic_segments(self)


cdef class PathPen:

    cdef Path path
    cdef object glyphSet
    cdef bint allow_open_paths

    cpdef moveTo(self, pt)

    cpdef lineTo(self, pt)

    # def curveTo(self, *points)

    # def qCurveTo(self, *points)

    cdef _qCurveToOne(self, pt1, pt2)

    cpdef closePath(self)

    cpdef endPath(self)

    cpdef addComponent(self, glyphName, transformation)


cdef double get_path_area(const SkPathBuilder& path) except? -1234567


cdef class _SkScalarArray:

    cdef SkScalar *data
    cdef int count

    @staticmethod
    cdef _SkScalarArray create(object values)

    cdef SkSpan[SkScalar] as_span(self)


cdef int pts_in_verb(SkPathVerb v) except -1


cdef bint reverse_contour(SkPathBuilder& path) except False


cdef int path_is_inside(const SkPathBuilder& self, const SkPathBuilder& other) except -1


cpdef int restore_starting_points(Path path, list points) except -1


cpdef bint winding_from_even_odd(Path path, bint clockwise=*) except False


cdef list _decompose_quadratic_segment(tuple points)


cdef int find_oncurve_point(
    SkScalar x,
    SkScalar y,
    const SkPoint *pts,
    int pt_count,
    const SkPathVerb *verbs,
    int verb_count,
    int *pt_index,
    int *verb_index,
) except -1


cdef int contour_is_closed(SkSpan[const SkPathVerb] verbs) except -1


cdef int set_contour_start_point(SkPathBuilder& path, SkScalar x, SkScalar y) except -1


cdef int compute_conic_to_quad_pow2(
    SkPoint p0, SkPoint p1, SkPoint p2, SkScalar weight, SkScalar tol
) except -1


cpdef Path op(
    Path one,
    Path two,
    SkPathOp operator,
    bint fix_winding=*,
    bint keep_starting_points=*,
    bint clockwise=*,
)


cpdef Path simplify(
    Path path,
    bint fix_winding=*,
    bint keep_starting_points=*,
    bint clockwise=*,
)


cdef class OpBuilder:

    cdef SkOpBuilder builder
    cdef bint fix_winding
    cdef bint keep_starting_points
    cdef list first_points
    cdef bint clockwise

    cpdef add(self, Path path, SkPathOp operator)

    cpdef Path resolve(self)
