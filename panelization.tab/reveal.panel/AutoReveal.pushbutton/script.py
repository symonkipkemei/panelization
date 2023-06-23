

# METADATA
################################################################################################################################


__title__ = "AutoReveal"

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



def main():
    # select part element
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    part = uidoc.Document.GetElement(reference)
    #get host id from
    host_wall_id = m.get_host_wall_id(part)
    variable_distance = 3

    try:
        with Transaction(doc, __title__) as t:
            t.Start()

            m.place_reveal(host_wall_id, variable_distance)

            t.Commit()
    except Exception as e:
        print ('The following error has occurred: {}'.format(e))
        print (Exception)

if __name__ == "__main__":
    main()