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



def main():
    pass

    # test environment

if __name__ == "__main__":
    # print(get_part_length(496067))
    main()
