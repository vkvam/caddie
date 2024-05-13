import dataclasses

from OCC.Core.Bnd import Bnd_Box
from caddie.ladybug_geometry.geometry2d import Point2D
from caddie.ladybug_geometry.geometry3d import Point3D


@dataclasses.dataclass
class BoundingBox:
    def __init__(self, p_min, p_max):
        self.__p_min = p_min
        self.__p_max = p_max
        self.size = self.__p_max - self.__p_min

    @classmethod
    def from_bnd_box(cls, bb: Bnd_Box):
        xmin, ymin, zmin, xmax, ymax, zmax = bb.Get()
        return cls(
            Point3D(
                xmin,
                ymin,
                zmin
            ),
            Point3D(
                xmax,
                ymax,
                zmax
            )
        )

    @classmethod
    def from_points(cls, *pnts: Point3D):
        xmin = min(p.x for p in pnts)
        ymin = min(p.y for p in pnts)
        zmin = min(p.z for p in pnts)

        xmax = max(p.x for p in pnts)
        ymax = max(p.y for p in pnts)
        zmax = max(p.z for p in pnts)
        return cls(
            Point3D(
                xmin,
                ymin,
                zmin
            ),
            Point3D(
                xmax,
                ymax,
                zmax
            )
        )

    @property
    def min(self):
        return self.__p_min

    @property
    def max(self):
        return self.__p_max

    def center(self):
        d = (self.__p_min + self.__p_max) * 0.5
        return Point3D(*d.to_array())

    def __hash__(self):
        return hash(
            self.__p_min.to_array() + self.__p_max.to_array()
        )

    def __repr__(self):
        return str(f"{self.__p_min}, {self.__p_max}")
