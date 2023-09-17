from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType
import clr
clr.AddReference("System")
from _create import _parts as p
from _create import _test as tt
from _create import _openings as o
from _create import _coordinate as c
from _create import _errorhandler as eh
from _create import _forms as ff

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project
rvt_year = int(app.VersionNumber)
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PLACE REVEAL TRANSACTION

def auto_place_reveal(__title__, host_wall_id, lap_type_id, variable_distance, side_of_wall):
    """
    Places a wall sweep on a part by initializing a transaction.All warnings are suppressed by deleting the dialog boxes.
    :param __title__:Tool title
    :param lap_type_id:Element id of the wall sweep type used
    :param host_wall_id:host wall id
    :param variable_distance: distance along the wall's path curve
    :param side_of_wall: side of the wall to which the reveal is attached.
    :return: A wall sweep
    """
    with Transaction(doc, __title__) as t:
        try:
            t.Start("01. PlacingReveal")
            # Provides access to option to control how failures should be handled by end of transaction.
            options = t.GetFailureHandlingOptions()

            # deletes warnings captured
            failureProcessor = eh.WarningSwallower()

            # sets how failures should be handled during transaction
            options.SetFailuresPreprocessor(failureProcessor)
            t.SetFailureHandlingOptions(options)

            reveal = p.create_reveal(host_wall_id, lap_type_id, variable_distance, side_of_wall)
            status = t.Commit()

            if status != TransactionStatus.Committed:
                # if transaction has not been committed, this would result to an error.
                print("The transaction has not been committed")

        except Exception as e:
            print ('The following error has occurred on Transaction 03. Panelize parts : {}'.format(e))
            reveal = None

    return reveal


def get_reveal_coordinate_at_0(__title__, part):
    """
    Get the coordinates of the reveal at distance 0
    :param __title__: Tool title
    :param part: Part to be panelized

    """
    host_wall_id = p.get_host_wall_id(part)
    host_wall_type_id = p.get_host_wall_type_id(host_wall_id)
    layer_index = p.get_layer_index(part)
    lap_type_id, side_of_wall, exterior = p.get_wall_sweep_parameters(layer_index, host_wall_type_id)
    x_axis_plane = c.determine_x_plane(host_wall_id)

    # establish the length of part
    length_before_reveal = p.get_part_length(part)

    # determine the reveal that cuts through the part, the script will continue until the correct reveal is found,
    # a reveal that does not cut through the part will not give us it's coordinates

    # reveal 1 plane coordinate
    variable_distance = 3
    while True:
        reveal_1 = auto_place_reveal(__title__, host_wall_id, lap_type_id, variable_distance, side_of_wall)
        if reveal_1 is None:
            raise eh.VariableDistanceNotFoundError

        length_after_reveal = p.get_part_length(part)
        # print (variable_distance)
        if c.get_bounding_box_center(reveal_1) is not None:
            break
        elif length_before_reveal != length_after_reveal:
            break
        delete_element(__title__, reveal_1.Id)
        variable_distance += 3
        if variable_distance > 100:
            raise eh.VariableDistanceNotFoundError

    reveal_xyz_coordinates_1 = c.get_bounding_box_center(reveal_1)
    reveal_plane_coordinate_1 = float(c.get_plane_coordinate(reveal_xyz_coordinates_1, x_axis_plane))

    # create snd wall sweep, this will help establish the reveal at 0
    move_distance = 0.166667  # 1/4", small distance to ensure part is cut
    reveal_2 = auto_place_reveal(__title__, host_wall_id, lap_type_id, variable_distance + move_distance,
                                   side_of_wall)

    if reveal_2 is None:
        raise eh.VariableDistanceNotFoundError

    # reveal 2 plane coordinate
    reveal_xyz_coordinates_2 = c.get_bounding_box_center(reveal_2)
    reveal_plane_coordinate_2 = float(c.get_plane_coordinate(reveal_xyz_coordinates_2, x_axis_plane))

    # reveal plane coordinates at 0
    if reveal_plane_coordinate_2 < reveal_plane_coordinate_1:
        reveal_plane_coordinate_0 = reveal_plane_coordinate_1 + variable_distance
    else:
        reveal_plane_coordinate_0 = reveal_plane_coordinate_1 - variable_distance

    # delete the reveal after abstracting the coordinate at o
    delete_element(__title__, reveal_1.Id, reveal_2.Id)

    return reveal_plane_coordinate_0


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PANELIZE TRANSACTIONS


def auto_panel(__title__, host_wall_id, lap_type_id, reveal_indexes, side_of_wall):
    """
    Auto place reveals along the wall's path curve as per reveal indexes provided
    :param __title__:Tool title
    :param lap_type_id:Element id of the wall sweep type used
    :param host_wall_id:host wall id
    :param reveal_indexes: list of reveal distance indexes along the wall's path curve
    :param side_of_wall: side of the wall to which the reveal is attached.
    :return: None
    """

    try:
        with Transaction(doc, __title__) as t:
            t.Start("03. Panelize parts")
            # Provides access to option to control how failures should be handled by end of transaction.
            options = t.GetFailureHandlingOptions()

            # deletes warnings captured
            failureProcessor = eh.WarningSwallower()

            # sets how failures should be handled during transaction
            options.SetFailuresPreprocessor(failureProcessor)
            t.SetFailureHandlingOptions(options)

            for reveal_index in reveal_indexes:
                wall_sweep = p.create_reveal(host_wall_id, lap_type_id, reveal_index, side_of_wall)
            status = t.Commit()

            if status != TransactionStatus.Committed:
                # if transaction has not been committed, this would result to an error
                print("The transaction has not been committed")

    except Exception as e:
        print ('The following error has occurred on Transaction 03. Panelize parts : {}'.format(e))


