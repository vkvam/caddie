from enum import Enum
from typing import Union
from caddie.ladybug_geometry.geometry2d import Point2D, Arc2D, Polyline2D, LineSegment2D, Polygon2D

TYPES = Union[
    Polygon2D,
    Polyline2D,
    Arc2D,
    LineSegment2D
]


class MODE(Enum):
    ADD = 0
    SUB = 1
    INT = 2


class Face:
    """
    Shapes must form a single Face.
    """
    def __init__(self, mode: MODE, *shape: TYPES) -> None:
        self.mode = mode
        self.shape = shape

    def __hash__(self) -> int:
        return hash((s.__hash__() for s in self.shape))


class Sketch:
    def __init__(self, *shapes: Face):
        self.shapes = shapes

    def __hash__(self) -> int:
        return hash(s.__hash__() for s in self.shapes)


class Text:
    def __init__(self, txt, size: float = 12, h_align: str = '', v_align: str = '', offset: Point2D = Point2D()):
        self.txt = txt
        self.size = size
        self.h_align = h_align
        self.v_align = v_align
        self.offset = offset

    def __hash__(self):
        return hash(self.txt, self.size, self.h_align, self.v_align, self.offset)
