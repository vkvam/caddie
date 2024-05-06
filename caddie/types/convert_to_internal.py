import time

from OCC.Core.BRepAdaptor import BRepAdaptor_Curve
from OCC.Core.BRepBndLib import brepbndlib
from OCC.Core.BRepTools import breptools

from OCC.Core.Bnd import Bnd_Box
from OCC.Core.GCPnts import GCPnts_UniformDeflection
from OCC.Core.TopAbs import TopAbs_EDGE, TopAbs_FACE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import TopoDS_Shape, topods_Edge
from OCC.Core.gp import gp_Pnt2d, gp_Pnt
from ladybug_geometry.geometry2d import Polygon2D, Point2D, Vector2D

from math import atan2

from caddie.types import BoundingBox


def to_bb(*shapes: TopoDS_Shape) -> BoundingBox:
    bb = Bnd_Box()
    for shape in shapes:
        brepbndlib.Add(shape, bb)
    return BoundingBox.from_bnd_box(bb)


def to_Point2D(*pnt: gp_Pnt):
    return [Point2D(p.X(), p.Y()) for p in pnt]

def orientation(p, q, r):
    return (q.y - p.y) * (r.x - q.x) - (q.x - p.x) * (r.y - q.y)

def distance(p, line_start, line_end):
    """Calculate the distance between point p and the line defined by line_start and line_end"""
    return abs((line_end.y - line_start.y)*p.x - (line_end.x - line_start.x)*p.y + line_end.x*line_start.y - line_end.y*line_start.x)

def quickhull(points):
    if len(points) < 3:
        return points

    def recurse(left, right, point_set):
        if not point_set:
            return []

        # Find the farthest point from the line formed by 'left' and 'right'
        max_point = max(point_set, key=lambda p: distance(p, left, right))
        new_set1 = [p for p in point_set if orientation(left, max_point, p) > 0]  # Points to the left of the line left-max_point
        new_set2 = [p for p in point_set if orientation(max_point, right, p) > 0]  # Points to the left of the line max_point-right

        return recurse(left, max_point, new_set1) + [max_point] + recurse(max_point, right, new_set2)

    # Get the leftmost and rightmost points
    leftmost = min(points, key=lambda p: p.x)
    rightmost = max(points, key=lambda p: p.x)

    # Split the points into two halves based on their orientation with the line formed by leftmost and rightmost
    upper = [p for p in points if orientation(leftmost, rightmost, p) > 0]
    lower = [p for p in points if orientation(leftmost, rightmost, p) < 0]

    # Compute the convex hull for each subset
    upper_hull = recurse(leftmost, rightmost, upper)
    lower_hull = recurse(rightmost, leftmost, lower)

    return [leftmost] + upper_hull + [rightmost] + lower_hull

def shape_to_convex(wire, deflection=0.01):
    """Extract the points from the wire's edges and project them to 2D."""
    explorer = TopExp_Explorer(wire, TopAbs_FACE)
    points = []

    while explorer.More():
        wire = breptools.OuterWire(explorer.Value())
        #wire = breptools_OuterWire(explorer.Value())
        edge_explorer = TopExp_Explorer(wire, TopAbs_EDGE)
        while edge_explorer.More():
            curve_adaptor = BRepAdaptor_Curve(edge_explorer.Value())

            # Discretize curved edges
            discretizer = GCPnts_UniformDeflection(curve_adaptor, deflection)
            for i in range(1, discretizer.NbPoints() + 1):
                p = discretizer.Value(i)
                points.append(Point2D(p.X(), p.Y()))  # Projecting onto XY plane
            edge_explorer.Next()

        explorer.Next()
    return Polygon2D(quickhull(points))
