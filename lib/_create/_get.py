from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType

import clr

clr.AddReference("System")

from _create import _auto as a

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


def get_host_wall_id(part):
    """
    Retrieves the host wall id, when a Part is selected
    :param part: selected part
    :return: host_wall_id
    """
    linkedElementIdCollection = part.GetSourceElementIds()
    host_wall_id = linkedElementIdCollection[0].HostElementId  # pick first linkedelement in collection

    return host_wall_id


def select_all_parts():
    """Selects all parts in a project"""
    all_parts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Parts). \
        WhereElementIsNotElementType().ToElements()

    return all_parts


def select_part():
    """Selects a part from the uidoc
    :return: returns the Part object
    """
    # select part element
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    part = uidoc.Document.GetElement(reference)

    return part


def get_edge_index(__title__, part, lap_type_id, variable_distance, side_of_wall):
    """
    Get the edge indexes ( left and right) when a part is selected
    :param __title__: tool title
    :param part: selected part
    :param variable_distance: distance from reveal at 0
    :param side_of_wall: side to place reveals
    :return:
    """

    try:

        # abstract the length of the part
        part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
        half_part_length = part_length / 2

        # place reveal
        host_wall_id = get_host_wall_id(part)

        with Transaction(doc, __title__) as t:
            t.Start()
            wall_sweep = a.auto_reveal(host_wall_id, lap_type_id, variable_distance, side_of_wall)
            t.Commit()

        # get new_part_length
        new_part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

        # determine the edge index in reference to reveal at 0
        left_edge_index = 0
        right_edge_index = 0

        if new_part_length < half_part_length:
            # get distance between the left edge and wallSweepInfo.Distance at 0
            left_edge_index = (part_length - new_part_length) + variable_distance
            right_edge_index = left_edge_index - part_length

        elif new_part_length > half_part_length:
            left_edge_index = new_part_length + variable_distance
            right_edge_index = left_edge_index - part_length

        # delete reveal after abstracting the length
        with Transaction(doc, __title__) as t:
            t.Start()
            doc.Delete(wall_sweep.Id)
            t.Commit()

        return left_edge_index, right_edge_index

    except Exception as e:
        print ('The following error has occurred: {}'.format(e))

        return None


def get_reveal_indexes(left_edge, right_edge, exterior_face=True):
    """
    Retrieve the posiyion to place reveals
    :param left_edge: The left edge of the wall ( from exterior)
    :param right_edge: The right edge of the wall ( from exterior)
    :param panel_size: The size of each panel
    :param exterior_face: if exterior face, the panel position starts from left to right
    and right to left if not exterior face
    :return: the indexes of the reveal position
    """

    # place reveal at correct position
    part_length = left_edge - right_edge
    panel_size = 3.927083  # 3' 11 1/8"
    half_panel_size = 1.927083  # 1' 11 1/8"
    minimum_panel = 2
    reveal_width = 0.072917  # the width of the reveal 7/8"

    no_complete_panels = int(part_length // panel_size)
    incomplete_panel_length = part_length % panel_size

    # store all reveal indexes
    reveal_indexes = []

    if incomplete_panel_length == 0:  # the length of Parts can be divided perfectly into panels
        if exterior_face:
            for x in range(0, no_complete_panels):
                left_edge -= panel_size
                reveal_indexes.append(left_edge)
        else:
            right_edge = right_edge + reveal_width
            for x in range(0, no_complete_panels):
                right_edge += panel_size
                reveal_indexes.append(right_edge)


    elif incomplete_panel_length < 2:  # the remaining length after whole panels, if less than 2', split previous panel,
        # the remainder would be less than 4'
        if exterior_face:
            for x in range(0, (no_complete_panels - 1)):
                left_edge -= panel_size
                reveal_indexes.append(left_edge)
            left_edge -= half_panel_size
            reveal_indexes.append(left_edge)

        else:
            right_edge = right_edge + reveal_width  # to allow reveals cut internal panels at 4'
            for x in range(0, (no_complete_panels - 1)):
                right_edge += panel_size
                reveal_indexes.append(right_edge)
            right_edge += half_panel_size
            reveal_indexes.append(right_edge)

    elif incomplete_panel_length > minimum_panel:  # the remaining length after whole panels, if greater than 2', retain it
        if exterior_face:
            for x in range(0, no_complete_panels):
                left_edge -= panel_size
                reveal_indexes.append(left_edge)
        else:
            right_edge = right_edge + reveal_width
            for x in range(0, no_complete_panels):
                right_edge += panel_size
                reveal_indexes.append(right_edge)

    else:
        print ("The incomplete panel length is unknown or faulty")

    # check if there is a remainder
    return reveal_indexes


def get_single_panel_reveal_indexes(left_edge, right_edge, exterior_face=True):
    """Determine the position of a reveal index for a single panel
    :param left_edge:
    :param right_edge:
    :param exterior_face:
    :return:
    """
    panel_size = 3.927083
    reveal_indexes = []
    if exterior_face:
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
    layer Index 2 - internal partition walls
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
    :return: filter list of parts yet to be panelized
    """
    parts_to_panelize = []
    for part in parts:
        part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
        if part_length > 4:
            parts_to_panelize.append(part)

    return parts_to_panelize


def check_if_part_panelized(part):
    """
    Checks if a single part has already been panelized
    :param part: Part
    :return: non panelized parts
    """
    part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
    if part_length > 4:
        return part
    else:
        print ("Part already panelized")
