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
from _create import _test as tt
from _create import _parts as p
from _create import _coordinate as c
from _create import _openings as o

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


class RevealWarningSwallower(IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        failList = []
        # Inside event handler, get all warnings
        failList = failuresAccessor.GetFailureMessages()

        for failure in failList:
            print ("failure", failure)
            # check FailureDefinitionIds against ones that you want to dismiss
            failID = failure.GetFailureDefinitionId()
            # prevent Revit from showing Unenclosed room warnings
            if failID == BuiltInFailures.SweepFailures.CannotDrawSweep:
                print ("warning deletion")
                failuresAccessor.DeleteWarning(failure)
            else:
                failuresAccessor.DeleteWarning(failure)
                print ("Continue irregardless")
        return FailureProcessingResult.Continue


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
    left_edge, right_edge = p.get_edge_index(__title__, part, host_wall_id, lap_type_id, variable_distance, side_of_wall)

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

    variable_distance = p.get_variable_distance(__title__, part)
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

    centre_index, direction = p.get_variable_distance(__title__, part)
    length = p.get_part_length(part)
    left_edge, right_edge = p.get_part_edges_v2(length, centre_index, direction)
    a.auto_place_reveal(__title__, host_wall_id, lap_type_id, left_edge, side_of_wall)