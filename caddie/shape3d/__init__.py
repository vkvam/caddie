from dataclasses import dataclass

from OCC.Core.TopoDS import TopoDS_Shape

@dataclass
class Shape:
    obj: "TopoDS_Shape"