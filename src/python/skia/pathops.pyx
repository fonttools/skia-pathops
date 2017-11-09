from .core cimport (
    SkPath,
    SkPoint,
    kMove_Verb,
    kLine_Verb,
    kQuad_Verb,
    kConic_Verb,
    kCubic_Verb,
    kClose_Verb,
    kDone_Verb
)

cpdef int test():
    cdef SkOpBuilder builder
    cdef SkPath path1, path2, result
    cdef SkPath.Iter iterator
    cdef SkPoint p[4]
    cdef SkPath.Verb verb
    cdef bint ok = 0

    path1.moveTo(5, -225)
    path1.lineTo(-225, 7425)
    path1.lineTo(7425, 7425)
    path1.lineTo(7425, -225)
    path1.lineTo(-225, -225)
    path1.lineTo(5, -225)
    path1.close()

    path2.moveTo(5940, 2790)
    path2.lineTo(5940, 2160)
    path2.lineTo(5970, 1980)
    path2.lineTo(5688, 773669888)
    path2.lineTo(5688, 2160)
    path2.lineTo(5688, 2430)
    path2.lineTo(5400, 4590)
    path2.lineTo(5220, 4590)
    path2.lineTo(5220, 4920)
    path2.cubicTo(5182.22900390625, 4948.328125, 5160,
                  4992.78662109375, 5160, 5040.00048828125)
    path2.lineTo(5940, 2790)
    path2.close()

    builder.add(path1, kUnion_SkPathOp)
    builder.add(path2, kUnion_SkPathOp)
    ok = builder.resolve(&result)

    iterator = SkPath.Iter(result, False)

    if ok:
        verb = iterator.next(p, False)
        while verb != kDone_Verb:
            if verb == kMove_Verb:
                print("moveTo (%g, %g)" % (p[0].x(), p[0].y()))
            elif verb == kLine_Verb:
                print("lineTo (%g, %g)" % (p[1].x(), p[1].y()))
            elif verb == kCubic_Verb:
                print("cubicTo (%g, %g) (%g, %g) (%g, %g)" % (
                    p[1].x(), p[1].y(),
                    p[2].x(), p[2].y(),
                    p[3].x(), p[3].y()))
            elif verb == kQuad_Verb:
                print("quadTo (%g, %g) (%g, %g)" % (
                    p[1].x(), p[1].y(), p[2].x(), p[2].y()))
            elif verb == kConic_Verb:
                print("conicTo (%g, %g) (%g, %g) (%g)" % (
                    p[1].x(), p[1].y(), p[2].x(), p[2].y(),
                    iterator.conicWeight()))
            elif verb == kClose_Verb:
                print("close")
            elif verb == kDone_Verb:
                pass
            else:
                raise RuntimeError("unknown verb: %d" % int(verb))
            verb = iterator.next(p, False)

    return ok
