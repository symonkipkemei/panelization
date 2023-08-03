from __future__ import division

# METADATA

__title__ = "Test"

__doc__ = """Version  1.3
Date  = 09.06.2023
___________________________________________________________
Description:

This tool will create multiple panel of 4' or less 
by breaking down a Part into panels 

Direction based on type of the Parts

Exterior Parts  -> left to right
Interior Parts  -> right to left
Partition Parts -> right to left

Laps based on type of Parts
Exterior Parts  -> right lap
Interior Parts  -> left lap
Partition Parts -> left lap

___________________________________________________________
How-to:
-> Click on the button
-> Select a Part
___________________________________________________________
last update:
- [01.07.2023] - 1.3 RELEASE

___________________________________________________________
To do:
-> Allow the user to set a constrain of the smallest panel size
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
from Autodesk.Revit.DB import Structure
from Autodesk.Revit.UI.Selection import ObjectType
import clr

clr.AddReference("System")

from _create import _auto as a
from _create import _get as g
from _create import _coordinate as c
from _create import _openings as o

# VARIABLES
################################################################################################################################

# __revit__  used to create an instance
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


def place_reveal_window_centres():
    """
    Places reveals at the centre of the windows
    :return:
    """

    global lap_type_id, side_of_wall, window_centre_index
    # get hosted windows
    part = g.select_part()
    hosted_wall_id = g.get_host_wall_id(part)
    hosted_windows = o.get_hosted_windows(hosted_wall_id)

    layer_index = g.get_layer_index(part)
    left_lap_id = ElementId(352818)
    right_lap_id = ElementId(352808)
    variable_distance = 3

    if layer_index == 1:  # exterior
        side_of_wall = WallSide.Exterior
        lap_type_id = right_lap_id
        exterior = True

    elif layer_index == 3:  # interior
        side_of_wall = WallSide.Interior
        lap_type_id = left_lap_id
        exterior = False

    left_edge_index, right_edge_index = g.get_edge_index(__title__, part, hosted_wall_id, lap_type_id,
                                                         variable_distance, side_of_wall)

    # get the direction of each panel
    x_axis_plane = c.determine_x_plane(hosted_wall_id)
    direction = c.get_panel_direction(__title__, hosted_wall_id, lap_type_id, left_edge_index, right_edge_index,
                                      side_of_wall, x_axis_plane, exterior=exterior)

    # Determine the left edge coordinate as the datum

    part_xyz_centre = c.get_bounding_box_center(part)  # get part center(xyz)
    part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()  # get part length
    part_coordinate_centre = c.get_plane_coordinate(part_xyz_centre, x_axis_plane)  # get the part coordinates

    left_edge_coordinate, right_edge_coordinate = c.get_part_edges_coordinate(
        part_length, part_coordinate_centre, direction, layer_index)  # get left edge based on direction

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

    # get window index centre

    # loop through windows, determine the window index and place reveals
    for window in hosted_windows:  # loop through hosted windows
        window_xyz_centre = o.get_window_xyz_centre(window.Id)  # get window centre
        window_coordinate_centre = c.get_plane_coordinate(window_xyz_centre, x_axis_plane)  # get window coordinate

        if layer_index == 1:  # exterior
            print ("exterior")
            window_centre_index = c.convert_window_coordinate_to_index(left_edge_index, left_edge_coordinate,
                                                                       window_coordinate_centre, plus=False)
        elif layer_index == 3:  # interior
            print ("interior")
            window_centre_index = c.convert_window_coordinate_to_index(right_edge_index, right_edge_coordinate,
                                                                       window_coordinate_centre, plus=True
                                                                       )
        # convert window coordinate to index

        print ("_____________________________\n")

        print ("window centre index", window_centre_index)
        print ("window centre coordinate ", window_coordinate_centre)

        a.auto_place_reveal(__title__, hosted_wall_id, lap_type_id, window_centre_index, side_of_wall)


def main(wall_origin):
    """
    Determining the location of objects
    :return:
    """

    # wall_length = get_wall_length(hosted_wall_id)
    # reference = uidoc.Selection.PickObject(ObjectType.Element)
    # wall = uidoc.Document.GetElement(reference)
    # wall_origin = wall.Location.Curve.Origin

    symbol = get_type_by_name("test-family")

    with Transaction(doc, __title__) as t:
        t.Start()
        element = doc.Create.NewFamilyInstance(wall_origin, symbol, Structure.StructuralType.NonStructural)
        t.Commit()


def texting():
    from _create._coordinate import get_bounding_box_center
    el = uidoc.Selection.PickObject(ObjectType.Element, "Select something.")
    id = doc.GetElement(el)
    get_bounding_box_center(id)


if __name__ == "__main__":
    # print(get_part_length(496067))
    # window_location = get_window_location(499209)

    # main()

    # reveal_window_centres()
    # get_edge_indexes()

    # centre = get_bounding_box_center(500296)
    # main(centre)
    place_reveal_window_centres()
    # testing_bounding_box()
