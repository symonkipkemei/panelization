# METADATA
################################################################################################################################


__title__ = "PanelTakeoff"

__doc__ = """ 
Auto Generate panel Material takeoff
by inputting the cost estimate per panel and
selecting the parts type
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


def get_parts_data(part_type="both"):
    parts = g.select_all_parts()
    exterior_parts, interior_parts = g.filter_exterior_interior_parts(parts)
    if part_type == "External Parts":
        filtered_parts = exterior_parts
    elif part_type == "Internal Parts":
        filtered_parts = interior_parts
    elif part_type == "External and Internal Parts":
        filtered_parts = interior_parts + exterior_parts
    else:
        filtered_parts = None

    parts_data = {}

    for part in filtered_parts:
        # abstract length, height and index from model
        parts_id = part.Id

        height = part.get_Parameter(BuiltInParameter.DPART_HEIGHT_COMPUTED).AsValueString()
        length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsValueString()
        thickness = part.get_Parameter(BuiltInParameter.DPART_LAYER_WIDTH).AsDouble()
        volume = part.get_Parameter(BuiltInParameter.DPART_VOLUME_COMPUTED).AsDouble()
        base_level = part.get_Parameter(BuiltInParameter.DPART_BASE_LEVEL).AsDouble()
        area = part.get_Parameter(BuiltInParameter.DPART_AREA_COMPUTED).AsDouble()

        part_type = height + " x " + length

        parts_data[parts_id] = [part_type, height, length, thickness, volume, base_level, area]

    return parts_data


def get_parts_type_data(parts_data):
    data = {}

    for part_data in parts_data.values():  # the default type
        default_part_type = part_data[0]
        count = 0
        for part in parts_data.values():
            part_type = part[0]

            if default_part_type == part_type:
                count += 1

        data[default_part_type] = count

    return data


def get_summary_data(parts_data, parts_type_data, cost_per_sf ):
    final_data = []
    sum_panels = 0
    sum_area = 0
    sum_cost = 0

    for part_type, count in parts_type_data.items():
        for part in parts_data.values():
            if part_type == part[0]:
                total_area = count * part[6]
                total_cost = total_area * cost_per_sf
                combine_data = part[1:] + [count] + [total_area] + [cost_per_sf] + [total_cost]
                final_data.append(combine_data)

                sum_panels += count
                sum_area += total_area
                sum_cost += total_cost

                break

    sum_total = ["-", "-", "-", "-", "-", "-", sum_panels, sum_area, "-", sum_cost]
    final_data.append(sum_total)

    return final_data


def main():
    cost_per_sf = float(f.single_digit_value())
    parts_type = f.select_part_type()
    parts_data = get_parts_data(parts_type)
    parts_type_data = get_parts_type_data(parts_data)

    final_data = get_summary_data(parts_data, parts_type_data,cost_per_sf)

    # display panels data
    header = ["HEIGHT(F)", "LENGTH(F)", "THICKNESS(F)", "VOLUME (CF) ", "BASE LEVEL", "AREA (SF)", "COUNT",
              "TOTAL AREA(SF)",
              "COST PER SF (USD)", " COST(USD)"]

    f.display_form(final_data, header, "Parts Material Takeoff" + "-" + parts_type)


if __name__ == "__main__":
    main()
