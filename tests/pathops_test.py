from pathops import (
    Path,
    PathPen,
    OpenPathError,
    OpBuilder,
    PathOp,
    PathVerb,
    FillType,
    bits2float,
    float2bits,
    ArcSize,
    Direction,
    simplify,
)

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

    def test_eq_operator(self):
        path1 = Path()
        path2 = Path()
        assert path1 == path2
        path1.moveTo(0, 0)
        assert path1 != path2
        path2.moveTo(0, 0)
        assert path1 == path2
        path1.fillType = FillType.EVEN_ODD
        assert path1 != path2

    def test_copy(self):
        path1 = Path()
        path2 = Path(path1)
        assert path1 == path2

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

        assert path == path2

    def test_allow_open_contour(self):
        path = Path()
        pen = path.getPen()
        pen.moveTo((0, 0))
        # pen.endPath() is implicit here
        pen.moveTo((1, 0))
        pen.lineTo((1, 1))
        pen.curveTo((2, 2), (3, 3), (4, 4))
        pen.endPath()

        assert list(path.segments) == [
            ('moveTo', ((0.0, 0.0),)),
            ('endPath', ()),
            ('moveTo', ((1.0, 0.0),)),
            ('lineTo', ((1.0, 1.0),)),
            ('curveTo', ((2.0, 2.0), (3.0, 3.0), (4.0, 4.0))),
            ('endPath', ()),
        ]

    def test_raise_open_contour_error(self):
        path = Path()
        pen = path.getPen(allow_open_paths=False)
        pen.moveTo((0, 0))
        with pytest.raises(OpenPathError):
            pen.endPath()

    def test_decompose_join_quadratic_segments(self):
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

        # when drawn back onto a SegmentPen, the implicit on-curves are omitted
        assert list(path.segments) == [
            ('moveTo', ((0.0, 0.0),)),
            ('qCurveTo', ((1.0, 1.0), (2.0, 2.0), (3.0, 3.0))),
            ('closePath', ())]

    def test_last_implicit_lineTo(self):
        # https://github.com/fonttools/skia-pathops/issues/6
        path = Path()
        pen = path.getPen()
        pen.moveTo((100, 100))
        pen.lineTo((100, 200))
        pen.closePath()
        assert list(path.segments) == [
            ('moveTo', ((100.0, 100.0),)),
            ('lineTo', ((100.0, 200.0),)),
            # ('lineTo', ((100.0, 100.0),)),
            ('closePath', ())]

    def test_transform(self):
        path = Path()
        path.moveTo(125, 376)
        path.cubicTo(181, 376, 218, 339, 218, 290)
        path.cubicTo(218, 225, 179, 206, 125, 206)
        path.close()

        # t = Transform().rotate(radians(-45)).translate(-100, 0)
        matrix = (0.707107, -0.707107, 0.707107, 0.707107, -70.7107, 70.7107)

        result = path.transform(*matrix)

        expected = Path()
        expected.moveTo(
            bits2float(0x438dc663),  # 283.55
            bits2float(0x437831ce),  # 248.195
        )
        expected.cubicTo(
            bits2float(0x43a192ee),  # 323.148
            bits2float(0x435098b8),  # 208.597
            bits2float(0x43a192ee),  # 323.148
            bits2float(0x431c454a),  # 156.271
            bits2float(0x43903ff5),  # 288.5
            bits2float(0x42f33ead),  # 121.622
        )
        expected.cubicTo(
            bits2float(0x437289a8),  # 242.538
            bits2float(0x42975227),  # 75.6605
            bits2float(0x43498688),  # 201.526
            bits2float(0x42b39aee),  # 89.8026
            bits2float(0x4323577c),  # 163.342
            bits2float(0x42fff906),  # 127.986
        )
        expected.close()

        result.dump(as_hex=True)
        assert result == expected

    def test_pen_addComponent_missing_required_glyphSet(self):
        path = Path()
        pen = path.getPen()
        with pytest.raises(TypeError, match="Missing required glyphSet"):
            pen.addComponent("a", (1, 0, 0, 1, 0, 0))

    def test_pen_addComponent_decomposed_from_glyphSet(self):
        a = Path()
        a.moveTo(0, 0)
        a.lineTo(1, 0)
        a.lineTo(1, 1)
        a.lineTo(0, 1)
        a.close()
        glyphSet = {"a": a}

        b = Path()
        pen = b.getPen(glyphSet=glyphSet)
        pen.addComponent("a", (2, 0, 0, 2, 10, 10))
        glyphSet["b"] = b

        assert list(b) == [
            (PathVerb.MOVE, ((10, 10),)),
            (PathVerb.LINE, ((12, 10),)),
            (PathVerb.LINE, ((12, 12),)),
            (PathVerb.LINE, ((10, 12),)),
            (PathVerb.CLOSE, ()),
        ]

        c = Path()
        pen = c.getPen(glyphSet=glyphSet)
        pen.addComponent("a", (1, 0, 0, 1, 2, 2))
        pen.addComponent("b", (1, 0, 0, 1, -10, -10))
        glyphSet["c"] = c

        assert list(c) == [
            (PathVerb.MOVE, ((2, 2),)),
            (PathVerb.LINE, ((3, 2),)),
            (PathVerb.LINE, ((3, 3),)),
            (PathVerb.LINE, ((2, 3),)),
            (PathVerb.CLOSE, ()),
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((2, 0),)),
            (PathVerb.LINE, ((2, 2),)),
            (PathVerb.LINE, ((0, 2),)),
            (PathVerb.CLOSE, ()),
        ]


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

        assert list(result.segments) == [
            ("moveTo", ((5316.0, 4590.0),)),
            ("lineTo", ((5220.0, 4590.0),)),
            ("lineTo", ((5220.0, 4866.92333984375),)),
            ("lineTo", ((5316.0, 4590.0),)),
            ("closePath", ()),
            ("moveTo", ((5192.18701171875, 4947.15283203125),)),
            (
                "curveTo",
                (
                    (5171.5654296875, 4973.322265625),
                    (5160.0, 5005.9443359375),
                    (5160.0, 5040.00048828125),
                ),
            ),
            ("lineTo", ((5192.18701171875, 4947.15283203125),)),
            ("closePath", ()),
            ("moveTo", ((5688.0, 7425.0),)),
            ("lineTo", ((-225.0, 7425.0),)),
            ("lineTo", ((5.0, -225.0),)),
            ("lineTo", ((7425.0, -225.0),)),
            ("lineTo", ((7425.0, 7425.0),)),
            ("lineTo", ((5688.0, 7425.0),)),
            ("closePath", ()),
        ]


