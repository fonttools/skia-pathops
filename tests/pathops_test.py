from pathops import _pathops
from pathops import (
    Path, PathPen, OpenPathError, OpBuilder, UNION,
)
from fontTools.pens.recordingPen import RecordingPen

import pytest


def test_demo():
    assert _pathops.demo()


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

    def test_decompose_quadratic_segments(self):
        rec = RecordingPen()
        path = Path()
        pen = path.getPen()
        pen.moveTo((0, 0))
        pen.qCurveTo((1, 1), (2, 2), (3, 3))
        pen.closePath()
        path.draw(rec)
        assert rec.value == [
            ('moveTo', ((0.0, 0.0),)),
            ('qCurveTo', ((1.0, 1.0), (1.5, 1.5))),
            ('qCurveTo', ((2.0, 2.0), (3.0, 3.0))),
            ('lineTo', ((0.0, 0.0),)),
            ('closePath', ())]

    @pytest.mark.xfail(strict=True)
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
        builder.add(path, UNION)

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

        builder = OpBuilder()
        builder.add(path1, UNION)
        builder.add(path2, UNION)
        result = builder.resolve()

        rec = RecordingPen()
        result.draw(rec)
        assert rec.value == [
            ('moveTo', ((5316.0, 4590.0),)),
            ('lineTo', ((5220.0, 4590.0),)),
            ('lineTo', ((5220.0, 4866.92333984375),)),
            ('lineTo', ((5316.0, 4590.0),)),
            ('closePath', ()),
            ('moveTo', ((-225.0, 7425.0),)),
            ('lineTo', ((5.0, -225.0),)),
            ('lineTo', ((7425.0, -225.0),)),
            ('lineTo', ((7425.0, 7425.0),)),
            ('lineTo', ((5688.0, 7425.0),)),
            ('lineTo', ((-225.0, 7425.0),)),
            ('closePath', ())]

