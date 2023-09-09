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
from _create import _test as t
from _create import _parts as g
from _create import _coordinate as c
from _create import _checks as cc

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

rvt_year = int(app.VersionNumber)
# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS
# ________________________________________________________________________________________________ATOMIC FUNCTIONS

def get_fenestration_width(fenestration_id):
    """
    Establish the width of the window
    :param fenestration_id: window/door id
    :return: the width
    """
    # establish the width of the window
    fenestration = doc.GetElement(fenestration_id)
    fenestration_type = fenestration.Symbol
    width = fenestration_type.get_Parameter(BuiltInParameter.DOOR_WIDTH).AsDouble()

    # interchangabley the width can be 0 but rough width has dimensions
    if width == 0:
        width = fenestration_type.get_Parameter(BuiltInParameter.FAMILY_ROUGH_WIDTH_PARAM).AsDouble()

    return width


def get_fenestration_xyz_centre(fenestration_id):
    """
    Get xyz locations coordinates of an fenestration. An fenestration can be a window/door opening
    :param fenestration_id: A window/door id
    :return: xyz_centre
    """
    fenestration = doc.GetElement(fenestration_id)
    xyz_centre = fenestration.Location.Point
    return xyz_centre


def get_fenestration_centre_index(part, fenestration, reveal_coordinate_0):
    """
    Get window Index centres by referencing it to the right/left edges as datum
    :param reveal_coordinate_0: reveal coordinate at 0
    :param part:Part with window/door
    :param fenestration:Window or door
    :return:index centre
    """

    hosted_wall_id = g.get_host_wall_id(part)
    x_axis_plane = c.determine_x_plane(hosted_wall_id)

    # get window/door index centre
    fenestration_xyz_centre = get_fenestration_xyz_centre(fenestration.Id)  # get window centre
    fenestration_coordinate_centre = c.get_plane_coordinate(fenestration_xyz_centre,
                                                            x_axis_plane)  # get window coordinate

    if fenestration_coordinate_centre > reveal_coordinate_0:
        fenestration_index = fenestration_coordinate_centre - reveal_coordinate_0
    else:  # interior
        fenestration_index = reveal_coordinate_0 - fenestration_coordinate_centre

    return fenestration_index


def get_fenestration_edge_indexes(fenestration_width, fenestration_centre_index):
    """
    Determine the index of fenestration edges (window & door)
    :param fenestration_width: window/door width
    :param fenestration_centre_index: The reveal index of the centre of the window/door
    :return:
    """
    half_width = fenestration_width / 2
    # establish the edge of windows coordinates
    left_fenestration_edge_index = fenestration_centre_index + half_width
    right_fenestration_edge_index = fenestration_centre_index - half_width

    return left_fenestration_edge_index, right_fenestration_edge_index


def get_fenestration_out_range(fenestration_left_index, fenestration_right_index, displacement):
    """
    Determine the ranges the reveals should not be placed
    :param fenestration_centre_index: the index of the window/door centre
    :param fenestration_width: the width of the window/door
    :param displacement: the displacement distance away from the edges of the windows.
    This creates the range the reveals cannot be placed
    :return: the left/right window range, this is in reveal index format
    """

    # window width
    fenestration_width = fenestration_left_index - fenestration_right_index
    displacement = cc.check_displacement_distance(displacement, fenestration_width)

    # window left edge
    left_box_range_1 = fenestration_left_index - displacement
    left_box_range_2 = fenestration_left_index + displacement
    left_range = [left_box_range_1, left_box_range_2]

    # window right edge
    right_box_range_1 = fenestration_right_index - displacement
    right_box_range_2 = fenestration_right_index + displacement
    right_range = [right_box_range_1, right_box_range_2]

    return left_range, right_range


def get_hosted_fenestrations(wall_id, built_in_category):
    """
    Abstract all windows/doors hosted in a provided wall
    :param wall_id:  host wall id
    :param built_in_category:  filter selection based on built in category doors or windows
    i.e. BuiltInCategory.OST_Windows
    :return: list of all windows
    """
    # select all windows
    all_fenestration = FilteredElementCollector(doc).OfCategory(built_in_category). \
        WhereElementIsNotElementType().ToElements()

    # store in a list all windows hosted by the wall
    hosted_fenestrations = []

    for window in all_fenestration:
        if window.Host.Id == wall_id:
            hosted_fenestrations.append(window)

    return hosted_fenestrations


