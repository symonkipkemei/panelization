from __future__ import division

# METADATA

__title__ = "AutoPanel"

__doc__ = """
Auto select all parts and panelize
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
from _create import _checks as cc
from _create import  _errorhandler as eh
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
    selected_parts = g.select_all_parts()
    non_panelized_parts = cc.check_if_parts_panelized(selected_parts)
    parts = cc.check_if_host_wall_edited(non_panelized_parts)

    exterior_parts = []
    interior_parts = []

    # sorted parts, starting with exterior followed by interior
    for part in parts:
        host_wall_id = g.get_host_wall_id(part)
        host_wall_type_id = g.get_host_wall_type_id(host_wall_id)
        layer_index = g.get_layer_index(part)
        lap_type_id, side_of_wall, exterior = g.get_wallsweep_parameters(layer_index, host_wall_type_id)

        if exterior:
            exterior_parts.append(part)
        else:
            interior_parts.append(part)

    all_parts = exterior_parts + interior_parts
    print (parts)

    for part in all_parts:
        try:
            a.auto_parts(__title__, part)
        except eh.CannotPanelizeError:
            pass
        except eh.CannotSplitPanelError:
            pass
        except eh.VariableDistanceNotFoundError:
            pass
        except Exception:
            pass


if __name__ == "__main__":
    # print(get_part_length(496067))
    main()
