ctypedef float SkScalar


cdef extern from "SkPath.h":

    cdef cppclass SkPoint:

        @staticmethod
        SkPoint Make(SkScalar x, SkScalar y)

        SkScalar x()
        SkScalar y()

    cdef cppclass SkPath:

        SkPath() except +
        SkPath(SkPath& path) except +

        void moveTo(SkScalar x, SkScalar y)

        void lineTo(SkScalar x, SkScalar y)

        void cubicTo(
            SkScalar x1, SkScalar y1,
            SkScalar x2, SkScalar y2,
            SkScalar x3, SkScalar y3)

        void quadTo(SkScalar x1, SkScalar y1, SkScalar x2, SkScalar y2)

        void conicTo(SkScalar x1, SkScalar y1, SkScalar x2, SkScalar y2,
                     SkScalar w)

        void close()

        void dump()

        cppclass Iter:

            Iter() except +
            Iter(const SkPath& path, bint forceClose) except +

            Verb next(SkPoint pts[4],
                      bint doConsumeDegenerates,
                      bint exact)
            Verb next(SkPoint pts[4],
                      bint doConsumeDegenerates)
            Verb next(SkPoint pts[4])

            SkScalar conicWeight()


cdef extern from * namespace "SkPath":

    enum Verb:
        kMove_Verb,
        kLine_Verb,
        kQuad_Verb,
        kConic_Verb,
        kCubic_Verb,
        kClose_Verb,
        kDone_Verb
