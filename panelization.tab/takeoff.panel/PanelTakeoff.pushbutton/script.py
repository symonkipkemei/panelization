# METADATA
################################################################################################################################


__title__ = "PanelTakeoff"

__doc__ = """ Version  1.1
Date  = 24.06.2023
___________________________________________________________
Description:

This tool will auto schedule all panels in the project

___________________________________________________________
-> Click on the button

___________________________________________________________
last update:
- [24.07.2023] - 1.1 RELEASE

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


def get_parts_data():
    parts = g.select_all_parts()
    parts_data = {}

    for part in parts:
        # abstract length, height and index from model
        parts_id = part.Id
        length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsValueString()
        height = part.get_Parameter(BuiltInParameter.DPART_HEIGHT_COMPUTED).AsValueString()
        index = g.get_layer_index(part)
        # store in a dictionary

        parts_data[parts_id] = [length, height, index]

    return parts_data


def get_parts_group(parts_data):
    # filter only to external and internal parts:
    external_part_group = []
    internal_part_group = []
    total_part_group = []

    for part in parts_data.values():
        length = part[0]
        height = part[1]
        index = part[2]

        part_type = length + " x " + height

        if index == 1:
            if part_type not in external_part_group:
                external_part_group.append(part_type)
        elif index == 3:
            if part_type not in internal_part_group:
                internal_part_group.append(part_type)
        if index == 3 or index == 1:
            if part_type not in total_part_group:
                total_part_group.append(part_type)

    return external_part_group, internal_part_group, total_part_group


def count_part_type(part_group_name, part_group, parts_data, group_index):
    data = {}
    for default_part_type in part_group:
        count = 0

        for part in parts_data.values():
            length = part[0]
            height = part[1]
            index = part[2]
            part_type = length + " x " + height

            if part_type == default_part_type and index == group_index:
                count += 1
            elif part_type == default_part_type and group_index == 0:
                count += 1

        data[default_part_type] = count

    print ("\n{group_name}".format(group_name=part_group_name))
    print ("_______________________________")
    for i, (key, value) in enumerate(data.items(),1):
        key = key.replace("-", "")
        key = key.replace("\\", "")
        print ("{i}. Panel type: {key} ______ count:{value}".format(i=i,key=key, value=value))
    print ("_______________________________\n")

    return data


def main():
    # get parts data
    parts_data = get_parts_data()

    # get parts type
    external_part_group, internal_part_group, total_part_group = get_parts_group(parts_data)

    external_count_types = count_part_type("External Panels", external_part_group, parts_data, 1)
    internal_count_types = count_part_type("Internal Panels", internal_part_group, parts_data, 3)
    total_count_types = count_part_type("Total Panels", total_part_group, parts_data, 0)


if __name__ == "__main__":
    main()
