from ._pathops import (
    Path,
    PathOp,
    OpBuilder,
    fix_winding,
)


def _union_path(contours):
    if not contours:
        return Path()
    builder = OpBuilder()
    for contour in contours:
        path = Path()
        pen = path.getPen()
        contour.draw(pen)
        builder.add(path, PathOp.UNION)
    return builder.resolve()


def union(contours, outpen):
    result = _union_path(contours)
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
    builder = OpBuilder()

    one = _union_path(subject_contours)
    builder.add(one, PathOp.UNION)

    two = _union_path(clip_contours)
    builder.add(two, operator)

    result = builder.resolve()

    fix_winding(result)

    result.draw(outpen)
