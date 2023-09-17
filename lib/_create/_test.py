from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType

import clr

clr.AddReference("System")

from _create import _transactions as a
from _create import _test as tt
from _create import _parts as p
from _create import _coordinate as c
from _create import _openings as o
from _create import _errorhandler as e
from _create import _checks as cc
from pyrevit import forms

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project


# ________________________________________________________________________________________________TESTS


def test_centre_window_index(__title__, window_option=True):
    part = p.select_part()
    host_wall_id = p.get_host_wall_id(part)
    host_wall_type_id = p.get_host_wall_type_id(host_wall_id)
    layer_index = p.get_layer_index(part)
    lap_type_id, side_of_wall, exterior = p.get_wallsweep_parameters(layer_index, host_wall_type_id)
    hosted_windows = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Windows)
    hosted_doors = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Doors)

    reveal_coordinate_0 = p.get_reveal_coordinate_at_0(__title__, part)

    if window_option:
        for window in hosted_windows:
            window_index = o.get_fenestration_centre_index(part, window, reveal_coordinate_0)
            a.auto_place_reveal(__title__, host_wall_id, lap_type_id, window_index, side_of_wall)

    else:
        for window in hosted_doors:
            window_index = o.get_fenestration_centre_index(part, window, reveal_coordinate_0)
            a.auto_place_reveal(__title__, host_wall_id, lap_type_id, window_index, side_of_wall)


def test_fenestration_edges(__title__, window_option=True):
    part = p.select_part()
    host_wall_id = p.get_host_wall_id(part)
    host_wall_type_id = p.get_host_wall_type_id(host_wall_id)
    layer_index = p.get_layer_index(part)
    lap_type_id, side_of_wall, exterior = p.get_wallsweep_parameters(layer_index, host_wall_type_id)
    hosted_windows = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Windows)
    hosted_doors = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Doors)

    reveal_coordinate_0 = p.get_reveal_coordinate_at_0(__title__, part)

    if window_option:
        for window in hosted_windows:
            window_centre_index = o.get_fenestration_centre_index(part, window, reveal_coordinate_0)
            fenestration_width = o.get_fenestration_width(window.Id)
            print (fenestration_width)
            edges_1, edges_2 = o.get_fenestration_edge_indexes(fenestration_width, window_centre_index)
            a.auto_place_reveal(__title__, host_wall_id, lap_type_id, edges_1, side_of_wall)
            a.auto_place_reveal(__title__, host_wall_id, lap_type_id, edges_2, side_of_wall)

    else:
        for door in hosted_doors:
            door_centre_index = o.get_fenestration_centre_index(part, door, reveal_coordinate_0)
            fenestration_width = o.get_fenestration_width(door.Id)
            print (fenestration_width)
            edges_1, edges_2 = o.get_fenestration_edge_indexes(fenestration_width, door_centre_index)
            a.auto_place_reveal(__title__, host_wall_id, lap_type_id, edges_1, side_of_wall)
            a.auto_place_reveal(__title__, host_wall_id, lap_type_id, edges_2, side_of_wall)


def test_out_ranges(__title__, displacement_distance, window_option=True):
    part = p.select_part()
    host_wall_id = p.get_host_wall_id(part)
    host_wall_type_id = p.get_host_wall_type_id(host_wall_id)
    layer_index = p.get_layer_index(part)
    lap_type_id, side_of_wall, exterior = p.get_wallsweep_parameters(layer_index, host_wall_type_id)
    hosted_windows = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Windows)
    hosted_doors = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Doors)

    reveal_coordinate_0 = p.get_reveal_coordinate_at_0(__title__, part)

    if window_option:
        for window in hosted_windows:
            window_centre_index = o.get_fenestration_centre_index(part, window, reveal_coordinate_0)
            fenestration_width = o.get_fenestration_width(window.Id)

            edges_1, edges_2 = o.get_fenestration_edge_indexes(fenestration_width, window_centre_index)
            out_ranges = o.get_fenestration_out_range(edges_1, edges_2, displacement_distance)

            for fen_range in out_ranges:
                a.auto_place_reveal(__title__, host_wall_id, lap_type_id, fen_range[0], side_of_wall)
                a.auto_place_reveal(__title__, host_wall_id, lap_type_id, fen_range[1], side_of_wall)


    else:
        for door in hosted_doors:
            window_centre_index = o.get_fenestration_centre_index(part, door, reveal_coordinate_0)
            fenestration_width = o.get_fenestration_width(door.Id)

            edges_1, edges_2 = o.get_fenestration_edge_indexes(fenestration_width, window_centre_index)
            out_ranges = o.get_fenestration_out_range(edges_1, edges_2, displacement_distance)

            for fen_range in out_ranges:
                a.auto_place_reveal(__title__, host_wall_id, lap_type_id, fen_range[0], side_of_wall)
                a.auto_place_reveal(__title__, host_wall_id, lap_type_id, fen_range[1], side_of_wall)


def check_centre_index(__title__, part, centre_index):
    """Check if the centre index is correct"""
    host_wall_id = p.get_host_wall_id(part)
    layer_index = p.get_layer_index(part)
    host_wall_type_id = p.get_host_wall_type_id(host_wall_id)
    lap_type_id, side_of_wall, exterior = p.get_wallsweep_parameters(layer_index, host_wall_type_id)

    length_before = p.get_part_length(part)

    # split the part into two
    reveal = a.auto_place_reveal(__title__, host_wall_id, lap_type_id, centre_index, side_of_wall)

    length_after = p.get_part_length(part)

    # delete reveal after split
    p.delete_element(__title__, reveal.Id)

    half_length = length_before / 2
    reveal_size = 0.0390625  # 3/64"
    length_parameter = round(half_length, 7) + reveal_size
    if round(length_after, 7) == length_parameter:
        centre_index = True
    else:
        centre_index = False

    return centre_index
