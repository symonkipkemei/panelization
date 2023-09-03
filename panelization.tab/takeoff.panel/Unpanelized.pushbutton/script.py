# METADATA
################################################################################################################################


__title__ = "Unpanelized"

__doc__ = """ 
Auto select all panels that have not been panelized.
List them down for action
"""

__author__ = "Symon Kipkemei"
__helpurl__ = "https://www.linkedin.com/in/symon-kipkemei/"
__min_revit_ver__ = 2020
__max_revit_ver__ = 2023

# IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType

from _create import _auto as a
from _create import _parts as g

from _create import _forms as f
from _create import _checks as c
from pyrevit import forms
import clr

clr.AddReference("System")

# VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# FUNCTIONS

# check if a panel is less than 4' and filtered, remove filter

def get_unpanelized_parts():
    # select interior and exterior parts
    parts = g.select_all_parts()
    exterior_parts, interior_parts = g.filter_exterior_interior_parts(parts)

    # filter into parts that have not been panelized
    unpanelized_exterior_parts = c.check_if_parts_panelized(exterior_parts)
    unpanelized_interior_parts = c.check_if_parts_panelized(interior_parts)

    unpanelized_parts = unpanelized_exterior_parts + unpanelized_interior_parts
    # display there id, length, height, base_level

    return unpanelized_parts


def get_unpanalized_parts_data(unpanelized_parts):
    parts_data = []

    for part in unpanelized_parts:
        part_id = part.Id
        height = part.get_Parameter(BuiltInParameter.DPART_HEIGHT_COMPUTED).AsValueString()
        length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsValueString()
        base_level = part.get_Parameter(BuiltInParameter.DPART_BASE_LEVEL).AsDouble()

        data = [part_id, height, length, base_level]

        parts_data.append(data)
    return parts_data


def isolate_unpanelized_parts():
    """Color code unapnelized parts for ease of identification"""
    pass


def main():
    parts = get_unpanelized_parts()
    parts_data = get_unpanalized_parts_data(parts)

    # display panels data
    header = ["PART ID", "HEIGHT(F)", "LENGTH(F)", "BASE LEVEL"]

    f.display_form(parts_data, header, "Unpanelized parts",last_line_color='color:blue;')


if __name__ == "__main__":
    main()