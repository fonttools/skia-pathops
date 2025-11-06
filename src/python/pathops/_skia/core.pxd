from libc.stdint cimport uint8_t
from libcpp.optional cimport optional


ctypedef float SkScalar

cdef extern from "include/core/SkSpan.h":
    cdef cppclass SkSpan[T]:
        SkSpan[T] subspan(size_t offset) const
        T& operator[](size_t) const
        bint empty() const
        size_t size() const
        T* data() const
        T* begin() const
        T* end() const


cdef extern from "include/core/SkPathTypes.h":

    enum SkPathFillType:
        kWinding "SkPathFillType::kWinding",
        kEvenOdd "SkPathFillType::kEvenOdd",
        kInverseWinding "SkPathFillType::kInverseWinding",
        kInverseEvenOdd "SkPathFillType::kInverseEvenOdd"

    enum SkPathDirection:
        kCW "SkPathDirection::kCW"
        kCCW "SkPathDirection::kCCW"

    enum class SkPathVerb(uint8_t):
        kMove "SkPathVerb::kMove"
        kLine "SkPathVerb::kLine"
        kQuad "SkPathVerb::kQuad"
        kConic "SkPathVerb::kConic"
        kCubic "SkPathVerb::kCubic"
        kClose "SkPathVerb::kClose"


cdef extern from "include/core/SkMatrix.h":
    cdef cppclass SkMatrix:
        SkMatrix() except +

        @staticmethod
        SkMatrix MakeAll(
            SkScalar scaleX,
            SkScalar skewX,
            SkScalar transX,
            SkScalar skewY,
            SkScalar scaleY,
            SkScalar transY,
            SkScalar pers0,
            SkScalar pers1,
            SkScalar pers2,
        )


cdef extern from "include/core/SkPoint.h":

    cdef cppclass SkPoint:

        @staticmethod
        SkPoint Make(SkScalar x, SkScalar y)

        SkScalar x()
        SkScalar y()

        bint equals(SkScalar x, SkScalar y)

        bint operator==(const SkPoint& other)

        bint operator!=(const SkPoint& other)


cdef extern from "include/core/SkPath.h":

    cdef cppclass SkPath:

        SkPath() except +
        SkPath(SkPath& path) except +

        bint operator==(const SkPath& other)

        bint operator!=(const SkPath& other)

        void dump()

        void dumpHex()

        SkPathFillType getFillType()

        bint isConvex()

        bint contains(SkScalar x, SkScalar y)

        const SkRect& getBounds()

        SkRect computeTightBounds()

        int countPoints()

        SkPoint getPoint(int index)

        int getPoints(SkPoint points[], int maximum)

        int countVerbs()

        bint isEmpty()

        int getVerbs(uint8_t verbs[], int maximum)

        bint getLastPt(SkPoint* lastPt)


cdef extern from * namespace "SkPath":

    cdef int ConvertConicToQuads(const SkPoint& p0, const SkPoint& p1,
                                 const SkPoint& p2, SkScalar w,
                                 SkPoint pts[], int pow2)


cdef extern from "include/core/SkPathIter.h":

    cdef cppclass SkPathIter:

        cppclass Rec:
            SkSpan[const SkPoint] fPoints
            SkPathVerb fVerb
            float conicWeight() const

        optional[Rec] next()