TEST_DATA = [
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.LINE, ((2, 2),)),
            (PathVerb.LINE, ((3, 3),)),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((3, 3),)),
            (PathVerb.LINE, ((2, 2),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.LINE, ((0, 0),)),
            (PathVerb.CLOSE, ())
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.LINE, ((2, 2),)),
            (PathVerb.LINE, ((0, 0),)),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((2, 2),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.LINE, ((0, 0),)),
            (PathVerb.CLOSE, ())
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((0, 0),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.LINE, ((2, 2),)),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((2, 2),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.LINE, ((0, 0),)),
            (PathVerb.LINE, ((0, 0),)),
            (PathVerb.CLOSE, ()),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((1, 1),)),
            (PathVerb.LINE, ((0, 0),)),
            (PathVerb.CLOSE, ()),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.CUBIC, ((1, 1), (2, 2), (3, 3))),
            (PathVerb.CUBIC, ((4, 4), (5, 5), (0, 0))),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.CUBIC, ((5, 5), (4, 4), (3, 3))),
            (PathVerb.CUBIC, ((2, 2), (1, 1), (0, 0))),
            (PathVerb.CLOSE, ()),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.CUBIC, ((1, 1), (2, 2), (3, 3))),
            (PathVerb.CUBIC, ((4, 4), (5, 5), (6, 6))),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((6, 6),)),
            (PathVerb.CUBIC, ((5, 5), (4, 4), (3, 3))),
            (PathVerb.CUBIC, ((2, 2), (1, 1), (0, 0))),
            (PathVerb.CLOSE, ()),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.CUBIC, ((2, 2), (3, 3), (4, 4))),
            (PathVerb.CUBIC, ((5, 5), (6, 6), (7, 7))),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((7, 7),)),
            (PathVerb.CUBIC, ((6, 6), (5, 5), (4, 4))),
            (PathVerb.CUBIC, ((3, 3), (2, 2), (1, 1))),
            (PathVerb.LINE, ((0, 0),)),
            (PathVerb.CLOSE, ()),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.QUAD, ((1, 1), (2.5, 2.5))),
            (PathVerb.QUAD, ((3, 3), (0, 0))),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.QUAD, ((3, 3), (2.5, 2.5))),
            (PathVerb.QUAD, ((1, 1), (0, 0))),
            (PathVerb.CLOSE, ()),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.QUAD, ((1, 1), (2.5, 2.5))),
            (PathVerb.QUAD, ((3, 3), (4, 4))),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((4, 4),)),
            (PathVerb.QUAD, ((3, 3), (2.5, 2.5))),
            (PathVerb.QUAD, ((1, 1), (0, 0))),
            (PathVerb.CLOSE, ()),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.QUAD, ((2, 2), (3, 3))),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((3, 3),)),
            (PathVerb.QUAD, ((2, 2), (1, 1))),
            (PathVerb.LINE, ((0, 0),)),
            (PathVerb.CLOSE, ()),
        ]
    ),
    (
        [], []
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
        ],
        [
            (PathVerb.MOVE, ((0, 0),)),
        ],
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.CLOSE, ()),
        ],
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.CLOSE, ()),
        ],
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((1, 1),)),
        ],
        [
            (PathVerb.MOVE, ((1, 1),)),
            (PathVerb.LINE, ((0, 0),)),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.CUBIC, ((1, 1), (2, 2), (3, 3))),
        ],
        [
            (PathVerb.MOVE, ((3, 3),)),
            (PathVerb.CUBIC, ((2, 2), (1, 1), (0, 0))),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.CUBIC, ((1, 1), (2, 2), (3, 3))),
            (PathVerb.LINE, ((4, 4),)),
        ],
        [
            (PathVerb.MOVE, ((4, 4),)),
            (PathVerb.LINE, ((3, 3),)),
            (PathVerb.CUBIC, ((2, 2), (1, 1), (0, 0))),
        ]
    ),
    (
        [
            (PathVerb.MOVE, ((0, 0),)),
            (PathVerb.LINE, ((1, 1),)),
            (PathVerb.CUBIC, ((2, 2), (3, 3), (4, 4))),
        ],
        [
            (PathVerb.MOVE, ((4, 4),)),
            (PathVerb.CUBIC, ((3, 3), (2, 2), (1, 1))),
            (PathVerb.LINE, ((0, 0),)),
        ]
    ),
    # Test case from:
    # https://github.com/googlei18n/cu2qu/issues/51#issue-179370514
    (
        [
            (PathVerb.MOVE, ((848, 348),)),
            (PathVerb.LINE, ((848, 348),)),  # duplicate lineTo point after moveTo
            (PathVerb.QUAD, ((848, 526), (748.5, 615))),
            (PathVerb.QUAD, ((649, 704), (449, 704))),
            (PathVerb.QUAD, ((449, 704), (348.5, 704))),
            (PathVerb.QUAD, ((248, 704), (149, 615))),
            (PathVerb.QUAD, ((50, 526), (50, 348))),
            (PathVerb.LINE, ((50, 348),)),
            (PathVerb.QUAD, ((50, 348), (50, 259.5))),
            (PathVerb.QUAD, ((50, 171), (149, 84))),
            (PathVerb.QUAD, ((248, -3), (449, -3))),
            (PathVerb.QUAD, ((449, -3), (549, -3))),
            (PathVerb.QUAD, ((649, -3), (748.5, 84))),
            (PathVerb.QUAD, ((848, 171), (848, 348))),
            (PathVerb.CLOSE, ())
        ],
        [
            (PathVerb.MOVE, ((848, 348),)),
            (PathVerb.QUAD, ((848, 171), (748.5, 84))),
            (PathVerb.QUAD, ((649, -3), (549, -3))),
            (PathVerb.QUAD, ((449, -3), (449, -3))),
            (PathVerb.QUAD, ((248, -3), (149, 84))),
            (PathVerb.QUAD, ((50, 171), (50, 259.5))),
            (PathVerb.QUAD, ((50, 348), (50, 348))),
            (PathVerb.LINE, ((50, 348),)),
            (PathVerb.QUAD, ((50, 526), (149, 615))),
            (PathVerb.QUAD, ((248, 704), (348.5, 704))),
            (PathVerb.QUAD, ((449, 704), (449, 704))),
            (PathVerb.QUAD, ((649, 704), (748.5, 615))),
            (PathVerb.QUAD, ((848, 526), (848, 348))),
            (PathVerb.LINE, ((848, 348),)),  # the duplicate point is kept
            (PathVerb.CLOSE, ())
        ]
    )
]
@pytest.mark.parametrize("operations, expected", TEST_DATA)
def test_reverse_path(operations, expected):
    path = Path()
    for verb, pts in operations:
        path.add(verb, *pts)

    path.reverse()

    assert list(path) == expected


