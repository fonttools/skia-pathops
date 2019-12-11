from .core cimport SkPath


cdef extern from "include/pathops/SkPathOps.h":

    enum SkPathOp:
        kDifference_SkPathOp,            # subtract the op path from the first path
        kIntersect_SkPathOp,             # intersect the two paths
        kUnion_SkPathOp,                 # union (inclusive-or) the two paths
        kXOR_SkPathOp,                   # exclusive-or the two paths
        kReverseDifference_SkPathOp      # subtract the first path from the op path

    bint Op(const SkPath& one, const SkPath& two, SkPathOp op, SkPath* result)

    bint Simplify(const SkPath& path, SkPath* result)

    bint AsWinding(const SkPath& path, SkPath* result)

    cdef cppclass SkOpBuilder:

        SkOpBuilder() except +

        void add(const SkPath& path, SkPathOp _operator)

        bint resolve(SkPath* result)
