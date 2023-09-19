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
from Autodesk.Revit.DB import OverrideGraphicSettings
from Autodesk.Revit.DB import View
from _create import _transactions as a
from _create import _parts as g
from _create import _forms as f
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
    """
    Select all parts and filter to unpanelized parts
    :return: unpanelized parts
    """
    # select interior and exterior parts
    parts = g.select_all_parts()
    exterior_parts, interior_parts = g.sort_parts_by_side(parts)

    # filter into parts that have not been panelized
    underpanelized, panalized, unpanelized_exterior_parts = g.sort_parts_by_length(exterior_parts)
    underpanelized, panalized, unpanelized_interior_parts = g.sort_parts_by_length(interior_parts)

    unpanelized_parts = unpanelized_exterior_parts + unpanelized_interior_parts
    # display there id, length, height, base_level

    return unpanelized_parts


def get_unpanalized_parts_data(unpanelized_parts):
    """Abstract unpanelized parts data from the model"""
    parts_data = []
    count = 0

    for part in unpanelized_parts:
        count += 1
        part_id = part.Id
        height = part.get_Parameter(BuiltInParameter.DPART_HEIGHT_COMPUTED).AsValueString()
        length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsValueString()
        base_level = part.get_Parameter(BuiltInParameter.DPART_BASE_LEVEL).AsDouble()

        data = [count, part_id, height, length, base_level]

        parts_data.append(data)
    return parts_data



def main():
    parts = get_unpanelized_parts()
    if len(parts) != 0:
        parts_data = get_unpanalized_parts_data(parts)

        g.highlight_unpanelized_underpanelized_parts(__title__)

        # display panels data
        header = ["COUNT", "PART ID", "HEIGHT(F)", "LENGTH(F)", "BASE LEVEL"]

        f.display_form(parts_data, header, "Unpanelized parts", last_line_color='color:blue;')

    else:
        forms.alert("Congratulations! All parts have been panelized")


    


if __name__ == "__main__":
    main()