def test_duplicate_start_point():
    # https://github.com/fonttools/skia-pathops/issues/13
    path = Path()
    path.moveTo(
        bits2float(0x43480000),  # 200
        bits2float(0x43db8ce9),  # 439.101
    )
    path.lineTo(
        bits2float(0x43480000),  # 200
        bits2float(0x4401c000),  # 519
    )
    path.cubicTo(
        bits2float(0x43480000),  # 200
        bits2float(0x441f0000),  # 636
        bits2float(0x43660000),  # 230
        bits2float(0x44340000),  # 720
        bits2float(0x43c80000),  # 400
        bits2float(0x44340000),  # 720
    )
    path.cubicTo(
        bits2float(0x4404c000),  # 531
        bits2float(0x44340000),  # 720
        bits2float(0x440d0000),  # 564
        bits2float(0x442b8000),  # 686
        bits2float(0x44118000),  # 582
        bits2float(0x4416c000),  # 603
    )
    path.lineTo(
        bits2float(0x442cc000),  # 691
        bits2float(0x441c8000),  # 626
    )
    path.cubicTo(
        bits2float(0x44260000),  # 664
        bits2float(0x443d4000),  # 757
        bits2float(0x44114000),  # 581
        bits2float(0x444a8000),  # 810
        bits2float(0x43c88000),  # 401
        bits2float(0x444a8000),  # 810
    )
    path.cubicTo(
        bits2float(0x43350000),  # 181
        bits2float(0x444a8000),  # 810
        bits2float(0x42c80000),  # 100
        bits2float(0x442e0000),  # 696
        bits2float(0x42c80000),  # 100
        bits2float(0x4401c000),  # 519
    )
    path.lineTo(
        bits2float(0x42c80000),  # 100
        bits2float(0x438a8000),  # 277
    )
    path.cubicTo(
        bits2float(0x42c80000),  # 100
        bits2float(0x42cc0000),  # 102
        bits2float(0x433e0000),  # 190
        bits2float(0xc1200000),  # -10
        bits2float(0x43cd0000),  # 410
        bits2float(0xc1200000),  # -10
    )
    path.cubicTo(
        bits2float(0x441d8000),  # 630
        bits2float(0xc1200000),  # -10
        bits2float(0x442f0000),  # 700
        bits2float(0x42e60000),  # 115
        bits2float(0x442f0000),  # 700
        bits2float(0x437a0000),  # 250
    )
    path.lineTo(
        bits2float(0x442f0000),  # 700
        bits2float(0x43880000),  # 272
    )
    path.cubicTo(
        bits2float(0x442f0000),  # 700
        bits2float(0x43d18000),  # 419
        bits2float(0x44164000),  # 601
        bits2float(0x43fa0000),  # 500
        bits2float(0x43c88000),  # 401
        bits2float(0x43fa0000),  # 500
    )
    path.cubicTo(
        bits2float(0x43964752),  # 300.557
        bits2float(0x43fa0000),  # 500
        bits2float(0x436db1ed),  # 237.695
        bits2float(0x43ef6824),  # 478.814
        bits2float(0x43480000),  # 200
        bits2float(0x43db8ce9),  # 439.101
    )
    path.close()
    path.moveTo(
        bits2float(0x434805cb),  # 200.023
        bits2float(0x43881798),  # 272.184
    )
    path.cubicTo(
        bits2float(0x43493da4),  # 201.241
        bits2float(0x43b2a869),  # 357.316
        bits2float(0x437bd6b1),  # 251.839
        bits2float(0x43cd0000),  # 410
        bits2float(0x43c80000),  # 400
        bits2float(0x43cd0000),  # 410
    )
    path.cubicTo(
        bits2float(0x44098000),  # 550
        bits2float(0x43cd0000),  # 410
        bits2float(0x44160000),  # 600
        bits2float(0x43b20000),  # 356
        bits2float(0x44160000),  # 600
        bits2float(0x43868000),  # 269
    )
    path.lineTo(
        bits2float(0x44160000),  # 600
        bits2float(0x43808000),  # 257
    )
    path.cubicTo(
        bits2float(0x44160000),  # 600
        bits2float(0x43330000),  # 179
        bits2float(0x44110000),  # 580
        bits2float(0x429c0000),  # 78
        bits2float(0x43cd0000),  # 410
        bits2float(0x429c0000),  # 78
    )
    path.cubicTo(
        bits2float(0x43725298),  # 242.323
        bits2float(0x429c0000),  # 78
        bits2float(0x43491e05),  # 201.117
        bits2float(0x431ccd43),  # 156.802
        bits2float(0x434805cb),  # 200.023
        bits2float(0x43881797),  # 272.184
    )
    path.close()

    contours = list(path.contours)

    # on the second contour, the last and first points' Y coordinate only
    # differ by one bit: 0x43881798 != 0x43881797
    points = contours[1].points
    assert points[0] != points[-1]
    assert points[0] == pytest.approx(points[-1])

    # when "drawn" as segments, almost equal last/first points are treated
    # as exactly equal, without the need of an extra closing lineTo
    for contour in path.contours:
        segments = list(contour.segments)
        assert segments[-1][0] == "closePath"
        first_type, first_pts = segments[0]
        last_type, last_pts = segments[-2]
        assert first_type == "moveTo"
        assert last_type == "curveTo"
        assert last_pts[-1] == first_pts[-1]


