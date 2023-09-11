from __future__ import division

# METADATA

__title__ = "AutoParts"

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
from _create import  _forms as f
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

    exterior_parts, interior_parts = g.sort_parts_by_side(selected_parts)
    all_parts = exterior_parts + interior_parts
    #all_parts = cc.check_if_host_wall_edited(all_parts)
    underpanelized, panalized, non_panelized_parts = g.sort_parts_by_length(all_parts)
    switch_option = f.switch_option()
    displacement_distance = f.displacement_distance_form()
    for part in non_panelized_parts:
        try:
            a.auto_parts(__title__, part, displacement_distance, switch_option, multiple=True)
        except Exception:
            pass

    g.highlight_unpanelized_underpanelized_parts(__title__)


if __name__ == "__main__":
    # print(get_part_length(496067))
    main()
