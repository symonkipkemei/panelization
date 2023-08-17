from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.DB.BuiltInFailures import CreationFailures as cf
import clr

clr.AddReference("System")

from _create import _auto as a
from _create import _test as t

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

rvt_year = int(app.VersionNumber)
# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS


# ________________________________________________________________________________________________COORDINATES

def determine_x_plane(wall_id):
    """
    Determine the orientation of the wall placement plane
    for hosted families such as windows, openings and reveals.
    This helps determine which coordinate to work with when given
    xyz coordinates

    :param wall_id: The host wall id
    :return: if it's x axis or not.
    """
    global x_axis
    wall = doc.GetElement(wall_id)

    # determine the plane of the wall
    wall_direction = wall.Location.Curve.Direction

    # direction coordinates
    x_direction = wall_direction.X
    y_direction = wall_direction.Y

    if x_direction == -1 or x_direction == 1:
        x_axis = True

    elif y_direction == -1 or y_direction == 1:
        x_axis = False

    return x_axis


def get_plane_coordinate(coordinates, x_axis_plane):
    """
    Get coordinate for the specified plane
    :param coordinates: xyz coordinates
    :param x_axis_plane: plane of choice
    :return: coordinates in relation to the plane
    """
    global plane_coordinate
    if x_axis_plane:
        plane_coordinate = coordinates.X

    elif not x_axis_plane:
        plane_coordinate = coordinates.Y

    return plane_coordinate


def get_part_edges_coordinate(part_length, centre_coordinate, correct_direction, exterior):
    """
    Get the coordinate of both edges of part
    :param exterior: Bool, determines if panel is exterior or not
    :param correct_direction: The direction of the panels
    :param part_length: the length of the part
    :param centre_coordinate:  the centre coordinate
    :return: the edge coordinate
    """

    global coordinate_left_edge, coordinate_right_edge

    half_part_length = part_length / 2
    edge_1 = centre_coordinate + half_part_length
    edge_2 = centre_coordinate - half_part_length

    edges = sorted([edge_1, edge_2])
    lowest_point = edges[0]
    highest_point = edges[1]

    if exterior:  # exterior
        if correct_direction:
            coordinate_left_edge = lowest_point
            coordinate_right_edge = highest_point
        else:
            coordinate_left_edge = highest_point
            coordinate_right_edge = lowest_point
    else:  # interior
        if correct_direction:
            coordinate_left_edge = highest_point
            coordinate_right_edge = lowest_point
        else:
            coordinate_left_edge = lowest_point
            coordinate_right_edge = highest_point

    return coordinate_left_edge, coordinate_right_edge


def convert_window_coordinate_to_index(part_index_edge, part_coordinate_edge, window_coordinate_center, exterior):
    """
    converts coordinates to reveal indexes
    :param exterior:
    :param part_index_edge: The reveal indexes of one of the edges, preferably the left edge as the reference point/datum
    :param part_coordinate_edge: The coordinate of one of the edges,
    :param window_coordinate_center: The coordinate of the centre of the window
    :return: The reveal index of the window at the centre
    """


    #The position of the window coordinates relative to the coordinates of the edges

    window_index_centre = 0

    if window_coordinate_center > part_coordinate_edge:
        index_difference = (window_coordinate_center) - (part_coordinate_edge)
        # Get absolute value of  the index
        index_difference = abs(index_difference)

        if exterior:  # exterior , the index difference is  subtracted from the left edge panel
            window_index_centre = part_index_edge - index_difference
        else:  # interior, the index difference is added to the right edge panel
            window_index_centre = part_index_edge + index_difference
    else:
        index_difference = (part_coordinate_edge) - (window_coordinate_center)
        index_difference = abs(index_difference)
        if exterior:  # exterior , the index difference is  subtracted from the left edge panel
            window_index_centre = part_index_edge - index_difference
        else:  # interior, the index difference is added to the right edge panel
            window_index_centre = part_index_edge + index_difference

    return window_index_centre

