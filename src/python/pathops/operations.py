from . import Path, PathOp, op


def union(contours, outpen, fix_winding=True, keep_starting_points=True):
    if not contours:
        return
    path = Path()
    pen = path.getPen()
    for contour in contours:
        contour.draw(pen)
    path.simplify(
        fix_winding=fix_winding,
        keep_starting_points=keep_starting_points
    )
    path.draw(outpen)


# TODO remove repetition by defining these functions dynamically; they only
# differ by the name and the respective PathOp operator

def difference(
    subject_contours,
    clip_contours,
    outpen,
    fix_winding=True,
    keep_starting_points=True
):
    return _do(
        PathOp.DIFFERENCE,
        subject_contours,
        clip_contours,
        outpen,
        fix_winding=fix_winding,
        keep_starting_points=keep_starting_points,
    )


def intersection(
    subject_contours,
    clip_contours,
    outpen,
    fix_winding=True,
    keep_starting_points=True,
):
    return _do(
        PathOp.INTERSECTION,
        subject_contours,
        clip_contours,
        outpen,
        fix_winding=fix_winding,
        keep_starting_points=keep_starting_points,
    )


def xor(
    subject_contours,
    clip_contours,
    outpen,
    fix_winding=True,
    keep_starting_points=True,
):
    return _do(
        PathOp.XOR,
        subject_contours,
        clip_contours,
        outpen,
        fix_winding=fix_winding,
        keep_starting_points=keep_starting_points,
    )


def reverse_difference(
    subject_contours,
    clip_contours,
    outpen,
    fix_winding=True,
    keep_starting_points=True,
):
    return _do(
        PathOp.REVERSE_DIFFERENCE,
        subject_contours,
        clip_contours,
        outpen,
        fix_winding=fix_winding,
        keep_starting_points=keep_starting_points,
    )


def _do(
    operator,
    subject_contours,
    clip_contours,
    outpen,
    fix_winding=True,
    keep_starting_points=True,
):
    one = Path()
    pen = one.getPen()
    for contour in subject_contours:
        contour.draw(pen)

    two = Path()
    pen = two.getPen()
    for contour in clip_contours:
        contour.draw(pen)

    result = op(one, two, operator, fix_winding, keep_starting_points)

    result.draw(outpen)
