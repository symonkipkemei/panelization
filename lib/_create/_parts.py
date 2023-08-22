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
from _create import _coordinate as c
from _create import _openings as o

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

rvt_year = int(app.VersionNumber)
# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ATOMIC FUNCTIONS


def get_host_wall_id(part):
    """
    Retrieves the host wall id, when a Part is selected
    :param part: selected part
    :return: host_wall_id
    """
    linkedElementIdCollection = part.GetSourceElementIds()
    host_wall_id = linkedElementIdCollection[0].HostElementId  # pick first linkedelement in collection

    return host_wall_id


def get_host_wall_type_id(host_wall_id):
    """
    Abstract the type of the wall by retrieving the wall type id
    :param host_wall_id: id of the wall
    :return: id of the wall type
    """
    host_wall = doc.GetElement(host_wall_id)
    type_id = host_wall.GetTypeId()

    return type_id


def select_all_parts():
    """
    Selects all parts in a active project
    :return: A collection of all parts
    """
    all_parts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Parts). \
        WhereElementIsNotElementType().ToElements()

    return all_parts


def select_part():
    """Selects a part from the active project
    :return: returns the Part object
    """
    # select part element
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    part = uidoc.Document.GetElement(reference)

    if str(type(part)) == "<type 'Part'>":
        return part
    else:
        print("Select a Part for it to be multi-panelized, you've selected", type(part))


def select_parts():
    """Selects parts from the uidoc
    :return: returns a list of parts
    """

    # select part element
    references = uidoc.Selection.PickObjects(ObjectType.Element)

    parts = []
    for reference in references:
        part = uidoc.Document.GetElement(reference)
        parts.append(part)

    return parts


def delete_element(__title__, *args):
    """
    Delete a single/many element in revit
    :param __title__: tool title
    :return: None
    """
    with Transaction(doc, __title__) as t:
        t.Start()
        for element_id in args:
            doc.Delete(element_id)
        t.Commit()


def get_edge_index(__title__, part, host_wall_id, lap_type_id, variable_distance, side_of_wall):
    """
    Get the edge indexes ( left and right) when a part is selected.
    The index are relative to the position of the reveal at distance 0
    :param __title__: tool title
    :param part: selected part
    :param variable_distance: distance from reveal at 0
    :param side_of_wall: side to place reveals
    :return: collection of left and right edges
    """

    global left_edge_index, right_edge_index

    # abstract the length of the part
    part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

    # split parts  by placing a reveal: old_part(retains the original part id), new_part (assigned a new part id)

    # fst_wall_sweep
    with Transaction(doc, __title__) as t:
        t.Start()
        fst_wall_sweep = a.auto_reveal(host_wall_id, lap_type_id, variable_distance, side_of_wall)
        t.Commit()

        # get old_part_length ( part with original id)
    old_part_length_before_snd_reveal = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

    # create snd wall sweep
    move_distance = 0.166667  # 1/4", small distance to ensure part is cut
    with Transaction(doc, __title__) as t:
        t.Start()
        snd_wall_sweep = a.auto_reveal(host_wall_id, lap_type_id, (variable_distance + move_distance), side_of_wall)
        t.Commit()

    # get old_part_length after snd reveal ( part with original id)
    old_part_length_after_snd_reveal = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

    # determine the left/right edge index in reference to reveal at 0
    if old_part_length_after_snd_reveal == old_part_length_before_snd_reveal and \
            old_part_length_after_snd_reveal != part_length:
        # the old part is on the right, not affected by reveal moving (right to left)
        left_edge_index = (part_length - (old_part_length_before_snd_reveal - variable_distance))
        right_edge_index = left_edge_index - part_length

    elif old_part_length_after_snd_reveal != old_part_length_before_snd_reveal and \
            old_part_length_after_snd_reveal != part_length:
        # the old part is on the left affected by reveal moving (right to left)

        left_edge_index = old_part_length_before_snd_reveal - variable_distance
        right_edge_index = left_edge_index - part_length

    elif old_part_length_after_snd_reveal == part_length:
        # The parts were not cut, thus length did not change, possibly a non-orthogonal wall
        # or reveals are outside the Parts
        with Transaction(doc, __title__) as t:
            t.Start()
            doc.Delete(fst_wall_sweep.Id)
            doc.Delete(snd_wall_sweep.Id)
            t.Commit()
        raise ValueError

    else:
        # unforeseen errors, the tool is dysfunctional check for errors, catch un-panelized panels
        with Transaction(doc, __title__) as t:
            t.Start()
            doc.Delete(fst_wall_sweep.Id)
            doc.Delete(snd_wall_sweep.Id)
            t.Commit()

        raise ValueError

    # delete reveals after abstracting the edge indexes
    with Transaction(doc, __title__) as t:
        t.Start()
        doc.Delete(fst_wall_sweep.Id)
        doc.Delete(snd_wall_sweep.Id)
        t.Commit()

    return left_edge_index, right_edge_index


