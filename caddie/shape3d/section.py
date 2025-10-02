import dataclasses

from typing import Union, List, Optional

from caddie.ladybug_geometry.geometry2d import Point2D

from caddie.plane import Plane, ORIGIN, AXIS_Z, AXIS_X
from caddie.shape2d import Shape2D
from caddie.shape2d.shapes import Text
from caddie.shape2d.sketch import Sketch, SketchBuilder
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

    def to_shape(self, tolerance: float) -> Shape2D:
        if isinstance(self.sketch, Sketch):
            return SketchBuilder(self.sketch, tolerance).shape2d
        elif isinstance(self.sketch, Text):
            return TextBuilder(self.sketch, tolerance).shape2d
        else:
            raise NotImplementedError(f"{type(self.sketch)} not supported")