def auto_parts(__title__, part, displacement_distance, switch_option, multiple=True):
    """
    Auto Identifies :
    1. The part wall side ( exterior, interior or partition ) intuitively
    2. The lap (right or left) to be used to be used intuitively
    3. Direction to be used  right-> left or left->right by user choice
    and places reveals along the wall's path's curve thus creating panels

    :param multiple: Bool to determine single panel or multi-panel reveal distances
    :param switch_option: Bool to switch direction of placing reveals: left to right/right to left
    :param displacement_distance: Distance away from the edges of openings
    :param part: Part to be panelized
    :param __title__: tool title

    :return: None
    """

    host_wall_id = p.get_host_wall_id(part)
    host_wall_type_id = p.get_host_wall_type_id(host_wall_id)
    layer_index = p.get_layer_index(part)
    lap_type_id, side_of_wall, exterior = p.get_wall_sweep_parameters(layer_index, host_wall_type_id)

    # Test if the panel is divisible into two equal parts
    reveal_plane_coordinate_0 = get_reveal_coordinate_at_0(__title__, part)
    centre_index = p.get_part_centre_index(part, reveal_plane_coordinate_0)

    # create left and right edge
    part_length = p.get_part_length(part)
    left_edge, right_edge = p.get_part_edge_index(part_length, centre_index)

    hosted_windows = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Windows)
    hosted_doors = o.get_hosted_fenestrations(host_wall_id, BuiltInCategory.OST_Doors)

    # check if part has openings or not
    if len(hosted_windows) == 0 and len(hosted_doors) == 0:
        out_ranges = []
    else:
        displacement = displacement_distance
        out_ranges = o.get_out_ranges(part, hosted_doors, hosted_windows, reveal_plane_coordinate_0, displacement)

    # interchanges the direction of placing reveals
    exterior = p.switch_directions(exterior, switch_direction=switch_option)

    # determine single panel or multi-panel reveal distances
    if multiple:
        reveal_indexes = p.get_reveal_indexes(left_edge, right_edge, out_ranges, exterior)
    else:
        reveal_indexes = p.get_single_panel_reveal_indexes(left_edge, right_edge, exterior)

    # Place reveals creating panels
    auto_panel(__title__, host_wall_id, lap_type_id, reveal_indexes, side_of_wall)


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> DELETE TRANSACTIONS

def delete_element(__title__, *args):
    """
    Delete a single/many element in revit
    :param __title__: tool title
    :param args: Collection of Element Ids to be deleted

    :return: None
    """
    with Transaction(doc, __title__) as t:
        t.Start("02. Delete reveals")
        options = t.GetFailureHandlingOptions()
        failureProcessor = eh.WarningSwallower()
        options.SetFailuresPreprocessor(failureProcessor)
        t.SetFailureHandlingOptions(options)
        for element_id in args:
            doc.Delete(element_id)
        t.Commit()


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GRAPHICS TRANSACTIONS

def highlight_unpanelized_underpanelized_parts(__title__):
    """
    Highlight unpanelized and underpanelized parts by color
    :param __title__: Tool title
    :return: Graphics settings for unpanelized and panelized parts
    """

    # select all parts
    parts = select_all_parts()
    exterior_parts, interior_parts = sort_parts_by_side(parts)
    filtered_parts = exterior_parts + interior_parts
    underpanalized, panelized, unpanelized = sort_parts_by_length(filtered_parts)

    solid_fill_id = ElementId(20)

    # color codes - unpanelized
    graphics_settings_unpanelized = OverrideGraphicSettings()
    graphics_settings_unpanelized.SetSurfaceForegroundPatternId(solid_fill_id)
    clr_bytes_a = [255, 99, 71]
    color_unpanelized_a = Color(clr_bytes_a[0], clr_bytes_a[1], clr_bytes_a[2])
    graphics_settings_unpanelized.SetSurfaceForegroundPatternColor(color_unpanelized_a)

    # color codes - underpanelized
    graphics_settings_underpanelized = OverrideGraphicSettings()
    graphics_settings_underpanelized.SetSurfaceForegroundPatternId(solid_fill_id)
    clr_bytes_b = [251, 191, 0]
    color_underpanelized_b = Color(clr_bytes_b[0], clr_bytes_b[1], clr_bytes_b[2])
    graphics_settings_underpanelized.SetSurfaceForegroundPatternColor(color_underpanelized_b)

    with Transaction(doc, __title__) as t:
        t.Start()
        if len(unpanelized) != 0:
            for part in unpanelized:
                active_view.SetElementOverrides(part.Id, graphics_settings_unpanelized)
        if len(underpanalized) != 0:
            for part in underpanalized:
                active_view.SetElementOverrides(part.Id, graphics_settings_underpanelized)

        t.Commit()

    return graphics_settings_unpanelized, graphics_settings_underpanelized


def remove_graphics(__title__):
    """
    Reset graphics for unpanelized parts that have been panelized (under development)
    :param __title__: Tool title
    :return: None
    """
    pass
