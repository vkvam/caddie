import os
import sys
import types
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))


def _install_fake_occ():
    if "OCC" in sys.modules:
        return

    class _TopoShape:
        def __init__(self, label="shape", parts=None):
            self.label = label
            self.parts = list(parts or [])

        def __repr__(self):  # pragma: no cover - debug helper
            return f"TopoShape({self.label})"

    class _TopoDS_Shape(_TopoShape):
        pass

    class _TopoDS_Compound(_TopoShape):
        pass

    class _TopoDS_Face(_TopoShape):
        pass

    class _BRep_Builder:
        def MakeCompound(self, compound):
            compound.parts = []

        def Add(self, compound, shape):
            compound.parts.append(shape)

    class _AlgoBase:
        def __init__(self, a, b):
            self._a = a
            self._b = b
            self._done = True

        def SetFuzzyValue(self, tolerance):  # pragma: no cover - no effect needed
            self._tolerance = tolerance

        def Build(self):
            self._done = True

        def IsDone(self):
            return self._done

    class _BRepAlgoAPI_Fuse(_AlgoBase):
        def Shape(self):
            return _TopoDS_Compound("fuse", [self._a, self._b])

    class _BRepAlgoAPI_Cut(_AlgoBase):
        def Shape(self):
            return _TopoDS_Compound("cut", [self._a, self._b])

    class _Wire:
        def __init__(self):
            self.edges = []

    class _BRepBuilderAPI_MakePolygon:
        def __init__(self):
            self.vertices = []

        def Add(self, point):
            self.vertices.append(point)

        def Close(self):  # pragma: no cover - noop for fake
            pass

        def Wire(self):
            return _Wire()

    class _Edge:
        def __init__(self, start, end):
            self.start = start
            self.end = end

    class _BRepBuilderAPI_MakeEdge:
        def __init__(self, start, end):
            self._edge = _Edge(start, end)

        def Edge(self):
            return self._edge

    class _BRepBuilderAPI_MakeWire:
        def __init__(self):
            self.wire = _Wire()

        def Add(self, shape):
            self.wire.edges.append(shape)

        def Wire(self):
            return self.wire

    class _BRepBuilderAPI_MakeFace:
        def __init__(self, wire):
            self.wire = wire

        def Face(self):
            return _TopoDS_Face("face", self.wire.edges)

    class _gp_Pnt:
        def __init__(self, x, y, z):
            self.x, self.y, self.z = x, y, z

    class _gp_Dir(_gp_Pnt):
        pass

    class _gp_Vec(_gp_Pnt):
        pass

    class _gp_Ax2:
        def __init__(self, pnt, dir_normal, dir_x):
            self.pnt = pnt
            self.dir_normal = dir_normal
            self.dir_x = dir_x

    class _gp_Ax3:
        def __init__(self, ax2):
            self.ax2 = ax2

    class _gp_Trsf:
        def __init__(self):
            self.transformations = []

        def SetTransformation(self, ax3_from, ax3_to):  # pragma: no cover - noop
            self.transformations.append(("transform", ax3_from, ax3_to))

        def SetTranslation(self, vec):  # pragma: no cover - noop
            self.transformations.append(("translate", vec))

    class _gp_Pln:
        def __init__(self, ax3):
            self.ax3 = ax3

    class _gp_Circ:
        def __init__(self, ax2, radius):
            self.ax2 = ax2
            self.radius = radius

    class _TopLoc_Location:
        def __init__(self, trsf):
            self.trsf = trsf

    occ_module = types.ModuleType("OCC")
    core_module = types.ModuleType("OCC.Core")

    brep_module = types.ModuleType("OCC.Core.BRep")
    brep_module.BRep_Builder = _BRep_Builder

    brepalgo_module = types.ModuleType("OCC.Core.BRepAlgoAPI")
    brepalgo_module.BRepAlgoAPI_Fuse = _BRepAlgoAPI_Fuse
    brepalgo_module.BRepAlgoAPI_Cut = _BRepAlgoAPI_Cut

    brepbuilder_module = types.ModuleType("OCC.Core.BRepBuilderAPI")
    brepbuilder_module.BRepBuilderAPI_MakePolygon = _BRepBuilderAPI_MakePolygon
    brepbuilder_module.BRepBuilderAPI_MakeEdge = _BRepBuilderAPI_MakeEdge
    brepbuilder_module.BRepBuilderAPI_MakeWire = _BRepBuilderAPI_MakeWire
    brepbuilder_module.BRepBuilderAPI_MakeFace = _BRepBuilderAPI_MakeFace

    topo_module = types.ModuleType("OCC.Core.TopoDS")
    topo_module.TopoDS_Compound = _TopoDS_Compound
    topo_module.TopoDS_Face = _TopoDS_Face
    topo_module.TopoDS_Shape = _TopoDS_Shape

    gp_module = types.ModuleType("OCC.Core.gp")
    gp_module.gp_Pnt = _gp_Pnt
    gp_module.gp_Dir = _gp_Dir
    gp_module.gp_Vec = _gp_Vec
    gp_module.gp_Ax2 = _gp_Ax2
    gp_module.gp_Ax3 = _gp_Ax3
    gp_module.gp_Trsf = _gp_Trsf
    gp_module.gp_Pln = _gp_Pln
    gp_module.gp_Circ = _gp_Circ

    toploc_module = types.ModuleType("OCC.Core.TopLoc")
    toploc_module.TopLoc_Location = _TopLoc_Location

    sys.modules["OCC"] = occ_module
    sys.modules["OCC.Core"] = core_module
    sys.modules["OCC.Core.BRep"] = brep_module
    sys.modules["OCC.Core.BRepAlgoAPI"] = brepalgo_module
    sys.modules["OCC.Core.BRepBuilderAPI"] = brepbuilder_module
    bnd_module = types.ModuleType("OCC.Core.Bnd")

    class _Bnd_Box:
        def __init__(self, bounds=(0, 0, 0, 0, 0, 0)):
            self._bounds = bounds

        def Get(self):
            return self._bounds

    bnd_module.Bnd_Box = _Bnd_Box

    sys.modules["OCC.Core.TopoDS"] = topo_module
    sys.modules["OCC.Core.gp"] = gp_module
    sys.modules["OCC.Core.TopLoc"] = toploc_module
    sys.modules["OCC.Core.Bnd"] = bnd_module


