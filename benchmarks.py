from pathops import union as pathops_union
from booleanOperations import union as boolops_union
from defcon import Font as DefconFont
from ufoLib2 import Font as UfoLib2Font
import math
import timeit


REPEAT = 10
NUMBER = 1


def remove_overlaps(font, union_func, pen_getter, **kwargs):
    for glyph in font:
        contours = list(glyph)
        if not contours:
            continue
        glyph.clearContours()
        pen = getattr(glyph, pen_getter)()
        union_func(contours, pen, **kwargs)


def mean_and_stdev(runs, loops):
    timings = [t / loops for t in runs]
    n = len(runs)
    mean = math.fsum(timings) / n
    stdev = (math.fsum([(x - mean) ** 2 for x in timings]) / n) ** 0.5
    return mean, stdev


def run(
    ufo,
    FontClass,
    union_func,
    pen_getter,
    repeat=REPEAT,
    number=NUMBER,
    **kwargs,
):
    all_runs = timeit.repeat(
        stmt="remove_overlaps(font, union_func, pen_getter, **kwargs)",
        setup="font = FontClass(ufo); list(font)",
        repeat=repeat,
        number=number,
        globals={
            "ufo": ufo,
            "FontClass": FontClass,
            "union_func": union_func,
            "pen_getter": pen_getter,
            "remove_overlaps": remove_overlaps,
            "kwargs": kwargs,
        },
    )
    mean, stdev = mean_and_stdev(all_runs, number)
    class_module = FontClass.__module__.split(".")[0]
    func_module = union_func.__module__.split(".")[0]
    print(
        f"{class_module}::{func_module}: {mean:.3f} s +- {stdev:.3f} s per loop "
        f"(mean +- std. dev. of {repeat} run(s), {number} loop(s) each)"
    )


def main():
    import sys

    try:
        ufo = sys.argv[1]
    except IndexError:
        sys.exit("usage: %s FONT.ufo [N]" % sys.argv[0])

    if len(sys.argv) > 2:
        repeat = int(sys.argv[2])
    else:
        repeat = REPEAT

    for FontClass in [DefconFont, UfoLib2Font]:
        for union_func, pen_getter, kwargs in [
            (boolops_union, "getPointPen", {}),
            (pathops_union, "getPen", {}),
            # (pathops_union, "getPen", {"keep_starting_points": True}),
        ]:
            run(
                ufo, FontClass, union_func, pen_getter, repeat=repeat, **kwargs
            )

    # import os
    # import shutil

    # font = UfoLib2Font(ufo)
    # font = DefconFont(ufo)

    # union_func = pathops_union
    # pen_getter = "getPen"

    # union_func = boolops_union
    # pen_getter = "getPointPen"

    # remove_overlaps(font, union_func, pen_getter)
    # output = ufo.rsplit(".", 1)[0] + "_ro.ufo"
    # if os.path.isdir(output):
    #     shutil.rmtree(output)
    # font.save(output)


if __name__ == "__main__":
    main()
