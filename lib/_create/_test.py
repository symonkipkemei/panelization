from __future__ import division

# Autodesk
#from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType
# pyrevit

# __revit__  used to create an instance
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# custtom errors

class RevealMissingError(Exception): pass


# test kit for get_window_index center

"""
print ("_____________________________\n")

    print ("left edge index", left_edge_index)
    print ("right edge index", right_edge_index)

    print ("_____________________________\n")
    print ("left edge coordinate", left_edge_coordinate)
    print ("right edge coordinate", right_edge_coordinate)

    print ("_____________________________\n")
    print ("left index - right index", left_edge_index - right_edge_index)
    print ("left_co_ right_co", left_edge_coordinate - right_edge_coordinate)
    print ("_____________________________\n")

    print ("direction", direction)

"""

