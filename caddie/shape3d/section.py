import dataclasses
from abc import abstractmethod
from typing import Union, List

from OCC.Core.BRep import BRep_Builder, BRep_Tool_Curve
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepTools import breptools_OuterWire
from OCC.Core.Geom import Geom_Curve
from OCC.Core.ShapeExtend import ShapeExtend_WireData
from OCC.Core.Standard import Standard_Type
from OCC.Core.TopAbs import TopAbs_WIRE, TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import topods_Wire, TopoDS_Compound, topods_Face, topods_Compound, TopoDS_Edge
from caddie.ladybug_geometry.geometry2d import Point2D

from caddie.plane import Plane, ORIGIN, AXIS_Z, AXIS_X
from caddie.shape2d.shapes import Text
from caddie.shape2d.sketch import Sketch, FaceBuilder
from caddie.shape2d.text import TextBuilder

@dataclasses.dataclass
class SectionIdentities:
    outer: List[str]
    inner: List[str]

class Section:
    def __init__(self, plane: Plane, sketch: Union[Point2D, Sketch, Text], identities: SectionIdentities = SectionIdentities(
        "0123456789", "0123456789"
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
