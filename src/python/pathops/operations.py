from ._pathops import (
    Path,
    PathOp,
    op,
    OpBuilder,
)


def union(contours, outpen, fix_winding=True):
    if not contours:
        return
    builder = OpBuilder()
    for contour in contours:
        path = Path(contour)
        builder.add(path, PathOp.UNION)
    result = builder.resolve()
    if fix_winding:
        result.fix_winding()
    result.draw(outpen)


def union2(contours, outpen, fix_winding=True):
    if not contours:
        return
    result = Path()
    for contour in contours:
        path = Path(contour)
        path.simplify(fix_winding)
        result.addPath(path)
    result.simplify(fix_winding)
    result.draw(outpen)


def union3(contours, outpen, fix_winding=True):
    if not contours:
        return
    path = Path()
    pen = path.getPen()
    for contour in contours:
        contour.draw(pen)
    path.simplify(fix_winding)
    path.draw(outpen)


def union4(contours, outpen, fix_winding=True):
    if not contours:
        return
    result = Path()
    for contour in contours:
        path = Path(contour)
        result = op(result, path, PathOp.UNION, fix_winding)
    result.draw(outpen)


def difference(subject_contours, clip_contours, outpen):
    return _do(PathOp.DIFFERENCE, subject_contours, clip_contours, outpen)


def intersection(subject_contours, clip_contours, outpen):
    return _do(PathOp.INTERSECTION, subject_contours, clip_contours, outpen)


def xor(subject_contours, clip_contours, outpen):
    return _do(PathOp.XOR, subject_contours, clip_contours, outpen)


def reverse_difference(subject_contours, clip_contours, outpen):
    return _do(PathOp.REVERSE_DIFFERENCE, subject_contours, clip_contours, outpen)


def _do(operator, subject_contours, clip_contours, outpen, fix_winding=True):
    one = Path()
    pen = one.getPen()
    for contour in subject_contours:
        contour.draw(pen)

    two = Path()
    pen = two.getPen()
    for contour in clip_contours:
        contour.draw(pen)

    result = op(one, two, operator, fix_winding)

    result.draw(outpen)
