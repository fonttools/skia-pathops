from ._pathops import (
    Path,
    PathOp,
    op,
    OpBuilder,
    fix_winding,
)


def union(contours, outpen):
    if not contours:
        return
    builder = OpBuilder()
    for contour in contours:
        path = Path()
        pen = path.getPen()
        contour.draw(pen)
        builder.add(path, PathOp.UNION)
    result = builder.resolve()
    fix_winding(result)
    result.draw(outpen)


def difference(subject_contours, clip_contours, outpen):
    return _do(PathOp.DIFFERENCE, subject_contours, clip_contours, outpen)


def intersection(subject_contours, clip_contours, outpen):
    return _do(PathOp.INTERSECTION, subject_contours, clip_contours, outpen)


def xor(subject_contours, clip_contours, outpen):
    return _do(PathOp.XOR, subject_contours, clip_contours, outpen)


def reverse_difference(subject_contours, clip_contours, outpen):
    return _do(PathOp.REVERSE_DIFFERENCE, subject_contours, clip_contours, outpen)


def _do(operator, subject_contours, clip_contours, outpen):
    one = Path()
    pen = one.getPen()
    for contour in subject_contours:
        contour.draw(pen)

    two = Path()
    pen = two.getPen()
    for contour in clip_contours:
        contour.draw(pen)

    result = op(one, two, operator)

    fix_winding(result)

    result.draw(outpen)
