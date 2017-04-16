from abaqusGui import *
from abaqusConstants import ALL
import osutils, os
from myIcons import showNodeIcon
import i18n


###########################################################################
# Class definition
###########################################################################

class ShowNode_plugin(AFXForm):

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, owner):
        
        # Construct the base class.
        #
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='showPickedNode',
            objectName='myPluginFunctions', registerQuery=False)
        pickedDefault = ''
        self.myNodeKw = AFXObjectKeyword(self.cmd, 'myNode', TRUE, pickedDefault)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def getFirstDialog(self):

        import showNodeDB
        return showNodeDB.ShowNodeDB(self)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def doCustomChecks(self):

        # Try to set the appropriate radio button on. If the user did
        # not specify any buttons to be on, do nothing.
        #
        for kw1,kw2,d in self.radioButtonGroups.values():
            try:
                value = d[ kw1.getValue() ]
                kw2.setValue(value)
            except:
                pass
        return True

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def okToCancel(self):

        # No need to close the dialog when a file operation (such
        # as New or Open) or model change is executed.
        #
        return False

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Register the plug-in
#
thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()

pluginDesc = i18n.tr( \
    'A simple Node Extractor')

# Register a GUI plug-in in the Plug-ins menu.
#
toolset.registerGuiMenuButton(
    object=ShowNode_plugin(toolset),
    buttonText=i18n.tr('My Plugins|Get a Node Label'),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import myPluginFunctions',
    applicableModules=ALL,
    #applicableModules = ['Visualization'],
    version='1.0',
    author='Johannes Huber',
    description=pluginDesc,
    helpUrl='N/A'
)

# Register a GUI plug-in in a toolbox.
#
icon = FXXPMIcon(getAFXApp(), showNodeIcon)

toolset.registerGuiToolButton('My Toolbox', 
    object=ShowNode_plugin(toolset),
    buttonText=i18n.tr('\tFind a Node\nand show Label'),
    kernelInitString='import myPluginFunctions',
    icon=icon,
    applicableModules=ALL,
    #applicableModules = ['Part', 'Property', 'Assembly', 'Step', 
    #    'Interaction', 'Load', 'Mesh', 'Job'],
    version='1.0',
    author='Johannes Huber',
    description=pluginDesc,
    helpUrl='N/A'
)
