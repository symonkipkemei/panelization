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


def get_edge_index(__title__, part, host_wall_id, lap_type_id, variable_distance, side_of_wall):
    """
    Get the edge indexes ( left and right) when a part is selected
    :param __title__: tool title
    :param part: selected part
    :param variable_distance: distance from reveal at 0
    :param side_of_wall: side to place reveals
    :return:
    """

    # abstract the length of the part
    part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
    print("PART_LENGTH", part_length)

    # split parts  by placing a reveal: old_part(retains the original part Id), new_part (assigned a new part id)

    with Transaction(doc, __title__) as t:
        t.Start()
        wall_sweep = a.auto_reveal(host_wall_id, lap_type_id, variable_distance, side_of_wall)
        t.Commit()

    # get old_part_length
    old_part_length_a = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
    print("OLD PART LENGTH A", old_part_length_a)
    new_part_length = part_length - old_part_length_a
    print("NEW PART LENGTH", new_part_length)

    # move sweep, to determine the placement/orientation of the two parts
    move_distance = 0.010417  # 1/8", small distance to ensure part is cut
    move_wall_sweep(host_wall_id, wall_sweep, move_distance)

    # get old length (after moving wall sweep)
    old_part_length_b = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
    print("OLD PART LENGTH B", old_part_length_b)

    # determine the edge index in reference to reveal at 0
    if old_part_length_b < old_part_length_a:  # the new part is on the left
        left_edge_index = old_part_length_a
        right_edge_index = left_edge_index - part_length

    else:  # the new part is on the right

        left_edge_index = new_part_length
        right_edge_index = left_edge_index - part_length

    # delete reveal after abstracting the edge indexes
    with Transaction(doc, __title__) as t:
        t.Start()
        doc.Delete(wall_sweep.Id)
        t.Commit()

    return left_edge_index, right_edge_index


def move_wall_sweep(host_wall_id, wall_sweep, move_distance):
    """
    Move sweep by a particular distance,
    to check if panel if it's on right or left
    :param host_wall_id: To determine wall orientation
    :param move_distance: The distance to move by
    :param wall_sweep: The sweep to be moved
    """
    with Transaction(doc, __title__) as t:
        t.Start()
        # move either way depending on the orientation of the part
        orientation = get_wall_orientation(host_wall_id)
        if orientation[1]:
            if orientation[0] == -1
            location = wall_sweep.Location.Move(XYZ(move_distance, 0, 0))
            location = wall_sweep.Location.Move(XYZ(0, move_distance, 0))

        elif not orientation[1]:
            location = wall_sweep.Location.Move(XYZ(0 - move_distance, 0, 0))
            location = wall_sweep.Location.Move(XYZ(0, 0 - move_distance, 0))

        t.Commit()


def get_wall_orientation(host_wall_id):
    """
    Determines the orientation of the wall
    :param host_wall_id: The selected wall
    :return: If wall is negative or positive
    """

    direction = ()
    host_wall = doc.GetElement(host_wall_id)
    orientation = host_wall.Orientation

    if orientation[0] == -1:
        direction = (0, False)
    elif orientation[0] == 1:
        direction = (0, True)
    elif orientation[1] == -1:
        direction = (1, False)
    elif orientation[1] == 1:
        direction = (1, True)

    return direction


def test():
    part = g.select_part()
    host_wall_id = g.get_host_wall_id(part)
    side_of_wall = WallSide.Exterior
    lap_type_id = ElementId(352808)
    variable_distance = 0
    left_edge, right_edge = get_edge_index(__title__, part, host_wall_id, lap_type_id, variable_distance,
                                           side_of_wall)
    print (left_edge, right_edge)


def main(host_wall_id):
    # select a part
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    wall_sweep = uidoc.Document.GetElement(reference)
    distance = 2
    move_wall_sweep(host_wall_id, wall_sweep, distance)


if __name__ == "__main__":
    # print(get_part_length(496067))
    #get_wall_orientation(ElementId(709990))
    #test()
    main(ElementId(709888))
