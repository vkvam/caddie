import unittest

from caddie.ladybug_geometry.geometry2d import Arc2D, Point2D
from caddie.plane import Plane
from caddie.shape2d.shapes import Sketch, Shape, MODE
from caddie.shape3d.extrude import ExtrusionBuilder

from caddie.render import shape_to_gltf
from OCC.Extend.DataExchange import write_stl_file


class TestBasic(unittest.TestCase):
    def test_build_basic_model(self):
        fb = Sketch(
            Shape(MODE.ADD, Arc2D(Point2D(), 7))
        )

        out = ExtrusionBuilder(
            Plane.build()
        ).add(fb).build(10)

        with open("output.gltf", "w") as f:
            f.write(shape_to_gltf(out, linear_deflect=1, angular_deflect=1))
        write_stl_file(out, "output.stl")

