from typing import List, Union

from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.gp import gp_Pln

from caddie.plane import Plane, ORIGIN, AXIS_Z, AXIS_X
from caddie.shape2d.shapes import Sketch, Text, MODE
from caddie.shape2d.sketch import SketchBuilder
from caddie.shape2d.text import TextBuilder
from caddie.shape3d import Shape3D
from caddie.shape3d.section import Section
from caddie.types.convert_to_gp import to_gp_Ax3


class ExtrusionBuilder:
    def __init__(self, section: Section, tolerance=0.001):
        self.section = section
        self.tolerance = tolerance

    def build(self, distance: float) -> Shape3D:
        compound_shape = self.section.build(self.tolerance)

        # All 2D shapes are constructed in XY plane, move them into the provided desired plane.
        compound_shape = self.section.plane.moved_into(compound_shape)

        prism_maker = BRepPrimAPI_MakePrism(
            compound_shape,
            self.section.plane.gp_norm_distance(distance),
            True
        )

        return Shape3D(prism_maker.Shape())
