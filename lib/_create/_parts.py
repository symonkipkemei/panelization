from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
from Autodesk.Revit.DB import Transaction, Element, ElementId, FilteredElementCollector
from Autodesk.Revit.DB.Structure import StructuralType
from Autodesk.Revit.UI.Selection import ObjectType

import clr

clr.AddReference("System")

from _create import _transactions as a
from _create import _test as tt
from _create import _coordinate as c
from _create import _openings as o
from _create import _errorhandler as eh

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VARIABLES

app = __revit__.Application  # represents the Revit Autodesk Application
doc = __revit__.ActiveUIDocument.Document  # obj used to create new instances of elements within the active project
uidoc = __revit__.ActiveUIDocument  # obj that represent the current active project

rvt_year = int(app.VersionNumber)

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> VIEWS
active_view = doc.ActiveView
active_level = doc.ActiveView.GenLevel


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SELECT FUNCTIONS

def select_all_parts():
    """
    Selects all parts in a active project
    :return: A collection of all parts
    """
    all_parts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Parts). \
        WhereElementIsNotElementType().ToElements()

    return all_parts


def select_part():
    """Selects a part from the active project
    :return: returns the Part object
    """
    # select part element
    reference = uidoc.Selection.PickObject(ObjectType.Element)
    part = uidoc.Document.GetElement(reference)

    return part


def select_parts():
    """Selects multiple/single part from the active project
    :return: returns a collection of parts
    """
    # select part element
    references = uidoc.Selection.PickObjects(ObjectType.Element)

    parts = []
    for reference in references:
        part = uidoc.Document.GetElement(reference)
        parts.append(part)

    return parts


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET ELEMENT ID FUNCTIONS


def get_host_wall_id(part):
    """
    Retrieves the host wall id, when a Part is selected
    :param part: selected part
    :return: host_wall_id
    """
    linkedElementIdCollection = part.GetSourceElementIds()
    host_wall_id = linkedElementIdCollection[0].HostElementId  # pick first linked element in collection

    return host_wall_id


def get_host_wall_type_id(host_wall_id):
    """
    Abstract the type of the wall i.e BamCore 9 3/4" Seperate I-E
    :param host_wall_id: host wall id
    :return: host wall type id
    """
    host_wall = doc.GetElement(host_wall_id)
    type_id = host_wall.GetTypeId()

    return type_id


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET PARAMETERS FUNCTIONS


def get_layer_index(part):
    """
    Abstract the layer index of a part if
    layer Index 1- Exterior face
    layer Index 2 - internal partition walls ( only applies for Bamcore Int Wall Type)
    layer Index 3- Interior face

    :param part: Part to be abstracted
    :return: The layer index
    """
    # abstract the layer index of part
    layer_index = int(part.get_Parameter(BuiltInParameter.DPART_LAYER_INDEX).AsString())
    return layer_index


def get_wall_sweep_parameters(layer_index, host_wall_type_id):
    """Abstract parameters based on the layer index of the part"""

    left_lap_id = ElementId(352818)
    right_lap_id = ElementId(352808)

    # default setting for exterior
    side_of_wall = WallSide.Exterior
    lap_type_id = right_lap_id
    exterior = True

    # collection of walls with interior and exterior parts
    I_E_wall_types = [ElementId(384173), ElementId(391917), ElementId(391949), ElementId(391949), ElementId(391971)]

    # collection of walls with interior parts
    I_wall_types = [ElementId(400084)]

    # if wall types have both  the interior and exterior parts
    if host_wall_type_id not in I_wall_types:
        if layer_index == 1:  # exterior face
            side_of_wall = WallSide.Exterior
            lap_type_id = right_lap_id
            exterior = True

        elif layer_index == 3:  # interior face
            side_of_wall = WallSide.Interior
            lap_type_id = left_lap_id
            exterior = False
        else:
            exterior = None

    # if wall types has interior part only
    elif host_wall_type_id in I_wall_types:
        if layer_index == 2:  # interior face of partition walls, ignore layer-index 1 (the core)
            side_of_wall = WallSide.Interior
            lap_type_id = left_lap_id
            exterior = False

    return lap_type_id, side_of_wall, exterior


