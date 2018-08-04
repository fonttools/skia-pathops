from ._pathops import (
    Path,
    PathOp,
    op,
)


def union(contours, outpen):
    return _do(PathOp.UNION, contours, (), outpen)


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

    result.draw(outpen)
