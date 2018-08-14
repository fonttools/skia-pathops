from pathops import (
    Path, PathPen, OpenPathError, OpBuilder, PathOp, PathVerb
)
from fontTools.pens.recordingPen import RecordingPen

import pytest


class PathTest(object):

    def test_init(self):
        path = Path()
        assert isinstance(path, Path)

    def test_getPen(self):
        path = Path()
        pen = path.getPen()
        assert isinstance(pen, PathPen)
        assert id(pen) != id(path.getPen())

    def test_copy(self):
        path1 = Path()
        path2 = Path(path1)
        # TODO expose operator== to check for equality

    def test_draw(self):
        path = Path()
        pen = path.getPen()
        pen.moveTo((0, 0))
        pen.lineTo((1.0, 2.0))
        pen.curveTo((3.5, 4), (5, 6), (7, 8))
        pen.qCurveTo((9, 10), (11, 12))
        pen.closePath()

        path2 = Path()
        path.draw(path2.getPen())

    def test_allow_open_contour(self):
        rec = RecordingPen()
        path = Path()
        pen = path.getPen()
        pen.moveTo((0, 0))
        # pen.endPath() is implicit here
        pen.moveTo((1, 0))
        pen.lineTo((1, 1))
        pen.curveTo((2, 2), (3, 3), (4, 4))
        pen.endPath()
        path.draw(rec)
        assert rec.value == [
            ('moveTo', ((0.0, 0.0),)),
            ('endPath', ()),
            ('moveTo', ((1.0, 0.0),)),
            ('lineTo', ((1.0, 1.0),)),
            ('curveTo', ((2.0, 2.0), (3.0, 3.0), (4.0, 4.0))),
            ('endPath', ()),
        ]

    def test_raise_open_contour_error(self):
        rec = RecordingPen()
        path = Path()
        pen = path.getPen(allow_open_paths=False)
        pen.moveTo((0, 0))
        with pytest.raises(OpenPathError):
            pen.endPath()

    def test_decompose_join_quadratic_segments(self):
        rec = RecordingPen()
        path = Path()
        pen = path.getPen()
        pen.moveTo((0, 0))
        pen.qCurveTo((1, 1), (2, 2), (3, 3))
        pen.closePath()

        items = list(path)
        assert len(items) == 4
        # the TrueType quadratic spline with N off-curves is stored internally
        # as N atomic quadratic Bezier segments
        assert items[1][0] == PathVerb.QUAD
        assert items[1][1] == ((1.0, 1.0), (1.5, 1.5))
        assert items[2][0] == PathVerb.QUAD
        assert items[2][1] == ((2.0, 2.0), (3.0, 3.0))

        path.draw(rec)

        # when drawn back onto a SegmentPen, the implicit on-curves are omitted
        assert rec.value == [
            ('moveTo', ((0.0, 0.0),)),
            ('qCurveTo', ((1.0, 1.0), (2.0, 2.0), (3.0, 3.0))),
            ('closePath', ())]

    def test_last_implicit_lineTo(self):
        # https://github.com/fonttools/skia-pathops/issues/6
        rec = RecordingPen()
        path = Path()
        pen = path.getPen()
        pen.moveTo((100, 100))
        pen.lineTo((100, 200))
        pen.closePath()
        path.draw(rec)
        assert rec.value == [
            ('moveTo', ((100.0, 100.0),)),
            ('lineTo', ((100.0, 200.0),)),
            # ('lineTo', ((100.0, 100.0),)),
            ('closePath', ())]


