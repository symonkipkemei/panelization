from __future__ import division

# METADATA

__title__ = "Test"

__doc__ = """Version  1.3
Date  = 09.06.2023
___________________________________________________________
Description:

This tool will test the out ranges position of windows

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
########################################################################################################################

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Structure
from Autodesk.Revit.UI.Selection import ObjectType
import clr

clr.AddReference("System")

from _create import _auto as a
from _create import _parts as g
from _create import _coordinate as c
from _create import _openings as o
from _create import _test as t

# VARIABLES
########################################################################################################################

# __revit__  used to create an instance
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# ________________________________________________________________________________________________TESTS


if __name__ == "__main__":
    t.test_variable_distance(__title__)
    #t.test_left_edge(__title__)



