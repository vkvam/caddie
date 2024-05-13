import math
from typing import Optional, Iterable, Union

from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.gp import gp_Ax2, gp_Pnt, gp_Trsf, gp_Ax3, gp_Pln, gp_Dir, gp_Vec
from caddie.ladybug_geometry.geometry2d import Point2D, Vector2D
from caddie.ladybug_geometry.geometry3d import Vector3D, Point3D
from caddie.ladybug_geometry.geometry3d.plane import Plane as LPlane

from caddie.types.convert_to_gp import to_gp_Ax2, to_gp_Ax3, to_gp_Pnt, to_gp_Dir, to_gp_Vec

AXIS_X = Vector3D(1, 0, 0)
AXIS_Y = Vector3D(0, 1, 0)
AXIS_Z = Vector3D(0, 0, 1)
ORIGIN = Point3D(0, 0, 0)


class Translation(Vector3D):
    pass


class Rotation:
    def __init__(self, angle: float, axis: Vector3D = AXIS_Z, pivot_point: Point3D = ORIGIN):
        self.pivot_point = pivot_point
        self.axis = axis
        self.angle_rad = (angle/180)*math.pi


class Plane:

    def __init__(self, parent: Optional['Plane'], origin: Point3D, normal: Vector3D, x_dir: Vector3D):
        self.parent = parent
        self.__plane = LPlane(normal, origin, x_dir)

    @classmethod
    def build(cls, parent: Optional['Plane'] = None, *transformations: Union[Translation, Rotation]):
        if parent:
            plane: Plane = cls(parent, parent.__plane.o, parent.__plane.n, parent.__plane.x)
        else:
            plane: Plane = cls(parent, Point3D(0, 0, 0), Vector3D(0, 0, 1), Vector3D(1, 0, 0))

        if transformations:
            for trans in transformations:
                if isinstance(trans, Translation):
                    move = plane.__plane.x * trans.x + plane.__plane.y * trans.y + plane.__plane.n * trans.z
                    plane.__plane = plane.__plane.move(move)
                elif isinstance(trans, Rotation):
                    origin = Point3D(*plane.to_global(trans.pivot_point).to_array())
                    axis = plane.to_global(trans.axis) - plane.__plane.o
                    angle = trans.angle_rad
                    plane.__plane = plane.__plane.rotate(
                        axis,
                        angle,
                        origin,
                    )
        return plane

    def transformed(self, *transformation: Union[Translation, Rotation]):
        return Plane.build(
            self,
            *transformation
        )

    def to_global(self, local: Vector3D):
        origin = self.__plane.o
        x_dir = self.__plane.x
        y_dir = self.__plane.y
        z_dir = self.__plane.n

        # Convert from local to global coordinates
        return Vector3D(
            origin.x + local.x * x_dir.x + local.y * y_dir.x + local.z * z_dir.x,
            origin.y + local.x * x_dir.y + local.y * y_dir.y + local.z * z_dir.y,
            origin.z + local.x * x_dir.z + local.y * y_dir.z + local.z * z_dir.z
        )

    def gp_ax3(self) -> gp_Ax3:
        return to_gp_Ax3(
            self.__plane.xy_to_xyz(Vector2D()),
            self.__plane.n,
            self.__plane.x
        )

    def gp_pln(self) -> gp_Pln:
        return gp_Pln(self.gp_ax3())

    def gp_ax2(self, vec: Vector2D(0, 0)) -> gp_Ax2:
        return to_gp_Ax2(
            self.__plane.xy_to_xyz(vec),
            self.__plane.n,
            self.__plane.x
        )

    def gp_pnt(self, *local: Point2D) -> Iterable[gp_Pnt]:
        for l in local:
            yield to_gp_Pnt(self.__plane.xy_to_xyz(l))

    def gp_Trsf(self, other: 'Plane'):
        rotation = gp_Trsf()
        rotation.SetTransformation(
            self.gp_ax3(),
            other.gp_ax3()
        )
        return rotation

    def gp_norm_distance(self, distance: float) -> gp_Vec:
        return to_gp_Vec(self.__plane.n * distance)

    @property
    def o(self) -> Point3D:
        return self.__plane.o

    @property
    def n(self) -> Vector3D:
        return self.__plane.n

    @property
    def x(self) -> Vector3D:
        return self.__plane.x

    @property
    def y(self) -> Vector3D:
        return self.__plane.y

    def moved_into(self, shape):
        return shape.Moved(TopLoc_Location(
            self.gp_Trsf(
                Plane(None, ORIGIN, AXIS_Z, AXIS_X)
            )

        ))