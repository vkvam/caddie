from dataclasses import dataclass
from typing import Any, Union

from OCC.Core.TopoDS import TopoDS_Compound, TopoDS_Shape

from caddie.shape2d.shapes import Text

TOL = 1e-5

@dataclass
class Shape2D:
    compound: Union[
        TopoDS_Compound,
        TopoDS_Shape
    ]

class Shape2DBuilder:
    def __init__(self):
        self.plane = None
