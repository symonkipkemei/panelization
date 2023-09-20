from __future__ import division

# METADATA

__title__ = "MultiParts"

__doc__ = """
Select Multiple/Single Part(s) and panelize
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

from _create import _transactions as a
from _create import _parts as p
from _create import _errorhandler as eh
from _create import _forms as f
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
    parts = p.select_parts()
    switch_option = f.form_switch_panelization_direction()
    displacement_distance = f.form_displacement_distance()
    for part in parts:
        try:
            a.auto_parts(__title__, part, displacement_distance, switch_option, multiple=True)
        except eh.RevealNotCreatedError:
            forms.alert('Reveal at coordinate 0 could not be created')
        except eh.CentreIndexError:
            forms.alert("Centre Index could not be established")
        except eh.VariableDistanceNotFoundError:
            forms.alert("The variable distance could not be established")
        except eh.DeleteElementsError:
            forms.alert('Error occurred. Could not delete reveals')
        except eh.XYAxisPlaneNotEstablishedError:
            forms.alert('Could not Panelize. Selected Part not on X or Y axis')
        except Exception:
            pass


if __name__ == "__main__":
    main()
