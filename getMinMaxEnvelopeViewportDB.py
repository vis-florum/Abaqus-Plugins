from abaqusConstants import *
from abaqusGui import *
from kernelAccess import mdb, session
import os

thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)


###########################################################################
# Class definition
###########################################################################

class GetMinMaxEnvelopeViewportDB(AFXDataDialog):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, form):

        # Construct the base class.
        #

        AFXDataDialog.__init__(self, form, 'MinMax Envelope Viewport',
            self.OK|self.CANCEL, DIALOG_ACTIONS_SEPARATOR)
            

        okBtn = self.getActionButton(self.ID_CLICKED_OK)
        okBtn.setText('GET')
            
        l = FXLabel(p=self, text='Choose a primary variable and set deformed state!', opts=JUSTIFY_LEFT)
        l = FXLabel(p=self, text='This will give Envelopes of the currently shown Variable.', opts=JUSTIFY_LEFT)
