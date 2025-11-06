from .core cimport SkPath
from libcpp.optional cimport optional

cdef extern from "third_party/skia/HEAD/include/pathops/SkPathOps.h":

    enum SkPathOp:
        kDifference_SkPathOp,            # subtract the op path from the first path
        kIntersect_SkPathOp,             # intersect the two paths
        kUnion_SkPathOp,                 # union (inclusive-or) the two paths
        kXOR_SkPathOp,                   # exclusive-or the two paths
        kReverseDifference_SkPathOp      # subtract the first path from the op path

    optional[SkPath] Op(const SkPath& one, const SkPath& two, SkPathOp op)

    optional[SkPath] Simplify(const SkPath& path)

    optional[SkPath] AsWinding(const SkPath& path)

    cdef cppclass SkOpBuilder:

        SkOpBuilder() except +

        void add(const SkPath& path, SkPathOp _operator)

        optional[SkPath] resolve()
