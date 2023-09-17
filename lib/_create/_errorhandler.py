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


# catch instances where parts are less than 4'
class CannotPanelizeError(Exception):
    pass


# Cannot split the panel into equal parts
class CannotSplitPanelError(Exception):
    pass


# catch variable distance cannot  be found
class VariableDistanceNotFoundError(Exception):
    pass


# catch reveal not selected error
class RevealNotSelectedError(Exception):
    pass


# catch elements that are Null in value
class NoneError(Exception):
    pass
