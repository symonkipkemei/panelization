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


def get_part_edges_coordinate(part_length, centre_coordinate):
    """
    Get the coordinate of both edges of part
    :param part_length: the length of the part
    :param centre_coordinate:  the centre coordinate
    :return: the edge coordinate
    """

    half_part_length = part_length / 2
    edge1 = centre_coordinate + half_part_length
    edge2 = centre_coordinate - half_part_length

    return edge1, edge2


def convert_window_coordinate_to_index(part_index_left_edge, part_coordinate_edge, window_coordinate_center):
    """
    converts coordinates to reveal indexes
    :param part_index_edge: The reveal indexes of one of the edges, preferably the left edge as the reference point/datum
    :param part_coordinate_edge: The coordinate of one of the edges,
    :param window_coordinate_center: The coordinate of the centre of the window
    :return: The reveal index of the window at the centre
    """

    window_index_centre = 0

    if part_coordinate_edge < 0 and window_coordinate_center < 0:
        index_difference = (part_coordinate_edge) - (window_coordinate_center)

        # Get absolute value of  the index
        index_difference = abs(index_difference)

        print ("index_difference", index_difference)
        window_index_centre = part_index_left_edge - index_difference

    else:
        print ("The script is faulty")

    return window_index_centre


def get_direction(reveal_center_1, reveal_center_2, x_axis):
    """
    Determine the correct direction  based on the reveal coordinates
    :param reveal_coordinate_1:
    :param reveal_coordinate_2:
    :return: correct_direction
    """

    global correct_direction

    if x_axis:
        reveal_coordinate_1 = reveal_center_1.X
        reveal_coordinate_2 = reveal_center_2.X
    else:
        reveal_coordinate_1 = reveal_center_1.Y
        reveal_coordinate_2 = reveal_center_2.Y

    print ("Reveal coordinate 1", reveal_coordinate_1)
    print ("Reveal coordinate 2", reveal_coordinate_2)

    if reveal_coordinate_2 > reveal_coordinate_1:
        correct_direction = True  # the lowest point becomes the left edge
    elif reveal_coordinate_2 < reveal_coordinate_1:
        correct_direction = False  # the highest point becomes the left edge
    else:
        print ("Reveal positioning failed")

    return correct_direction


def get_part_coordinate_left_edge(edge_1, edge_2, correct_direction):
    """
    Determine which is the left edge based on the direction of the reveals
    :param edge_1:
    :param edge_2:
    :param correct_direction:
    :return: The left edge coordinate
    """

    edges = sorted([edge_1, edge_2])
    lowest_point = edges[0]
    highest_point = edges[1]

    if correct_direction:
        coordinate_left_edge = lowest_point
        coordinate_right_edge = highest_point

    else:
        coordinate_left_edge = highest_point
        coordinate_right_edge = lowest_point

    return coordinate_left_edge


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