def create_reveal(host_wall_id, lap_type_id, variable_distance, side_of_wall):
    """ Creates a wall sweep
    :param lap_type_id:Element id of the wall sweep type used
    :param host_wall_id:host wall id
    :param variable_distance: distance along the wall's path curve
    :param side_of_wall: side of the wall to which the reveal is attached.
    :return:  A wall sweep
    """

    # Get host wall
    wall = doc.GetElement(host_wall_id)

    # Get Wall Sweep type
    wallSweepTypeId = lap_type_id

    # Get wall sweep info
    wallSweepType = WallSweepType.Reveal
    wallSweepInfo = WallSweepInfo(wallSweepType, True)
    wallSweepInfo.CutsWall = True
    wallSweepInfo.IsCutByInserts = True
    wallSweepInfo.Distance = variable_distance
    wallSweepInfo.WallSide = side_of_wall
    wallSweepInfo.DistanceMeasuredFrom = DistanceMeasuredFrom.Base

    # create a wall sweep
    wall_sweep = WallSweep.Create(wall, wallSweepTypeId, wallSweepInfo)

    return wall_sweep


def get_part_length(part):
    """
    Abstract the length of selected part
    :return: length
    """
    part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
    return part_length


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET INDEX FUNCTIONS

def get_part_centre_index(part, reveal_plane_coordinate_0):
    """
    Determine the centre index of the panel
    :param part: Part to be panelized
    :param reveal_plane_coordinate_0: coordinates of reveal at 0
    :
    :return: part centre index
    """
    # project parameters
    host_wall_id = get_host_wall_id(part)
    x_axis_plane = c.determine_x_plane(host_wall_id)

    # determine the coordinates of the centre of the part
    part_centre_xyz_coordinates = c.get_bounding_box_center(part)
    part_centre_coordinate = float(c.get_plane_coordinate(part_centre_xyz_coordinates, x_axis_plane))

    # determine the difference between two to abstract the centre-index
    if reveal_plane_coordinate_0 > part_centre_coordinate:
        centre_index = (reveal_plane_coordinate_0 - part_centre_coordinate)
    else:
        centre_index = (part_centre_coordinate - reveal_plane_coordinate_0)

    return centre_index


def get_part_edge_index(part_length, part_centre_index):
    """
    Determine the left or the right edge
    :param part_length: Length of part
    :param part_centre_index: Index of part centre
    :return: left_edge, right_edge
    """
    half_length = part_length / 2
    edge_1 = part_centre_index + half_length
    edge_2 = part_centre_index - half_length

    edges = sorted([edge_1, edge_2])

    right_edge = edges[0]  # the smallest value becomes the right-edge,
    # the distance 0 begins at the right end of the wall's path curve
    left_edge = edges[1]  # the largest value becomes the left edge

    return left_edge, right_edge


