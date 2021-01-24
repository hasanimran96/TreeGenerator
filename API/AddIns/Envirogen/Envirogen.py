import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import math
import random

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []
progresscounter = 0
forProgressTotal = 0

#Gets called initially, everything else will be called from here or is a handler etc
def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('EnviroGenDefIdPython',
                                                   'EnviroGen',
                                                   'Generate a different looking tree every time with the ease of a click',
                                                   './resources/Button')

        # Connect to the command created event.
        sampleCommandCreated = CommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)

        # Get the ADD-INS panel in the model workspace.
        addInsPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')

        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(buttonSample)

        # Make the button available in the panel.
        buttonControl.isPromotedByDefault = True
        buttonControl.isPromoted = True

        # prevent this module from being terminate when the script returns
        # because we are waiting for event handlers to fire
        adsk.autoTerminate(False)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

#clean up the UI when we stop the add in from the add ins menu
def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('EnviroGenDefIdPython')
        if cmdDef:
            cmdDef.deleteMe()

        addinsPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        cntrl = addinsPanel.controls.itemById('EnviroGenDefIdPython')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class CommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command

        # Get the CommandInputs collection to create new command inputs.
        inputs = cmd.commandInputs

        # Create a selection input.
        selectionInput = inputs.addSelectionInput(
            'surfaceInput', 'Tree location', 'Select a construction point or Vertex to create the tree at. \nIf a Surface is selected, the tree will be placed at its center. \nOtherwise the default position is (0,0,0)')
        selectionInput.setSelectionLimits(0, 1)
        selectionInput.addSelectionFilter('Faces')
        selectionInput.addSelectionFilter('ConstructionPoints')
        selectionInput.addSelectionFilter('Vertices')
        selectionInput.isFullWidth = False

        # Create the value input to get the base size of the Tree
        baseSize = inputs.addFloatSpinnerCommandInput(
            'baseSize', 'Tree size', 'm', 0.01, 100, 0.1, 10)
        baseSize.isFullWidth = False
        baseSize.tooltip = 'Approximate size of the tree. \nIt might vary slightly due to the randomnes.'


        # Create a check box to get if high cusomizability is desired
        highCustomizability = inputs.addBoolValueInput('highCustomizability', 'Customize tree',
                                                       True, '', False)
        highCustomizability.tooltip = 'Show options to customize the appearance of your tree.'



        # Create group input. Brnching Angle
        groupCmdInputAngle = inputs.addGroupCommandInput(
            'Branching Angle Group', 'Branching Angle')
        groupCmdInputAngle.isExpanded = False
        groupCmdInputAngle.isVisible = False
        groupCmdInputAngle.isEnabledCheckBoxDisplayed = False
        groupChildInputsAngle = groupCmdInputAngle.children
        branchinAngleImage = groupChildInputsAngle.addImageCommandInput(
            'image', 'Image', "resources/Graffle-Trees.png")
        branchinAngleImage.isFullWidth = True
        # Create the slider to get the BranchingAngle
        branchingAngle = groupChildInputsAngle.addIntegerSliderCommandInput('branchingAngle',
                                                                            'branchingAngle',

                                                                            5, 10)
        branchingAngle.isVisible = True
        branchingAngle.setText("narrow", "wide")
        branchingAngle.isFullWidth = True
        branchingAngle.valueOne = 7
        branchingAngle.tooltip = 'Customize how wide the branches will split at each branching.'
  

        # Create group input. Depth of recursion
        groupCmdInputDepth = inputs.addGroupCommandInput(
            'Branching Depth Group', 'Detail Level')
        groupCmdInputDepth.isExpanded = False
        groupCmdInputDepth.isVisible = False
        groupCmdInputDepth.isEnabledCheckBoxDisplayed = False
        groupChildInputsDepth = groupCmdInputDepth.children
        branchingDepthImage = groupChildInputsDepth.addImageCommandInput(
            'image2', 'Image2', "resources/Graffle-Trees-Detail.png")
        branchingDepthImage.isFullWidth = True
        branchDepth = groupChildInputsDepth.addIntegerSliderCommandInput(
            'recursionDepth', 'Depth of branching', 0, 4)
        branchDepth.isVisible = True
        branchDepth.isFullWidth = True
        branchDepth.valueOne = 2
        branchDepth.tooltip = 'Customize how often each branch will split. \nThe higher the value, the more detailed the tree. \nWARNING: High values will increase the processing time.'



        # Create group input. Chaos Value
        groupCmdInputChaos = inputs.addGroupCommandInput(
            'Chaos Group', 'Variation')
        groupCmdInputChaos.isExpanded = False
        groupCmdInputChaos.isVisible = False
        groupCmdInputChaos.isEnabledCheckBoxDisplayed = False
        groupChildInputsChaos = groupCmdInputChaos.children
        chaosImage = groupChildInputsChaos.addImageCommandInput(
            'imageChaos', 'ImageChaos', "resources/Graffle-Trees-Chaos.png")
        chaosImage.isFullWidth = True
        chaosValue = groupChildInputsChaos.addIntegerSliderCommandInput('chaosValue',
                                                                            'chaosValue',

                                                                            0, 10)
        chaosValue.isVisible = True
        chaosValue.setText("orderly", "irregular")
        chaosValue.isFullWidth = True
        chaosValue.valueOne = 5
        chaosValue.tooltip = 'Customize how much variation the tree will have. \nOn a high setting, the trees will have more variation.'






        # Connect to the execute event.
        onExecute = CommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

        # Connect to the inputChanged event.
        onInputChanged = CommandInputChangedHandler()
        cmd.inputChanged.add(onInputChanged)
        handlers.append(onInputChanged)


