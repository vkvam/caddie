from collections import defaultdict
from typing import List

from OCC.Core.BRepExtrema import BRepExtrema_DistShapeShape
from OCC.Core.BRepOffsetAPI import BRepOffsetAPI_ThruSections
from OCC.Core.BRepTools import breptools
from OCC.Core.TopAbs import TopAbs_FACE, TopAbs_WIRE
from OCC.Core.TopExp import TopExp_Explorer
from OCC.Core.TopoDS import TopoDS_Compound

from caddie.shape3d.boolean import BooleanBuilder
from caddie.shape3d.section import Section


def combine_lists(lists, index=0, path=[]):
    if not lists:
        return [[]]

    # Generate all combinations of the remaining lists
    combinations = combine_lists(lists[1:])

    # For each element in the first list, pair it with each combination of the remaining lists
    result = []
    for item in lists[0]:
        for combination in combinations:
            result.append([[item]] + combination)

    return result


def combine_lists2(other_lists):
    # TODO: Attempt to link as many faces as possible.
    # limit to the maximum sublist length
    # with as few collisions as possible

    combined = []
    base_list = other_lists[0]
    other_lists = other_lists[1:]
    base_len = len(base_list)

    for i, base_item in enumerate(base_list):
        combined_group = [[base_item]]  # Start with a sublist containing the base item

        for lst in other_lists:
            lst_len = len(lst)

            if lst_len >= base_len:
                # Group items from the larger list with the base item
                chunk_size = lst_len // base_len
                combined_group.append(lst[i * chunk_size: (i + 1) * chunk_size])
            else:
                # Repeat the item from the smaller list for each element in the base list
                combined_group.append([lst[i % lst_len]])

        combined.append(combined_group)

    return combined


def faces_intersect(face1, face2, tolerance=1e-7):
    """Check if two faces intersect."""
    dist_shape_shape = BRepExtrema_DistShapeShape(face1, face2)
    dist_shape_shape.Perform()
    return dist_shape_shape.Value() < tolerance


def group_intersecting_faces(faces):
    """Group faces that intersect."""
    # Create an empty graph
    G = nx.Graph()

    # Add each face as a node in the graph
    for face in faces:
        G.add_node(face)

    # Check each pair of faces for intersection
    for i, face1 in enumerate(faces):
        for j, face2 in enumerate(faces):
            if i < j and faces_intersect(face1, face2):
                G.add_edge(face1, face2)

    # Find connected components (groups of intersecting faces)
    return list(nx.connected_components(G))


class LoftBuilder:
    def __init__(self, ruled: bool = True, solid: bool = True, precision: float = 1e-6):
        self.segments: List[Section] = []
        self.ruled = ruled
        self.solid = solid
        self.precision = precision

    def add(self, *segment: Section):
        self.segments.extend(segment)
        return self

    def build(self) -> 'TopoDS_Shape const':
        grouped_segments = defaultdict(lambda: ([], []))

        for idx, section in enumerate(self.segments):
            shape = section.build(self.precision)

            inner_wires = []
            outer_wires = []

            grouped_outer_wires = defaultdict(list)
            grouped_inner_wires = defaultdict(list)
            outer_idx = 0
            inner_idx = 0

            if isinstance(shape, TopoDS_Compound):
                explorer = TopExp_Explorer(shape, TopAbs_FACE)
                while explorer.More():

                    face = explorer.Value()
                    face = section.plane.moved_into(face)

                    outer_wire = breptools.OuterWire(face)

                    wire_explorer = TopExp_Explorer(face, TopAbs_WIRE)
                    while wire_explorer.More():
                        wire = wire_explorer.Value()
                        if not wire.IsEqual(outer_wire):
                            inner_wires.append(wire)
                            if section.wire_groups.inner is None:
                                ident = [inner_idx]
                            else:
                                ident = section.wire_groups.inner[inner_idx]
                            if ident != "0":
                                for ident_seg in ident:
                                    grouped_inner_wires[ident_seg].append(wire)
                            inner_idx += 1
                        else:
                            outer_wires.append(wire)
                            if section.wire_groups.inner is None:
                                ident = [outer_idx]
                            else:
                                ident = section.wire_groups.outer[outer_idx]

                            if ident != "0":
                                for ident_seg in ident:
                                    grouped_outer_wires[ident_seg].append(wire)
                            outer_idx += 1
                        wire_explorer.Next()
                    explorer.Next()
            else:
                raise NotImplemented

            for k, v in grouped_outer_wires.items():
                grouped_segments[k][0].append(v)

            for k, v in grouped_inner_wires.items():
                grouped_segments[k][1].append(v)

        bool_builder = BooleanBuilder(sort_filter=lambda x: 0 if x[1] == 'fuse' else 1)
        for k, v in grouped_segments.items():
            outer_w, inner_w = v
            if outer_w:
                outer_shape = self.__build_bb_shape(outer_w)
                outer_shape_built = outer_shape.build()
                bool_builder.add(outer_shape_built)
                if inner_w:
                    inner_shape = self.__build_bb_shape(v[1], outer_shape_built) if v[1] else None
                    if inner_shape is not None and len(inner_shape.modifiers) > 0:
                        bool_builder.add(inner_shape.build(), mode="cut")
        return bool_builder.build()

    def __build_bb_shape(self, wire_segments, contained_in=None):
        wire_segment_paths = combine_lists(wire_segments)
        bb = BooleanBuilder()
        for path in wire_segment_paths:
            shape = BRepOffsetAPI_ThruSections(self.solid, self.ruled, self.precision)
            for w in path:
                for w2 in w:
                    shape.AddWire(w2)
            built_shape = shape.Shape()
            bb.add(built_shape, "fuse")
        return bb
