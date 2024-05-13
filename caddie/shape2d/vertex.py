from OCC.Core.BRepBuilderAPI import BRepBuilderAPI_MakeVertex


from caddie.ladybug_geometry.geometry2d import Point2D

from caddie.shape2d import Shape2DBuilder
class Shape2DVertexBuilder(Shape2DBuilder):
    def build(self, point: Point2D) -> "TopoDS_Shape const":
        return self.__gen__point(point)
    def __gen__point(self, point: Point2D):
        gp_pnt = next(self.plane.gp_pnt(point))
        vert = BRepBuilderAPI_MakeVertex(gp_pnt)
        return vert.Vertex()