cdef extern from "include/core/SkPathBuilder.h":

    enum SkArcSize "SkPathBuilder::ArcSize":
        kSmall_ArcSize "SkPathBuilder::kSmall_ArcSize"
        kLarge_ArcSize "SkPathBuilder::kLarge_ArcSize"

    cdef cppclass SkPathBuilder:

        SkPathBuilder() except +
        SkPathBuilder(SkPath& path) except +
        SkPathBuilder(SkPathBuilder& path) except +
        SkPathBuilder& operator=(const SkPath&)
        SkPathBuilder& operator=(const SkPathBuilder&)

        bint operator==(const SkPathBuilder&)

        bint operator!=(const SkPathBuilder&)

        enum class DumpFormat "SkPathBuilder::DumpFormat":
            kDecimal "SkPathBuilder::DumpFormat::kDecimal",
            kHex "SkPathBuilder::DumpFormat::kHex"
        void dump(DumpFormat)

        void moveTo(SkScalar x, SkScalar y)
        void moveTo(const SkPoint& p)

        void lineTo(SkScalar x, SkScalar y)
        void lineTo(const SkPoint& p)

        void cubicTo(
            SkScalar x1, SkScalar y1,
            SkScalar x2, SkScalar y2,
            SkScalar x3, SkScalar y3)
        void cubicTo(const SkPoint& p1, const SkPoint& p2, const SkPoint& p3)

        void quadTo(SkScalar x1, SkScalar y1, SkScalar x2, SkScalar y2)
        void quadTo(const SkPoint& p1, const SkPoint& p2)

        void conicTo(SkScalar x1, SkScalar y1, SkScalar x2, SkScalar y2,
                     SkScalar w)
        void conicTo(const SkPoint& p1, const SkPoint& p2, SkScalar w)

        void arcTo(const SkPoint& r, SkScalar xAxisRotate, SkArcSize largeArc,
                   SkPathDirection sweep, const SkPoint& xy)

        void close()

        void transform(const SkMatrix& matrix)

        void reset()

        SkPath detach()
        SkPath snapshot()

        void setFillType(SkPathFillType ft)
        SkPathFillType fillType()

        # TODO also expose optional AddPathMode enum
        void addPath(const SkPath& src) except +

        bint contains(SkPoint)

        optional[SkRect] computeFiniteBounds()

        optional[SkRect] computeTightBounds()

        bint isEmpty() const

        SkSpan[const SkPoint] points() const

        optional[SkPoint] getLastPt() const

        SkSpan[const SkPathVerb] verbs() const

        SkPathIter iter() const


cdef extern from "include/core/SkRect.h":

    cdef cppclass SkRect:

        SkScalar left()
        SkScalar top()
        SkScalar right()
        SkScalar bottom()

        @staticmethod
        bint Intersects(const SkRect& a, const SkRect& b)


cdef extern from "include/core/SkScalar.h":

    cdef enum:
        SK_ScalarNearlyZero


# 'opaque' types used by SkDashPathEffect::Make and SkPaint::setPathEffect
cdef extern from "include/core/SkRefCnt.h":
    cdef cppclass sk_sp[T]:
        pass


cdef extern from "include/core/SkPathEffect.h":
    cdef cppclass SkPathEffect:
        pass


cdef extern from "include/effects/SkDashPathEffect.h":
    cdef cppclass SkDashPathEffect:
        @staticmethod
        sk_sp[SkPathEffect] Make(const SkScalar intervals[], int count, SkScalar phase)


cdef extern from "include/core/SkPaint.h":
    enum SkPaintStyle "SkPaint::Style":
        kFill_Style "SkPaint::Style::kFill_Style",
        kStroke_Style "SkPaint::Style::kStroke_Style",
        kStrokeAndFill_Style "SkPaint::Style::kStrokeAndFill_Style",

    enum SkLineCap "SkPaint::Cap":
        kButt_Cap "SkPaint::Cap::kButt_Cap",
        kRound_Cap "SkPaint::Cap::kRound_Cap",
        kSquare_Cap "SkPaint::Cap::kSquare_Cap"

    enum SkLineJoin "SkPaint::Join":
        kMiter_Join "SkPaint::Join::kMiter_Join",
        kRound_Join "SkPaint::Join::kRound_Join",
        kBevel_Join "SkPaint::Join::kBevel_Join"

    cdef cppclass SkPaint:
        SkPaint()
        void setStyle(SkPaintStyle style)
        void setStrokeWidth(SkScalar width)
        void setStrokeCap(SkLineCap cap)
        void setStrokeJoin(SkLineJoin join)
        void setStrokeMiter(SkScalar miter)
        void setPathEffect(sk_sp[SkPathEffect] pathEffect)
        bint getFillPath(const SkPath& src, SkPath* dst) const

cdef extern from "include/core/SkPathUtils.h" namespace "skpathutils":
    cdef bint FillPathWithPaint(const SkPath& src, const SkPaint& paint, SkPathBuilder* dst)
