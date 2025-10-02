from OCC.Core.BRepPrimAPI import BRepPrimAPI_MakePrism

from caddie.shape2d import Shape2D
from caddie.shape3d import Shape3D
from caddie.shape3d.section import Section


class ExtrusionBuilder:
    def __init__(self, section: Section, tolerance=0.001):
        self.section = section
        self.tolerance = tolerance

    def to_shape(self, distance: float) -> Shape3D:
        shape2d: Shape2D = self.section.to_shape(self.tolerance)

        # All 2D shapes are constructed in XY plane, move them into the provided desired plane.
        compound_shape = self.section.plane.moved_into(shape2d.compound)

        prism_maker = BRepPrimAPI_MakePrism(
            compound_shape,
            self.section.plane.gp_norm_distance(distance),
            True
        )

        return Shape3D(prism_maker.Shape())
