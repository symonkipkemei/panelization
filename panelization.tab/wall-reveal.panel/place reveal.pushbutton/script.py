

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



def place_reveal():

    # create a new  wall sweep
    tmp = """
    public static WallSweep Create(
	Wall wall,
	ElementId wallSweepType,
	WallSweepInfo wallSweepInfo
    )
    """

    # get part
    part = doc.GetElement(ElementId(478665))
    print(part)

    # get symbol
    wallSweepType = WallSweepType.Reveal
    wallSweepTypeId = ElementId(352808)

    wallSweepInfo = WallSweepInfo(wallSweepType, True)
    wallSweepInfo.CutsWall = True
    wallSweepInfo.Distance = 3


    wall_sweep = WallSweep.Create(part, wallSweepTypeId, wallSweepInfo)
    info = wall_sweep.GetWallSweepInfo()
    print (info.WallOffset)




def copy_element(element_id):


    tmp = """
    public static ICollection<ElementId> CopyElement(
	Document document,
	ElementId elementToCopy,
	XYZ translation
    )
    """

    ElementTransformUtils.CopyElement(doc)



if __name__ == "__main__":
    try:
        with Transaction(doc, __title__) as t:
            t.Start()

            # place function here
            place_reveal()

            t.Commit()
    except Exception as e:
        print ('The following error has occurred: {}'.format(e))



