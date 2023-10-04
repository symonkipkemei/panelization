import clr
import System

clr.AddReferenceByName("RevitAPI.dll");
clr.AddReferenceByName("RevitAPIUI.dll");

from Autodesk.Revit import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.UI.Macros import *
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from System.Collections.Generic import *
from System.Collections import *
from System import *
from math import *


class ThisApplication(ApplicationEntryPoint):
    # region Revit Macros generated code
    def FinishInitialization(self):
        ApplicationEntryPoint.FinishInitialization(self)
        self.InternalStartup()

    def OnShutdown(self):
        self.InternalShutdown()
        ApplicationEntryPoint.OnShutdown(self)

    def InternalStartup(self):
        self.Startup()

    def InternalShutdown(self):
        self.Shutdown()

    # endregion

    def Startup(self):
        self

    def Shutdown(self):
        self

    # TAKE OFF MODULE
    """ This module contains functions that relates to take off of panelized and unpanelized parts"""

    ####################################################################################################################
    ####################################################################################################################

    def get_unpanelized_parts(self, doc):
        """
        Select all parts and filter to unpanelized  exterior and interior parts
        :param doc: Active Revit Document
        :return: List of unpanelized parts
        """

        # filter interior and exterior parts, exclude core parts
        parts = self.select_all_parts(doc)
        exterior_parts, interior_parts = self.sort_parts_by_side(doc, parts)

        # filter into parts that have not been panelized
        underpanelized_ep, panalized_ep, unpanelized_exterior_parts = self.sort_parts_by_length(exterior_parts)
        underpanelized_ip, panalized_ip, unpanelized_interior_parts = self.sort_parts_by_length(interior_parts)

        # combine exterior and interior unpanelized parts
        unpanelized_parts = unpanelized_exterior_parts + unpanelized_interior_parts

        return unpanelized_parts

    def get_unpanalized_parts_data(self, unpanelized_parts):
        """
        Abstract unpanelized parts data
        :param unpanelized_parts: List of unpanelized parts
        :return: Nested list of unpanelized part data
        """
        parts_data = []
        count = 0

        for part in unpanelized_parts:
            count += 1
            part_id = part.Id
            height = part.get_Parameter(BuiltInParameter.DPART_HEIGHT_COMPUTED).AsValueString()
            length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsValueString()
            base_level = part.get_Parameter(BuiltInParameter.DPART_BASE_LEVEL).AsDouble()

            data = [count, part_id, height, length, base_level]
            parts_data.append(data)

        return parts_data

    def get_panelized_parts_data(self, filtered_parts):
        """
        Abstract panelized parts data
        :param filtered_parts: List of panelized parts
        :return: A dictionary collection of panelized parts data
        """

        parts_data = {}
        for part in filtered_parts:
            # abstract length, height and index from model
            parts_id = part.Id

            height = part.get_Parameter(BuiltInParameter.DPART_HEIGHT_COMPUTED).AsValueString()
            length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsValueString()
            thickness = part.get_Parameter(BuiltInParameter.DPART_LAYER_WIDTH).AsDouble()
            volume = part.get_Parameter(BuiltInParameter.DPART_VOLUME_COMPUTED).AsDouble()
            base_level = part.get_Parameter(BuiltInParameter.DPART_BASE_LEVEL).AsDouble()
            area = part.get_Parameter(BuiltInParameter.DPART_AREA_COMPUTED).AsDouble()

            part_type = height + " x " + length
            parts_data[parts_id] = [part_type, height, length, thickness, volume, base_level, area]

        return parts_data

    def get_panelized_parts_type_data(self, parts_data):
        """Aggregate panelized parts data of similar length and height
        :param parts_data:
        :return: A dictionary of aggregated parts type and their count
        """
        data = {}
        for part_data in parts_data.values():
            default_part_type = part_data[0]
            count = 0
            for part in parts_data.values():
                part_type = part[0]

                if default_part_type == part_type:
                    count += 1

            data[default_part_type] = count

        return data

    def get_panelized_parts_summary_data(self, parts_data, parts_type_data, cost_per_sf):
        """
        Sum up parts data into total panels, area and cost
        :param parts_data: List of Parts data
        :param parts_type_data: a dictionary of parts type data
        :param cost_per_sf: cost
        :return: Summary of all parts and their sum
        """

        final_data = []
        sum_panels = 0
        sum_area = 0
        sum_cost = 0

        for part_type, count in parts_type_data.items():
            for part in parts_data.values():
                if part_type == part[0]:
                    total_area = count * part[6]
                    total_cost = total_area * cost_per_sf
                    combine_data = part[1:] + [count] + [total_area] + [cost_per_sf] + [total_cost]
                    final_data.append(combine_data)

                    sum_panels += count
                    sum_area += total_area
                    sum_cost += total_cost

                    break

        # add last line as sum total of parts data

        sum_total = ["-", "-", "-", "-", "-", "-", sum_panels, sum_area, "-", sum_cost]
        final_data.append(sum_total)

        return final_data

    # REVEALS MODULE
    """ This module contains functions that will allow you to auto select all reveals and create reveal in a project"""

    ####################################################################################################################
    ####################################################################################################################

    def create_reveal(self, doc, host_wall_id, lap_type_id, variable_distance, side_of_wall):
        """ Creates a wall sweep
        :param doc: Active Revit Document
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

    class RevealSelectionFilter(ISelectionFilter):
        """
        A class to filter selections to reveals only during selecting. Makes it easier to select reveals.
        """

        def AllowElement(self, element):
            if element.Category.Name == "Reveals":
                return True
            return False

        def AllowReference(self, refer, point):
            return False

    def select_reveal(self, uidoc):
        """
        Selects a single  reveal
        :return:A reveal
        """
        reveal_filter = self.RevealSelectionFilter()
        reference = uidoc.Selection.PickObject(ObjectType.Element, reveal_filter)
        reveal = uidoc.Document.GetElement(reference)
        if str(type(reveal)) == "<type 'WallSweep'>":
            return reveal
        else:
            raise self.RevealNotSelectedError

    def get_wall_side(self, reveal):
        """
        Determine the wall side hosting the reveal
        :param reveal: reveal
        :return: wall side
        """
        wall_sweep_info = reveal.GetWallSweepInfo()
        wall_side = wall_sweep_info.WallSide
        return wall_side

    def get_reveal_host_wall_id(self, reveal):
        """
        Abstract the host wall id of a  selected reveal
        :param reveal: Reveal
        :return: host wall Element Id
        """
        host_ids = reveal.GetHostIds()
        host_id = host_ids[0]

        return host_id

    def select_all_reveals(self, doc):
        """
        Select all reveals in a project
        :return: Collection of all reveals
        """
        all_reveals = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Reveals). \
            WhereElementIsNotElementType().ToElements()

        return all_reveals

    def get_filtered_reveals(self, reference_host_id, reference_wall_side, all_reveals):
        """
        Selects all reveals and Filter reveals based on the host wall and the wall side
        :param reference_host_id: Host id of selected reveal
        :param reference_wall_side: Wall side of selected reveal
        :param all_reveals: All reveals in an active document
        :return: A collection of filtered reveals
        """
        filtered_reveals = []
        for reveal in all_reveals:
            wall_side = self.get_wall_side(reveal)
            host_id = self.get_reveal_host_wall_id(reveal)

            if wall_side == reference_wall_side and host_id == reference_host_id:
                filtered_reveals.append(reveal.Id)

        return filtered_reveals

    def display_selected_reveals(self, uidoc, filtered_reveals):
        """
        Display filtered reveals to the user on the Revit UI
        :param uidoc:
        :param filtered_reveals:
        :return:
        """
        uidoc.Selection.SetElementIds(filtered_reveals)

    # PARTS MODULE
    """This module contains all functions that handles parts and their data"""

    ####################################################################################################################
    ####################################################################################################################

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SELECT FUNCTIONS
    def select_all_parts(self, doc):
        """
        Selects all parts in a active project
        :return: A collection of all parts
        """
        all_parts = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Parts). \
            WhereElementIsNotElementType().ToElements()

        return all_parts

    def select_part(self, uidoc):
        """Selects a part from the active project
        :return: returns the Part object
        """
        # select part element
        reference = uidoc.Selection.PickObject(ObjectType.Element)
        part = uidoc.Document.GetElement(reference)

        return part

    def select_parts(self, uidoc):
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

    def get_host_wall_id(self, part):
        """
        Retrieves the host wall id, when a Part is selected
        :param part: selected part
        :return: host_wall_id
        """
        linkedElementIdCollection = part.GetSourceElementIds()
        host_wall_id = linkedElementIdCollection[0].HostElementId  # pick first linked element in collection

        return host_wall_id

    def get_host_wall_type_id(self, doc, host_wall_id):
        """
        Abstract the type of the wall i.e BamCore 9 3/4" Seperate I-E
        :param doc: Active Revit Document
        :param host_wall_id: host wall id
        :return: host wall type id
        """
        host_wall = doc.GetElement(host_wall_id)
        type_id = host_wall.GetTypeId()

        return type_id

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET PARAMETERS FUNCTIONS

    def get_layer_index(self, part):
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

    def get_wall_sweep_parameters(self, layer_index, host_wall_type_id):
        """
        Abstract wall sweep parameters based on the layer index of the par
        :param layer_index: Index representing the wall side
        :param host_wall_type_id: Element Id for the host wall type
        :return: lap_type_id, side_of_wall, exterior
        """

        left_lap_id = ElementId(352818)
        right_lap_id = ElementId(352808)

        # Settings defaults to  exterior
        side_of_wall = WallSide.Exterior
        lap_type_id = right_lap_id
        exterior = True

        # collection of walls with interior and exterior parts
        # I_E_wall_types = [ElementId(384173), ElementId(391917), ElementId(391949), ElementId(391949),

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

    def get_part_length(self, part):
        """
        Abstract the length of selected part
        :param part: Part element
        :return: part length
        """
        part_length = part.get_Parameter(BuiltInParameter.DPART_LENGTH_COMPUTED).AsDouble()
        return part_length

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET INDEX FUNCTIONS

    def get_part_centre_index(self, doc, part, reveal_plane_coordinate_0):
        """
        Determine the centre index of the panel
        :param doc:
        :param part: Part to be panelized
        :param reveal_plane_coordinate_0: coordinates of reveal at 0
        :return: part centre index
        """
        # project parameters
        host_wall_id = self.get_host_wall_id(part)
        x_axis_plane = self.determine_x_plane(doc, host_wall_id)

        # determine the coordinates of the centre of the part
        part_centre_xyz_coordinates = self.get_bounding_box_center(doc, part)
        part_centre_coordinate = float(self.get_plane_coordinate(part_centre_xyz_coordinates, x_axis_plane))

        # determine the difference between two to abstract the centre-index
        if reveal_plane_coordinate_0 > part_centre_coordinate:
            centre_index = (reveal_plane_coordinate_0 - part_centre_coordinate)
        else:
            centre_index = (part_centre_coordinate - reveal_plane_coordinate_0)

        return centre_index

    def get_part_edge_index(self, part_length, part_centre_index):
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

    def get_reveal_indexes(self, left_edge, right_edge, out_ranges, minimum_panel_size, exterior=True):
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

        # template provided uses reveal width 15/16"
        panelling_distance = 3.927083 - 0.005208  # 3' 11 1/8" - 1/16"

        # offset reveal width from edge to allow cutting of first panel at 4'
        # template provided uses reveal width 15/16"
        reveal_width = 0.039063
        right_edge = right_edge + reveal_width
        left_edge = left_edge - reveal_width

        # minimum panel when panelizing
        minimum_panel = minimum_panel_size

        # store all reveal indexes
        reveal_indexes = []

        # determine reveals required to panelize part
        while True:
            reveal_edge_width = 0.078125  # subtracted 15/16"from panel to allow it cut at 2'
            if exterior:  # panelization is left to right, the left edge reduces towards the right edge
                left_edge -= panelling_distance
                # skipping the out range if there is a window
                left_edge = self.check_out_range(left_edge, out_ranges, exterior=True)

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
                right_edge += panelling_distance  # panelization is right to left, the right edge increases towards
                # the left edge skipping the out range if there is a window
                right_edge = self.check_out_range(right_edge, out_ranges, exterior=False)

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

    def get_single_panel_reveal_indexes(self, left_edge, right_edge, exterior=True):
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

    def sort_parts_by_side(self, doc, parts):
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
            host_wall_id = self.get_host_wall_id(part)
            host_wall_type_id = self.get_host_wall_type_id(doc, host_wall_id)
            layer_index = self.get_layer_index(part)
            lap_type_id, side_of_wall, exterior = self.get_wall_sweep_parameters(layer_index, host_wall_type_id)

            if exterior == True:
                exterior_parts.append(part)
            elif exterior == False:
                interior_parts.append(part)
            elif exterior == None:
                core_parts.append(part)

        return exterior_parts, interior_parts

    def sort_parts_by_length(self, parts):
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

    def sort_parts_by_orthogonal(self, doc, parts):
        """
        filters out non-orthogonal parts
        :param parts: Parts to be panelized
        :return: orthogonal parts
        """
        orthogonal_parts = []
        non_orthogonal_parts = []
        for part in parts:
            host_wall_id = self.get_host_wall_id(part)
            host_wall = doc.GetElement(host_wall_id)
            sketch = host_wall.SketchId  # if sketchId is not -1, then the wall has been edited

            if sketch == ElementId(-1):
                orthogonal_parts.append(part)
            else:
                non_orthogonal_parts.append(part)
        return orthogonal_parts

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> SWITCH FUNCTIONS

    def switch_directions(self, exterior, switch_direction=False):
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

    # FENESTRATIONS MODULE
    """ This module allows you to interact with all fenestration functions """

    ####################################################################################################################
    ####################################################################################################################

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET WIDTH
    def get_fenestration_width(self, doc, fenestration_id):
        """
        Establish the width of the window
        :param doc: Active Revit document
        :param fenestration_id: window/door id
        :return: the width
        """
        # establish the width of the window
        fenestration = doc.GetElement(fenestration_id)
        fenestration_type = fenestration.Symbol
        width = fenestration_type.get_Parameter(BuiltInParameter.DOOR_WIDTH).AsDouble()

        # interchangeably the width can be 0 but rough width has dimensions
        if width == 0:
            width = fenestration_type.get_Parameter(BuiltInParameter.FAMILY_ROUGH_WIDTH_PARAM).AsDouble()

        return width

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET COORDINATES

    def get_fenestration_xyz_centre(self, doc, fenestration_id):
        """
        Get xyz centre coordinates of an opening: window, door or empty opening
        :param fenestration_id: A window/door id
        :return: xyz_centre
        """
        fenestration = doc.GetElement(fenestration_id)
        xyz_centre = fenestration.Location.Point
        return xyz_centre

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET HOSTED FENESTRATIONS

    def get_hosted_fenestrations(self, doc, wall_id, built_in_category):
        """
        Abstract all windows/doors hosted in a provided wall
        :param wall_id:  host wall id
        :param built_in_category:  filter selection based on built in category doors or windows
        i.e. BuiltInCategory.OST_Windows
        :return: list of filtered fenestrations
        """
        # select all windows
        all_fenestration = FilteredElementCollector(doc).OfCategory(built_in_category). \
            WhereElementIsNotElementType().ToElements()

        # store in a list all windows hosted by the wall
        hosted_fenestrations = []

        for window in all_fenestration:
            if window.Host.Id == wall_id:
                hosted_fenestrations.append(window)

        return hosted_fenestrations

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET INDEXES

    def get_fenestration_centre_index(self, doc, part, fenestration, reveal_coordinate_0):
        """
        Get distance position (index) of the window along the wall's path curve
        :param reveal_coordinate_0: reveal coordinate at 0 as datum of wall's path curve
        :param part:Part with hosted window/door
        :param fenestration:Window or door
        :return: Window centre index
        """

        # determine the direction, x or y-axis
        hosted_wall_id = self.get_host_wall_id(part)
        x_axis_plane = self.determine_x_plane(doc, hosted_wall_id)

        # get window/door coordinate centre
        fenestration_xyz_centre = self.get_fenestration_xyz_centre(doc, fenestration.Id)  # get window centre
        fenestration_coordinate_centre = self.get_plane_coordinate(fenestration_xyz_centre,
                                                                   x_axis_plane)  # get window coordinate

        # Get window index
        if fenestration_coordinate_centre > reveal_coordinate_0:
            fenestration_index = fenestration_coordinate_centre - reveal_coordinate_0
        else:  # interior
            fenestration_index = reveal_coordinate_0 - fenestration_coordinate_centre

        return fenestration_index

    def get_fenestration_edge_indexes(self, fenestration_width, fenestration_centre_index):
        """
        Determine the index of fenestration edges (window & door)
        :param fenestration_width: window/door width
        :param fenestration_centre_index: The reveal index of the centre of the window/door
        :return:
        """
        half_width = fenestration_width / 2

        # establish the edge of windows coordinates
        left_fenestration_edge_index = fenestration_centre_index + half_width
        right_fenestration_edge_index = fenestration_centre_index - half_width

        return left_fenestration_edge_index, right_fenestration_edge_index

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GET OUT-RANGES

    # single opening out-range
    def get_fenestration_out_range(self, fenestration_left_index, fenestration_right_index, displacement):
        """
        Determine the ranges the reveals should not be placed.
        :param fenestration_left_index: Index of the left edge of the opening
        :param fenestration_right_index: Index of the right edge of the opening
        :param displacement: the displacement distance set away from edges of openings
        This creates the range the reveals cannot be placed
        :return: list of left/right window range
        """

        # window width
        fenestration_width = fenestration_left_index - fenestration_right_index
        displacement = self.check_displacement_distance(displacement, fenestration_width)

        # window left edge
        left_box_range_1 = fenestration_left_index - displacement
        left_box_range_2 = fenestration_left_index + displacement
        left_range = [left_box_range_1, left_box_range_2]

        # window right edge
        right_box_range_1 = fenestration_right_index - displacement
        right_box_range_2 = fenestration_right_index + displacement
        right_range = [right_box_range_1, right_box_range_2]

        return left_range, right_range

    # get multiple hosted openings out-range per fenestration type
    def get_hosted_fenestrations_out_range(self, doc, part, hosted_fenestrations, reveal_coordinate_0, displacement):
        """
        Loop through all hosted openings and abstract the ranges the reveals should not pass through
        :param doc: Active revit document
        :param part: the part being panelized
        :param hosted_fenestrations: all hosted fenestrations
        :param reveal_coordinate_0: coordinates of reveal at 0
        :param displacement: the displacement distance set away from edges of openings
        :return: list of all out_ranges
        """
        out_ranges = []

        # loop through each window
        for fenestration in hosted_fenestrations:
            # determine the window center index of each window
            fenestration_center_index = self.get_fenestration_centre_index(doc, part, fenestration, reveal_coordinate_0)
            fenestration_width = self.get_fenestration_width(doc, fenestration.Id)

            # determine the out-range for each window
            fenestration_left_index, fenestration_right_index = self.get_fenestration_edge_indexes \
                (fenestration_width, fenestration_center_index)
            left_out_range, right_out_range = self.get_fenestration_out_range(fenestration_left_index,
                                                                              fenestration_right_index,
                                                                              displacement)

            out_ranges.append(left_out_range)
            out_ranges.append(right_out_range)

        # return a list of all out-range
        return out_ranges

    # get all hosted openings out-range by combining all fenestration types

    def get_out_ranges(self, doc, part, hosted_doors, hosted_windows, reveal_coordinate_0, displacement):
        """
        Determine if a part host wall has fenestrations door/window and abstract the out ranges
        :param doc: Active Revit document
        :param part:  Part to be panelized
        :param hosted_doors: Hosted doors in a part host wall
        :param hosted_windows: Hosted windows in a part host wall
        :param reveal_coordinate_0: Coordinates of reveal at 0
        :param displacement: Displacement distance from edges of fenestration
        :return: list of all out ranges
        """
        # when a part has both doors and windows
        if len(hosted_doors) != 0 and len(hosted_windows) != 0:
            door_out_ranges = self.get_hosted_fenestrations_out_range(doc, part, hosted_doors, reveal_coordinate_0,
                                                                      displacement)
            window_out_ranges = self.get_hosted_fenestrations_out_range(doc, part, hosted_windows, reveal_coordinate_0,
                                                                        displacement)
            out_ranges = door_out_ranges + window_out_ranges
        # when a part has only doors
        elif len(hosted_doors) != 0:
            out_ranges = self.get_hosted_fenestrations_out_range(doc, part, hosted_doors, reveal_coordinate_0,
                                                                 displacement)
        # when a part has only windows
        elif len(hosted_windows) != 0:
            out_ranges = self.get_hosted_fenestrations_out_range(doc, part, hosted_windows, reveal_coordinate_0,
                                                                 displacement)
        # when a part has no fenestration's
        else:
            out_ranges = []
        return out_ranges

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> CHECK PARAMETERS

    def check_out_range(self, edge, out_ranges, exterior=True):
        """
        Checks if the edge(reveal index) is within the outrange, if within the out range it defaults to the edge of the outrange
        :param edge: right/left edge
        :param out_ranges: the index ranges to be skipped
        :param exterior: if exterior or interior
        :return: the new reveal position
        """

        if exterior:
            # skipping the out_range
            # _____________________________________________________________________
            for edge_range in out_ranges:
                edge_range = sorted(edge_range)  # sort to determine the smallest
                if edge_range[0] <= edge <= edge_range[1]:  # the range the reveal should not fall within
                    if edge_range[0] > edge:
                        edge = edge_range[
                            0]  # because we are moving left to right, the greatest value is the smallest
                    elif edge_range[1] > edge:
                        edge = edge_range[1]
            # _____________________________________________________________________
        else:
            # skipping the out_range
            # _____________________________________________________________________
            for edge_range in out_ranges:
                if edge_range[0] <= edge <= edge_range[1]:
                    if edge_range[0] < edge:
                        edge = edge_range[0]
                    elif edge_range[1] < edge:
                        edge = edge_range[1]
            # _____________________________________________________________________

        return edge

    def check_displacement_distance(self, displacement_distance, fenestration_width):
        """
        Check if displacement distance surpasses the centre of the opening
        :param displacement_distance:
        :param fenestration_width:
        :return:displacement_distance
        """
        limit = fenestration_width / 2
        if displacement_distance >= limit:
            displacement_distance = limit - 0.5
            TaskDialog.Show("The displacement distance set is beyond half width fenestration limit")
        return displacement_distance

    # COORDINATES MODULE

    ####################################################################################################################
    ####################################################################################################################
    def determine_x_plane(self, doc, wall_id):
        """
        Determine the direction of the wall's path curve : x or y-axis
        :param doc: Active revit document
        :param wall_id: The host wall id
        :return: X-axis bool. host wall curve direction : x axis (True) , y axis (False)
        or neither on x nor y-axis (None)
        """

        wall = doc.GetElement(wall_id)

        # determine the plane of the wall
        wall_direction = wall.Location.Curve.Direction

        # direction coordinates
        x_direction = wall_direction.X
        y_direction = wall_direction.Y

        if x_direction == -1 or x_direction == 1:
            x_axis = True

        elif y_direction == -1 or y_direction == 1:
            x_axis = False

        else:
            # the wall curve is neither on x or y axis
            raise self.XYAxisPlaneNotEstablishedError

        return x_axis

    def get_plane_coordinate(self, xyz_coordinates, x_axis_plane):
        """
        Abstract plane coordinate ( x or y coordinate) from the xyz_coordinates based on the plane direction
        :param xyz_coordinates: xyz coordinates of an element
        :param x_axis_plane: plane direction
        :return: x or y coordinate
        """
        plane_coordinate = 0
        if x_axis_plane:
            plane_coordinate = xyz_coordinates.X

        elif not x_axis_plane:
            plane_coordinate = xyz_coordinates.Y

        return plane_coordinate

    def get_bounding_box_center(self, doc, element):
        """
        Get the centre coordinates af an element using its bounding box
        :param doc: Active revit document
        :param element: Element in revit (part)
        :return: centre xyz coordinates
        """

        box_coordinates = element.get_BoundingBox(doc.ActiveView)
        if box_coordinates is not None:
            maximum = box_coordinates.Max
            minimum = box_coordinates.Min
            centre = (maximum + minimum) / 2
        else:
            centre = None

        return centre

    # ERROR HANDLER MODULE
    ####################################################################################################################
    ####################################################################################################################

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ERROR HANDLER

    # Delete reveal warning dialog boxes
    class WarningSwallower(IFailuresPreprocessor):
        """
        Suppresses all warning dialog boxes by deleting them . Cannot delete Errors.
        Errors have to be addressed by the user
        """

        def PreprocessFailures(self, failuresAccessor):

            # Inside event handler, get all warnings
            failList = failuresAccessor.GetFailureMessages()

            for failure in failList:
                # check FailureDefinitionIds against ones that you want to dismiss
                failID = failure.GetFailureDefinitionId()
                if failID == BuiltInFailures.SweepFailures.CannotDrawSweep:
                    failuresAccessor.DeleteWarning(failure)
                elif failID == BuiltInFailures.PartMakerMethodForWallFailures.CouldNotCreateWallPartDueToWallJoin:
                    failuresAccessor.DeleteWarning(failure)
                else:
                    failuresAccessor.DeleteAllWarnings()

            return FailureProcessingResult.Continue

    class CentreIndexError(Exception):
        """
        Catch error: Centre index of the part could not be established correctly
        """
        pass

    # catch variable distance cannot be found
    class VariableDistanceNotFoundError(Exception):
        """
        Catch error: variable distance cannot be found
        """
        pass

    # catch reveal not selected error
    class RevealNotCreatedError(Exception):
        """
        Catch error: reveal not selected error
        """
        pass

    # Error occurred deleting elements
    class DeleteElementsError(Exception):
        """
        Catch error: reveal not selected error
        """
        pass

    # catch instances where parts/walls are not along a x or y-axis
    class XYAxisPlaneNotEstablishedError(Exception):
        """
        Catch error: parts/walls are not along a X or Y axis
        """
        pass

    # TRANSACTIONS
    ####################################################################################################################
    ####################################################################################################################

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PLACE REVEAL TRANSACTION

    def auto_place_reveal(self, doc, host_wall_id, lap_type_id, variable_distance, side_of_wall):
        """
        Places a wall sweep on a part by initializing a transaction.All warnings are suppressed
        by deleting the dialog boxes.

        :param doc: Active Revit Document
        :param lap_type_id:Element id of the wall sweep type used
        :param host_wall_id:host wall id
        :param variable_distance: distance along the wall's path curve
        :param side_of_wall: side of the wall to which the reveal is attached.
        :return: A wall sweep
        """
        with Transaction(doc, "panelization") as t:
            t.Start("01. PlacingReveal")
            # Provides access to option to control how failures should be handled by end of transaction.
            options = t.GetFailureHandlingOptions()

            # deletes warnings captured
            failureProcessor = self.WarningSwallower()

            # sets how failures should be handled during transaction
            options.SetFailuresPreprocessor(failureProcessor)
            t.SetFailureHandlingOptions(options)

            reveal = self.create_reveal(doc, host_wall_id, lap_type_id, variable_distance, side_of_wall)

            status = t.Commit()

            if status != TransactionStatus.Committed:
                raise eh.RevealNotCreatedError

        return reveal

    def get_reveal_coordinate_at_0(self, doc, part):
        """
        Get the coordinates of the reveal at distance 0
        :param doc: Revit active document
        :param part: Part to be panelized

        """

        # project parameters
        host_wall_id = self.get_host_wall_id(part)
        host_wall_type_id = self.get_host_wall_type_id(doc, host_wall_id)
        layer_index = self.get_layer_index(part)
        lap_type_id, side_of_wall, exterior = self.get_wall_sweep_parameters(layer_index, host_wall_type_id)
        x_axis_plane = self.determine_x_plane(doc, host_wall_id)

        # set variable distance at 3, most parts are cut with reveals at a distance from the path curve origin,0 .
        # Thus, coordinates of the reveal can be established

        variable_distance = 3
        while True:
            reveal_1 = self.auto_place_reveal(doc, host_wall_id, lap_type_id, variable_distance, side_of_wall)

            if self.get_bounding_box_center(doc, reveal_1) is not None:
                break  # script breaks once coordinates are established

            # if the coordinates are not established, the script deletes the reveal and before looping to
            # the next at an adjusted distance
            self.delete_element(doc, reveal_1.Id)

            variable_distance += 3

            if variable_distance > 100:
                # the script has to break , the reveal coordinates could not be established.
                raise self.VariableDistanceNotFoundError

        reveal_xyz_coordinates_1 = self.get_bounding_box_center(doc, reveal_1)
        reveal_plane_coordinate_1 = float(self.get_plane_coordinate(reveal_xyz_coordinates_1, x_axis_plane))

        # create snd wall sweep, this will help establish the reveal at 0
        move_distance = 0.166667  # 1/4", small distance to ensure part is cut
        reveal_2 = self.auto_place_reveal(doc, host_wall_id, lap_type_id, variable_distance + move_distance,
                                          side_of_wall)

        # reveal 2 plane coordinate
        reveal_xyz_coordinates_2 = self.get_bounding_box_center(doc, reveal_2)
        reveal_plane_coordinate_2 = float(self.get_plane_coordinate(reveal_xyz_coordinates_2, x_axis_plane))

        # reveal plane coordinates at 0
        if reveal_plane_coordinate_2 < reveal_plane_coordinate_1:
            reveal_plane_coordinate_0 = reveal_plane_coordinate_1 + variable_distance
        else:
            reveal_plane_coordinate_0 = reveal_plane_coordinate_1 - variable_distance

        # delete the reveal after abstracting the coordinate at o
        self.delete_element(doc, reveal_1.Id, reveal_2.Id)

        return reveal_plane_coordinate_0

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> PANELIZE TRANSACTIONS

    def auto_panel(self, doc, host_wall_id, lap_type_id, reveal_indexes, side_of_wall):
        """
        Auto place reveals along the wall's path curve as per reveal indexes provided
        :param doc:  Active revit document
        :param lap_type_id:Element id of the wall sweep type used
        :param host_wall_id:host wall id
        :param reveal_indexes: list of reveal distance indexes along the wall's path curve
        :param side_of_wall: side of the wall to which the reveal is attached.
        :return: None
        """

        with Transaction(doc, "Panelization") as t:
            t.Start("03. Panelize parts")
            # Provides access to option to control how failures should be handled by end of transaction.
            options = t.GetFailureHandlingOptions()

            # deletes warnings captured
            failureProcessor = self.WarningSwallower()

            # sets how failures should be handled during transaction
            options.SetFailuresPreprocessor(failureProcessor)
            t.SetFailureHandlingOptions(options)

            for reveal_index in reveal_indexes:
                self.create_reveal(doc, host_wall_id, lap_type_id, reveal_index, side_of_wall)
            status = t.Commit()

            if status != TransactionStatus.Committed:
                # if transaction has not been committed.Raise an error, the cause is that the centre index for
                # the part could not be established correctly generating a wrong set of reveal indexes outside the panel
                raise self.CentreIndexError

    def auto_parts(self, doc, part, displacement_distance, switch_option, minimum_panel_size, multiple=True):
        """
        Auto Identifies :
        1. The part wall side ( exterior, interior or partition ) intuitively
        2. The lap (right or left) to be used to be used intuitively
        3. Direction to be used  right-> left or left->right by user choice
        and places reveals along the wall's path's curve thus creating panels

        :param minimum_panel_size: Smallest panel size allowed
        :param doc: Active revit document
        :param multiple: Bool to determine single panel or multi-panel reveal distances
        :param switch_option: Bool to switch direction of placing reveals: left to right/right to left
        :param displacement_distance: Distance away from the edges of openings
        :param part: Part to be panelized

        :return: None
        """

        host_wall_id = self.get_host_wall_id(part)
        host_wall_type_id = self.get_host_wall_type_id(doc, host_wall_id)
        layer_index = self.get_layer_index(part)
        lap_type_id, side_of_wall, exterior = self.get_wall_sweep_parameters(layer_index, host_wall_type_id)

        # Test if the panel is divisible into two equal parts
        reveal_plane_coordinate_0 = self.get_reveal_coordinate_at_0(doc, part)
        centre_index = self.get_part_centre_index(doc, part, reveal_plane_coordinate_0)

        # create left and right edge
        part_length = self.get_part_length(part)
        left_edge, right_edge = self.get_part_edge_index(part_length, centre_index)

        hosted_windows = self.get_hosted_fenestrations(doc, host_wall_id, BuiltInCategory.OST_Windows)
        hosted_doors = self.get_hosted_fenestrations(doc, host_wall_id, BuiltInCategory.OST_Doors)

        # check if part has openings or not
        if len(hosted_windows) == 0 and len(hosted_doors) == 0:
            out_ranges = []
        else:
            displacement = displacement_distance
            out_ranges = self.get_out_ranges(doc, part, hosted_doors, hosted_windows, reveal_plane_coordinate_0,
                                             displacement)

        # interchanges the direction of placing reveals
        exterior = self.switch_directions(exterior, switch_direction=switch_option)

        # determine single panel or multi-panel reveal distances
        if multiple:
            reveal_indexes = self.get_reveal_indexes(left_edge, right_edge, out_ranges, minimum_panel_size, exterior)
        else:
            reveal_indexes = self.get_single_panel_reveal_indexes(left_edge, right_edge, exterior)

        # Place reveals creating panels
        self.auto_panel(doc, host_wall_id, lap_type_id, reveal_indexes, side_of_wall)

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> DELETE TRANSACTIONS

    def delete_element(self, doc, *args):
        """
        Delete a single/many element in revit
        :param doc:
        :param args: Collection of Element Ids to be deleted
        :return: None
        """
        with Transaction(doc, "Panelization- deleting elements") as t:
            t.Start("02. Delete reveals")

            options = t.GetFailureHandlingOptions()
            failureProcessor = self.WarningSwallower()
            options.SetFailuresPreprocessor(failureProcessor)
            t.SetFailureHandlingOptions(options)
            for element_id in args:
                doc.Delete(element_id)
            status = t.Commit()

            if status != TransactionStatus.Committed:
                # if transaction has not been rollback. Could not therefore delete elements
                raise self.DeleteElementsError

    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> GRAPHICS TRANSACTIONS

    def highlight_unpanelized_underpanelized_parts(self, doc):
        """
        Highlight unpanelized and underpanelized parts by color
        :return: Graphics settings for unpanelized and panelized parts
        """
        active_view = doc.ActiveView

        # select all parts
        parts = self.select_all_parts(doc)
        exterior_parts, interior_parts = self.sort_parts_by_side(doc, parts)
        filtered_parts = exterior_parts + interior_parts
        underpanalized, panelized, unpanelized = self.sort_parts_by_length(filtered_parts)

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

        with Transaction(doc, "Graphics") as t:
            t.Start("04. Graphics adjustment")
            if len(unpanelized) != 0:
                for part in unpanelized:
                    active_view.SetElementOverrides(part.Id, graphics_settings_unpanelized)
            if len(underpanalized) != 0:
                for part in underpanalized:
                    active_view.SetElementOverrides(part.Id, graphics_settings_underpanelized)

            t.Commit()

        return graphics_settings_unpanelized, graphics_settings_underpanelized

    # TOOLS BUTTOMS
    ####################################################################################################################
    ####################################################################################################################
    # >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> AUTO PARTS

    def panelize_allParts(self):
        """Auto selects all parts and panelizes them. If a part bears an error, it is skipped."""

        doc = self.ActiveUIDocument.Document

        selected_parts = self.select_all_parts(doc)
        exterior_parts, interior_parts = self.sort_parts_by_side(doc, selected_parts)
        all_parts = exterior_parts + interior_parts
        underpanelized, panalized, non_panelized_parts = self.sort_parts_by_length(all_parts)

        if len(non_panelized_parts) != 0:

            # panelization parameters
            switch_option = False
            TaskDialog.Show("Form required", "Switching panelization direction. Default: Left to Right")
            displacement_distance = 0.5
            TaskDialog.Show("Form required", "Displacement distance from edge of openings. Default: 0.5'")
            minimum_panel_size = 2
            TaskDialog.Show("Form required", "Minimum panel size. Default: 2' ")

            for part in non_panelized_parts:
                try:
                    self.auto_parts(doc, part, displacement_distance, switch_option, minimum_panel_size, multiple=True)
                except Exception:
                    pass

            self.highlight_unpanelized_underpanelized_parts(doc)

        else:
            TaskDialog.Show("Info", "There are no non-panelized parts")

    def panelize_multiParts(self):
        """Allows the user to select parts to be panelized, If a part bears an error, a dialog box is shown and
        the part is skipped. If the error is exceptionally not captured, the part will be skipped without displaying
        a dialog box"""

        uidoc = self.ActiveUIDocument
        doc = self.ActiveUIDocument.Document

        parts = self.select_parts(uidoc)

        # panelization parameters
        switch_option = False
        TaskDialog.Show("Form required", "Switching panelization direction. Default: Left to Right")
        displacement_distance = 0.5
        TaskDialog.Show("Form required", "Displacement distance from edge of openings. Default: 0.5'")
        minimum_panel_size = 2
        TaskDialog.Show("Form required", "Minimum panel size. Default: 2' ")

        for part in parts:
            try:
                self.auto_parts(doc, part, displacement_distance, switch_option, minimum_panel_size, multiple=True)
            except self.RevealNotCreatedError:
                TaskDialog.Show("Error", 'Reveal at coordinate 0 could not be created')
            except self.CentreIndexError:
                TaskDialog.Show("Error", "Centre Index could not be established")
            except self.VariableDistanceNotFoundError:
                TaskDialog.Show("Error", "The variable distance could not be established")
            except self.DeleteElementsError:
                TaskDialog.Show("Error", 'Error occurred. Could not delete reveals')
            except self.XYAxisPlaneNotEstablishedError:
                TaskDialog.Show("Error", "Could not Panelize. Selected Part not on X or Y axis")
            except Exception:
                pass

    def panelize_singlePart(self):
        """
        Allows the user to select a part. If a part bears an error, a dialog box is shown and
        error displayed. If the part cannot be panelized, the user should resort to the manual panelization process
        """
        uidoc = self.ActiveUIDocument
        doc = self.ActiveUIDocument.Document

        try:
            part = self.select_part(uidoc)

            # project parameters
            switch_option = False
            TaskDialog.Show("Form required", "Switching panelization direction. Default: Left to Right")
            displacement_distance = 0.5
            TaskDialog.Show("Form required", "Displacement distance from edge of openings. Default: 0.5'")
            minimum_panel_size = 2
            TaskDialog.Show("Form required", "Minimum panel size. Default: 2' ")

            self.auto_parts(doc, part, displacement_distance, switch_option, minimum_panel_size, multiple=True)

        except self.RevealNotCreatedError:
            TaskDialog.Show("Error", 'Reveal at coordinate 0 could not be created')

        except self.CentreIndexError:
            TaskDialog.Show("Error", "Centre Index could not be established")

        except self.VariableDistanceNotFoundError:
            TaskDialog.Show("Error", "The variable distance could not be established")

        except self.XYAxisPlaneNotEstablishedError:
            TaskDialog.Show("Error", 'Could not Panelize. Selected Part not on X or Y axis')

        except self.DeleteElementsError:
            TaskDialog.Show("Error", 'Error occurred. Could not delete reveals')

        except Exception as e:
            error_message = "Error occurred. Could not panelize selected Part. \n {}".format(e)
            TaskDialog.Show("Error", error_message)

    def panelize_splitPart(self):
        """Allows user to split a part into two equal parts infinitely"""

        doc = self.ActiveUIDocument.Document
        uidoc = self.ActiveUIDocument

        try:
            part = self.select_part(uidoc)
            host_wall_id = self.get_host_wall_id(part)
            host_wall_type_id = self.get_host_wall_type_id(doc, host_wall_id)
            layer_index = self.get_layer_index(part)
            lap_type_id, side_of_wall, exterior = self.get_wall_sweep_parameters(layer_index, host_wall_type_id)

            reveal_plane_coordinate_0 = self.get_reveal_coordinate_at_0(doc, part)
            centre_index = self.get_part_centre_index(doc, part, reveal_plane_coordinate_0)

            self.auto_place_reveal(doc, host_wall_id, lap_type_id, centre_index, side_of_wall)

        except self.VariableDistanceNotFoundError:
            TaskDialog.Show("Error", "The variable distance could not be established")
        except self.RevealNotCreatedError:
            TaskDialog.Show("Error", "Reveal at coordinate 0 could not be created")
        except self.DeleteElementsError:
            TaskDialog.Show("Error", 'Error occurred. Could not delete reveals')
        except self.XYAxisPlaneNotEstablishedError:
            TaskDialog.Show("Error", 'Could not Panelize. Selected Part not on X or Y axis')
        except Exception as e:
            error_message = "Error occurred. Could not split part \n {}".format(e)
            TaskDialog.Show("Error", error_message)

    def select_faceReveals(self):
        """This tool allows you to select all reveals in a face of a part"""

        uidoc = self.ActiveUIDocument
        doc = self.ActiveUIDocument.Document

        reveal = self.select_reveal(uidoc)
        reference_host_id = self.get_reveal_host_wall_id(reveal)
        reference_wall_side = self.get_wall_side(reveal)
        all_reveals = self.select_all_reveals(doc)
        filtered_reveals = self.get_filtered_reveals(reference_host_id, reference_wall_side, all_reveals)

        # Create a C# List[int] and add the Python list elements to it
        filtered_reveals_collection = List[ElementId](filtered_reveals)
        self.display_selected_reveals(uidoc, filtered_reveals_collection)

    def takeoff_unpanelizedParts(self):
        """ Abstract how many parts have not been panelized.
        Unpanelized parts will be highlighted for further intervention"""

        doc = self.ActiveUIDocument.Document
        parts = self.get_unpanelized_parts(doc)
        if len(parts) != 0:
            parts_data = self.get_unpanalized_parts_data(parts)
            header = ["COUNT", "PART ID", "HEIGHT(F)", "LENGTH(F)", "BASE LEVEL"]
            self.highlight_unpanelized_underpanelized_parts(doc)

            TaskDialog.Show("Form required", "create a table to display unpanelized data")

        else:
            TaskDialog.Show("Info", "Congratulations! All parts have been panelized")

    def takeoff_panelizedParts(self):
        """
        Displays panel schedule of a panelized parts
        :return:
        """

        doc = self.ActiveUIDocument.Document

        # select all parts
        parts = self.select_all_parts(doc)
        exterior_parts, interior_parts = self.sort_parts_by_side(doc, parts)

        options = ['External Parts', 'Internal Parts', 'External and Internal Parts']
        message = "Allow user to select parts type for take off. Options {} \n. default: {} ".format(options,
                                                                                                     options[2])
        TaskDialog.Show("Form required", message)

        filtered_parts = interior_parts + exterior_parts

        # filter by length, take off of panelized and underpanalized parts
        underpanalized, panelized, unpanalized = self.sort_parts_by_length(filtered_parts)
        selected_parts = underpanalized + panelized

        if len(selected_parts) != 0:
            cost_per_sf = 0.5
            TaskDialog.Show("Form required", "Cost per square feet. Default: 0.5 USD ")

            parts_data = self.get_panelized_parts_data(selected_parts)
            parts_type_data = self.get_panelized_parts_type_data(parts_data)
            final_data = self.get_panelized_parts_summary_data(parts_data, parts_type_data, cost_per_sf)

            # display panels data
            header = ["HEIGHT(F)", "LENGTH(F)", "THICKNESS(F)", "VOLUME (CF) ", "BASE LEVEL", "AREA (SF)", "COUNT",
                      "TOTAL AREA(SF)",
                      "COST PER SF (USD)", " COST(USD)"]

            TaskDialog.Show("Form required", "create a table to display panelized data")

            if len(unpanalized) != 0:
                self.highlight_unpanelized_underpanelized_parts(doc)
                TaskDialog.Show("Info", "Highlighted parts (red) have not been panelized")

            else:
                TaskDialog.Show("Info", "Congratulations! All parts have been panelized")

        else:
            self.highlight_unpanelized_underpanelized_parts(doc)
            TaskDialog.Show("Info", "Parts (red) not panelized. Proceed with Panelization")

    # Transaction mode
    def GetTransactionMode(self):
        return Attributes.TransactionMode.Manual

    # Addin Id
    def GetAddInId(self):
        return '17602E07-6755-4E7F-9702-BA0B1784D2F4'
