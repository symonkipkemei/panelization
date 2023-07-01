# METADATA
__title__ = "SinglePanel"

__doc__ = """Version  1.3
Date  = 09.06.2023
___________________________________________________________
Description:

This tool will create a single panel of 4' 
based on the  type of the Parts

Exterior Parts  -> left to right
Interior Parts  -> right to left
Partition Parts -> right to left

The tool is able to intuitively identify the 
type of parts and use the correct lap

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
Author: Symon Kipkemei

"""

__author__ = "Symon Kipkemei"
__helpurl__ = "https://www.linkedin.com/in/symon-kipkemei/"

__highlight__ = 'new'

__min_revit_ver__ = 2020
__max_revit_ver__ = 2023


# IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType

from _create import _get as g
from _create import _auto as a

import clr
clr.AddReference("System")

# VARIABLES
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel

# FUNCTIONS

def main():
    part = g.get_part()
    host_wall_id = g.get_host_wall_id(part)
    layer_index = g.get_layer_index(part)
    left_lap_id = ElementId(352818)
    right_lap_id = ElementId(352808)

    variable_distance = 3

    if layer_index == 1:  # exterior face
        side_of_wall = WallSide.Exterior
        lap_type_id = right_lap_id
        left_edge, right_edge = g.get_edge_index(__title__, part, lap_type_id, variable_distance, side_of_wall)
        reveal_indexes = g.get_single_panel_reveal_indexes(left_edge, right_edge, exterior_face=True)
        a.auto_panel(__title__, host_wall_id, lap_type_id, reveal_indexes, side_of_wall)

    elif layer_index == 2:  # interior face of partition walls
        side_of_wall = WallSide.Interior
        lap_type_id = left_lap_id
        left_edge, right_edge = g.get_edge_index(__title__, part, lap_type_id, variable_distance, side_of_wall)
        reveal_indexes = g.get_single_panel_reveal_indexes(left_edge, right_edge, exterior_face=False)
        a.auto_panel(__title__, host_wall_id, lap_type_id, reveal_indexes, side_of_wall)

    elif layer_index == 3:  # interior face
        side_of_wall = WallSide.Interior
        lap_type_id = left_lap_id
        left_edge, right_edge = g.get_edge_index(__title__, part, lap_type_id, variable_distance, side_of_wall)
        reveal_indexes = g.get_single_panel_reveal_indexes(left_edge, right_edge, exterior_face=False)
        a.auto_panel(__title__, host_wall_id, lap_type_id, reveal_indexes, side_of_wall)


if __name__ == "__main__":
    # print(get_part_length(496067))
    main()