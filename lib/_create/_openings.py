
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


def get_out_of_bounce_range(window_edge_index, displacement_width):
    """
    Provide the displacement range for a particular edge of a window
    :param window_edge_index:
    :param displacement_width:
    :return:
    """
    left_range = window_edge_index - displacement_width
    right_range = window_edge_index + displacement_width
    edge_range = [left_range, right_range]

    return edge_range

def get_window_xyz_centre(window_id):
    """
    Get centre of window
    :param window_id:
    :return:
    """
    window = doc.GetElement(window_id)
    xyz_centre = window.Location.Point
    return  xyz_centre
