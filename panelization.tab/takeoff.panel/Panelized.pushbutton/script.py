# METADATA
################################################################################################################################


__title__ = "Panelized"

__doc__ = """ 
Auto Generate panel Material takeoff of panelized parts
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


def get_parts_data(filtered_parts):
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


def get_summary_data(parts_data, parts_type_data, cost_per_sf):
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


def user_filters_part_type(exterior_parts,interior_parts):
    # user selects which parts for take off

    ops = ['External Parts', 'Internal Parts', 'External and Internal Parts']
    user_choice = forms.SelectFromList.show(ops, button_name='Select Option',
                                            title="Panel Material Takeoff", height=250)

    if user_choice == ops[0]:
        filtered_parts = exterior_parts
    elif user_choice == ops[1]:
        filtered_parts = interior_parts
    elif user_choice == ops[2]:
        filtered_parts = interior_parts + exterior_parts
    else:
        filtered_parts = None

    return filtered_parts, user_choice


def main():
    # select all parts
    parts = g.select_all_parts()
    exterior_parts, interior_parts = g.sort_parts_by_side(parts)
    filtered_parts, user_choice = user_filters_part_type(exterior_parts, interior_parts)

    # filter by length, take off of panelized and underpanalized parts
    underpanalized, panelized, unpanalized = g.sort_parts_by_length(filtered_parts)

    selected_parts = underpanalized + panelized

    if len(selected_parts) != 0:
        cost_per_sf = float(f.single_digit_value())

        # filter to parts that have been panelized
        parts_data = get_parts_data(selected_parts)
        parts_type_data = get_parts_type_data(parts_data)

        final_data = get_summary_data(parts_data, parts_type_data, cost_per_sf)

        # display panels data
        header = ["HEIGHT(F)", "LENGTH(F)", "THICKNESS(F)", "VOLUME (CF) ", "BASE LEVEL", "AREA (SF)", "COUNT",
                  "TOTAL AREA(SF)",
                  "COST PER SF (USD)", " COST(USD)"]

        f.display_form(final_data, header, "Parts Material Takeoff" + "-" + user_choice)

        if len(unpanalized) != 0:
            g.highlight_unpanelized_underpanelized_parts(__title__)
            forms.alert("Highlighted parts (red) have not been panelized")

        else:
            forms.alert("Congratualtions! All parts have been panelized")


    else:
        g.highlight_unpanelized_underpanelized_parts(__title__)
        forms.alert("Parts (red) not panelized (parts < 4 ). Proceed with Panelization")



if __name__ == "__main__":
    main()
