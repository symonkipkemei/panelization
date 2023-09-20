from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
import clr

clr.AddReference("System")


# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ERROR HANDLER


# Delete reveal warning dialog boxes
class WarningSwallower(IFailuresPreprocessor):
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


# Error occured deleteing elements
class DeleteElementsError(Exception):
    """
    Catch error: reveal not selected error
    """
    pass

# catch instances where parts/walls are not along a x or y axis
class XYAxisPlaneNotEstablishedError(Exception):
    """
    Catch error: parts/walls are not along a X or Y axis
    """
    pass

