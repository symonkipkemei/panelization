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

from _create import _transactions as a
from _create import _test as t

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

rvt_year = int(app.VersionNumber)
# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> COORDINATES

def determine_x_plane(wall_id):
    """
    Determine the direction of the wall's path curve : x or y-axis
    :param wall_id: The host wall id
    :return: X-axis bool. host wall curve direction : x axis (True) , y axis (False) or neither on x nor y-axis (None)
    """

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

    else:
        # the wall curve is neither on x or y axis
        x_axis = None

    return x_axis


def get_plane_coordinate(xyz_coordinates, x_axis_plane):
    """
    Abstract plane coordinate ( x or y coordinate) from the xyz_coordinates based on the plane direction
    :param xyz_coordinates: xyz coordinates of an element
    :param x_axis_plane: plane direction
    :return: x or y coordinate
    """
    global plane_coordinate
    if x_axis_plane:
        plane_coordinate = xyz_coordinates.X

    elif not x_axis_plane:
        plane_coordinate = xyz_coordinates.Y

    return plane_coordinate


def get_bounding_box_center(element):
    """
    Get the centre coordinates af an element using its bounding box
    :param element:
    :return: centre xyz coordinates
    """

    box_coordinates = element.get_BoundingBox(doc.ActiveView)
    if box_coordinates is not None:
        maximum = box_coordinates.Max
        minimum = box_coordinates.Min
        centre = (maximum + minimum) / 2
    else:
        centre = None

    return centre

