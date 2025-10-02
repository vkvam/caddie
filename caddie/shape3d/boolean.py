from typing import List, Optional, Literal, Tuple

from OCC.Core.BRepAlgoAPI import (BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse)
from OCC.Core.TopoDS import TopoDS_Shape

from caddie.shape3d import Shape

OPS = Literal["cut", "fuse"]


class BooleanBuilder:
    def __init__(self, sort_filter: Optional[callable] = None):
        self.modifiers: List[Tuple[TopoDS_Shape, OPS]] = []
        self.sort_filter = sort_filter # lambda x: 0 if x[1] == 'fuse' else 1
    def add(self, shape: Shape, mode: OPS = "fuse"):
        self.modifiers.append((shape.obj, mode))
        return self

    def build(self) -> Shape:
        
        sorted_mods = sorted(
            self.modifiers,
            key=self.sort_filter
        ) if self.sort_filter else self.modifiers

        shape = sorted_mods[0][0]#self.base_shape

        for mod_shape, op in sorted_mods[1:]:
            if op == "fuse":
                shape = BRepAlgoAPI_Fuse(shape, mod_shape).Shape()
            elif op == "cut":
                shape = BRepAlgoAPI_Cut(shape, mod_shape).Shape()
        return Shape(shape)