def get_reveal_indexes_v2(left_edge, right_edge, out_ranges, exterior=True):
    """
    Retrieve the reveal indexes, taking into consideration the window out-ranges
    :param out_ranges: The ranges where the reveals should not be positioned closed to fenestration edges
    :param left_edge: The left edge of the part ( from exterior)
    :param right_edge: The right edge of the part ( from exterior)
    :param exterior: if exterior face, the panel position starts from left to right,
     if not the panel position starts from right to left
    :return: the indexes of the reveal position
    """

    panelling_distance = 3.927083

    # The panelling distance (Distance required to generate a panel of 4')
    # from one reveal to another, varies based on the type of reveal

    if rvt_year >= 2023:  # template provided uses reveal width 15/16"
        panelling_distance = 3.927083 - 0.005208  # 3' 11 1/8" - 1/16"
    elif rvt_year <= 2022:  # template provided uses reveal width 7/8"
        panelling_distance = 3.927083  # 3' 11 1/8"

    # offset reveal width from edge to allow cutting of first panel at 4'
    if rvt_year <= 2022:  # template provided uses reveal width 7/8"
        reveal_width = 0.072917
        right_edge = right_edge + reveal_width
    elif rvt_year >= 2023:  # template provided uses reveal width 15/16"
        reveal_width = 0.039063
        right_edge = right_edge + reveal_width
        left_edge = left_edge - reveal_width

    # minimum panel when panelizing
    minimum_panel = 2

    # store all reveal indexes
    reveal_indexes = []

    # determine reveals required to panelize part
    while True:
        if exterior:  # panelization is left to right, the left edge reduces towards the right edge
            left_edge -= panelling_distance
            # skipping the out range if there is a window
            left_edge = o.skip_out_range(left_edge, out_ranges, exterior=True)
            # remaining length established, will determine when panelization is complete ( < 4 script breaks)
            rem_length = left_edge - right_edge
            # the new left edge appended to the list
            reveal_indexes.append(left_edge)

            if rem_length < 4:
                if rem_length < minimum_panel:
                    # remove the last record on list to allow for further splitting
                    del reveal_indexes[-1]
                    # the new left edge becomes the last item on list after deleting the last reveal
                    left_edge = reveal_indexes[-1]
                    # the part left behind is determined
                    part_left_behind = left_edge - right_edge
                    # determine the remainder left edge position
                    reveal_edge_width = 0.078125  # subtracted 15/16"from panel to allow it cut at 2'
                    # what remains after setting aside minimum panel
                    rem = part_left_behind - (minimum_panel - reveal_edge_width)
                    # position the new left edge
                    left_edge -= rem
                    reveal_indexes.append(left_edge)
                    # the script now ends
                    break
                else:
                    # the script now ends
                    break
        else:
            right_edge += panelling_distance  # panelization is right to left, the right edge increases towards the left edge
            # skipping the out range if there is a window
            right_edge = o.skip_out_range(right_edge, out_ranges, exterior=False)
            rem_length = left_edge - right_edge
            reveal_indexes.append(right_edge)
            if rem_length < 4:
                if rem_length < minimum_panel:
                    # remove the last record on list to allow for further splitting
                    del reveal_indexes[-1]
                    right_edge = reveal_indexes[-1]  # the right edge becomes the last item on list
                    part_left_behind = left_edge - right_edge
                    reveal_edge_width = 0.078125  # subtracted from panel to allow it cut at 2'
                    rem = part_left_behind - (minimum_panel - reveal_edge_width)
                    right_edge += rem
                    reveal_indexes.append(right_edge)
                    break
                else:
                    break

    return reveal_indexes


def get_single_panel_reveal_indexes(left_edge, right_edge, exterior=True):
    """Determine the position of a reveal index for a single panel
    :param exterior: if part exterior or not
    :param left_edge:left edge reveal index
    :param right_edge:right edge reveal index
    :return: reveal index position to form a panel
    """
    panel_size = 3.927083
    reveal_indexes = []
    if exterior:
        new_reveal_distance = left_edge - panel_size
        reveal_indexes.append(new_reveal_distance)

    else:
        new_reveal_distance = right_edge + panel_size
        reveal_indexes.append(new_reveal_distance)

    return reveal_indexes


def get_layer_index(part):
    """
    Abstract the layer index of a part if
    layer Index 1- Exterior face
    layer Index 2 - internal partition walls ( only applies for Bamcore Int Wall Type)
    layer Index 3- Interior face

    :param part: Part to be abstracted
    :return: The layer index
    """
    # abstract the layer index of part
    layer_index = int(part.get_Parameter(BuiltInParameter.DPART_LAYER_INDEX).AsString())
    return layer_index