def get_reveal_indexes(left_edge, right_edge, out_ranges, exterior=True):
    """
    Retrieve the reveal indexes, taking into consideration the openings out-ranges
    :param out_ranges: The ranges where the reveals should not be positioned closed to fenestration edges
    :param left_edge: The left edge of the part ( from exterior)
    :param right_edge: The right edge of the part ( from exterior)
    :param exterior: if exterior face, the panel position starts from left to right,
     if not the panel position starts from right to left
    :return: collection of indexes of the reveal position
    """

    # The panelling distance (3' 11 1/8" Distance required to generate a panel of 4')
    panelling_distance = 3.927083

    if rvt_year >= 2023:  # template provided uses reveal width 15/16"
        panelling_distance = 3.927083 - 0.005208  # 3' 11 1/8" - 1/16"
    elif rvt_year <= 2022:  # template provided uses reveal width 7/8"
        panelling_distance = 3.927083  # 3' 11 1/8"

    # offset reveal width from edge to allow cutting of first panel at 4'
    if rvt_year <= 2022:  # template provided uses reveal width 7/8"
        reveal_width = 0.072917
        right_edge = right_edge + reveal_width
    elif rvt_year >= 2023:  # template provided uses reveal width 15/16"
        reveal_width = 0.039063
        right_edge = right_edge + reveal_width
        left_edge = left_edge - reveal_width

    # minimum panel when panelizing
    minimum_panel = 2

    # store all reveal indexes
    reveal_indexes = []

    # determine reveals required to panelize part
    while True:
        reveal_edge_width = 0.078125  # subtracted 15/16"from panel to allow it cut at 2'
        if exterior:  # panelization is left to right, the left edge reduces towards the right edge
            left_edge -= panelling_distance
            # skipping the out range if there is a window
            left_edge = o.check_out_range(left_edge, out_ranges, exterior=True)

            # the new left edge appended to the list
            reveal_indexes.append(left_edge)

            # remaining length established,this will determine when panelization is complete ( < 4 script breaks)
            rem_length = left_edge - (right_edge - reveal_edge_width)

            if rem_length < 4.0000:
                if rem_length < minimum_panel:
                    # remove the last record on list to allow for further splitting
                    del reveal_indexes[-1]
                    # the new left edge becomes the last item on list after deleting the last reveal
                    if len(reveal_indexes) != 0:
                        left_edge = reveal_indexes[-1]

                    # the part left behind is determined
                    part_left_behind = left_edge - right_edge
                    # determine the remainder left edge position
                    # what remains after setting aside minimum panel
                    rem = part_left_behind - (minimum_panel - reveal_edge_width)
                    # position the new left edge
                    left_edge -= rem
                    reveal_indexes.append(left_edge)
                    # the script now ends
                    break
                else:
                    # the script now ends
                    break
        else:
            right_edge += panelling_distance  # panelization is right to left, the right edge increases towards the left edge
            # skipping the out range if there is a window
            right_edge = o.check_out_range(right_edge, out_ranges, exterior=False)

            reveal_indexes.append(right_edge)

            # reveal edge width subtracted from the right edge , to factor a 4' panel
            rem_length = left_edge - (right_edge - reveal_edge_width)

            if rem_length < 4.0000:
                if rem_length < minimum_panel:
                    # remove the last record on list to allow for further splitting
                    del reveal_indexes[-1]
                    if len(reveal_indexes) != 0:
                        right_edge = reveal_indexes[-1]  # the right edge becomes the last item on list
                    part_left_behind = left_edge - right_edge
                    rem = part_left_behind - (minimum_panel - reveal_edge_width)
                    right_edge += rem
                    reveal_indexes.append(right_edge)
                    break
                else:
                    break

    return reveal_indexes


def get_single_panel_reveal_indexes(left_edge, right_edge, exterior=True):
    """Determine the position of a reveal index for a single panel
    :param exterior: if part exterior or not
    :param left_edge:left edge reveal index
    :param right_edge:right edge reveal index
    :return: reveal index position to form a panel
    """
    panel_size = 3.927083
    reveal_indexes = []
    if exterior:
        new_reveal_distance = left_edge - panel_size
        reveal_indexes.append(new_reveal_distance)

    else:
        new_reveal_distance = right_edge + panel_size
        reveal_indexes.append(new_reveal_distance)

    return reveal_indexes


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SORT FUNCTIONS

def sort_parts_by_side(parts):
    """
    Sorts parts based on the side of wall
    :param parts: Collection of parts
    :return: collection of exterior parts, interior parts
    """
    exterior_parts = []
    interior_parts = []
    core_parts = []

    # sorted parts, starting with exterior followed by interior
    for part in parts:
        host_wall_id = get_host_wall_id(part)
        host_wall_type_id = get_host_wall_type_id(host_wall_id)
        layer_index = get_layer_index(part)
        lap_type_id, side_of_wall, exterior = get_wall_sweep_parameters(layer_index, host_wall_type_id)

        if exterior == True:
            exterior_parts.append(part)
        elif exterior == False:
            interior_parts.append(part)
        elif exterior == None:
            core_parts.append(part)

    return exterior_parts, interior_parts


