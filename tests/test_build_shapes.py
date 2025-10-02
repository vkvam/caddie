import pathlib
import unittest

from caddie.ladybug_geometry.geometry2d import Arc2D, Point2D
from caddie.plane import Plane, Translation, Rotation, AXIS_X
from caddie.shape2d.shapes import Face, Sketch, MODE, Text
from caddie.shape3d import Shape3D
from caddie.shape3d.boolean import BooleanBuilder
from caddie.shape3d.extrude import ExtrusionBuilder
from OCC.Extend.DataExchange import write_stl_file

from caddie.shape3d.loft import LoftBuilder
from caddie.shape3d.section import Section, WireGroups
from tests.shapes import triangle_w_arc_add, circle_add


class TestBasic(unittest.TestCase):
    OUTPUT_PATH = "tests/output"

    @classmethod
    def setUpClass(cls):
        pathlib.Path(cls.OUTPUT_PATH).mkdir(exist_ok=True)

    def assertFileMinSize(self, path: str, min_bytes: int):
        p = pathlib.Path(path)
        self.assertTrue(p.exists(), f"{path} was not created")
        size = p.stat().st_size
        self.assertGreater(
            size, min_bytes, f"{path} too small: {size} bytes (expected > {min_bytes})"
        )

    def test_extrude_basic(self):
        out: Shape3D = ExtrusionBuilder(
            Section(Plane(), Sketch(triangle_w_arc_add))
        ).to_shape(1)
        path = f"{self.OUTPUT_PATH}/extrude_basic.stl"
        write_stl_file(out.occ_shape, path, mode="binary", angular_deflection=0.1)
        self.assertFileMinSize(path, 1000)  # set threshold you consider “real”

    def test_extrude_text(self):
        out: Shape3D = ExtrusionBuilder(
            Section(Plane(), Text("ABC"))
        ).to_shape(1)
        path = f"{self.OUTPUT_PATH}/extrude_text.stl"
        write_stl_file(out.occ_shape, path, mode="binary", angular_deflection=0.1)
        self.assertFileMinSize(path, 1000)  # set threshold you consider “real”

    def test_bool_3d(self):
        p0 = Plane()
        out_add: Shape3D = ExtrusionBuilder(
            Section(p0, Sketch(circle_add))
        ).to_shape(12)

        out_cut: Shape3D = ExtrusionBuilder(
            Section(p0, Sketch(triangle_w_arc_add))
        ).to_shape(12)

        out = BooleanBuilder().add(
            out_add
        ).add(out_cut, "cut").to_shape()

        path = f"{self.OUTPUT_PATH}/bool_3d.stl"
        write_stl_file(out.occ_shape, path, mode="binary", linear_deflection=0.1, angular_deflection=0.1)
        self.assertFileMinSize(path, 1000)  # set threshold you consider “real”

    def test_loft_simple(self):
        p0 = Plane()
        p1 = p0.transformed(Translation(0, 0, 10), Rotation(15, AXIS_X))
        p2 = p1.transformed(Rotation(15, AXIS_X), Translation(0, 0, 10))
        section = Sketch(
            Face(
                MODE.ADD,
                Arc2D(Point2D(0, 0), 3)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(0, 0), 2)
            )
        )
        out = LoftBuilder(False).add(
            Section(
                p0,
                section
            ),
            Section(
                p1,
                section
            ),
            Section(
                p2,
                section
            )
        ).to_shape()
        path = f"{self.OUTPUT_PATH}/loft_simple.stl"
        write_stl_file(out.occ_shape, path, mode="binary", linear_deflection=0.1, angular_deflection=0.1)

    def test_loft_complex(self):
        l_0 = ["a", "b", "c"]  # 3 faces
        l_1 = ["a", "bc"]  # 2 faces
        l_2 = ["ab", "a", "cd"]  # 3 faces
        l_3 = ["d"]  # 1 face

        p0 = Plane()
        p1 = p0.transformed(Translation(0, 0, 30))
        p2 = p1.transformed(Translation(0, 0, 30), Rotation(15, AXIS_X))
        p3 = p2.transformed(Rotation(15, AXIS_X), Translation(0, 0, 30))

        s_0 = Sketch(
            Face(
                MODE.ADD,
                Arc2D(Point2D(-17, 0), 1)
            ),
            Face(
                MODE.ADD,
                Arc2D(Point2D(0, 0), 3)
            ),
            Face(
                MODE.ADD,
                Arc2D(Point2D(17, 0), 1)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(17, 0), 0.5)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(-17, 0), 0.5)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(0, 0), 0.5)
            ),
        )

        s_1 = Sketch(
            Face(
                MODE.ADD,
                Arc2D(Point2D(0, 18), 6)
            ),
            Face(
                MODE.ADD,
                Arc2D(Point2D(0, 0), 3)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(0, 18), 2)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(0, 0), 1)
            )
        )

        s_2 = Sketch(
            Face(
                MODE.ADD,
                Arc2D(Point2D(-11, 0), 1)
            ),
            Face(
                MODE.ADD,
                Arc2D(Point2D(0, 0), 3)
            ),
            Face(
                MODE.ADD,
                Arc2D(Point2D(11, 0), 1)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(-11, 0), 0.5)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(0, 0), 1)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(11, 0), 0.5)
            )
        )

        s_3 = Sketch(
            Face(
                MODE.ADD,
                Arc2D(Point2D(0, 0), 3)
            ),
            Face(
                MODE.SUB,
                Arc2D(Point2D(0, 0), 2)
            )
        )

        lb = LoftBuilder(True, True).add(
            Section(
                p0,
                s_0,
                WireGroups(
                    l_0, l_0
                )
            ),

        ).add(
            Section(
                p1,
                s_1,
                WireGroups(
                    l_1, l_1
                )
            )
        ).add(
            Section(
                p2,
                s_2,
                WireGroups(
                    l_2, l_2
                )
            )
        ).add(
            Section(
                p3,
                s_3,
                WireGroups(
                    l_3, l_3
                )
            )
        ).to_shape()
        path = f"{self.OUTPUT_PATH}/loft_complex.stl"
        write_stl_file(lb.occ_shape, path, mode="binary", linear_deflection=0.5, angular_deflection=0.5)
        self.assertFileMinSize(path, 1000)