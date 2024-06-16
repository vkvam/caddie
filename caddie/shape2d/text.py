from OCC.Core.TopLoc import TopLoc_Location
from OCC.Core.TopoDS import TopoDS_Shape
from OCC.Core.Addons import text_to_brep, Font_FA_Regular, Font_FA_Bold

from caddie.plane import Plane, Translation, AXIS_Z, AXIS_X, ORIGIN
from caddie.shape2d import Shape2DBuilder, TOL
from caddie.shape2d.shapes import Text
from caddie.types.convert_to_internal import to_bb, shape_to_convex
from caddie.ladybug_geometry.geometry2d import Polygon2D


class TextBuilder(Shape2DBuilder):
    cache = {}

    def __init__(self, text: Text, tolerance: float = TOL) -> "TopoDS_Shape":
        super().__init__()
        cache_key = hash(text)
        if cache_key in TextBuilder.cache:
            self.bb, self.shape2d, self.hull = TextBuilder.cache[cache_key]
        else:
            text_shape: TopoDS_Shape = text_to_brep(text.txt, "Arial", Font_FA_Bold, text.size, False)

            bb = to_bb(text_shape)

            x_shift = 0
            y_shift = 0
            z_shift = -bb.min.z - bb.size.z * 0.5

            if text.h_align == 'CENTERED':
                x_shift = -bb.min.x - bb.size.x * 0.5
            elif text.h_align == 'LEFT':
                x_shift = -bb.min.x
            elif text.h_align == 'RIGHT':
                x_shift = -bb.min.x - bb.size.x
            elif text.h_align == 'RIGHT_MARGIN':
                x_shift = -bb.min.x * 2 - bb.size.x

            if text.v_align == 'CENTERED':
                y_shift = -bb.min.y - bb.size.y * 0.5
            elif text.v_align == 'BOTTOM':
                y_shift = -bb.min.y
            elif text.v_align == 'TOP':
                y_shift = -bb.min.y - bb.size.y

            x_shift += text.offset.x
            y_shift += text.offset.y

            text_shape = text_shape.Moved(
                TopLoc_Location(
                    Plane(None, ORIGIN, AXIS_Z, AXIS_X).transformed(
                        Translation(x_shift, y_shift, z_shift)
                    ).gp_Trsf(
                        Plane(None, ORIGIN, AXIS_Z, AXIS_X)
                    )
                )
            )
            self.bb = to_bb(text_shape)
            self.shape2d = text_shape
            self.hull = shape_to_convex(text_shape, 0.001)
            TextBuilder.cache[cache_key] = self.bb, self.shape2d, self.hull

    @staticmethod
    def get_bounding_box(text: Text):
        return TextBuilder.cache[hash(text)][0]

    @staticmethod
    def get_hull(text: Text) -> Polygon2D:
        return TextBuilder.cache[hash(text)][2]

    @staticmethod
    def get_shape2d(text: Text):
        return TextBuilder.cache[hash(text)][1]
