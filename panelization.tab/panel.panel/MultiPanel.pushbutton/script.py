from __future__ import division

# METADATA
################################################################################################################################


__title__ = "MultiPanel"

__doc__ = """ Version  1.1
Date  = 09.06.2023
___________________________________________________________________________
Description:

This tool will auto place reveals in a selected wall :

___________________________________________________________________________
How-to:

-> Click on the button
___________________________________________________________________________
last update:
- [09.06.2023] - 1.0 RELEASE

___________________________________________________________________________
To-Do:
-> Develop the abstract tool
___________________________________________________________________________
Author: Symon Kipkemei

"""

__author__ = "Symon Kipkemei"
__helpurl__ = "https://www.linkedin.com/in/symon-kipkemei/"

__highlight__ = 'new'

__min_revit_ver__ = 2020
__max_revit_ver__ = 2022

# IMPORTS
################################################################################################################################


# regular

import random

# Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType
# pyrevit


# custom ( Remember to include the csutom lib package to the pythonpath)

from _create import _annotations as an

# .NET imports ( I have no idea why I am importing this)
import clr

clr.AddReference("System")
from System.Collections.Generic import \
    List  # List<ElementType>() <-it's special type of list that RevitAPI often requires

# VARIABLES
################################################################################################################################


# instance variables from revitAPI


# __revit__  used to create an instance
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

# create
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


def place_reveal(host_wall_id, variable_distance):
    # get part, this is the hosted element containing the part
    wall = doc.GetElement(host_wall_id)
    # get symbol
    wallSweepType = WallSweepType.Reveal
    wallSweepTypeId = ElementId(352808)

    wallSweepInfo = WallSweepInfo(wallSweepType, True)
    wallSweepInfo.CutsWall = True
    wallSweepInfo.Distance = variable_distance
    wallSweepInfo.WallSide = WallSide.Exterior
    wallSweepInfo.DistanceMeasuredFrom = DistanceMeasuredFrom.Base
    wall_sweep = WallSweep.Create(wall, wallSweepTypeId, wallSweepInfo)

    return wall_sweep



def get_host_wall_id(part):
    """
    Returns the host wall id when a par element is selected

    :param part_element_id:
    :return:
    """

    linkedElementIdCollection = part.GetSourceElementIds()

    host_wall_id = linkedElementIdCollection[0].HostElementId  # pick first linkedelement in collection

    return host_wall_id


def get_part():
    # select part element
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    part = uidoc.Document.GetElement(reference)

    return part


def get_edge_index(part):
    """
    Abstract the distance between the left edge and reveal postioned at o
    :return: part_length and part_distance_origin
    """
    try:

        # abstract the length of the part
        part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

        half_part_length = part_length/2

        # place reveal
        host_wall_id = get_host_wall_id(part)
        variable_distance = 1

        with Transaction(doc, __title__) as t:
            t.Start()
            wall_sweep = place_reveal(host_wall_id, variable_distance)
            t.Commit()

        # get new_part_length
        new_part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

        #determine the panel size
        left_edge_index = 0
        right_edge_index = 0

        if new_part_length < half_part_length:
            # get distance between the left edge and wallSweepInfo.Distance at 0
            left_edge_index = (part_length - new_part_length) + variable_distance
            right_edge_index = left_edge_index - part_length

        elif new_part_length > half_part_length:
            left_edge_index = new_part_length + variable_distance
            right_edge_index = left_edge_index - part_length

        # delete reveal after abstracting the length
        with Transaction(doc, __title__) as t:
            t.Start()
            doc.Delete(wall_sweep.Id)
            t.Commit()

        return left_edge_index, right_edge_index

    except Exception as e:
        print ('The following error has occurred: {}'.format(e))

        return None




def get_reveal_indexes(left_edge, right_edge):
    # place reveal at correct position
    part_length = left_edge - right_edge
    panel_size = 3.927083 #3' 11 1/8"
    half_panel_size = 1.927083 #1' 11 1/8"

    no_complete_panels = int(part_length // panel_size)
    incomplete_panel_length = part_length % panel_size

    reveal_indexes = []

    if incomplete_panel_length == 0:
        for x in range(0, no_complete_panels):
            left_edge -= panel_size
            reveal_indexes.append(left_edge)

    elif incomplete_panel_length < 2:
        # If there is an incomplete panel half the panel before the last reveal
        for x in range(0, (no_complete_panels - 1)):
            left_edge -= panel_size
            reveal_indexes.append(left_edge)
        left_edge -= half_panel_size
        reveal_indexes.append(left_edge)

    elif incomplete_panel_length > 2:
        # If there is an incomplete panel half the panel before the last reveal
        for x in range(0, no_complete_panels):
            left_edge -= panel_size
            reveal_indexes.append(left_edge)

    else:
        print ("The incomplete panel length is unknown or faulty")

    # check if there is a remainder
    return reveal_indexes


def auto_panel(host_wall_id, reveal_indexes):
    # place new reveal
    try:
        with Transaction(doc, __title__) as t:
            t.Start()

            for reveal_index in reveal_indexes:
                wall_sweep = place_reveal(host_wall_id, reveal_index)

            t.Commit()
    except Exception as e:
        print ('The following error has occurred: {}'.format(e))


def main():
    part = get_part()
    host_wall_id = get_host_wall_id(part)
    left_edge_index, right_edge_index = get_edge_index(part)
    reveal_indexes = get_reveal_indexes(left_edge_index, right_edge_index)

    auto_panel(host_wall_id, reveal_indexes)


if __name__ == "__main__":
    # print(get_part_length(496067))
    main()
