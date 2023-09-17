# METADATA
################################################################################################################################

__title__ = "SplitPart"
__doc__ = """ 
Select a single part and split into two equal Parts
"""
__author__ = "Symon Kipkemei"
__helpurl__ = "https://www.linkedin.com/in/symon-kipkemei/"
__min_revit_ver__ = 2020
__max_revit_ver__ = 2025


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from _create import _transactions as t
from _create import _parts as p
from _create import _errorhandler as eh
import clr
clr.AddReference("System")
from pyrevit import forms

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> FUNCTIONS

def main():
    """Auto split tool"""
    try:
        part = p.select_part()
        host_wall_id = p.get_host_wall_id(part)
        host_wall_type_id = p.get_host_wall_type_id(host_wall_id)
        layer_index = p.get_layer_index(part)
        lap_type_id, side_of_wall, exterior = p.get_wall_sweep_parameters(layer_index, host_wall_type_id)

        reveal_plane_coordinate_0 = t.get_reveal_coordinate_at_0(__title__, part)
        distance = p.get_part_centre_index(part, reveal_plane_coordinate_0)

        t.auto_place_reveal(__title__, host_wall_id, lap_type_id, distance, side_of_wall)

    except eh.VariableDistanceNotFoundError:
        forms.alert("The variable distance could not be established")

    except Exception:
        forms.alert("Error occurred.Could not panelize")


if __name__ == "__main__":
    main()