# Event handler for the execute event.
class CommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        # Code to react to the event.
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Get the values from the command inputs.
        inputs = eventArgs.command.commandInputs

        hasHighCustomizability = inputs.itemById('highCustomizability').value
        baseSize = inputs.itemById('baseSize').value
        forselectioninputs = eventArgs.firingEvent.sender.commandInputs
        selectionInput = forselectioninputs.itemById('surfaceInput')


        #if nothing is selected create tree at origin(0,0,0)
        #otherwise create it at the selected point or center of surface
        if selectionInput.selectionCount== 0:
            pointForTreestart = adsk.core.Point3D.create(0, 0, 0)
        else:
            print(selectionInput.selection(0).entity.objectType) 
            if selectionInput.selection(0).entity.objectType == 'adsk::fusion::BRepFace':
                selectedBRepFace = selectionInput.selection(0).entity
                pointForTreestart = selectedBRepFace.centroid
            if selectionInput.selection(0).entity.objectType == 'adsk::fusion::ConstructionPoint':
                pointForTreestart = selectionInput.selection(0).entity.geometry
            if selectionInput.selection(0).entity.objectType == 'adsk::fusion::BRepVertex':
                point = selectionInput.selection(0).entity
                pointForTreestart = point.geometry
                

        #calculation thinckness and height of the tree and add some randomness
        baseSize = baseSize/30 #to scale correctly to the actual size of the finished tree
        treeThickness = baseSize*2 + random.uniform(0, baseSize)
        treeHeight = baseSize*10 + random.uniform(0, baseSize*3)


        #assign user selected values to branching angle, depth and randomnes
        if hasHighCustomizability:
            branchingAngle = inputs.itemById('branchingAngle').valueOne
            #turn the integer into a rad value betweeen 0.5 to 1.0
            branchingAngle = branchingAngle/10
            recursionDepthValue = inputs.itemById('recursionDepth').valueOne
            chaosValue = inputs.itemById('chaosValue').valueOne
        #otherwise use default values that give nice looking trees
        else:
            branchingAngle = 0.75
            recursionDepthValue = 2
            chaosValue = 5

        # call the method to create the tree
        createTree(treeThickness, treeHeight,
                      pointForTreestart, branchingAngle, recursionDepthValue, chaosValue)




