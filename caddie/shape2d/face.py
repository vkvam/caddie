import inspect
import math
from typing import Union

from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, \
    BRepBuilderAPI_MakeFace
from OCC.Core.GC import GC_MakeArcOfCircle
from OCC.Core.TopoDS import TopoDS_Face
from OCC.Core.gp import gp_Pnt, gp_Circ, gp_Ax2
from ladybug_geometry.geometry2d import Arc2D, Polyline2D, LineSegment2D, Polygon2D, Point2D
from ladybug_geometry.geometry3d import Point3D, Vector3D

from caddie.shape2d import Shape2DBuilder
from caddie.types.convert_to_gp import to_gp_Pnt, to_gp_Ax2

TOL = 1e-5

TYPES = Union[
    Polyline2D,
    LineSegment2D,
    Arc2D
]


class WireBuilder(Shape2DBuilder):
    def __init__(self, *edges: TYPES):
        super().__init__()
        self.dispatcher = {}

        method_list = inspect.getmembers(self, predicate=inspect.ismethod)
        for method_name, method in method_list:
            if '__gen__' in method_name:
                for name, param in inspect.signature(method).parameters.items():
                    type_hint = param.annotation
                    if hasattr(type_hint, '__args__'):
                        for t in type_hint.__args__:
                            self.dispatcher[t] = method
                    else:
                        self.dispatcher[type_hint] = method

        self.wire_builder = BRepBuilderAPI_MakeWire()
        for e in edges:
            wire = self.dispatcher[type(e)](e)
            self.wire_builder.Add(wire)

        # Check for errors
        if not self.wire_builder.IsDone():
            raise Exception("NOT DONE :/")

    def __gen__polyline(self, polyline: Union[Polyline2D, Polygon2D]):
        poly = BRepBuilderAPI_MakePolygon()
        local_vertices = [to_gp_Pnt(Point3D.from_point2d(p)) for p in polyline.vertices]
        for p in local_vertices:
            poly.Add(p)
        return poly.Wire()

    def __gen__edge(self, line: LineSegment2D):
        return BRepBuilderAPI_MakeEdge(
            to_gp_Pnt(Point3D.from_point2d(line.p1)),
            to_gp_Pnt(Point3D.from_point2d(line.p2))
        ).Edge()

    def __gen__arc(self, arc: Arc2D):
        # Create the circular arc
        if arc.is_circle:

            arc_maker = GC_MakeArcOfCircle(
                gp_Circ(
                    to_gp_Ax2(
                        Point3D(0, 0, 0),
                        Vector3D(0, 0, 1),
                        Vector3D(1, 0, 0)
                    ),
                    arc.r
                ),
                0, math.pi*2, True
            )
        else:
            arc_maker = GC_MakeArcOfCircle(
                to_gp_Pnt(Point3D.from_point2d(arc.p1)),
                to_gp_Pnt(Point3D.from_point2d(arc.midpoint)),
                to_gp_Pnt(Point3D.from_point2d(arc.p2))
            )

        # Convert to edge
        edge = BRepBuilderAPI_MakeEdge(arc_maker.Value()).Edge()
        return edge

    def build_face(self) -> TopoDS_Face:
        return BRepBuilderAPI_MakeFace(
            self.wire_builder.Wire(),
            True
        ).Face()
