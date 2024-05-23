from caddie.shape2d.shapes import Sketch, Face, MODE
from caddie.ladybug_geometry.geometry2d import Arc2D, Point2D, LineSegment2D, Polyline2D, Polygon2D

p0 = Point2D(10, 0)
p1 = Point2D(0, 0)
p_mid_tri = Point2D(5, 5)
p_mid_arc = Point2D(5, 2)

triangle_w_arc_add = Face(
    MODE.ADD,
    Polyline2D(
        [
            p0,
            p_mid_tri,
            p1
        ]
    ),
    Arc2D.from_start_mid_end(
        p0,
        p_mid_arc,
        p1
    )
)

circle_add = Face(
    MODE.ADD,
    Arc2D(Point2D(), 12)
)

circle_sub = Face(
    MODE.SUB,
    Arc2D(Point2D(), 3)
)
