from typing import List, Union

from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeFace
from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism
from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.gp import gp_Pln

from caddie.plane import Plane, ORIGIN, AXIS_Z, AXIS_X
from caddie.shape2d.shapes import Sketch, Text
from caddie.shape2d.sketch import FaceBuilder
from caddie.shape2d.text import TextBuilder
from caddie.types.convert_to_gp import to_gp_Ax3


class ExtrusionBuilder:
    def __init__(self, plane: Plane, tolerance=0.001):
        self.plane = plane
        self.tolerance = tolerance
        self.segments: List[Sketch] = []

    def add(self, *faces: Sketch):
        self.segments.extend(faces)
        return self

    def build(self, distance: float) -> "TopoDS_Shape":

        from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse
        compound_shape = None
        for shape2d in self.segments:
            # shape2d = self.segments[0]
            if isinstance(shape2d, Sketch):
                s = FaceBuilder(shape2d, self.tolerance).compound
            else:
                # TODO: Stop this from ever happening
                raise Exception("Not supported")
            if compound_shape is None:
                compound_shape = s
            else:
                compound_shape = BRepAlgoAPI_Fuse(compound_shape, s).Shape()


        # All 2D shapes are constructed in XY plane, move them into the provided desired plane.
        compound_shape = self.plane.moved_into(compound_shape)

        prism_maker = BRepPrimAPI_MakePrism(
            compound_shape,
            self.plane.gp_norm_distance(distance),
            True
        ).Shape()

        return prism_maker
