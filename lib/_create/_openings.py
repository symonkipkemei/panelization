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

# ________________________________________________________________________________________________FAMILY CREATION

def get_type_by_name(type_name):
    """
    abstract the symbol of a family by providing its name
    :param type_name: Name of the family
    :return: symbol
    """
    param_type = ElementId(BuiltInParameter.ALL_MODEL_TYPE_NAME)
    f_param = ParameterValueProvider(param_type)
    evaluator = FilterStringEquals()
    f_rule = FilterStringRule(f_param, evaluator, type_name)

    # create filter
    filter_type_name = ElementParameterFilter(f_rule)
    return FilteredElementCollector(doc).WherePasses(filter_type_name).WhereElementIsElementType().FirstElement()


# ________________________________________________________________________________________________WINDOWS

def get_window_width(window_id):
    """
    Establish the width of the window
    :param window_id: window id
    :return: the width
    """
    # establish the width of the window
    window = doc.GetElement(ElementId(window_id))
    window_type = window.GetTypeId
    width = window_type.get_Parameter(BuiltInParameter.DOOR_WIDTH).AsDouble()

    return width


def get_window_location(element_id):
    """
    Abstract the XYZ origin coordinates of a window
    :param element_id: id for the window
    :return: xyz orgin location
    """
    window = doc.GetElement(ElementId(element_id))
    location = window.Location.Point
    return location


def get_window_edge_indexes(window_width, window_index):
    """
    Determine the index of window edges
    :param window_width: window width
    :param window_index: The reveal index of the centre of the window
    :return:
    """
    half_width = window_width / 2
    # establish the edge of windows coordinates
    left_window_edge_index = window_index - half_width
    right_window_edge_index = window_index + half_width

    return left_window_edge_index, right_window_edge_index


def get_hosted_windows(wall_id):
    """
    Abstract all windows hosted in a provided wall
    :param wall_id:  host wall id
    :return: list of all windows
    """
    # select all windows
    all_windows = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Windows). \
        WhereElementIsNotElementType().ToElements()

    # store in a list all windows hosted by the wall
    hosted_windows = []

    for window in all_windows:
        if window.Host.Id == wall_id:
            hosted_windows.append(window)

    return hosted_windows


def get_out_of_bounce_range(window_centre_index, window_length, displacement):
    """
    Provide the displacement range for a particular edge of a window
    :return:
    """
    width = window_length / 2
    window_left_index = window_centre_index - width
    window_right_index = window_centre_index + width

    # window left edge
    left_box_range_1 = window_left_index - displacement
    left_box_range_2 = window_right_index + displacement
    left_range = [left_box_range_1, left_box_range_2]

    # window right edge
    right_box_range_1 = window_left_index - displacement
    right_box_range_2 = window_right_index + displacement
    right_range = [right_box_range_1, right_box_range_2]

    return left_range, right_range


def get_window_xyz_centre(window_id):
    """
    Get centre of window
    :param window_id:
    :return:
    """
    window = doc.GetElement(window_id)
    xyz_centre = window.Location.Point
    return xyz_centre


def get_window_index_centre(__title__, part):
    """
    Places reveals at the centre of the windows
    :return:
    """

    global lap_type_id, side_of_wall, window_centre_index, exterior

    hosted_wall_id = g.get_host_wall_id(part)

    # get hosted windows
    hosted_windows = o.get_hosted_windows(hosted_wall_id)
    layer_index = g.get_layer_index(part)
    variable_distance = 3
    x_axis_plane = c.determine_x_plane(hosted_wall_id)

    if layer_index == 1:  # exterior
        side_of_wall = WallSide.Exterior
        lap_type_id = ElementId(352808)  # right_lap_id
        exterior = True

    elif layer_index == 3:  # interior
        side_of_wall = WallSide.Interior
        lap_type_id = ElementId(352818)  # left_lap_id
        exterior = False

    left_edge_index, right_edge_index = g.get_edge_index(__title__, part, hosted_wall_id, lap_type_id,
                                                         variable_distance, side_of_wall)

    # get the direction of each panel

    direction = c.get_panel_direction(__title__, hosted_wall_id, lap_type_id, left_edge_index, right_edge_index,
                                      side_of_wall, x_axis_plane, exterior=exterior)

    # Determine the left edge coordinate/ right_edge coordinate as the datum

    part_xyz_centre = c.get_bounding_box_center(part)  # get part center(xyz)
    part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()  # get part length
    part_coordinate_centre = c.get_plane_coordinate(part_xyz_centre, x_axis_plane)  # get the part coordinates

    left_edge_coordinate, right_edge_coordinate = c.get_part_edges_coordinate(
        part_length, part_coordinate_centre, direction, layer_index)  # get left edge based on direction

    # get window index centre

    # loop through hosted windows, determine the window index and place reveals
    for window in hosted_windows:  # loop through hosted windows
        window_xyz_centre = o.get_window_xyz_centre(window.Id)  # get window centre
        window_coordinate_centre = c.get_plane_coordinate(window_xyz_centre, x_axis_plane)  # get window coordinate

        if layer_index == 1:  # exterior
            print ("exterior")
            window_centre_index = c.convert_window_coordinate_to_index(left_edge_index, left_edge_coordinate,
                                                                       window_coordinate_centre, exterior)
        elif layer_index == 3:  # interior
            print ("interior")
            window_centre_index = c.convert_window_coordinate_to_index(right_edge_index, right_edge_coordinate,
                                                                       window_coordinate_centre, exterior
                                                                       )

    return window_centre_index
