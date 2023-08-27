from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType

import clr

clr.AddReference("System")

from _create import _auto as a
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


def test_place_reveal_out_ranges(__title__):
    """
    Test placement of reveals on the out ranges
    :return:
    """
    # select part
    # get hosted windows
    global lap_type_id, side_of_wall
    part = g.select_part()
    hosted_wall_id = g.get_host_wall_id(part)

    layer_index = g.get_layer_index(part)
    left_lap_id = ElementId(352818)
    right_lap_id = ElementId(352808)
    variable_distance = 3

    if layer_index == 1:  # exterior
        side_of_wall = WallSide.Exterior
        lap_type_id = right_lap_id
        exterior = True

    elif layer_index == 3:  # interior
        side_of_wall = WallSide.Interior
        lap_type_id = left_lap_id
        exterior = False

    # get out ranges
    hosted_windows_out_ranges = o.get_hosted_windows_out_range(__title__, part)
    # print (hosted_windows_out_ranges)

    # place reveals on out ranges
    for window_range in hosted_windows_out_ranges:
        left_range = window_range[0]
        righ_range = window_range[1]

        # left edge reveals
        a.auto_place_reveal(__title__, hosted_wall_id, lap_type_id, left_range, side_of_wall)
        a.auto_place_reveal(__title__, hosted_wall_id, lap_type_id, righ_range, side_of_wall)


def test_window_width():
    """
    Test the window width
    :return: Window width
    """
    # select window width
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    window = uidoc.Document.GetElement(reference)
    # abstract the width
    width = o.get_window_width(window.Id)
    # display width
    print (width)


def test_element_origin(wall_origin):
    """
    Determining the location of element orgin by placing an abstract object at it
    :param wall_origin: The element origin
    :return: Element generated
    """

    symbol = get_type_by_name("test-family")

    with Transaction(doc, __title__) as t:
        t.Start()
        element = doc.Create.NewFamilyInstance(wall_origin, symbol, Structure.StructuralType.NonStructural)
        t.Commit()

    return element


def test_window_centres(__title__):
    global lap_type_id, side_of_wall
    part = g.select_part()
    hosted_wall_id = g.get_host_wall_id(part)

    layer_index = g.get_layer_index(part)
    left_lap_id = ElementId(352818)
    right_lap_id = ElementId(352808)

    if layer_index == 1:  # exterior
        side_of_wall = WallSide.Exterior
        lap_type_id = right_lap_id
        exterior = True

    elif layer_index == 3:  # interior
        side_of_wall = WallSide.Interior
        lap_type_id = left_lap_id
        exterior = False

    windows = o.get_hosted_windows(hosted_wall_id)
    for window in windows:
        window_index = o.get_window_index_centre(__title__, part, window)
        a.auto_place_reveal(__title__, hosted_wall_id, lap_type_id, window_index, side_of_wall)




def test_split_parts(__title__):
    part = p.select_part()
    host_wall_id = p.get_host_wall_id(part)
    layer_index = p.get_layer_index(part)
    lap_type_id = 0
    side_of_wall = None
    exterior = None
    if layer_index == 1:
        lap_type_id = ElementId(352808)  # right_lap_id
        side_of_wall = WallSide.Exterior
        exterior = True
    elif layer_index == 3:
        lap_type_id = ElementId(352818)  # left_lap_id
        side_of_wall = WallSide.Interior
        exterior = False

    variable_distance = p.get_variable_distance(__title__, part)
    left_edge, right_edge = p.get_edge_index(__title__, part, host_wall_id, lap_type_id, variable_distance,
                                             side_of_wall)

    out_ranges = []
    reveal_indexes = p.get_reveal_indexes_v2(left_edge, right_edge, out_ranges, exterior)

    for reveal in reveal_indexes:
        a.auto_place_reveal(__title__, host_wall_id, lap_type_id, reveal, side_of_wall)


def test_variable_distance(__title__):
    part = p.select_part()
    host_wall_id = p.get_host_wall_id(part)
    layer_index = p.get_layer_index(part)
    lap_type_id = 0
    side_of_wall = None
    exterior = None
    if layer_index == 1:
        lap_type_id = ElementId(352808)  # right_lap_id
        side_of_wall = WallSide.Exterior
        exterior = True
    elif layer_index == 3:
        lap_type_id = ElementId(352818)  # left_lap_id
        side_of_wall = WallSide.Interior
        exterior = False

    variable_distance = p.get_centre_index(__title__, part)
    a.auto_place_reveal(__title__, host_wall_id, lap_type_id, variable_distance, side_of_wall)