# Event handler for the inputChanged event.
class CommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.InputChangedEventArgs.cast(args)

        # Check the value of the check box.
        changedInput = eventArgs.input
        if changedInput.id == 'highCustomizability':
            inputs = eventArgs.firingEvent.sender.commandInputs

            # get all inputs
            angleGroup = inputs.itemById('Branching Angle Group')
            depthGroup = inputs.itemById('Branching Depth Group')
            chaosGroup = inputs.itemById('Chaos Group')

            # Change the visibility of the inputs related to high customizability
            if changedInput.value == True:
                angleGroup.isVisible = True
                depthGroup.isVisible = True
                chaosGroup.isVisible = True
            else:
                angleGroup.isVisible = False
                depthGroup.isVisible = False
                chaosGroup.isVisible = False

        #the selection input has to be gotten here, instead of in the input function
        if changedInput.id == 'surfaceInput':
            inputs = eventArgs.firingEvent.sender.commandInputs
            selectionInput = inputs.itemById('surfaceInput')
            #print(selectionInput.selection(0).entity.objectType)
            selectedBRepFace = selectionInput.selection(0).entity.objectType


# This method contains the actual code to create the tree
# arguments
# treeThickness radius of the treestump
# treeHeight height of the treestump
# pointForTreestart point at which the tree will be placed
# branchinAngle how wide the branching will open
# recursionDepthValue how many layers of recursion will be called
# chaosValue how value will increase the randomness 
def createTree(treeThickness, treeHeight, pointForTreestart, branchingAngle, recursionDepthValue, chaosValue):
    app = adsk.core.Application.get()
    ui = app.userInterface


    try:
        # get the design  
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('No active Fusion 360 design', 'No Design')
            return


        # Set styles of progress dialog.
        progressDialog = ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.isCancelButtonShown = True

        #calculation of values for progress, use 5^depth as max, so the user will only be surprised by early finish, not late finish
        global forProgressTotal
        forProgressTotal = 5**(recursionDepthValue)

        progressMin = 0
        progressMax = forProgressTotal
        progressIncrement = 1
        # Show dialog
        progressDialog.show(
            'Progress Dialog', '     %p Percent: Finished %v of up to. %m branches     ', progressMin, progressMax, progressIncrement)


        # Get the root component of the active design.
        rootComp = design.rootComponent

        # Create a new sketch on the xy plane.
        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch = sketches.add(xyPlane)

        # Get the SketchCircles collection from an existing sketch.
        circles = sketch.sketchCurves.sketchCircles

        # Get the SketchLines collection from an existing sketch.
        lines = sketch.sketchCurves.sketchLines

        # Get the RevolveFeatures collection.
        revolves = rootComp.features.revolveFeatures

        # Get the ExtrudeFeatures collection.
        extrudes = rootComp.features.extrudeFeatures

        # Get a reference to an appearance in the library.
        lib = app.materialLibraries.itemByName(
            'Fusion 360 Appearance Library')
        libAppear = lib.appearances.itemByName('Plastic - Matte (Yellow)')

        # copy material into the design
        libAppear.copyTo(design)
        yellowAppear = design.appearances.itemByName(libAppear.name)

        # new tree
        # Call an add method on the collection to create a new circle.
        circle = circles.addByCenterRadius(pointForTreestart, treeThickness)

        # Get the first profile from the sketch, which will be the profile defined by the circle in this case.
        prof = sketch.profiles.item(0)

        # Create a extrude input object that defines the input for a extrude feature.
        # When creating the input object, required settings are provided as arguments.
        extInput = extrudes.createInput(prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # extrude the cirlce by treeheight amount
        dist = adsk.core.ValueInput.createByReal(treeHeight)
        extInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
            dist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
        extInput.isSolid = True

        # Create the extrude by calling the add method on the ExtrudeFeatures collection and passing it the ExtrudeInput object.
        #this is where the body is actually added
        ext = extrudes.add(extInput)

        # just get the current trunk that we just extruded
        trunkBody = ext.bodies.item(0)

        # Create a copy of the existing appearance.
        newAppear = design.appearances.addByCopy(
            yellowAppear, 'Color ' + str(1))

        # Edit the "Color" property by setting it to a random brown color.
        colorProp = adsk.core.ColorProperty.cast(
            newAppear.appearanceProperties.itemByName('Color'))
        red = random.randint(100, 180)
        green = random.randint(50, 90)
        blue = random.randint(0, 20)
        colorProp.value = adsk.core.Color.create(
            red, green, blue, 1) 

        # and color the body with this new material
        trunkBody.appearance = newAppear

        #now create the base so the tree can spread out to the base
        # add a sketch for the base for the trunk
        trunkBaseSketch = sketches.add(xyPlane)

        # Get the SketchCircles collection from an existing sketch.
        trunkBaseCircles = trunkBaseSketch.sketchCurves.sketchCircles

        # circle on sketch
        trunkBase = trunkBaseCircles.addByCenterRadius(
            pointForTreestart, 1.6*treeThickness)

        # get profile
        trunkBaseProf = trunkBaseSketch.profiles.item(0)

        # create input object
        trunkBaseExtInput = extrudes.createInput(
            trunkBaseProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # extrude the cirlce by a small length
        trunkBaseDist = adsk.core.ValueInput.createByReal(treeThickness/100)
        trunkBaseExtInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
            trunkBaseDist), adsk.fusion.ExtentDirections.NegativeExtentDirection)
        trunkBaseExtInput.isSolid = True

        # add body
        trunkBaseExt = extrudes.add(trunkBaseExtInput)

        # get body
        trunkBaseBody = trunkBaseExt.bodies.item(0)

        # Get one face and edge of the extrusion body
        face = ext.endFaces.item(0)

        # adds the new sketch for later. sometimes however face is the cylinder instead of the flat face. maybe use endFace istead ::: face = ext.faces.item(1) :::this worked
        sk = rootComp.sketches.add(face)
        #neueSphere = adsk.core.Sphere.create(centerPoint, 10)

        # combine trunk and trunkbase
        #add the body that the others will be added to 
        TargetBody = trunkBody

        #add a collection of bodies that will be added to the target body
        ToolBodies = adsk.core.ObjectCollection.create()
        ToolBodies.add(trunkBaseBody)

        #actually combine the bodies, usual routine, create input object, feature and add
        CombineCutInput = rootComp.features.combineFeatures.createInput(
            TargetBody, ToolBodies)
        CombineCutFeats = rootComp.features.combineFeatures
        CombineCutInput = CombineCutFeats.createInput(
            TargetBody, ToolBodies)
        CombineCutFeats.add(CombineCutInput)

        #get the edge needed for the chamfer
        combinedTrunkEdges = trunkBody.edges
        edges = adsk.core.ObjectCollection.create()
        edges.add(combinedTrunkEdges.item(1))


        #create the chamfer, usual routine, create input object, feature and add
        chamferSize = adsk.core.ValueInput.createByReal(
            0.6*treeThickness)
        chamfers = rootComp.features.chamferFeatures
        chamferInput = chamfers.createInput(edges, False)
        chamferInput.setToEqualDistance(chamferSize)
        chamfer = chamfers.add(chamferInput)

        # define the edges anew after we have the new bod with chamfer
        combinedTrunkEdges = trunkBody.edges
        edges = adsk.core.ObjectCollection.create()
        edges.add(combinedTrunkEdges.item(1))

        #create the fillet, usual routine, create input object, feature and add
        fillets = rootComp.features.filletFeatures
        filletInput = fillets.createInput()
        filletSize = adsk.core.ValueInput.createByReal(0.5*treeHeight)
        filletInput.addConstantRadiusEdgeSet(edges, filletSize, False)
        fillet = fillets.add(filletInput)

        #set to 0 so that it will be passed to callSplit 
        #where 0 means a random branching between 3 and 5 will be executed
        branchFactor = 0

        #if recursion level is 0, the dimensions that fit for the more detailed trees will not 
        #create realisitc proportions. therefore in this case we create the tree differently.
        #add more height to the stump and add the leaves seperately
        if recursionDepthValue == 0:

            # extrude the cirlce (a second time) by treeheight amount
            extInput = extrudes.createInput(
            face, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            dist = adsk.core.ValueInput.createByReal(treeHeight)
            extInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
                dist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
            extInput.isSolid = True
            ext2 = extrudes.add(extInput)

            #update the face
            face = ext2.endFaces.item(0)

            #add color
            ext2.bodies.item(0).appearance = newAppear

            #add the leaves with a different size, suitable to 0 recursion trees
            addLeaves(face, treeThickness*4.5, yellowAppear, progressDialog, chaosValue)
        else:

            #add a collection of branches that will be added to the trunk in the end
            BranchBodies = adsk.core.ObjectCollection.create()


            #for all other trees, pass the required values to the callSplit which will start the recursion
            callSplit(face, treeThickness,
                      recursionDepthValue, newAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)


            #upscale all objects a tiny amount, because the combine feature sometimes wont recognize barely touching bodies 
            # Create a scale input
            #inputColl = adsk.core.ObjectCollection.create()
            #inputColl.add(body)
            
            basePt = sketch.sketchPoints.item(0)
            scaleFactor = adsk.core.ValueInput.createByReal(1.001)
            
            scales = rootComp.features.scaleFeatures
            scaleInput = scales.createInput(BranchBodies, basePt, scaleFactor)
            scale = scales.add(scaleInput)

            trunkBodyColl = adsk.core.ObjectCollection.create()
            trunkBodyColl.add(trunkBody)
            scalesTrunk = rootComp.features.scaleFeatures
            scaleInputTrunk = scalesTrunk.createInput(trunkBodyColl, basePt, scaleFactor)
            scaleTrunk = scalesTrunk.add(scaleInputTrunk)
        


            #actually add all branches to the trunk body, usual routine, create input object, feature and add
            BranchesCombineCutInput = rootComp.features.combineFeatures.createInput(
                TargetBody, BranchBodies)
            BranchesCombineCutFeats = rootComp.features.combineFeatures
            
            BranchesCombineCutInput = BranchesCombineCutFeats.createInput(
                TargetBody, BranchBodies)
            BranchesCombineCutFeats.add(BranchesCombineCutInput)
            #reset collection for next tree
            BranchBodies = adsk.core.ObjectCollection.create()

        #reset the progresscounter after the tree is finished for the nex time a tree is created
        global progresscounter
        progresscounter = 0

        # Hide the progress dialog at the end.
        progressDialog.hide()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


#gets called by the callSplit function for every branch that has to be created
#is the execution part of the recursion (which consists of two functions, createBranch and callSplit)
#creates the branch by adding an extrusion, rotating it and combining it with a loft 
#face, the face on which the branch will be added
#branchWidth, how thick the branch will be
#axis, used to determine in which direction the extrusion will be rotated
#depth, how many more recursions will happen
#yellowAppear, the color to add to the branch
#branchFactor, setting for how many branches will be added
#branchingAngle, how far will the extrusion be rotated
#progressDialog, the process dialog object, must be handed down to the addleaves, where the progress is updated
#chaosValue setting for how much variation will be added to all the parameters
#BranchBodies the collection to add branches to which will later be combined to reduce amount of bodies
def createBranch(face,  branchWidth, axis, depth, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies):
    app = adsk.core.Application.get()
    ui = app.userInterface

    #If progress dialog is cancelled, stop drawing.
    if progressDialog.wasCancelled:
        return

    try:
        # get the design 
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('No active Fusion 360 design', 'No Design')
            return
        else:
            # Get the root component of the active design.
            rootComp = design.rootComponent

            # Get the ExtrudeFeatures collection.
            extrudes = rootComp.features.extrudeFeatures

            # create sketch on old face
            oldFacesSketch = rootComp.sketches.add(face)

            # Get the SketchCircles collection from an existing sketch.
            circles = oldFacesSketch.sketchCurves.sketchCircles

            # Call an add method on the collection to create a new circle.
            circle = circles.addByCenterRadius(
                oldFacesSketch.modelToSketchSpace(face.centroid), branchWidth)

            # Get the profile from the sketch, which will be the profile defined by the circle in this case.
            prof = oldFacesSketch.profiles.item(1)

            # Create a extrude input object that defines the input for a extrude feature.
            # When creating the input object, required settings are provided as arguments.
            extInput = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

            # prepare the cirlce by three times the branchwidth
            dist = adsk.core.ValueInput.createByReal(branchWidth*3)
            extInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
                dist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
            extInput.isSolid = True

            # Create a start extent that starts from a brep face with an offset of three times the branchwidth
            abstand = adsk.core.ValueInput.createByReal(branchWidth*3)
            start_from = adsk.fusion.FromEntityStartDefinition.create(
                face, abstand)
            extInput.startExtent = start_from

            # Create the extrude by calling the add method on the ExtrudeFeatures collection and passing it the ExtrudeInput object.
            ext = extrudes.add(extInput)

            # just get the current brach that we just extruded
            branchbody = ext.bodies.item(0)

            # color branch
            branchbody.appearance = yellowAppear

            # Create a collection of entities (here just the branch) for move
            bodies = adsk.core.ObjectCollection.create()
            bodies.add(branchbody)

            # Create a transform to do move
            transform = adsk.core.Matrix3D.create()
            #the rotation value is based on the branching angle, 
            #depending on the chaos value, a vatiation will be added/subtracted
            transform.setToRotation(branchingAngle + random.uniform(-0.03*chaosValue,0.03*chaosValue) , 
                                    axis, 
                                    face.centroid)

            # Create a move feature, pass bodies and rotation, and execute
            moveFeats = rootComp.features.moveFeatures
            moveFeatureInput = moveFeats.createInput(bodies, transform)
            moveFeats.add(moveFeatureInput)

            # get face for next iteration
            topFace = branchbody.faces.item(1)

            # Create loft feature input
            #loft creates a smooth transistion between new and old branch
            loftFeats = rootComp.features.loftFeatures
            loftInput = loftFeats.createInput(
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            loftSectionsObj = loftInput.loftSections

            #first edge, upper one from the underlying branch
            path1 = adsk.fusion.Path.create(face.edges.item(
                0), adsk.fusion.ChainedCurveOptions.noChainedCurves)
            section1 = loftSectionsObj.add(path1)
            section1.setTangentEndCondition(
                adsk.core.ValueInput.createByReal(1.0))

            #second edge, lower one from the new branch
            path2 = adsk.fusion.Path.create(branchbody.edges.item(
                1), adsk.fusion.ChainedCurveOptions.noChainedCurves)
            section2 = loftSectionsObj.add(path2)
            section2.setTangentEndCondition(
                adsk.core.ValueInput.createByReal(1.0))

            loftInput.isSolid = True

            # Create loft feature
            loftbodies = loftFeats.add(loftInput)

            # color the created loft
            loftbody = loftbodies.bodies.item(0)
            loftbody.appearance = yellowAppear

            #add the branch to the collection to combine later
            BranchBodies.add(loftbody)
            BranchBodies.add(branchbody)
            
            #once branch is created, callSplit is used to create further branchings on top 
            callSplit(topFace, branchWidth,
                      depth, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# actually makes the recursive calls for the function and
# calculates the random values and angles
#face, the face on which the branch will be added
#branchWidth, how thick the branch will be
#depth, how many more recursions will happen
#yellowAppear, the color to add to the branch
#branchFactor, setting for how many branches will be added
# if branchFactor == 0, it will select a random between 3, 4 and 5
#branchingAngle, how far will the extrusion be rotated
#progressDialog, the process dialog object, must be handed down to the addleaves, where the progress is updated
#chaosValue setting for how much variation will be added to all the parameters
#BranchBodies the collection to add branches to which will later be combined to reduce amount of bodies
def callSplit(face, branchWidth, depth, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies):
    app = adsk.core.Application.get()
    ui = app.userInterface

    #If progress dialog is cancelled, stop drawing.
    if progressDialog.wasCancelled:
        return

    try:

        
        if depth == 0:
            #the recursion is done, add the leaves at end of branch
            leavSize = branchWidth*5
            addLeaves(face, leavSize, yellowAppear, progressDialog, chaosValue)
        else:
            #logic that decides how many branches to call
            branchDecision = branchFactor
            #branchFactor == 0 is the setting that will lead to a random number of splits between 3 and 5 
            if branchFactor == 0:
                branchDecision = random.randint(3, 5)

            #depending on the branchDecision, 3,4, or 5 branches will be created
            #thickfactor (depends on chaosvalue) determines how much thinner the next branch will be
            #axis these have precalculated values so that the rotation will go into the appropriate angles for the respective nr of branchings
            #createBranch is called with new thickness, depth reduced by one
            if branchDecision == 3:
                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis = adsk.core.Vector3D.create(0.0, 1.0, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis = adsk.core.Vector3D.create(1.0, -0.577, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis = adsk.core.Vector3D.create(-1, -0.577, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

            if branchDecision == 4:
                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(axis1, 0.0, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, axis1, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, -axis1, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(-axis1, 0.0, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

            if branchDecision == 5:
                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis = adsk.core.Vector3D.create(0.0, 1.0, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis = adsk.core.Vector3D.create(1.0, 0.325, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis = adsk.core.Vector3D.create(-1, 0.325, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis = adsk.core.Vector3D.create(0.727, -1.0, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis = adsk.core.Vector3D.create(-0.727, -1, 0.0)
                createBranch(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue, BranchBodies)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

#adds a green sphere at the end of each branch
#face, the face on which the branch will be added
#leavesRadius how big the leaves will be
#yellowAppear, the old color to add to the branch, will be modified to green
#progressDialog, the process dialog object, it will finally be updated here after each branach is finished 
#chaosValue setting for how much variation will be added to all the parameters
def addLeaves(face, leavesRadius, yellowAppear, progressDialog, chaosValue):
    app = adsk.core.Application.get()
    ui = app.userInterface

    #If progress dialog is cancelled, stop drawing.
    if progressDialog.wasCancelled:
        return

    try:
        # get the design
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('No active Fusion 360 design', 'No Design')
            return
        else:
            # Get the root component of the active design.
            rootComp = design.rootComponent
            # prepares the sphere, using only the centerpoint of the surface though.
            bodies = rootComp.bRepBodies
            tBrep = adsk.fusion.TemporaryBRepManager.get()
            centerPoint = face.centroid
            sphereBody = tBrep.createSphere(centerPoint, leavesRadius)

            # Create a base feature
            baseFeats = rootComp.features.baseFeatures
            baseFeat = baseFeats.add()

            # adds the sphere.
            baseFeat.startEdit()
            body = bodies.add(sphereBody, baseFeat)

            # Create a copy of the existing appearance.
            #assign a random name, so we can have different shades of green in the canopy
            newAppear = design.appearances.addByCopy(
                yellowAppear, 'Color ' + str(random.randint(0, 10000000000)))

            # Edit the "Color" property by setting it to a random green color.
            colorProp = adsk.core.ColorProperty.cast(
                newAppear.appearanceProperties.itemByName('Color'))
            red = random.randint(0, 30)
            green = random.randint(100, 200)
            blue = random.randint(0, 30)
            colorProp.value = adsk.core.Color.create(
                red, green, blue, 1) 

            # get the current sphere to color
            leavestocolor = body

            # and color the sphere with this new material
            leavestocolor.appearance = newAppear

            #stop the editing, the speres have to be added in this way. otherwise they are not a real body
            baseFeat.finishEdit()

            #update the progress counter values
            global progresscounter
            progresscounter = progresscounter + 1

            # Update progress value of progress dialog
            progressDialog.progressValue = progresscounter




    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