def get_bounding_box_center(element):
    """
    Get the centre af an element using its bounding box
    :param element:
    :return: centre xyz coordinates
    """

    box_coordinates = element.get_BoundingBox(doc.ActiveView)
    if box_coordinates is not None:
        maximum = box_coordinates.Max
        minimum = box_coordinates.Min

        centre = (maximum + minimum) / 2
    else:
        print ("Bounding box is none, error generating the centre")
        centre = None

    return centre


def get_panel_direction(__title__, host_wall_id, lap_type_id, left_edge_index, right_edge_index, side_of_wall,
                        x_axis_plane, exterior):
    """
    Determine the direction of the panels by determining the reveal coordinates in relation to it's direction
    :param __title__: tool title
    :param host_wall_id: host element
    :param lap_type_id: type of lap used
    :param left_edge_index: left edge of panel
    :param right_edge_index: right edge of panel
    :param side_of_wall: interior/exterior placement
    :param exterior: True if it's exterior
    :param x_axis_plane: True if it's the x_axis plane
    :return: The direction, True or False
    """

    # Establishing the correct reveal distance within the left -right edge range
    global plane_direction, dst_1, dst_2
    if exterior:
        if left_edge_index > right_edge_index:
            dst_1 = left_edge_index - 1
            dst_2 = left_edge_index - 2

        elif left_edge_index < right_edge_index:
            dst_1 = left_edge_index + 1
            dst_2 = left_edge_index + 2

    else:
        if right_edge_index > left_edge_index:
            dst_1 = right_edge_index - 1
            dst_2 = right_edge_index - 2

        elif right_edge_index < left_edge_index:
            dst_1 = right_edge_index + 1
            dst_2 = right_edge_index + 2

    # placing the reveals
    rvl_1 = a.auto_place_reveal(__title__, host_wall_id, lap_type_id, dst_1, side_of_wall)
    rvl_2 = a.auto_place_reveal(__title__, host_wall_id, lap_type_id, dst_2, side_of_wall)

    # Abstracting the centres of the reveals (xyz)
    reveal_center_1 = get_bounding_box_center(rvl_1)
    reveal_center_2 = get_bounding_box_center(rvl_2)

    # abstracting the X OR Y coordinate from their centers based on the plane ( x-axis or y-axis)

    if x_axis_plane:
        reveal_coordinate_1 = reveal_center_1.X
        reveal_coordinate_2 = reveal_center_2.X
    else:
        reveal_coordinate_1 = reveal_center_1.Y
        reveal_coordinate_2 = reveal_center_2.Y

    # Determine the direction based on value of each coordinate
    if reveal_coordinate_2 > reveal_coordinate_1:
        plane_direction = True  # the lowest point becomes the left edge
    elif reveal_coordinate_2 < reveal_coordinate_1:
        plane_direction = False  # the highest point becomes the left edge
    else:
        print ("Reveal positioning failed")

    # delete reveals after abstracting the edge direction
    with Transaction(doc, __title__) as t:
        t.Start()

        doc.Delete(rvl_1.Id)
        doc.Delete(rvl_2.Id)

        t.Commit()

    return plane_direction


# _______________________________________________________________________NON ATOMIC FUNCTION/COMBINES SEVERAL FUNCTIONS

def get_direction_abstract(fst_reveal_coordinates, snd_reveal_coordinates, host_wall_id):
    """
    An abstract way to get direction by providing:
    :param fst_reveal_coordinates: centre coordinates of the fst reveal
    :param snd_reveal_coordinates: centre coordinates of the snd reveal
    :param host_wall_id: The host wall
    :return: The direction
    """

    x_axis_plane = determine_x_plane(host_wall_id)
    reveal_coordinate_1 = get_plane_coordinate(fst_reveal_coordinates, x_axis_plane)
    reveal_coordinate_2 = get_plane_coordinate(snd_reveal_coordinates, x_axis_plane)

    direction = get_direction(reveal_coordinate_1, reveal_coordinate_2)

    return direction