def check_if_parts_panelized(parts):
    """
    Filter parts that have not been panelized only, to avoid panelizing panels further
    :param parts: list of parts selected from an open revit document
    :return: non-panelized parts
    """
    parts_to_panelize = []
    for part in parts:
        part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
        if part_length > 4:
            parts_to_panelize.append(part)

    return parts_to_panelize


def check_if_host_wall_edited(parts):
    """
    Parts with edited host walls results to non-orthogonal parts,
    these parts are not cut by reveals thus a need to skip them.
    The script filters non-orthogonal parts
    :param parts: list of parts selected from an open revit document
    :return: orthogonal parts
    """
    orthogonal_parts = []
    for part in parts:
        host_wall_id = get_host_wall_id(part)
        host_wall = doc.GetElement(host_wall_id)
        sketch = host_wall.SketchId  # if sketchId is not -1, then the wall has been edited

        if sketch == ElementId(-1):
            orthogonal_parts.append(part)
    return orthogonal_parts


def get_part_length(part):
    """
    Abstract the length of selected part
    :return: length
    """
    return part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()


def get_centre_index(__title__, part):
    """
    Determine the variable distance to be used
    :param part: Part to be panelized
    :param __title__: tool title
    :return: variable distance
    """

    # project parameters
    host_wall_id = get_host_wall_id(part)
    layer_index = get_layer_index(part)
    lap_type_id = 0
    side_of_wall = None
    x_axis_plane = c.determine_x_plane(host_wall_id)
    if layer_index == 1:
        lap_type_id = ElementId(352808)  # right_lap_id
        side_of_wall = WallSide.Exterior

    elif layer_index == 3:
        lap_type_id = ElementId(352818)  # left_lap_id
        side_of_wall = WallSide.Interior

    # establish the length of part
    length_before_reveal = get_part_length(part)

    # determine the reveal that cuts through the part, the script will continue until the correct reveal is found,
    # a reveal that does not cut through the part will not give us it's coordinates

    # reveal 1 plane coordinate
    variable_distance = -3
    while True:
        reveal_1 = a.auto_place_reveal_v2(__title__, host_wall_id, lap_type_id, variable_distance, side_of_wall)
        length_after_reveal = get_part_length(part)
        #print (variable_distance)
        if c.get_bounding_box_center(reveal_1) is not None:
            break
        elif length_before_reveal != length_after_reveal:
            break
        delete_element(__title__, reveal_1.Id)
        variable_distance += 3
        if variable_distance > 100:
            print ("The variable distance could not be established")
            break

    reveal_xyz_coordinates_1 = c.get_bounding_box_center(reveal_1)
    reveal_plane_coordinate_1 = float(c.get_plane_coordinate(reveal_xyz_coordinates_1, x_axis_plane))

    # create snd wall sweep, this will help establish the reveal at 0
    move_distance = 0.166667  # 1/4", small distance to ensure part is cut
    reveal_2 = a.auto_place_reveal_v2(__title__, host_wall_id, lap_type_id, variable_distance + move_distance,
                                      side_of_wall)

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

    # determine the coordinates of the centre of the part
    part_centre_xyz_coordinates = c.get_bounding_box_center(part)
    part_centre_coordinate = float(c.get_plane_coordinate(part_centre_xyz_coordinates, x_axis_plane))

    # determine the difference between two to abstract the centre-index
    if reveal_plane_coordinate_0 > part_centre_coordinate:
        centre_index = (reveal_plane_coordinate_0 - part_centre_coordinate)
    else:
        centre_index = (part_centre_coordinate - reveal_plane_coordinate_0)

    # Test parameters
    # print ("Variable distance", variable_distance)
    # print ("reveal plane coordinate", reveal_xyz_coordinates)
    # print ("part_centre_xyz_coordinates", part_centre_xyz_coordinates)
    # print("reveal coordinate", reveal_plane_coordinate_0)
    # print ("centre coordinate", part_centre_coordinate)
    # print ("reveal index", 0)
    # print ("parts indexes", dif)

    return centre_index


def get_edge_index_v2(length, centre_index):
    """
    Determine the left or the right edge
    :param length:
    :param centre_index:
    :return: left_edge, right_edge
    """
    half_length = length / 2
    edge_1 = centre_index + half_length
    edge_2 = centre_index - half_length

    edges = sorted([edge_1, edge_2])

    right_edge = edges[0]  # the smallest value becomes the right-edge,
    # the distance 0 begins at the right end of the wall's path curve
    left_edge = edges[1]  # the largest value becomes the left edge

    return left_edge, right_edge
