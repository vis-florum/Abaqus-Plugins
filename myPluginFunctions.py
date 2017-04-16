from abaqusConstants import *
from abaqus import mdb, session
import odb, odbAccess, xyPlot, visualization

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def showColor(myColor):
	# Just for test
	# Outputs a selection from a color wheel
	a = myColor
	print 'The color is: '
	print a
	return a

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def showPickedNode(myNode):
	# Just for test
	# Outputs the node label of a selected node
	print myNode.label

#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getCombineOfNode(pickedNode):
	# Creates a combine of logarithmic strain and Mises stress
	# of a picked node in the Viewport
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Delete all created XYData
	for i in session.xyDataObjects.keys():
		del session.xyDataObjects[i]
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### What are we looking at?
	# Get the displayed ODB in current Viewport (must be in Visualisation):
	vpName		= session.currentViewportName
	myViewport 	= session.viewports[vpName]
	myODB		= myViewport.displayedObject
	
	# Get active nodes labels:
	visibleNodes = myViewport.getActiveNodeLabels()
	visibleElement = myViewport.getActiveElementLabels()
	
	visiblePart = visibleNodes.keys()[0]
	visibleElementIndex = visibleElement.values()[0][0] - 1	# Because index starts at 0
	
	# Take only the one of the nodes:
	#chosenNode = int(getInput('Which Node to take? \n ' + str(visibleNodes.values()[0])))
	chosenNode = pickedNode.label
	
	# Take the chosen node:
	nodeTuples = ((visiblePart, tuple([chosenNode]) ), )
	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Get Field Data
	
	# Get section categories (if section integration points exist) for that specific element/node:
	# Works only if other elements are hidden
	visibleElementObject = myODB.rootAssembly.instances[visiblePart].elements[visibleElementIndex]
	
	# If there are section points, choose the first section point:
	if visibleElementObject.sectionCategory.sectionPoints:
		mySection = {visibleElementObject.sectionCategory.name : visibleElementObject.sectionCategory.sectionPoints[0].description , }
	else:
		mySection = {}
	
	fieldVar = (('S', INTEGRATION_POINT, ((INVARIANT, 'Mises' ), ), mySection), )
	varField_stress = session.xyDataListFromField(odb=myODB, outputPosition=NODAL, variable=fieldVar, nodeLabels=nodeTuples )
	
	fieldVar = (('LE', INTEGRATION_POINT, ((INVARIANT, 'Max. Principal (Abs)' ), ), mySection), )
	varField_strain = session.xyDataListFromField(odb=myODB, outputPosition=NODAL, variable=fieldVar, nodeLabels=nodeTuples )
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Combine
	
	# Arrange the data:	
	myCombine = []
	for i in range(len(varField_strain[0])):
		myCombine.append( (-varField_strain[0][i][1], varField_stress[0][i][1]) )
		
	# Make the Combine:
	session.XYData(data=myCombine, name='Combine-Stress-Strain-'+str(chosenNode), xValuesLabel='STRAIN', yValuesLabel='STRESS')

	
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getMinMaxViewport():
	# Make an XYData of the shown Variables MAX and MIN in the Viewport
	# Deformed state with the wanted variable must be activated!
	###
	
	from abaqusConstants import *
	import odb
	import odbAccess
	import xyPlot
	import visualization
	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Delete all created XYData:
	for i in session.xyDataObjects.keys():
		del session.xyDataObjects[i]
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### What are we looking at
	# Get the displayed ODB in current Viewport (must be in Visualisation):
	vpName		= session.currentViewportName
	myViewport 	= session.viewports[vpName]
	myODB		= myViewport.displayedObject	# ! Can be an XYPLot!!!
	
	shownVar 		= myViewport.odbDisplay.primaryVariable[0]
	shownComponent 	= myViewport.odbDisplay.primaryVariable[5]
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Get the times (cumulative)
	# Get a list of lists with times from 0 to end for each step:
	times = [list(thisstep[8]) for thisstep in myViewport.odbDisplay.fieldSteps]
	
	# Make an array that contains the nr of frames for each step:
	framesInSteps = map(len,times)
	
	# For steps>0 add the end time of the previous step to the times of the subsequent steps:
	for stepnr in range(len(times)):
		if stepnr>0:
			times[stepnr] = [thisframe+times[stepnr-1][-1] for thisframe in times[stepnr]]
	
	# Make everything to only one list:
	times = [k for i in times for k in i]
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Go through each frame and extract the MIN and MAX
	maxes = []
	mins  = []
	
	for stepnr in range(len(framesInSteps)):
		for framenr in range(framesInSteps[stepnr]):		# Much faster if range is used instead of frame objects
			myViewport.odbDisplay.setFrame(step=stepnr,frame=framenr)
			maxes.append(myViewport.getPrimVarMinMaxLoc()['maxValue'])
			mins.append(myViewport.getPrimVarMinMaxLoc()['minValue'])
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Make a XY Data of the extracted
	# Zip the data together to tuples:
	maxesData = zip(times,maxes)
	minsData = zip(times,mins)
	
	# Make the XY data for the Envelope:
	session.XYData(data=maxesData,
		name='Maximums-' + shownVar + '-' + shownComponent,
		xValuesLabel='TIME')
		#yValuesLabel='STRESS'
		
	session.XYData(data=minsData,
		name='Minimums-' + shownVar + '-' + shownComponent,
		xValuesLabel='TIME')
		#yValuesLabel='STRESS'
	
	# Getting quantity types seems unbelievably hard in this programme...
	# Could make a xyPlot of the current variable and then just extract the quantity type:
	#print session.xyPlots['XYPlot-1'].curves['Minimums-S-S33'].data.axis1QuantityType.type
	# Then I could copy that to the new XY Plots


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getMinMaxEnvelopeViewport():
	
	# Takes the shown variables in the Viewport and creates envelopes
	# of the MINs and MAXes at NODAL locations acros sall steps and frames
	#
	# Deformed state with the wanted variable must be activated!
	# Only the visible elements are regarded!
	# CPRESS and other variables that depend on parts cannot be ragarded!
	###
	
	from abaqusConstants import *
	import odb
	import odbAccess
	import xyPlot
	import visualization
	from abaqus import maxEnvelope
	from abaqus import minEnvelope
	
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Delete all created XYData
	for i in session.xyDataObjects.keys():
		del session.xyDataObjects[i]
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### What are we looking at
	# Get the displayed ODB in current Viewport (must be in Visualisation):
	vpName		= session.currentViewportName
	myViewport 	= session.viewports[vpName]
	myODB		= myViewport.displayedObject	# ! Can be an XYPLot!!!
	
	shownVar 		  = myViewport.odbDisplay.primaryVariable[0]
	shownComponent 	  = myViewport.odbDisplay.primaryVariable[5]
	allowedComponents = myODB.steps.values()[0].frames[0].fieldOutputs[shownVar].componentLabels
	allowedPosition   = myODB.steps.values()[0].frames[0].fieldOutputs[shownVar].values[0].position
	# Alternative:
	#allowedPosition   = myODB.steps.values()[0].frames[0].fieldOutputs[shownVar].locations[0].position
	# But how do we get CENTROID etc?
	
	# Get active nodes labels:
	visibleNodes = myViewport.getActiveNodeLabels()
	
	# Format nodes to a tuple to pass to function
	nodeTuples = tuple([(part, tuple(visibleNodes[part])) for part in visibleNodes])
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Prepare the Field Data Format
	
	# Set the wanted field Variable to component or invariant:
	if shownComponent in allowedComponents:
		fieldVar = ((shownVar,allowedPosition, ( (COMPONENT, shownComponent ), ), ), )
	elif shownComponent=='':
		fieldVar = ((shownVar,allowedPosition, ), )
	else:
		fieldVar = ((shownVar,allowedPosition, ( (INVARIANT, shownComponent ), ), ), )
	
	varField = session.xyDataListFromField(odb=myODB, outputPosition=NODAL, variable=fieldVar, nodeLabels=nodeTuples )
	
	#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
	### Output the data
	# Get the Envelope:
	myMaxEnveloppe = maxEnvelope(varField)
	myMinEnveloppe = minEnvelope(varField)
	
	# Make the XY data for the Envelope:
	session.XYData(data=myMaxEnveloppe.data, name='MaxEnvelope-' + shownVar + '-' + shownComponent)
	session.XYData(data=myMinEnveloppe.data, name='MinEnvelope-' + shownVar + '-' + shownComponent)

	
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getCombineUserInput(firstVar, secondVar):
	# TODO!
	# User chooses variables (depending on which exists)
	# Then make a combine of it
	return 0


#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
def getMinMaxEnvelopeUserInnput(firstVar, secondVar):
	# TODO!
	# User chooses variables (depending on which exists)
	# Then make min max envelopes of it
	return 0
	
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
