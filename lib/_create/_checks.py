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
from _create import _test as tt
from _create import _parts as p
from _create import _coordinate as c
from _create import _openings as o
from _create import _errorhandler as e
from pyrevit import forms

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project


def check_centre_index(__title__, part, centre_index):
    """Check if the centre index is correct"""
    host_wall_id = p.get_host_wall_id(part)
    layer_index = p.get_layer_index(part)
    host_wall_type_id = p.get_host_wall_type_id(host_wall_id)
    lap_type_id, side_of_wall, exterior = p.get_wallsweep_parameters(layer_index, host_wall_type_id)

    length_before = p.get_part_length(part)

    # split the part into two
    reveal = a.auto_place_reveal(__title__, host_wall_id, lap_type_id, centre_index, side_of_wall)

    length_after = p.get_part_length(part)

    # delete reveal after split
    p.delete_element(__title__, reveal.Id)

    half_length = length_before / 2
    reveal_size = 0.0390625  # 3/64"
    length_parameter = round(half_length, 7) + reveal_size
    if round(length_after, 7) == length_parameter:
        centre_index = True
    else:
        centre_index = False

    return centre_index


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
        host_wall_id = p.get_host_wall_id(part)
        host_wall = doc.GetElement(host_wall_id)
        sketch = host_wall.SketchId  # if sketchId is not -1, then the wall has been edited

        if sketch == ElementId(-1):
            orthogonal_parts.append(part)
    return orthogonal_parts


def check_displacement_distance(displacement_distance, fenestration_width):
    limit = fenestration_width/2
    if displacement_distance >= limit:
        displacement_distance = limit - 1
        forms.alert("The displacement distance set is beyond half width fenestration limit")
    return displacement_distance
