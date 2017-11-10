from ._pathops import (
    Path,
    op,
    DIFFERENCE,
    INTERSECTION,
    UNION,
    XOR,
    REVERSE_DIFFERENCE,
)


def union(contours, outpen):
    return _do(UNION, contours, (), outpen)


def difference(subject_contours, clip_contours, outpen):
    return _do(DIFFERENCE, subject_contours, clip_contours, outpen)


def intersection(subject_contours, clip_contours, outpen):
    return _do(INTERSECTION, subject_contours, clip_contours, outpen)


def xor(subject_contours, clip_contours, outpen):
    return _do(XOR, subject_contours, clip_contours, outpen)


def reverse_difference(subject_contours, clip_contours, outpen):
    return _do(REVERSE_DIFFERENCE, subject_contours, clip_contours, outpen)


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
