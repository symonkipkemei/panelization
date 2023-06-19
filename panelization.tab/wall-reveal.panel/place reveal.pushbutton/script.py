

# METADATA
################################################################################################################################


__title__ = "Place Reveal"

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
import  random

# Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import  StructuralType
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



def place_reveal(host_wall_id,variable_distance):

    # create a new  wall sweep
    tmp = """
    public static WallSweep Create(
	Wall wall,
	ElementId wallSweepType,
	WallSweepInfo wallSweepInfo
    )
    """

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




#  EXPLORE THE NORMAL PATH OF MOVING REVEAL AFTER PLACEMENT

def get_length(element_id):
    """
    Returns the length of the part and wall elements when a part is selected
    :param element_id: The id of the part element selected
    :return: the (part_length, wall_length)
    """

    element = ElementId(element_id)

    #get part length
    part = doc.GetElement(element)
    part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

    #get hosted wall length
    tmp = """public ICollection<LinkElementId> GetSourceElementIds()"""
    linkedElementIdCollection = part.GetSourceElementIds()

    host_wall_id = linkedElementIdCollection[0].HostElementId #pick first linkedelement in collection
    host_wall = doc.GetElement(host_wall_id)
    host_wall_length = host_wall.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH).AsDouble()

    return (part_length, host_wall_length)

def get_host_wall_id(part):
    """
    Returns the host wall id when a par element is selected

    :param part_element_id:
    :return:
    """

    tmp = """public ICollection<LinkElementId> GetSourceElementIds()"""
    linkedElementIdCollection = part.GetSourceElementIds()

    host_wall_id = linkedElementIdCollection[0].HostElementId  # pick first linkedelement in collection

    return  host_wall_id



def get_endpoints(part_element_id):
    part = doc.GetElement(ElementId(part_element_id))

    #get element face
    face = part.Faces

    return face



def first_reveal_position():
    pass
    # select a wall by picking

    # host element ( wall_id)
    # abstract length of the wall
    # subtract length of wall by 3 11 1/8 "
    # get position of the first reveal
#

def main():
    # select part element
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    part = uidoc.Document.GetElement(reference)

    # abstract the length of the part
    part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

    # place reveal
    host_wall_id = get_host_wall_id(part)
    variable_distance = 3
    try:
        with Transaction(doc, __title__) as t:
            t.Start()

            wall_sweep = place_reveal(host_wall_id, variable_distance)

            t.Commit()
    except Exception as e:
        print ('The following error has occurred: {}'.format(e))

    # get new_part_length
    new_part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()

    # get distance between the left edge and wallSweepInfo.Distance at 0
    part_distance_origin = (part_length - new_part_length) + variable_distance

    # delete the reveal


    try:
        with Transaction(doc, __title__) as t:
            t.Start()

            doc.Delete(wall_sweep.Id)

            t.Commit()
    except Exception as e:
        print ('The following error has occurred: {}'.format(e))

    # place reveal at correct position
    panel_size = 3.927083
    new_reveal_distance = part_distance_origin - panel_size

    # place new reveal
    try:
        with Transaction(doc, __title__) as t:
            t.Start()

            wall_sweep = place_reveal(host_wall_id, new_reveal_distance)

            t.Commit()
    except Exception as e:
        print ('The following error has occurred: {}'.format(e))



if __name__ == "__main__":
    #print(get_part_length(496067))
    main()




