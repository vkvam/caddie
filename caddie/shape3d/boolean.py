from typing import List, Optional, Literal, Tuple, Callable

from OCC.Core.BRepAlgoAPI import (BRepAlgoAPI_Cut, BRepAlgoAPI_Fuse)
from OCC.Core.TopoDS import TopoDS_Shape

from caddie.shape3d import Shape3D

OPS = Literal["cut", "fuse"]


class BooleanBuilder:
    def __init__(self, sort_filter: Optional[Callable[[Tuple[Shape3D, OPS]], int]] = None):
        self.modifiers: List[Tuple[Shape3D, OPS]] = []
        self.sort_filter = sort_filter

    def add(self, shape: Shape3D, mode: OPS = "fuse"):
        self.modifiers.append((shape, mode))
        return self

    def build(self) -> Shape3D:
        
        sorted_mods = sorted(
            self.modifiers,
            key=self.sort_filter
        ) if self.sort_filter else self.modifiers

        shape = sorted_mods[0][0].occ_shape

        for mod_shape, op in sorted_mods[1:]:
            if op == "fuse":
                shape = BRepAlgoAPI_Fuse(shape, mod_shape.occ_shape).Shape()
            elif op == "cut":
                shape = BRepAlgoAPI_Cut(shape, mod_shape.occ_shape).Shape()
        return Shape3D(shape)