def sort_parts_by_length(parts):
    """
    sort parts based on it's length
    :param parts: Collection of parts
    :return: collections of underpanelized, panalized and unpanalized parts
    """
    underpanelized = []
    panalized = []
    unpanalized = []

    minimum_panel = 2.0

    for part in parts:
        part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
        part_length = round(part_length, 2)
        if part_length > 4.0:
            unpanalized.append(part)
        elif part_length < minimum_panel:
            underpanelized.append(part)
        else:
            panalized.append(part)

    return underpanelized, panalized, unpanalized


def sort_parts_by_orthogonal(parts):
    """
    filters out non-orthogonal parts
    :param parts: Parts to be panelized
    :return: orthogonal parts
    """
    orthogonal_parts = []
    non_orthogonal_parts = []
    for part in parts:
        host_wall_id = p.get_host_wall_id(part)
        host_wall = doc.GetElement(host_wall_id)
        sketch = host_wall.SketchId  # if sketchId is not -1, then the wall has been edited

        if sketch == ElementId(-1):
            orthogonal_parts.append(part)
        else:
            non_orthogonal_parts.append(part)
    return orthogonal_parts


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SWITCH FUNCTIONS

def switch_directions(exterior, switch_direction=False):
    """
    Switch direction of panelization from left to right and vice versa
    :param exterior: Bool that determines if part is exterior or not
    :param switch_direction:  Bool if true switches the exterior bool
    :return: exterior bool
    """
    if switch_direction:
        if exterior == True:
            exterior = False
        else:
            exterior = True
    else:
        exterior = exterior

    return exterior


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> HIGHLIGHT FUNCTIONS

def highlight_unpanelized_underpanelized_parts(__title__):
    """Color code unpanelized parts and underpanleized parts for ease of identification
    :param __title__:
    :return: graphics_settings_unpanelized, graphics_settings_underpanelized
    """

    # select all parts
    parts = select_all_parts()
    exterior_parts, interior_parts = sort_parts_by_side(parts)
    filtered_parts = exterior_parts + interior_parts
    underpanalized, panelized, unpanelized = sort_parts_by_length(filtered_parts)

    solid_fill_id = ElementId(20)

    # color codes - unpanelized
    graphics_settings_unpanelized = OverrideGraphicSettings()
    graphics_settings_unpanelized.SetSurfaceForegroundPatternId(solid_fill_id)
    clr_bytes_a = [255, 99, 71]
    color_unpanelized_a = Color(clr_bytes_a[0], clr_bytes_a[1], clr_bytes_a[2])
    graphics_settings_unpanelized.SetSurfaceForegroundPatternColor(color_unpanelized_a)

    # color codes - underpanelized
    graphics_settings_underpanelized = OverrideGraphicSettings()
    graphics_settings_underpanelized.SetSurfaceForegroundPatternId(solid_fill_id)
    clr_bytes_b = [251, 191, 0]
    color_underpanelized_b = Color(clr_bytes_b[0], clr_bytes_b[1], clr_bytes_b[2])
    graphics_settings_underpanelized.SetSurfaceForegroundPatternColor(color_underpanelized_b)

    with Transaction(doc, __title__) as t:
        t.Start()
        if len(unpanelized) != 0:
            for part in unpanelized:
                active_view.SetElementOverrides(part.Id, graphics_settings_unpanelized)
        if len(underpanalized) != 0:
            for part in underpanalized:
                active_view.SetElementOverrides(part.Id, graphics_settings_underpanelized)

        t.Commit()

    return graphics_settings_unpanelized, graphics_settings_underpanelized
