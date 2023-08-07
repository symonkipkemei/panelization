from __future__ import division

# METADATA

__title__ = "AutoPanel"

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
import clr

clr.AddReference("System")
from _create import _auto as a
from _create import _parts as g

import time
import  random
# VARIABLES
################################################################################################################################

# __revit__  used to create an instance
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


def main():
    selected_parts = g.select_all_parts()
    non_panelized_parts = g.check_if_parts_panelized(selected_parts)
    parts = g.check_if_wall_edited(non_panelized_parts)

    # start by BamCore 8" Separate I-E - exterior parts
    for part in parts:
        layer_index = g.get_layer_index(part)
        if layer_index == 1:  # exterior parts
            try:
                a.auto_parts(__title__, part)
            except ValueError:
                pass

    # followed by BamCore 8" Separate I-E - interior parts
    for part in parts:
        layer_index = g.get_layer_index(part)
        if layer_index == 3:  # interior parts
            try:
                a.auto_parts(__title__, part)
            except ValueError:
                pass

    # followed by BamCore 8" Int Only - interior parts
    for part in parts:
        layer_index = g.get_layer_index(part)
        if layer_index == 2:  # interior parts
            try:
                a.auto_parts(__title__, part)
            except ValueError:
                pass

if __name__ == "__main__":
    # print(get_part_length(496067))
    main()
