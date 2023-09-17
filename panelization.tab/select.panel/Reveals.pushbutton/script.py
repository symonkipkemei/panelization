# METADATA
__title__ = "FaceReveals"

__doc__ = """
Select all reveals on a part face
"""

__author__ = "Symon Kipkemei"
__helpurl__ = "https://www.linkedin.com/in/symon-kipkemei/"

__min_revit_ver__ = 2020
__max_revit_ver__ = 2025

# IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType
from Autodesk.Revit.UI.Selection import ISelectionFilter

from _create import _parts as g
from _create import _transactions as a
from _create import _errorhandler as eh

import clr

clr.AddReference("System")
clr.AddReference('System.Collections')

from System.Collections.Generic import List, ICollection
from pyrevit import forms

# VARIABLES
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel

# FUNCTIONS

import clr


# a class to filter selections to reveals only
class RevealSelectionFilter(ISelectionFilter):
    def AllowElement(self, element):
        if element.Category.Name == "Reveals":
            return True
        return False

    def AllowReference(self, refer, point):
        return False


# select a reveal
def select_reveal():
    reveal_filter = RevealSelectionFilter()
    reference = uidoc.Selection.PickObject(ObjectType.Element, reveal_filter)
    reveal = uidoc.Document.GetElement(reference)
    if str(type(reveal)) == "<type 'WallSweep'>":
        return reveal
    else:
        raise eh.RevealNotSelectedError


# identify the host id


def get_wall_side(reveal):
    wall_sweep_info = reveal.GetWallSweepInfo()
    wall_side = wall_sweep_info.WallSide
    return wall_side


def get_host_wall_id(reveal):
    host_ids = reveal.GetHostIds()
    host_id = host_ids[0]

    return host_id


# select all reveals that have similar id and face


def select_all_reveals():
    all_reveals = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Reveals). \
        WhereElementIsNotElementType().ToElements()

    return all_reveals


def get_filtered_reveals(reference_host_id, reference_wall_side, all_reveals):
    filtered_reveals = []
    for reveal in all_reveals:
        wall_side = get_wall_side(reveal)
        host_id = get_host_wall_id(reveal)

        if wall_side == reference_wall_side and host_id == reference_host_id:
            filtered_reveals.append(reveal.Id)

    return filtered_reveals


def display_selected_reveals(filtered_reveals):
    uidoc.Selection.SetElementIds(filtered_reveals)


# filter reveals to same host id and face

def main():
    reveal = select_reveal()
    reference_host_id = get_host_wall_id(reveal)
    reference_wall_side = get_wall_side(reveal)
    all_reveals = select_all_reveals()
    filtered_reveals = get_filtered_reveals(reference_host_id, reference_wall_side,all_reveals)

    # Create a C# List[int] and add the Python list elements to it
    filtered_reveals_collection = List[ElementId](filtered_reveals)
    display_selected_reveals(filtered_reveals_collection)


if __name__ == "__main__":
    main()
