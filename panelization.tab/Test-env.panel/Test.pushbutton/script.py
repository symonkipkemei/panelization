from __future__ import division

# METADATA

__title__ = "Test"

__doc__ = """Version  1.0
Date  = 09.07.2023
___________________________________________________________
Description:

Devlopment environment for testing bugs and features before development

___________________________________________________________
How-to:
-> Click on the button
___________________________________________________________
last update:
- [09.07.2023] - 1.0 RELEASE

___________________________________________________________
To do:
-> Testing and development
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
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType
import clr

clr.AddReference("System")

from _create import _auto as a
from _create import _get as g

# VARIABLES
################################################################################################################################

# __revit__  used to create an instance
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


def get_edge_index_test(__title__, part, host_wall_id, lap_type_id, variable_distance, side_of_wall):
    """
    Get the edge indexes ( left and right) when a part is selected
    :param __title__: tool title
    :param part: selected part
    :param variable_distance: distance from reveal at 0
    :param side_of_wall: side to place reveals
    :return:
    """

    global left_edge_index, right_edge_index

    # abstract the length of the part
    part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
    print("PART_LENGTH", part_length)

    # split parts  by placing a reveal: old_part(retains the original part Id), new_part (assigned a new part id)

    with Transaction(doc, __title__) as t:
        t.Start()
        fst_wall_sweep = a.auto_reveal(host_wall_id, lap_type_id, variable_distance, side_of_wall)
        t.Commit()

    # get old_part_length
    old_part_length_before_snd_reveal = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

    # create snd wall sweep
    move_distance = 0.166667  # 1/2", small distance to ensure part is cut
    with Transaction(doc, __title__) as t:
        t.Start()
        snd_wall_sweep = a.auto_reveal(host_wall_id, lap_type_id, (variable_distance + move_distance), side_of_wall)
        t.Commit()

    # get old_part_length after snd reveal
    old_part_length_after_snd_reveal = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

    print("OLD PART LENGTH BEFORE SND REVEAL", old_part_length_before_snd_reveal)
    print("OLD PART LENGTH AFTER SND REVEAL", old_part_length_after_snd_reveal)


def test():
    part = g.select_part()
    host_wall_id = g.get_host_wall_id(part)
    side_of_wall = WallSide.Exterior
    lap_type_id = ElementId(352808)
    variable_distance = 1
    get_edge_index_test(__title__, part, host_wall_id, lap_type_id, variable_distance,
                        side_of_wall)
    panel_size = 3.927083

    # place reveals at left edge ,0 and  right edge
    # a.auto_place_reveal(__title__, host_wall_id, lap_type_id, (left_edge - panel_size), side_of_wall)
    # a.auto_place_reveal(__title__, host_wall_id, lap_type_id, variable_distance, side_of_wall)
    # a.auto_place_reveal(__title__, host_wall_id, lap_type_id, (right_edge + panel_size), side_of_wall)


def main(host_wall_id):
    # select a part
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    wall_sweep = uidoc.Document.GetElement(reference)
    distance = 6
    x_axis_bool, left_right_bool = get_wall_orientation(host_wall_id)
    move_wall_sweep(__title__, x_axis_bool, left_right_bool, wall_sweep, distance)


if __name__ == "__main__":
    # main(ElementId(713033)) #short side
    # main(ElementId(713030)) #longside A
    test()
