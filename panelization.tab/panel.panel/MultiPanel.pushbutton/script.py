from __future__ import division

# METADATA

__title__ = "MultiPanel"

__doc__ = """
Select Multiple/Single Parts and panelize
"""
__author__ = "Symon Kipkemei"
__helpurl__ = "https://www.linkedin.com/in/symon-kipkemei/"

__min_revit_ver__ = 2020
__max_revit_ver__ = 2025

# IMPORTS
################################################################################################################################

from Autodesk.Revit.DB import *
import clr

clr.AddReference("System")

from _create import _auto as a
from _create import _parts as g
from _create import _errorhandler as eh

from pyrevit import forms

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
    parts = g.select_parts()
    for part in parts:
        try:
            a.auto_parts(__title__, part, multiple=True)
        except eh.CannotPanelizeError:
            forms.alert('Select a Part to Panelize')
        except eh.CannotSplitPanelError:
            forms.alert("Centre Index could not be established")
        except eh.VariableDistanceNotFoundError:
            forms.alert("The variable distance could not be established")

if __name__ == "__main__":
    main()
