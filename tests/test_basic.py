import unittest

from OCC.Core.TopoDS import TopoDS_Shape

from caddie.ladybug_geometry.geometry2d import Arc2D, Point2D
from caddie.plane import Plane, Translation, Rotation, AXIS_X
from caddie.shape2d.shapes import Face, Sketch, MODE, Text
from caddie.shape3d.boolean import BooleanBuilder
from caddie.shape3d.extrude import ExtrusionBuilder
from OCC.Extend.DataExchange import write_stl_file

from caddie.shape3d.loft import LoftBuilder
from caddie.shape3d.section import Section, WireIdentities
from tests.shapes import triangle_w_arc_add, circle_add, circle_sub


class TestBasic(unittest.TestCase):
    def test_build_basic_model(self):
        out: TopoDS_Shape = ExtrusionBuilder(
            Section(Plane.build(), Sketch(triangle_w_arc_add))
        ).build(1)

        write_stl_file(out, "output.stl")

    def test_bool_2d(self):
        out: TopoDS_Shape = ExtrusionBuilder(
            Section(Plane.build(), Text("ABC"))
        ).build(1)

        write_stl_file(out, "output.stl")

    def test_bool_3d(self):
        p0 = Plane.build()
        out_add: TopoDS_Shape = ExtrusionBuilder(
            Section(p0, Sketch(circle_add))
        ).build(12)

        out_sub: TopoDS_Shape = ExtrusionBuilder(
            Section(p0, Sketch(triangle_w_arc_add))
        ).build(12)

        out = BooleanBuilder().add(
            out_add
        ).add(out_sub, "cut").build()

        write_stl_file(out, "output.stl", linear_deflection=0.1, angular_deflection=0.1)

    def test_loft_merge_faces(self):
        p0 = Plane.build()
        s = Sketch(circle_add, circle_sub)
        s2 = Sketch(
            Face(
                MODE.ADD,
                Arc2D(Point2D(-7, 0), 5)
            ),
            Face(
                MODE.ADD,
                Arc2D(Point2D(7, 0), 5)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(-7, 0), 3)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(7, 0), 3)
            )
        )
        lb = LoftBuilder().add(
            Section(
                p0.transformed(Translation(0, 0, 20)), s2,
                WireIdentities(
                    "11", "11"
                )
            ),

        ).add(
            Section(
                p0, s, WireIdentities(
                    "1", "1"
                )
            )
        ).build()

        write_stl_file(lb, "output_split.stl", linear_deflection=0.1, angular_deflection=0.1)

    def test_loft_merge_faces_multiple_sections(self):
        p0 = Plane.build()
        s0 = Sketch(
            Face(
                MODE.ADD,
                Arc2D(Point2D(-10, 0), 1)
            ),
            Face(
                MODE.ADD,
                Arc2D(Point2D(0, 0), 1)
            ),
            Face(
                MODE.ADD,
                Arc2D(Point2D(10, 0), 1)
            )
        )
        s1 = Sketch(
            Face(
                MODE.ADD,
                Arc2D(Point2D(-3, 0), 1)
            ),
            Face(
                MODE.ADD,
                Arc2D(Point2D(3, 0), 1)
            )
        )

        lb = LoftBuilder().add(
            Section(
                p0, s0,
                WireIdentities(
                    "112", ""
                )
            ),

        ).add(
            Section(
                p0.transformed(Translation(0, 0, 10)), s1,
                WireIdentities(
                    "12", ""
                )
            )
        ).add(
            Section(
                p0.transformed(Translation(0, 0, 20), Rotation(30)), s0,
                WireIdentities(
                    "211", ""
                )
            )
        ).build()

        write_stl_file(lb, "output_split.stl", linear_deflection=0.1, angular_deflection=0.1)

    def test_loft_non_rules(self):
        p0 = Plane.build(None, )
        p1 = p0.transformed(Translation(0, 0, 5), Rotation(30, AXIS_X))
        p2 = p1.transformed(Translation(0, 0, 5))

        s0 = Sketch(
            Face(
                MODE.ADD,
                Arc2D(Point2D(0, 0), 1)
            )
        )

        lb = LoftBuilder(False).add(
            Section(
                p0, s0
            ),

        ).add(
            Section(
                p1, s0
            )
        ).add(
            Section(
                p2, s0
            )
        ).build()

        write_stl_file(lb, "output_split.stl", linear_deflection=0.5, angular_deflection=0.5, mode="binary")
