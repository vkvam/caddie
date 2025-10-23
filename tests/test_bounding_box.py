from caddie.ladybug_geometry.geometry3d import Point3D
from caddie.types import BoundingBox


def test_bounding_box_center_returns_midpoint():
    bbox = BoundingBox(Point3D(0, 2, 4), Point3D(10, 4, 8))

    center = bbox.center()

    assert isinstance(center, Point3D)
    assert center.as_tuple() == (5, 3, 6)