def test_float2bits():
    assert float2bits(17.5) == 0x418c0000
    assert float2bits(-10.0) == 0xc1200000


def test_bits2float():
    assert bits2float(0x418c0000) == 17.5
    assert bits2float(0xc1200000) == -10.0
    assert bits2float(-0x3ee00000) == -10.0  # this works too


def test_strip_collinear_moveTo():
    # https://github.com/fonttools/skia-pathops/issues/12
    path = Path()
    path.moveTo(
        bits2float(0x440b8000),  # 558
        bits2float(0x0),  # 0
    )
    path.lineTo(
        bits2float(0x44098000),  # 550
        bits2float(0x0),  # 0
    )
    path.lineTo(
        bits2float(0x440c247f),  # 560.57
        bits2float(0x41daf87e),  # 27.3713
    )
    path.lineTo(
        bits2float(0x440e247f),  # 568.57
        bits2float(0x41daf87e),  # 27.3713
    )
    path.close()
    path.moveTo(
        bits2float(0x440b0000),  # 556
        bits2float(0x40e00000),  # 7
    )
    path.lineTo(
        bits2float(0x440a4000),  # 553
        bits2float(0x0),  # 0
    )
    path.lineTo(
        bits2float(0x44049c26),  # 530.44
        bits2float(0x0),  # 0
    )
    path.lineTo(
        bits2float(0x44052891),  # 532.634
        bits2float(0x40e00000),  # 7
    )
    path.close()

    path.simplify()

    expected = Path()
    expected.moveTo(
        bits2float(0x440b8000),  # 558
        bits2float(0x0),  # 0
    )
    expected.lineTo(
        bits2float(0x440e247f),  # 568.57
        bits2float(0x41daf87e),  # 27.3713
    )
    expected.lineTo(
        bits2float(0x440c247f),  # 560.57
        bits2float(0x41daf87e),  # 27.3713
    )
    expected.lineTo(
        bits2float(0x440a2d02),  # 552.703
        bits2float(0x40e00000),  # 7
    )
    expected.lineTo(
        bits2float(0x44052891),  # 532.634
        bits2float(0x40e00000),  # 7
    )
    expected.lineTo(
        bits2float(0x44049c26),  # 530.44
        bits2float(0x0),  # 0
    )
    # expected.lineTo(
    #     bits2float(0x44098000),  # 550
    #     bits2float(0x0),  # 0
    # )
    expected.close()

    assert list(path) == list(expected)


