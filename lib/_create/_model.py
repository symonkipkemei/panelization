
# regular
import  random

# Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType
# pyrevit


# custom ( Remember to include the csutom lib package to the pythonpath)

from _create import _model as m

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

def place_reveal(__title__, host_wall_id,variable_distance):

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

    with Transaction(doc, __title__) as t:
        t.Start()
        wall_sweep = WallSweep.Create(wall, wallSweepTypeId, wallSweepInfo)
        t.Commit()

    return wall_sweep

def adjust_wall_sweep_length(__title__, wall_sweep):

    # get existing length of the wall parameter
    length_param = wall_sweep.get_Parameter(BuiltInParameter.CURVE_ELEM_LENGTH)
    print (length_param)
    current_length = length_param.AsDouble()

    # adjust length by an 1 inch to cut the panel completely
    new_length = current_length + 0.08

    with Transaction(doc, __title__) as t:
        t.Start()
        length_param.Set(new_length)
        t.Commit()


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

