import dataclasses

from typing import Union, List

from caddie.ladybug_geometry.geometry2d import Point2D

from caddie.plane import Plane, ORIGIN, AXIS_Z, AXIS_X
from caddie.shape2d.shapes import Text
from caddie.shape2d.sketch import Sketch, FaceBuilder
from caddie.shape2d.text import TextBuilder


@dataclasses.dataclass
class WireIdentities:
    """
    Groups wires in a loft operation.
    Wires with the same identity are merged into a
    single solid.

    The identity of a wire is determined by the letter in
    'self.outer' or 'self.inner' with string index matching
    the index of wires after face construction with 'Section.build()'.
    """
    outer: str
    inner: str


class Section:
    def __init__(self, plane: Plane, sketch: Union[Point2D, Sketch, Text],
                 identities: WireIdentities = WireIdentities(
                     "123456789", "123456789"
                 )):
        self.plane = plane
        self.sketch = sketch
        self.identities = identities

    def build(self, tolerance):
        if isinstance(self.sketch, Sketch):
            # TODO: Cache this
            compound = FaceBuilder(self.sketch, tolerance).compound
        elif isinstance(self.sketch, Text):
            compound = TextBuilder(self.sketch, tolerance).shape2d
        else:
            compound = self.sketch

        return compound
