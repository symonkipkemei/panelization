

# METADATA
################################################################################################################################


__title__ = "AutoReveal"

__doc__ = """ Version  1.1
Date  = 09.06.2023
___________________________________________________________
Description:

This tool will auto place reveals on a selected Part

___________________________________________________________
How-to:

-> Click on the button
-> Select a Part
___________________________________________________________
last update:
- [01.07.2023] - 1.1 RELEASE

___________________________________________________________
To-Do:
-> a form to allow the user adjust the distance from 0
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

from _create import _auto as a
from _create import _parts as g

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
    part = g.select_part()
    host_wall_id = g.get_host_wall_id(part)
    layer_index = g.get_layer_index(part)
    left_lap_id = ElementId(352818)
    right_lap_id = ElementId(352808)

    variable_distance = 4

    if layer_index == 1:  # exterior face
        side_of_wall = WallSide.Exterior
        lap_type_id = right_lap_id
        a.auto_place_reveal(__title__, host_wall_id,lap_type_id,variable_distance, side_of_wall)

    elif layer_index == 2:  # interior face of partition walls
        side_of_wall = WallSide.Interior
        lap_type_id = left_lap_id
        a.auto_place_reveal(__title__, host_wall_id, lap_type_id, variable_distance, side_of_wall)

    elif layer_index == 3:  # interior face
        side_of_wall = WallSide.Interior
        lap_type_id = left_lap_id
        a.auto_place_reveal(__title__, host_wall_id, lap_type_id, variable_distance, side_of_wall)


if __name__ == "__main__":
    main()
