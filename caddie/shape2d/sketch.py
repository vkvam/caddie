import inspect
from typing import Tuple

from OCC.Core.BRep import BRep_Builder
from OCC.Core.BRepAlgoAPI import BRepAlgoAPI_Fuse, BRepAlgoAPI_Cut, BRepAlgoAPI_Common
from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeEdge, BRepBuilderAPI_MakeWire, \
    BRepBuilderAPI_MakeFace
from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Face
from OCC.Core.gp import gp_Circ, gp_Lin
from caddie.ladybug_geometry.geometry2d import Arc2D, Polyline2D, Polygon2D, LineSegment2D
from caddie.ladybug_geometry.geometry3d import Point3D

from caddie.plane import ORIGIN, AXIS_Z, AXIS_X
from caddie.shape2d import Shape2DBuilder
from caddie.shape2d.face import WireBuilder
from caddie.shape2d.shapes import Face, Sketch, MODE, Text
from caddie.shape2d.text import TextBuilder
from caddie.types.convert_to_gp import to_gp_Pnt, to_gp_Ax2

TOL = 1e-5


def create_compound_from_shapes(shapes):
    # Step 1: Create a BRep_Builder instance
    builder = BRep_Builder()

    # Step 2: Initialize a TopoDS_Compound
    compound = TopoDS_Compound()
    builder.MakeCompound(compound)

    # Step 3: Add shapes to the compound
    for shape in shapes:
        builder.Add(compound, shape)

    return compound


class FaceBuilder(Shape2DBuilder):
    cache = {}

    def __init__(self, sketch: Sketch, tolerance: float = TOL):
        super().__init__()
        self.tolerance = tolerance
        cache_key = hash(sketch)
        if cache_key in FaceBuilder.cache:
            self.compound = FaceBuilder.cache[cache_key]
        else:
            self.dispatcher = {}

            method_list = inspect.getmembers(self, predicate=inspect.ismethod)
            for method_name, method in method_list:
                if '__gen__' in method_name:
                    for name, param in inspect.signature(method).parameters.items():
                        type_hint = param.annotation
                        self.dispatcher[type_hint] = method

            def is_face(s2):
                if isinstance(s2, Sketch):
                    return False
                return True

            def __build_add(add_compound, shape):
                print("ADD", add_compound, shape)
                new_face = self.__make_face([shape, ]) if is_face(shape) else build(shape.shapes)
                print("NEW FACE", new_face)
                if add_compound is None:
                    add_compound = create_compound_from_shapes([new_face])
                else:
                    algo = BRepAlgoAPI_Fuse(
                        new_face,
                        add_compound
                    )

                    algo.SetFuzzyValue(self.tolerance)
                    algo.Build()
                    if not algo.IsDone():
                        raise ValueError("Failed to fuse the given faces.")
                    add_compound = algo.Shape()
                return add_compound

            def __build_sub(add_compound, shape):
                print("SUB", add_compound, shape)
                new_face = self.__make_face([shape, ]) if is_face(shape) else build(shape.shapes)
                if add_compound is None:
                    add_compound = create_compound_from_shapes([new_face])
                else:
                    algo = BRepAlgoAPI_Cut(
                        add_compound,
                        new_face
                    )

                    if not algo.IsDone():
                        raise ValueError("Failed to fuse the given faces.")
                    add_compound = algo.Shape()
                return add_compound

            def build(shapes: Tuple[Face, ...]):
                add_compound = None
                for s in shapes:
                    if s.mode == MODE.ADD:
                        add_compound = __build_add(add_compound, s.shape)
                    elif s.mode == MODE.SUB:
                        add_compound = __build_sub(add_compound, s.shape)
                    else:
                        raise Exception("Not supported")
                return add_compound

            self.compound = build(sketch.shapes)
            FaceBuilder.cache[cache_key] = self.compound

    def __make_face(self, s):
        shapes = []
        for x in s:
            all_built_shapes = []
            for y in x:
                shape = self.dispatcher[type(y)](y)
                all_built_shapes.append(shape)
            print(all_built_shapes)

            if isinstance(shape, TopoDS_Face) or isinstance(shape, TopoDS_Compound):
                shapes.append(shape)
            else:
                wire_builder = BRepBuilderAPI_MakeWire()
                for s2 in all_built_shapes:
                    wire_builder.Add(s2)
                face_builder = BRepBuilderAPI_MakeFace(
                    wire_builder.Wire()
                )
                face = face_builder.Face()
                shapes.append(face)

        add_compound = None
        for s in shapes:
            if add_compound is None:
                add_compound = create_compound_from_shapes([s])
            else:
                algo = BRepAlgoAPI_Fuse(
                    s,
                    add_compound
                )

                algo.SetFuzzyValue(self.tolerance)
                algo.Build()
                if not algo.IsDone():
                    raise ValueError("Failed to fuse the given faces.")
                add_compound = algo.Shape()

        return add_compound

    def __gen__polyline(self, polyline: Polyline2D, is_polygon: bool = False):
        poly = BRepBuilderAPI_MakePolygon()
        local_vertices = [to_gp_Pnt(Point3D.from_point2d(p)) for p in polyline.vertices]
        for p in local_vertices:
            poly.Add(p)
        if is_polygon and not polyline.is_closed(self.tolerance):
            poly.Close()  # Ensure the polygon is closed
        return poly.Wire()

    def __gen__line(self, polyline: LineSegment2D):
        edge = BRepBuilderAPI_MakeEdge(
            to_gp_Pnt(Point3D.from_point2d(polyline.p1)),
            to_gp_Pnt(Point3D.from_point2d(polyline.p2))
        ).Edge()
        return edge

    def __gen__polygon(self, polygon: Polygon2D):
        if not polygon.is_clockwise:
            polygon = polygon.reverse()
        return self.__gen__polyline(Polyline2D.from_polygon(polygon), True)

    def __gen__face(self, line: WireBuilder) -> TopoDS_Face:
        return line.build_face()

    def __gen__text(self, text: Text) -> TopoDS_Face:
        return TextBuilder(text=text, tolerance=self.tolerance).shape2d

    def __gen__arc(self, arc: Arc2D):

        local_points = to_gp_Pnt(Point3D.from_point2d(arc.p1)), to_gp_Pnt(Point3D.from_point2d(arc.p2))
        gp_ax2 = to_gp_Ax2(
            Point3D.from_point2d(arc.c),
            AXIS_Z,
            AXIS_X
        )

        circle = gp_Circ(
            gp_ax2, arc.r
        )

        edge = BRepBuilderAPI_MakeEdge(circle, *local_points).Edge()
        return edge
