from pathops import _pathops
from pathops import Path, PathPen, OpenPathError

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
