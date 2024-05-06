from OCC.Core.gp import gp_Pnt, gp_Dir, gp_Ax2, gp_Ax3, gp_Trsf, gp_Vec
from ladybug_geometry.geometry3d import Point3D, Vector3D


def to_gp_Pnt(p: Vector3D):
    return gp_Pnt(p.x, p.y, p.z)

def to_gp_Dir(p: Vector3D):
    return gp_Dir(p.x, p.y, p.z)



def to_gp_Vec(p: Vector3D):
    return gp_Vec(p.x, p.y, p.z)


def to_gp_Ax2(center: Point3D, normal: Vector3D, x_dir: Vector3D):
    return gp_Ax2(
        gp_Pnt(center.x, center.y, center.z),
        gp_Dir(normal.x, normal.y, normal.z),
        gp_Dir(x_dir.x, x_dir.y, x_dir.z)
    )


def to_gp_Ax3(center: Point3D, normal: Vector3D, x_dir: Vector3D):
    return gp_Ax3(
        to_gp_Ax2(center,normal,x_dir)
    )


def to_gp_Trfs(vec: Vector3D):
    alignment = gp_Trsf()
    alignment.SetTranslation(
        to_gp_Vec(vec)
    )
    return alignment