@pytest.mark.parametrize(
    "message, operations, expected",
    [
        (
            'stroke_2_wide',
            (
                ('moveTo', (5, 5)),
                ('lineTo', (10, 5)),
                ('stroke', (2, 0, 0, 1)),
            ),
            (
                ('moveTo', ((5., 4.),)),
                ('lineTo', ((10., 4.),)),
                ('lineTo', ((10., 6.),)),
                ('lineTo', ((5., 6.),)),
                ('lineTo', ((5., 4.),)),
                ('closePath', ()),
            ),
        ),
        (
            'stroke_dash_array',
            (
                ('moveTo', (5, 5)),
                ('lineTo', (10, 5)),
                ('stroke', (2, 0, 0, 1, (1, 1))),
            ),
            (
                ('moveTo', ((5.0, 4.0),)),
                ('lineTo', ((6.0, 4.0),)),
                ('lineTo', ((6.0, 6.0),)),
                ('lineTo', ((5.0, 6.0),)),
                ('endPath', ()),
                ('moveTo', ((7.0, 4.0),)),
                ('lineTo', ((8.0, 4.0),)),
                ('lineTo', ((8.0, 6.0),)),
                ('lineTo', ((7.0, 6.0),)),
                ('endPath', ()),
                ('moveTo', ((9.0, 4.0),)),
                ('lineTo', ((10.0, 4.0),)),
                ('lineTo', ((10.0, 6.0),)),
                ('lineTo', ((9.0, 6.0),)),
                ('endPath', ()),
            ),
        ),
        (
            'stroke_dash_offset',
            (
                ('moveTo', (5, 5)),
                ('lineTo', (10, 5)),
                ('stroke', (2, 0, 0, 1, (1, 1), 0.5)),
            ),
            (
                ('moveTo', ((5.0, 4.0),)),
                ('lineTo', ((5.5, 4.0),)),
                ('lineTo', ((5.5, 6.0),)),
                ('lineTo', ((5.0, 6.0),)),
                ('endPath', ()),
                ('moveTo', ((6.5, 4.0),)),
                ('lineTo', ((7.5, 4.0),)),
                ('lineTo', ((7.5, 6.0),)),
                ('lineTo', ((6.5, 6.0),)),
                ('endPath', ()),
                ('moveTo', ((8.5, 4.0),)),
                ('lineTo', ((9.5, 4.0),)),
                ('lineTo', ((9.5, 6.0),)),
                ('lineTo', ((8.5, 6.0),)),
                ('endPath', ()),
            ),
        ),
        (
            'conic_2_quad',
            (
                ('moveTo', (10, 10)),
                ('conicTo', (20, 20, 10, 30, 3)),
                ('convertConicsToQuads', ()),
            ),
            (
                ('moveTo', ((10.0, 10.0),)),
                ('qCurveTo', ((14.39, 18.79), (17.50, 26.04), (17.50, 28.96), (14.39, 30.00), (10.0, 30.0))),
                ('endPath', ())
            ),
        ),
        (
            'arc_to_quads',
            (
                ('moveTo', (7, 5)),
                ('arcTo', (3, 1, 0, ArcSize.SMALL, Direction.CCW, 7, 2)),
                ('convertConicsToQuads', ()),
            ),
            (
                ('moveTo', ((7.0, 5.0),)),
                ('qCurveTo', ((11.5, 5.0), (11.5, 2.0), (7.0, 2.0))),
                ('endPath', ()),
            )
        )
    ]
)
def test_path_operation(message, operations, expected):
    path = Path()
    for op, args in operations:
        getattr(path, op)(*args)
    # round the values we get back
    rounded = []
    for verb, pts in path.segments:
        round_pts = []
        for pt in pts:
            round_pts.append(tuple(round(c, 2) for c in pt))
        rounded.append((verb, tuple(round_pts)))
    assert tuple(rounded) == expected, message



