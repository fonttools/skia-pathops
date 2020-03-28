from pathops import Path, PathVerb
from pathops.operations import union, difference, intersection, reverse_difference, xor
import pytest


@pytest.mark.parametrize(
    "subject_path, clip_path, expected",
    [
        [
            [
                (PathVerb.MOVE, ((0, 0),)),
                (PathVerb.LINE, ((0, 10),)),
                (PathVerb.LINE, ((10, 10),)),
                (PathVerb.LINE, ((10, 0),)),
                (PathVerb.CLOSE, ()),
            ],
            [
                (PathVerb.MOVE, ((5, 5),)),
                (PathVerb.LINE, ((5, 15),)),
                (PathVerb.LINE, ((15, 15),)),
                (PathVerb.LINE, ((15, 5),)),
                (PathVerb.CLOSE, ()),
            ],
            [
                (PathVerb.MOVE, ((5, 5),)),
                (PathVerb.LINE, ((10, 5),)),
                (PathVerb.LINE, ((10, 10),)),
                (PathVerb.LINE, ((5, 10),)),
                (PathVerb.CLOSE, ()),
            ],
        ]
    ],
)
def test_intersection(subject_path, clip_path, expected):
    sub = Path()
    for verb, pts in subject_path:
        sub.add(verb, *pts)
    clip = Path()
    for verb, pts in clip_path:
        clip.add(verb, *pts)
    result = Path()

    intersection([sub], [clip], result.getPen())

    assert list(result) == expected
