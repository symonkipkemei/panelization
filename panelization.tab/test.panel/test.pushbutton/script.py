from __future__ import division

# METADATA

__title__ = "Test"

__doc__ = """Version  1.3
Date  = 09.06.2023
___________________________________________________________
Description:

This tool will create multiple panel of 4' or less 
by breaking down a Part into panels 

Direction based on type of the Parts

Exterior Parts  -> left to right
Interior Parts  -> right to left
Partition Parts -> right to left

Laps based on type of Parts
Exterior Parts  -> right lap
Interior Parts  -> left lap
Partition Parts -> left lap

___________________________________________________________
How-to:
-> Click on the button
-> Select a Part
___________________________________________________________
last update:
- [01.07.2023] - 1.3 RELEASE

___________________________________________________________
To do:
-> Allow the user to set a constrain of the smallest panel size
___________________________________________________________
Author: Symon Kipkemei

"""

__author__ = "Symon Kipkemei"
__helpurl__ = "https://www.linkedin.com/in/symon-kipkemei/"

__highlight__ = 'new'

__min_revit_ver__ = 2020
__max_revit_ver__ = 2023

# IMPORTS
################################################################################################################################

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Structure
from Autodesk.Revit.UI.Selection import ObjectType
import clr

clr.AddReference("System")

from _create import _auto as a
from _create import _get as g
from _create import _coordinate as c
from _create import _openings as o

# VARIABLES
################################################################################################################################

# __revit__  used to create an instance
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


def test_place_reveal_out_ranges():
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
    print (hosted_windows_out_ranges)

    # place reveals on out ranges
    for window_range in hosted_windows_out_ranges:
        left_range = window_range[0]
        righ_range = window_range[1]

        # left edge reveals
        a.auto_place_reveal(__title__, hosted_wall_id, lap_type_id, left_range, side_of_wall)
        a.auto_place_reveal(__title__, hosted_wall_id, lap_type_id, righ_range, side_of_wall)


def main(wall_origin):
    """
    Determining the location of objects
    :return:
    """

    # wall_length = get_wall_length(hosted_wall_id)
    # reference = uidoc.Selection.PickObject(ObjectType.Element)
    # wall = uidoc.Document.GetElement(reference)
    # wall_origin = wall.Location.Curve.Origin

    symbol = get_type_by_name("test-family")

    with Transaction(doc, __title__) as t:
        t.Start()
        element = doc.Create.NewFamilyInstance(wall_origin, symbol, Structure.StructuralType.NonStructural)
        t.Commit()


def texting():
    from _create._coordinate import get_bounding_box_center
    el = uidoc.Selection.PickObject(ObjectType.Element, "Select something.")
    id = doc.GetElement(el)
    get_bounding_box_center(id)


def test_window_width():
    # select window width
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    window = uidoc.Document.GetElement(reference)
    # abstract the width
    width = o.get_window_width(window.Id)
    # display width
    print (width)


if __name__ == "__main__":
    test_window_width()