@pytest.fixture
def overlapping_path():
    path = Path()
    path.moveTo(0, 0)
    path.lineTo(10, 0)
    path.lineTo(10, 10)
    path.lineTo(0, 10)
    path.close()
    path.moveTo(5, 5)
    path.lineTo(15, 5)
    path.lineTo(15, 15)
    path.lineTo(5, 15)
    path.close()
    return path


def test_simplify(overlapping_path):
    result = simplify(overlapping_path)

    assert overlapping_path != result
    assert list(result) == [
        (PathVerb.MOVE, ((0, 0),)),
        (PathVerb.LINE, ((10, 0),)),
        (PathVerb.LINE, ((10, 5),)),
        (PathVerb.LINE, ((15, 5),)),
        (PathVerb.LINE, ((15, 15),)),
        (PathVerb.LINE, ((5, 15),)),
        (PathVerb.LINE, ((5, 10),)),
        (PathVerb.LINE, ((0, 10),)),
        (PathVerb.CLOSE, ()),
    ]

    overlapping_path.simplify()

    assert overlapping_path == result


def test_simplify_clockwise(overlapping_path):
    result = simplify(overlapping_path, clockwise=True)

    assert overlapping_path != result
    assert list(result) == [
        (PathVerb.MOVE, ((0, 0),)),
        (PathVerb.LINE, ((0, 10),)),
        (PathVerb.LINE, ((5, 10),)),
        (PathVerb.LINE, ((5, 15),)),
        (PathVerb.LINE, ((15, 15),)),
        (PathVerb.LINE, ((15, 5),)),
        (PathVerb.LINE, ((10, 5),)),
        (PathVerb.LINE, ((10, 0),)),
        (PathVerb.CLOSE, ()),
    ]

    overlapping_path.simplify(clockwise=True)

    assert overlapping_path == result
