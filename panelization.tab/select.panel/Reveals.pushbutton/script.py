# METADATA
__title__ = "FaceReveals"

__doc__ = """
Select all reveals on a part face
"""

__author__ = "Symon Kipkemei"
__helpurl__ = "https://www.linkedin.com/in/symon-kipkemei/"

__min_revit_ver__ = 2020
__max_revit_ver__ = 2025

# IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType

from _create import _parts as g
from _create import _auto as a
from _create import _errorhandler as eh

import clr

clr.AddReference("System")

from pyrevit import forms

# VARIABLES
app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# FUNCTIONS

def main():
    try:
        part = g.select_part()
        a.auto_parts(__title__, part, multiple=True)
    except eh.CannotPanelizeError:
        forms.alert('Select a Part to Panelize')
    except eh.CannotSplitPanelError:
        forms.alert("Centre Index could not be established")
    except eh.VariableDistanceNotFoundError:
        forms.alert("The variable distance could not be established")
    except Exception:
        pass

if __name__ == "__main__":
    main()
