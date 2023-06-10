#! python3

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

from tabulate import tabulate
# Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector

# pyrevit


# custom ( Remember to include the csutom lib package to the pythonpath)


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



# custom variable



# FUNCTION AND CLASSES
################################################################################################################################

Transaction(doc).Start()

# creating elements

# method 1 - go into that class you would like to create (revitapi)
# i.e creating a text note

position = XYZ(0, 0, 0)
text = "Hello symon kipkemei"
text_typeId = FilteredElementCollector(doc).OfClass(TextNoteType).FirstElementId()
TextNote.Create(doc, active_view.Id, position, text, text_typeId)

# Transaction guards any changes made to the revit Model
Transaction(doc).Commit()

# create a wall from a set  of points
