from enum import Enum
from dataclasses import dataclass
from typing import List, Union, Tuple, Literal, Iterable
from ladybug_geometry.geometry2d import Point2D, Arc2D, Polyline2D, LineSegment2D, Polygon2D, Vector2D

from .face import WireBuilder

TYPES = Union[
    Polygon2D,
    Arc2D,
    WireBuilder
]


class MODE(Enum):
    ADD = 0
    SUB = 1
    INT = 2

class Shape:
    def __init__(self, mode: MODE, *shape: Union[TYPES, 'Sketch']) -> None:
        self.mode = mode
        self.shape = shape
    def __hash__(self) -> int:
        return sum(s.__hash__() for s in self.shape)

class Sketch:
    def __init__(self, *shapes: Shape):
        self.shapes = shapes
    
    def __hash__(self) -> int:
        return sum(s.__hash__() for s in self.shapes)


class Text:
    def __init__(self, txt, size: float = 12, h_align: str = '', v_align: str = '', offset: Point2D = Point2D()):
        self.txt = txt
        self.size = size
        self.h_align = h_align
        self.v_align = v_align
        self.offset = offset