class OpBuilderTest(object):

    def test_init(self):
        builder = OpBuilder()

    def test_add(self):
        path = Path()
        pen = path.getPen()
        pen.moveTo((5, -225))
        pen.lineTo((-225, 7425))
        pen.lineTo((7425, 7425))
        pen.lineTo((7425, -225))
        pen.lineTo((-225, -225))
        pen.closePath()

        builder = OpBuilder()
        builder.add(path, PathOp.UNION)

    def test_resolve(self):
        path1 = Path()
        pen1 = path1.getPen()
        pen1.moveTo((5, -225))
        pen1.lineTo((-225, 7425))
        pen1.lineTo((7425, 7425))
        pen1.lineTo((7425, -225))
        pen1.lineTo((-225, -225))
        pen1.closePath()

        path2 = Path()
        pen2 = path2.getPen()
        pen2.moveTo((5940, 2790))
        pen2.lineTo((5940, 2160))
        pen2.lineTo((5970, 1980))
        pen2.lineTo((5688, 773669888))
        pen2.lineTo((5688, 2160))
        pen2.lineTo((5688, 2430))
        pen2.lineTo((5400, 4590))
        pen2.lineTo((5220, 4590))
        pen2.lineTo((5220, 4920))
        pen2.curveTo((5182.22900390625, 4948.328125),
                     (5160, 4992.78662109375),
                     (5160, 5040.00048828125))
        pen2.lineTo((5940, 2790))
        pen2.closePath()

        builder = OpBuilder(fix_winding=False, keep_starting_points=False)
        builder.add(path1, PathOp.UNION)
        builder.add(path2, PathOp.UNION)
        result = builder.resolve()

        rec = RecordingPen()
        result.draw(rec)
        assert rec.value == [
            ('moveTo', ((5316.0, 4590.0),)),
            ('lineTo', ((5220.0, 4590.0),)),
            ('lineTo', ((5220.0, 4866.92333984375),)),
            ('lineTo', ((5316.0, 4590.0),)),
            ('closePath', ()),
            ('moveTo', ((5688.0, 7425.0),)),
            ('lineTo', ((-225.0, 7425.0),)),
            ('lineTo', ((-225.0, 7425.0),)),
            ('lineTo', ((5.0, -225.0),)),
            ('lineTo', ((7425.0, -225.0),)),
            ('lineTo', ((7425.0, 7425.0),)),
            ('lineTo', ((5688.0, 7425.0),)),
            ('closePath', ())]


