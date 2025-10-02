from dataclasses import dataclass

from OCC.Core.TopoDS import TopoDS_Shape

@dataclass
class Shape3D:
    occ_shape: "TopoDS_Shape"