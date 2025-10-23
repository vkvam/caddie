import dataclasses
from typing import TYPE_CHECKING

from caddie.ladybug_geometry.geometry3d import Point3D

if TYPE_CHECKING:
    from OCC.Core.Bnd import Bnd_Box


@dataclasses.dataclass
class BoundingBox:
    def __init__(self, p_min, p_max):
        self.__p_min = p_min
        self.__p_max = p_max
        self.size = self.__p_max - self.__p_min

    @classmethod
    def from_bnd_box(cls, bb: 'Bnd_Box'):
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
        min_coords = self.__p_min.as_tuple()
        max_coords = self.__p_max.as_tuple()
        center_coords = tuple((mi + ma) * 0.5 for mi, ma in zip(min_coords, max_coords))
        return Point3D(*center_coords)

    def __hash__(self):
        return hash(
            self.__p_min.as_tuple() + self.__p_max.as_tuple()
        )

    def __repr__(self):
        return str(f"{self.__p_min}, {self.__p_max}")