def get_hosted_fenestrations_out_range(part, hosted_fenestrations, reveal_coordinate_0, displacement):
    """
    Loop through all windows and abstract the ranges the reveals should not pass through
    :param part: the part being panelized
    :param hosted_fenestrations: all hosted fenestrations
    :param reveal_coordinate_0: coordinates of reveal at 0
    :param displacement: Distance to be displaced from the edges of fenestration
    :return: list of all out_ranges
    """
    out_ranges = []

    # loop through each window
    for fenestration in hosted_fenestrations:
        # determine the window center index of each window
        fenestration_center_index = get_fenestration_centre_index(part, fenestration, reveal_coordinate_0)
        fenestration_width = get_fenestration_width(fenestration.Id)

        # determine the out-range for each window
        fenestration_left_index, fenestration_right_index = get_fenestration_edge_indexes \
            (fenestration_width, fenestration_center_index)
        left_out_range, right_out_range = get_fenestration_out_range(fenestration_left_index,
                                                                     fenestration_right_index, displacement)

        out_ranges.append(left_out_range)
        out_ranges.append(right_out_range)

    # return a list of all out-range
    return out_ranges

def get_out_ranges(part, hosted_doors, hosted_windows, reveal_coordinate_0, displacement):
    """
    Determine if a part host wall has fenestrations door/window and abstract the out ranges
    :param part:  Part to be panelized
    :param hosted_doors: Hosted doors in a part host wall
    :param hosted_windows: Hosted windows in a part host wall
    :param reveal_coordinate_0: Coordinates of reveal at 0
    :param displacement: Displacement distance from edges of fenestration
    :return: list of all out ranges
    """
    # when a part has both doors and windows
    if len(hosted_doors) != 0 and len(hosted_windows) != 0:
        door_out_ranges = get_hosted_fenestrations_out_range(part, hosted_doors, reveal_coordinate_0, displacement)
        window_out_ranges = get_hosted_fenestrations_out_range(part, hosted_windows, reveal_coordinate_0, displacement)
        out_ranges = door_out_ranges + window_out_ranges
    # when a part has only doors
    elif len(hosted_doors) != 0:
        out_ranges = get_hosted_fenestrations_out_range(part, hosted_doors, reveal_coordinate_0, displacement)
    # when a part has only windows
    elif len(hosted_windows) != 0:
        out_ranges = get_hosted_fenestrations_out_range(part, hosted_windows, reveal_coordinate_0, displacement)
    # when a part has no fenestrations
    else:
        out_ranges = []
    return out_ranges


def skip_out_range(edge, out_ranges, exterior=True):
    """
    The code skips out the out range by adjusting the left edge position to the lowest edge of the out range
    :param edge: right/left edge
    :param out_ranges: the index ranges to be skipped
    :param exterior: if exterior or interior
    :return: the new reveal position
    """

    if exterior:
        # skipping the out_range
        # _____________________________________________________________________
        for edge_range in out_ranges:
            edge_range = sorted(edge_range)  # sort to determine the smallest
            if edge_range[0] <= edge <= edge_range[1]:  # the range the reveal should not fall within
                if edge_range[0] > edge:
                    edge = edge_range[0]  # because we are moving left to right, the greatest value is the smallest
                elif edge_range[1] > edge:
                    edge = edge_range[1]
        # _____________________________________________________________________
    else:
        # skipping the out_range
        # _____________________________________________________________________
        for edge_range in out_ranges:
            if edge_range[0] <= edge <= edge_range[1]:
                if edge_range[0] < edge:
                    edge = edge_range[0]
                elif edge_range[1] < edge:
                    edge = edge_range[1]
        # _____________________________________________________________________

    return edge

# ________________________________________________________________________________________________NON ATOMIC FUNCTIONS
