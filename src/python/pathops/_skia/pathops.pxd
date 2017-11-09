from .core cimport SkPath


cdef extern from "SkPathOps.h":

    enum SkPathOp:
        kDifference_SkPathOp = 0         # subtract the op path from the first path
        kIntersect_SkPathOp = 1          # intersect the two paths
        kUnion_SkPathOp = 2              # union (inclusive-or) the two paths
        kXOR_SkPathOp = 3                # exclusive-or the two paths
        kReverseDifference_SkPathOp = 4  # subtract the first path from the op path

    cdef cppclass SkOpBuilder:

        SkOpBuilder() except +

        void add(const SkPath& path, SkPathOp _operator)

        bint resolve(SkPath* result)
