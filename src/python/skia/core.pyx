
cpdef test():
    cdef SkPoint p
    p = SkPoint.Make(1.0, 3.0)
    print(p.x(), p.y())

    cdef SkPath *path
    path = new SkPath()