_install_fake_occ()


def _install_fake_text_builder():
    if "caddie.shape2d.text" in sys.modules:
        return

    fake_text_module = types.ModuleType("caddie.shape2d.text")

    class _FakeTextBuilder:
        cache = {}

        def __init__(self, *_, **__):
            self.shape2d = None

    fake_text_module.TextBuilder = _FakeTextBuilder

    sys.modules["caddie.shape2d.text"] = fake_text_module


_install_fake_text_builder()

from caddie.ladybug_geometry.geometry2d import Point2D, Polygon2D
from caddie.shape2d.shapes import Face, MODE, Sketch
from caddie.shape2d.sketch import SketchBuilder


def _sample_sketch():
    return Sketch(
        Face(
            MODE.ADD,
            Polygon2D(
                [
                    Point2D(0, 0),
                    Point2D(1, 0),
                    Point2D(0, 1),
                ]
            ),
        )
    )


class TestSketchBuilderCache(unittest.TestCase):
    def setUp(self):
        SketchBuilder.cache.clear()

    def test_cache_reuse_same_tolerance(self):
        sketch = _sample_sketch()
        builder_a = SketchBuilder(sketch, tolerance=1e-3)
        builder_b = SketchBuilder(sketch, tolerance=1e-3)

        self.assertIs(builder_a.shape2d, builder_b.shape2d)
        self.assertEqual(len(SketchBuilder.cache), 1)

    def test_cache_separates_by_tolerance(self):
        sketch = _sample_sketch()
        builder_a = SketchBuilder(sketch, tolerance=1e-3)
        builder_b = SketchBuilder(sketch, tolerance=1e-4)

        self.assertIsNot(builder_a.shape2d, builder_b.shape2d)
        self.assertEqual(len(SketchBuilder.cache), 2)


if __name__ == "__main__":
    unittest.main()
