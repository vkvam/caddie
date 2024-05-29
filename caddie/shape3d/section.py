import dataclasses

from typing import Union, List, Optional

from caddie.ladybug_geometry.geometry2d import Point2D

from caddie.plane import Plane, ORIGIN, AXIS_Z, AXIS_X
from caddie.shape2d.shapes import Text
from caddie.shape2d.sketch import Sketch, FaceBuilder
from caddie.shape2d.text import TextBuilder


@dataclasses.dataclass
class WireGroups:
    """
    Wires are assigned to groups by a single character.
    Wires with the same group will be lofted.

    The index of items in outer/inner should match
    the index that shapes where added to a Sketch.

    """
    outer: Optional[List[str]] = None
    inner: Optional[List[str]] = None


class Section:
    def __init__(self, plane: Plane, sketch: Union[Sketch, Text],
                 wire_groups: WireGroups = WireGroups(
                     None, None
                 )):
        self.plane = plane
        self.sketch = sketch
        self.wire_groups = wire_groups

    def build(self, tolerance):
        if isinstance(self.sketch, Sketch):
            # TODO: Cache this
            compound = FaceBuilder(self.sketch, tolerance).compound
        elif isinstance(self.sketch, Text):
            compound = TextBuilder(self.sketch, tolerance).shape2d
        else:
            compound = self.sketch

        return compound
