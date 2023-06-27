from __future__ import division

# Autodesk
from Autodesk.Revit.DB import *
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



def get_panel_position(left_edge, right_edge):
    # place reveal at correct position
    part_length = left_edge - right_edge
    panel_size = 3.927083
    half_panel_size = panel_size / 2

    no_complete_panels = int(part_length // panel_size)
    incomplete_panel_length = part_length % panel_size

    reveal_indexes = []

    if incomplete_panel_length == 0:
        for x in range(0, no_complete_panels):
            left_edge -= panel_size
            reveal_indexes.append(left_edge)
    else:
        # If there is an incomplete panel half the panel before the last reveal
        for x in range(0, (no_complete_panels - 1)):
            left_edge -= panel_size
            reveal_indexes.append(left_edge)
        left_edge -= half_panel_size
        reveal_indexes.append(left_edge)

    # check if there is a remainder
    return reveal_indexes






if __name__ == "__main__":
    get_panel_position(19.729166666666817, -0.52083333333362347)