TEST_DATA = [
    (
        [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((1, 1),)),
            ('lineTo', ((2, 2),)),
            ('lineTo', ((3, 3),)),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((3, 3),)),
            ('lineTo', ((2, 2),)),
            ('lineTo', ((1, 1),)),
            ('lineTo', ((0, 0),)),
            ('closePath', ())
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((1, 1),)),
            ('lineTo', ((2, 2),)),
            ('lineTo', ((0, 0),)),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((2, 2),)),
            ('lineTo', ((1, 1),)),
            ('lineTo', ((0, 0),)),
            ('closePath', ())
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((0, 0),)),
            ('lineTo', ((1, 1),)),
            ('lineTo', ((2, 2),)),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((2, 2),)),
            ('lineTo', ((1, 1),)),
            ('lineTo', ((0, 0),)),
            ('lineTo', ((0, 0),)),
            ('closePath', ()),
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((1, 1),)),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((1, 1),)),
            ('lineTo', ((0, 0),)),
            ('closePath', ()),
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('curveTo', ((1, 1), (2, 2), (3, 3))),
            ('curveTo', ((4, 4), (5, 5), (0, 0))),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((0, 0),)),
            ('curveTo', ((5, 5), (4, 4), (3, 3))),
            ('curveTo', ((2, 2), (1, 1), (0, 0))),
            ('closePath', ()),
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('curveTo', ((1, 1), (2, 2), (3, 3))),
            ('curveTo', ((4, 4), (5, 5), (6, 6))),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((6, 6),)),
            ('curveTo', ((5, 5), (4, 4), (3, 3))),
            ('curveTo', ((2, 2), (1, 1), (0, 0))),
            ('closePath', ()),
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((1, 1),)),
            ('curveTo', ((2, 2), (3, 3), (4, 4))),
            ('curveTo', ((5, 5), (6, 6), (7, 7))),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((7, 7),)),
            ('curveTo', ((6, 6), (5, 5), (4, 4))),
            ('curveTo', ((3, 3), (2, 2), (1, 1))),
            ('lineTo', ((0, 0),)),
            ('closePath', ()),
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('qCurveTo', ((1, 1), (2.5, 2.5))),
            ('qCurveTo', ((3, 3), (0, 0))),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((0, 0),)),
            ('qCurveTo', ((3, 3), (2.5, 2.5))),
            ('qCurveTo', ((1, 1), (0, 0))),
            ('closePath', ()),
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('qCurveTo', ((1, 1), (2.5, 2.5))),
            ('qCurveTo', ((3, 3), (4, 4))),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((4, 4),)),
            ('qCurveTo', ((3, 3), (2.5, 2.5))),
            ('qCurveTo', ((1, 1), (0, 0))),
            ('closePath', ()),
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((1, 1),)),
            ('qCurveTo', ((2, 2), (3, 3))),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((3, 3),)),
            ('qCurveTo', ((2, 2), (1, 1))),
            ('lineTo', ((0, 0),)),
            ('closePath', ()),
        ]
    ),
    (
        [], []
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('endPath', ()),
        ],
        [
            ('moveTo', ((0, 0),)),
            ('endPath', ()),
        ],
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('closePath', ()),
        ],
        [
            ('moveTo', ((0, 0),)),
            ('closePath', ()),
        ],
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((1, 1),)),
            ('endPath', ())
        ],
        [
            ('moveTo', ((1, 1),)),
            ('lineTo', ((0, 0),)),
            ('endPath', ())
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('curveTo', ((1, 1), (2, 2), (3, 3))),
            ('endPath', ())
        ],
        [
            ('moveTo', ((3, 3),)),
            ('curveTo', ((2, 2), (1, 1), (0, 0))),
            ('endPath', ())
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('curveTo', ((1, 1), (2, 2), (3, 3))),
            ('lineTo', ((4, 4),)),
            ('endPath', ())
        ],
        [
            ('moveTo', ((4, 4),)),
            ('lineTo', ((3, 3),)),
            ('curveTo', ((2, 2), (1, 1), (0, 0))),
            ('endPath', ())
        ]
    ),
    (
        [
            ('moveTo', ((0, 0),)),
            ('lineTo', ((1, 1),)),
            ('curveTo', ((2, 2), (3, 3), (4, 4))),
            ('endPath', ())
        ],
        [
            ('moveTo', ((4, 4),)),
            ('curveTo', ((3, 3), (2, 2), (1, 1))),
            ('lineTo', ((0, 0),)),
            ('endPath', ())
        ]
    ),
    # Test case from:
    # https://github.com/googlei18n/cu2qu/issues/51#issue-179370514
    (
        [
            ('moveTo', ((848, 348),)),
            ('lineTo', ((848, 348),)),  # duplicate lineTo point after moveTo
            ('qCurveTo', ((848, 526), (649, 704), (449, 704))),
            ('qCurveTo', ((449, 704), (248, 704), (50, 526), (50, 348))),
            ('lineTo', ((50, 348),)),
            ('qCurveTo', ((50, 348), (50, 171), (248, -3), (449, -3))),
            ('qCurveTo', ((449, -3), (649, -3), (848, 171), (848, 348))),
            ('closePath', ())
        ],
        [
            ('moveTo', ((848, 348),)),
            ('qCurveTo', ((848, 171), (649, -3), (449, -3), (449, -3))),
            ('qCurveTo', ((248, -3), (50, 171), (50, 348), (50, 348))),
            ('lineTo', ((50, 348),)),
            ('qCurveTo', ((50, 526), (248, 704), (449, 704), (449, 704))),
            ('qCurveTo', ((649, 704), (848, 526), (848, 348))),
            ('lineTo', ((848, 348),)),  # the duplicate point is kept
            ('closePath', ())
        ]
    )
]
@pytest.mark.parametrize("operations, expected", TEST_DATA)
def test_reverse_path(operations, expected):
    path = Path()
    pen = path.getPen()
    for operator, operands in operations:
        getattr(pen, operator)(*operands)

    path.reverse()

    recpen = RecordingPen()
    path.draw(recpen)
    assert recpen.value == expected