def test_left_edge(__title__):
    part = p.select_part()
    host_wall_id = p.get_host_wall_id(part)
    layer_index = p.get_layer_index(part)
    lap_type_id = 0
    side_of_wall = None
    exterior = None
    if layer_index == 1:
        lap_type_id = ElementId(352808)  # right_lap_id
        side_of_wall = WallSide.Exterior
        exterior = True
    elif layer_index == 3:
        lap_type_id = ElementId(352818)  # left_lap_id
        side_of_wall = WallSide.Interior
        exterior = False

    centre_index = p.get_centre_index(__title__, part)
    length = p.get_part_length(part)
    left_edge, right_edge = p.get_edge_index_v2(length, centre_index)
    out_ranges = []
    reveal_indexes = p.get_reveal_indexes_v2(left_edge, right_edge, out_ranges, exterior=True)

    with Transaction(doc, __title__) as t:
        t.Start()
        for reveal in reveal_indexes:
            a.auto_reveal(host_wall_id, lap_type_id, reveal, side_of_wall)
        t.Commit()


def test_direction(__title__):
    """test direction by placing two reveals and abstracting their coordinates for comparison"""

    try:
        part = p.select_part()
        host_wall_id = p.get_host_wall_id(part)
        layer_index = p.get_layer_index(part)
        lap_type_id = 0
        side_of_wall = None
        exterior = None
        x_axis_plane = c.determine_x_plane(host_wall_id)
        if layer_index == 1:
            lap_type_id = ElementId(352808)  # right_lap_id
            side_of_wall = WallSide.Exterior
            exterior = True
        elif layer_index == 3:
            lap_type_id = ElementId(352818)  # left_lap_id
            side_of_wall = WallSide.Interior
            exterior = False

        reveal_1 = a.auto_place_reveal_v2(__title__, host_wall_id, lap_type_id, 1, side_of_wall)
        reveal_2 = a.auto_place_reveal_v2(__title__, host_wall_id, lap_type_id, 2, side_of_wall)
        reveal_4 = a.auto_place_reveal_v2(__title__, host_wall_id, lap_type_id, 4, side_of_wall)

        # reveal 1 coordinates
        reveal_xyz_coordinates_1 = c.get_bounding_box_center(reveal_1)
        reveal_plane_coordinate_1 = c.get_plane_coordinate(reveal_xyz_coordinates_1, x_axis_plane)
        reveal_plane_coordinate_1 = float(reveal_plane_coordinate_1)  # to determine coordinate at 0

        # reveal 2 coordinates
        reveal_xyz_coordinates_2 = c.get_bounding_box_center(reveal_2)
        reveal_plane_coordinate_2 = c.get_plane_coordinate(reveal_xyz_coordinates_2, x_axis_plane)
        reveal_plane_coordinate_2 = float(reveal_plane_coordinate_2)  # to determine coordinate at 0

        # reveal 4 coordinates
        reveal_xyz_coordinates_4 = c.get_bounding_box_center(reveal_4)
        reveal_plane_coordinate_4 = c.get_plane_coordinate(reveal_xyz_coordinates_4, x_axis_plane)
        reveal_plane_coordinate_4 = float(reveal_plane_coordinate_4)  # to determine coordinate at 0

        print ("reveal plane coordinate 1", reveal_plane_coordinate_1)
        print ("reveal plane coordinate 2", reveal_plane_coordinate_2)
        print ("reveal plane coordinate 4", reveal_plane_coordinate_4)

    except e.CannotPanelizeError:
        forms.alert('Select a Part to Panelize')





def test_reveal_distance(__title__):
    """
    Investigate the characteristics of a reveal that cuts through a part and one that does not
    :return:
    """

    part = p.select_part()
    host_wall_id = p.get_host_wall_id(part)
    layer_index = p.get_layer_index(part)
    lap_type_id = 0
    side_of_wall = None
    exterior = None
    if layer_index == 1:
        lap_type_id = ElementId(352808)  # right_lap_id
        side_of_wall = WallSide.Exterior
        exterior = True
    elif layer_index == 3:
        lap_type_id = ElementId(352818)  # left_lap_id
        side_of_wall = WallSide.Interior
        exterior = False

    variable_distance = 3

    a.auto_place_reveal_v2(__title__, host_wall_id, lap_type_id, variable_distance,side_of_wall)

def test_centre_index(__title__):
    """Check if the centre index is correct"""
    part = p.select_part()
    centre_index = p.get_part_centre_index(__title__, part)
    ans = cc.check_centre_index(__title__, part, centre_index)
    print ans


def test_window_index_centre(__title__):
    part = p.select_part()
    host_wall_id = p.get_host_wall_id(part)
    hosted_windows = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Windows)
    reveal_coordinate_0 = p.get_reveal_coordinate_at_0(__title__, part)
    layer_index = p.get_layer_index(part)
    host_wall_type_id = p.get_host_wall_type_id(host_wall_id)

    lap_type_id, side_of_wall, exterior = p.get_wallsweep_parameters(layer_index, host_wall_type_id)

    for window in hosted_windows:
        window_index = o.get_fenestration_centre_index(part, window, reveal_coordinate_0)
        a.auto_place_reveal(__title__,host_wall_id,lap_type_id,window_index,side_of_wall)

