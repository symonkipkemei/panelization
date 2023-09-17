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
from _create import _test as t
from _create import _parts as g
from _create import _coordinate as c


from pyrevit import forms

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

rvt_year = int(app.VersionNumber)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VIEWS
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET COORDINATES

def get_fenestration_xyz_centre(fenestration_id):
    """
    Get xyz centre coordinates of an opening: window, door or empty opening
    :param fenestration_id: A window/door id
    :return: xyz_centre
    """
    fenestration = doc.GetElement(fenestration_id)
    xyz_centre = fenestration.Location.Point
    return xyz_centre


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET HOSTED FENESTRATIONS

def get_hosted_fenestrations(wall_id, built_in_category):
    """
    Abstract all windows/doors hosted in a provided wall
    :param wall_id:  host wall id
    :param built_in_category:  filter selection based on built in category doors or windows
    i.e. BuiltInCategory.OST_Windows
    :return: list of filtered fenestrations
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


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET INDEXES

def get_fenestration_centre_index(part, fenestration, reveal_coordinate_0):
    """
    Get distance position (index) of the window along the wall's path curve
    :param reveal_coordinate_0: reveal coordinate at 0 as datum of wall's path curve
    :param part:Part with hosted window/door
    :param fenestration:Window or door
    :return: Window centre index
    """

    # determine the direction, x or y-axis
    hosted_wall_id = g.get_host_wall_id(part)
    x_axis_plane = c.determine_x_plane(hosted_wall_id)

    # get window/door coordinate centre
    fenestration_xyz_centre = get_fenestration_xyz_centre(fenestration.Id)  # get window centre
    fenestration_coordinate_centre = c.get_plane_coordinate(fenestration_xyz_centre,
                                                            x_axis_plane)  # get window coordinate

    # Get window index
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


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET OUT-RANGES

# single opening out-range
def get_fenestration_out_range(fenestration_left_index, fenestration_right_index, displacement):
    """
    Determine the ranges the reveals should not be placed.
    :param fenestration_left_index: Index of the left edge of the opening
    :param fenestration_right_index: Index of the right edge of the opening
    :param displacement: the displacement distance set away from edges of openings
    This creates the range the reveals cannot be placed
    :return: list of left/right window range
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


# get multiple hosted openings out-range per fenestration type
def get_hosted_fenestrations_out_range(part, hosted_fenestrations, reveal_coordinate_0, displacement):
    """
    Loop through all hosted openings and abstract the ranges the reveals should not pass through
    :param part: the part being panelized
    :param hosted_fenestrations: all hosted fenestrations
    :param reveal_coordinate_0: coordinates of reveal at 0
    :param displacement: the displacement distance set away from edges of openings
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


# get all hosted openings out-range by combining all fenestration types

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
    # when a part has no fenestration's
    else:
        out_ranges = []
    return out_ranges


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CHECK PARAMETERS

def check_out_range(edge, out_ranges, exterior=True):
    """
    Checks if the edge(reveal index) is within the outrange, if within the out range it defaults to the edge of the outrange
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


def check_displacement_distance(displacement_distance, fenestration_width):
    """
    Check if displacement distance surpasses the centre of the opening
    :param displacement_distance:
    :param fenestration_width:
    :return:
    """
    limit = fenestration_width / 2
    if displacement_distance >= limit:
        displacement_distance = limit - 0.5
        forms.alert("The displacement distance set is beyond half width fenestration limit")
    return displacement_distance
