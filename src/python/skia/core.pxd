ctypedef float SkScalar

cdef extern from "SkPath.h":

    cdef cppclass SkPoint:

        @staticmethod
        SkPoint Make(SkScalar x, SkScalar y) except +

        SkScalar x()
        SkScalar y()

    cdef cppclass SkPath:
        SkPath() except +
        SkPath(SkPath& path)

