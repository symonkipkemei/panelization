
from __future__ import division
# -*- coding: utf-8 -*-

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> IMPORTS

from Autodesk.Revit.DB import *
import clr
clr.AddReference("System")

# >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> ERROR HANDLER

# catch instances where parts are less than 4'
class CannotPanelizeError(Exception):
    pass

#Cannot split the panel into equal parts
class CannotSplitPanelError(Exception):
    pass

#Delete reveal warning dialog boxes
class RevealWarningSwallower(IFailuresPreprocessor):
    def PreprocessFailures(self, failuresAccessor):
        failList = []
        # Inside event handler, get all warnings
        failList = failuresAccessor.GetFailureMessages()

        for failure in failList:
            # check FailureDefinitionIds against ones that you want to dismiss
            failID = failure.GetFailureDefinitionId()
            # prevent Revit from showing Unenclosed room warnings
            if failID == BuiltInFailures.SweepFailures.CannotDrawSweep:
                failuresAccessor.DeleteWarning(failure)
            else:
                failuresAccessor.DeleteWarning(failure)

        return FailureProcessingResult.Continue


#catch variable distance cannot  be found
class VariableDistanceNotFoundError(Exception):
    pass
