from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType

import clr

clr.AddReference("System")

from _create import _parts as g
from _create import _test as tt
from _create import _openings as o
from _create import _coordinate as c
from _create import _errorhandler as eh
from _create import _checks as cc
from _create import _forms as ff

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

rvt_year = int(app.VersionNumber)

# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS

def auto_reveal(host_wall_id, lap_type_id, variable_distance, side_of_wall):
    """ AUto generates a wall sweep reveal
    :param host_wall_id: id of the host wall
    :param variable_distance: distance from the default o, ( some fall outside the
    part and therefore v.d places it inside the part)
    :param side_of_wall: wall face to receive the reveal
    :return:  wall sweep created
    """

    # get part, this is the hosted element containing the part
    wall = doc.GetElement(host_wall_id)
    # get symbol
    wallSweepType = WallSweepType.Reveal
    # if this type is not available, instruct the user to download the family
    wallSweepTypeId = lap_type_id  # ElementId(352808)

    wallSweepInfo = WallSweepInfo(wallSweepType, True)
    wallSweepInfo.CutsWall = True
    wallSweepInfo.IsCutByInserts = True
    wallSweepInfo.Distance = variable_distance
    wallSweepInfo.WallSide = side_of_wall  # WallSide.Exterior
    wallSweepInfo.DistanceMeasuredFrom = DistanceMeasuredFrom.Base

    wall_sweep = WallSweep.Create(wall, wallSweepTypeId, wallSweepInfo)

    return wall_sweep


def auto_place_reveal(__title__, host_wall_id, lap_type_id, variable_distance, side_of_wall):
    """
    places an autogenerated reveal on a Part thus splitting into two
    :return:
    """
    with Transaction(doc, __title__) as t:
        t.Start()
        wall_sweep = auto_reveal(host_wall_id, lap_type_id, variable_distance, side_of_wall)
        t.Commit()

    return wall_sweep


def auto_place_reveal_v2(__title__, host_wall_id, lap_type_id, variable_distance, side_of_wall):
    """
    places an autogenerated reveal on a Part thus splitting into two, if reveal outside part, suppress dialogbox/warning
    :return:
    """
    with Transaction(doc, __title__) as t:
        try:
            t.Start("01. PlacingReveal")
            # get failure handling options
            options = t.GetFailureHandlingOptions()
            failureProcessor = eh.RevealWarningSwallower()
            options.SetFailuresPreprocessor(failureProcessor)
            t.SetFailureHandlingOptions(options)

            reveal = auto_reveal(host_wall_id, lap_type_id, variable_distance, side_of_wall)
            status = t.Commit()

            if status != TransactionStatus.Committed:
                pass

        except Exception as ex:
            reveal = None

    return reveal


def auto_panel(__title__, host_wall_id, lap_type_id, reveal_indexes, side_of_wall):
    """
    Auto place reveals as per reveal indexes provided
    :param side_of_wall: The side of wall to be auto-paneled
    :param __title__: tool title
    :param host_wall_id: The host wall id
    :param reveal_indexes: a list of all reveal indexes
    :return: None
    """

    try:
        with Transaction(doc, __title__) as t:
            t.Start("03. Panelize parts")
            options = t.GetFailureHandlingOptions()
            failureProcessor = eh.RevealWarningSwallower()
            options.SetFailuresPreprocessor(failureProcessor)
            t.SetFailureHandlingOptions(options)

            for reveal_index in reveal_indexes:
                wall_sweep = auto_reveal(host_wall_id, lap_type_id, reveal_index, side_of_wall)
            t.Commit()

    except Exception as e:
        print ('The following error has occurred: {}'.format(e))


def auto_parts(__title__, part, displacement_distance, switch_option, multiple=True):
    """
    Identifies :
    1. the Parts ( exterior, interior or partition ) intuitively
    2. The lap (right or left) to be used to be used intuitively
    3. Direction to be used  right-> left or left->right intuitively
    :param part: Part to be panelized
    :param __title__: tool title
    :return: None
    """
    global exterior, lap_type_id, side_of_wall
    host_wall_id = g.get_host_wall_id(part)
    host_wall_type_id = g.get_host_wall_type_id(host_wall_id)
    layer_index = g.get_layer_index(part)
    lap_type_id, side_of_wall, exterior = g.get_wallsweep_parameters(layer_index, host_wall_type_id)

    # Test if the panel is divisible into two equal parts
    reveal_plane_coordinate_0 = g.get_reveal_coordinate_at_0(__title__, part)
    centre_index = g.get_part_centre_index(part, reveal_plane_coordinate_0)

    # create left and right edge
    part_length = g.get_part_length(part)
    left_edge, right_edge = g.get_edge_index_v2(part_length, centre_index)

    hosted_windows = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Windows)
    hosted_doors = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Doors)

    # check if part has openings or not
    if len(hosted_windows) == 0 and len(hosted_doors) == 0:
        out_ranges = []
    else:
        displacement = displacement_distance
        out_ranges = o.get_out_ranges(part, hosted_doors, hosted_windows, reveal_plane_coordinate_0, displacement)

    exterior = g.switch_directions(exterior, bool_option=switch_option)

    if multiple:
        reveal_indexes = g.get_reveal_indexes_v2(left_edge, right_edge, out_ranges, exterior)
    else:
        reveal_indexes = g.get_single_panel_reveal_indexes(left_edge, right_edge, exterior)

    auto_panel(__title__, host_wall_id, lap_type_id, reveal_indexes, side_of_wall)