def assert_approx_equal_paths(path1, path2):
    assert path1.verbs == path2.verbs
    points1 = path1.points
    points2 = path2.points
    assert len(points1) == len(points2)
    for pt1, pt2 in zip(points1, points2):
        assert pt1 == pytest.approx(pt2, rel=1e-3)


def test_duplicate_start_point():
    # https://github.com/fonttools/skia-pathops/issues/13
    path = Path()
    path.moveTo(177.0, 258.0)
    path.lineTo(200.0, 269.0)
    path.cubicTo(200.0, 356.0, 250.0, 410.0, 400.0, 410.0)
    path.cubicTo(550.0, 410.0, 600.0, 356.0, 600.0, 269.0)
    path.lineTo(600.0, 257.0)
    path.cubicTo(600.0, 179.0, 580.0, 78.0, 410.0, 78.0)
    path.cubicTo(240.0, 78.0, 200.0, 159.0, 200.0, 277.0)
    path.lineTo(200.0, 519.0)
    path.cubicTo(200.0, 636.0, 230.0, 720.0, 400.0, 720.0)
    path.cubicTo(531.0, 720.0, 564.0, 686.0, 582.0, 603.0)
    path.lineTo(691.0, 626.0)
    path.cubicTo(664.0, 757.0, 581.0, 810.0, 401.0, 810.0)
    path.cubicTo(181.0, 810.0, 100.0, 696.0, 100.0, 519.0)
    path.lineTo(100.0, 277.0)
    path.cubicTo(100.0, 102.0, 190.0, -10.0, 410.0, -10.0)
    path.cubicTo(630.0, -10.0, 700.0, 115.0, 700.0, 250.0)
    path.lineTo(700.0, 272.0)
    path.cubicTo(700.0, 419.0, 601.0, 500.0, 401.0, 500.0)
    path.cubicTo(201.0, 500.0, 150.0, 416.0, 150.0, 269.0)
    path.lineTo(177.0, 258.0)
    path.close()

    path.simplify()

    expected = Path()
    expected.moveTo(200.0, 439.1)
    expected.lineTo(200.0, 519.0)
    expected.cubicTo(200.0, 636.0, 230.0, 720.0, 400.0, 720.0)
    expected.cubicTo(531.0, 720.0, 564.0, 686.0, 582.0, 603.0)
    expected.lineTo(691.0, 626.0)
    expected.cubicTo(664.0, 757.0, 581.0, 810.0, 401.0, 810.0)
    expected.cubicTo(181.0, 810.0, 100.0, 696.0, 100.0, 519.0)
    expected.lineTo(100.0, 277.0)
    expected.cubicTo(100.0, 102.0, 190.0, -10.0, 410.0, -10.0)
    expected.cubicTo(630.0, -10.0, 700.0, 115.0, 700.0, 250.0)
    expected.lineTo(700.0, 272.0)
    expected.cubicTo(700.0, 419.0, 601.0, 500.0, 401.0, 500.0)
    expected.cubicTo(300.557, 500.0, 237.695, 478.814, 200.0, 439.1)
    expected.close()
    expected.moveTo(200.023, 272.184)
    expected.cubicTo(201.24, 357.316, 251.839, 410.0, 400.0, 410.0)
    expected.cubicTo(550.0, 410.0, 600.0, 356.0, 600.0, 269.0)
    expected.lineTo(600.0, 257.0)
    expected.cubicTo(600.0, 179.0, 580.0, 78.0, 410.0, 78.0)
    expected.cubicTo(242.323, 78.0, 201.117, 156.802, 200.023, 272.184)
    # expected.lineTo(200.023, 272.184)  # this should not be present
    expected.close()

    assert_approx_equal_paths(path, expected)
