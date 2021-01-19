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
        baseSize = inputs.addIntegerSpinnerCommandInput(
            'baseSize', 'Tree size', 5, 30, 1, 10)
        baseSize.isFullWidth = False

        # Create a check box to get if high cusomizability is desired
        highCustomizability = inputs.addBoolValueInput('highCustomizability', 'Customize tree',
                                                       True, '', False)



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
        # be 30 to 60 of whatever the current document unit is.
        branchingAngle = groupChildInputsAngle.addIntegerSliderCommandInput('branchingAngle',
                                                                            'branchingAngle',

                                                                            5, 10)
        branchingAngle.isVisible = True
        branchingAngle.setText("narrow", "wide")
        branchingAngle.isFullWidth = True
        branchingAngle.valueOne = 7


        # Create group input. Depth of recursion
        groupCmdInputDepth = inputs.addGroupCommandInput(
            'Branching Depth Group', 'Branching Depth')
        groupCmdInputDepth.isExpanded = False
        groupCmdInputDepth.isVisible = False
        groupCmdInputDepth.isEnabledCheckBoxDisplayed = False
        groupChildInputsDepth = groupCmdInputDepth.children
        branchingDepthImage = groupChildInputsDepth.addImageCommandInput(
            'image2', 'Image2', "resources/Graffle-Trees-Detail.png")
        branchingDepthImage.isFullWidth = True
        branchDepth = groupChildInputsDepth.addIntegerSliderCommandInput(
            'recursionDepth', 'Recursion Depth', 0, 4)
        branchDepth.isVisible = True
        branchDepth.isFullWidth = True
        branchDepth.valueOne = 2



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
        treeThickness = baseSize*2 + random.randint(0, round(baseSize))
        treeHeight = baseSize*10 + random.randint(0, baseSize*3)


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
            recursionDepthValue = 3
            chaosValue = 5

        # call the method to create the tree
        createDonuts(treeThickness, treeHeight,
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
def createDonuts(treeThickness, treeHeight, pointForTreestart, branchingAngle, recursionDepthValue, chaosValue):
    app = adsk.core.Application.get()
    ui = app.userInterface
    #ui.messageBox('in createDonuts')

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

        #calculation of values for progress
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

        ###########################
        # CODE REVIEW UNTIL HERE; TBC   
        ###########################

        # new tree
        # Call an add method on the collection to create a new circle.
        circle = circles.addByCenterRadius(
            # adsk.core.Point3D.create(5*i, 0, 0), treeThickness)
            pointForTreestart, treeThickness)



        # Get the first profile from the sketch, which will be the profile defined by the circle in this case.
        prof = sketch.profiles.item(0)

        # Create a extrude input object that defines the input for a extrude feature.
        # When creating the input object, required settings are provided as arguments.
        #revInput = revolves.createInput(prof, axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # NEW
        extInput = extrudes.createInput(
            prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # extrude the cirlce by treeheight amount

        dist = adsk.core.ValueInput.createByReal(treeHeight)
        extInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
            dist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
        extInput.isSolid = True

        # Create the extrude by calling the add method on the ExtrudeFeatures collection and passing it the ExtrudeInput object.
        #rev = revolves.add(revInput)
        # NEW
        ext = extrudes.add(extInput)
        #ext = extrudes.addSimple()

        # ---------------------------
        # Update progress value of progress dialog
    #    progressDialog.progressValue = progress+progressIncrement
        # ---------------------------

        # print(extrudes.endFaces.count)
        # print(extrudes.endFaces.classType)
        # print(extrudes.endFaces.objectType)

        # get component collection
        #comp = rev.parentComponent

        # used for debugging
        # print(rev.objectType)
        # print(libAppear.objectType)
        # print(libAppear.name)

        # get the current body
        # bodytocolor = rootComp.bRepBodies.item(i)
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
            red, green, blue, 1)  # use brown for trunk

        # and color the body with this new material
        trunkBody.appearance = newAppear

        # ---------------------------
        # Update progress value of progress dialog
    #    progressDialog.progressValue = progress+progressIncrement
        # ---------------------------

        # add the base for the trunk
        trunkBaseSketch = sketches.add(xyPlane)

        # Get the SketchCircles collection from an existing sketch.
        trunkBaseCircles = trunkBaseSketch.sketchCurves.sketchCircles

        # circle on sketch
        trunkBase = trunkBaseCircles.addByCenterRadius(
            pointForTreestart, 2*treeThickness)
        # get profile
        trunkBaseProf = trunkBaseSketch.profiles.item(0)
        # create input object
        trunkBaseExtInput = extrudes.createInput(
            trunkBaseProf, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        # extrude the cirlce by treeheight amount
        trunkBaseDist = adsk.core.ValueInput.createByReal(1)
        trunkBaseExtInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
            trunkBaseDist), adsk.fusion.ExtentDirections.NegativeExtentDirection)
        trunkBaseExtInput.isSolid = True
        # add body
        trunkBaseExt = extrudes.add(trunkBaseExtInput)
        # get body
        trunkBaseBody = trunkBaseExt.bodies.item(0)

        # ---------------------------
        # Update progress value of progress dialog
    #    progressDialog.progressValue = progress+progressIncrement
        # ---------------------------

        # Get one face and edge of the extrusion body
        #face = extrudes.endFaces.item(0)
        # print("extrudes")
        # print(face.objectType)
        # exttudes has no endfaces
        #face = extInput.endFaces.item(0)
        # print("extInput")
        # print(face.objectType)
        # has no endfaces
        # adds the sketch. sometimes however face is the cylinder instead of the flat face. maybe use endFace istead ::: face = ext.faces.item(1) :::this worked
        face = ext.endFaces.item(0)
        # print("ext")
        # print(face.objectType)
        # print(face.area)
        # print(face.geometry)
        # print(face.evaluator)
        # print(face.body)
        # print(face.attributes)
        #edge = face.edges.item(0)

        # Create a slant construction plane with an angle of 45 deg on the xZConstructionPlane
        #planeInput = rootComp.constructionPlanes.createInput()
        #planeInput.setByAngle(edge, adsk.core.ValueInput.createByString('45 deg'), rootComp.xZConstructionPlane)
        #plane = rootComp.constructionPlanes.add(planeInput)

        # Create another sketch containing a circle profile on the slant plane
        #toolSketch = rootComp.sketches.add(plane)
        #sketchCircles = toolSketch.sketchCurves.sketchCircles
        #circle = sketchCircles.addByCenterRadius(point0, 3)

        # Create a sketch.
        #sketchOnCylinder = sketches.add(face)
        #surface = ext.faces.item(0)
        # print(surface.objectType)

        #centerPoint = face.centroid
        # adds the sketch. sometimes however face is the cylinder instead of the flat face. maybe use endFace istead
        sk = rootComp.sketches.add(face)
        #neueSphere = adsk.core.Sphere.create(centerPoint, 10)

        # combine trunk and trunkbase
        TargetBody = trunkBody

        ToolBodies = adsk.core.ObjectCollection.create()
        ToolBodies.add(trunkBaseBody)

        # print("ToolBodies.objectType")
        # print(ToolBodies.objectType)

        CombineCutInput = rootComp.features.combineFeatures.createInput(
            TargetBody, ToolBodies)

        CombineCutFeats = rootComp.features.combineFeatures
        CombineCutInput = CombineCutFeats.createInput(
            TargetBody, ToolBodies)
        CombineCutFeats.add(CombineCutInput)

        combinedTrunkEdges = trunkBody.edges
        #print("combined edges")
        # print(combinedTrunkEdges.count)
        # print(combinedTrunkEdges.objectType)

        chamferSize = adsk.core.ValueInput.createByReal(
            0.6*treeThickness)
        # chamfersample
        # prepare chamfer
        #faces = sweep.faces
        edges = adsk.core.ObjectCollection.create()
        edges.add(combinedTrunkEdges.item(1))

        chamfers = rootComp.features.chamferFeatures

        chamferInput = chamfers.createInput(edges, False)
        chamferInput.setToEqualDistance(chamferSize)

        chamfer = chamfers.add(chamferInput)

        # define the edges anew after we have the new bod with chamfer
        combinedTrunkEdges = trunkBody.edges
        edges = adsk.core.ObjectCollection.create()
        edges.add(combinedTrunkEdges.item(1))
        # print(edges.count)

        # fillet
        fillets = rootComp.features.filletFeatures

        filletInput = fillets.createInput()
        filletSize = adsk.core.ValueInput.createByReal(0.5*treeHeight)
        filletInput.addConstantRadiusEdgeSet(edges, filletSize, False)
        # filletInput.isRollingBallCorner(True)

        fillet = fillets.add(filletInput)



        # ---------------------------
        # Update progress value of progress dialog
    #    progressDialog.progressValue = progress+progressIncrement
        # ---------------------------



        branchFactor = 0
        
        #call for add leaves because the size of the canopy is otherwise too big at recursion level 0
        if recursionDepthValue == 0:
            extInput = extrudes.createInput(
            face, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

            # extrude the cirlce by treeheight amount

            dist = adsk.core.ValueInput.createByReal(treeHeight)
            extInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
                dist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
            extInput.isSolid = True

            # Create the extrude by calling the add method on the ExtrudeFeatures collection and passing it the ExtrudeInput object.
            #rev = revolves.add(revInput)
            # NEW
            ext2 = extrudes.add(extInput)
            face = ext2.endFaces.item(0)
            ext2.bodies.item(0).appearance = newAppear


            addLeaves(face, treeThickness*5, yellowAppear, progressDialog, chaosValue)
        else:
            callSplit(face, treeThickness,
                      recursionDepthValue, newAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

        #reset the progresscounter after the tree is finished for the nex time a tree is created
        global progresscounter
        progresscounter = 0

        # in the end combine objects to one
        # color the bodys by actual reference instead of getting the number from the total bodies. will create issues with existing bodies
        # close program and start again. does fusion keep the material names that we created last time or does it store them internally
        # to create unique handle if needed: combination of all random values
        # hasan: color to body itself
        # simon: randomize integration with ui

        # Hide the progress dialog at the end.
        progressDialog.hide()

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def recursiveBranching(face,  branchWidth, axis, depth, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue):
    app = adsk.core.Application.get()
    ui = app.userInterface
    #ui.messageBox('in createDonuts')


    #If progress dialog is cancelled, stop drawing.
    if progressDialog.wasCancelled:
        return


    try:
        # get the design  //selfmade
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
            #topFace = branchbody.faces.item(1)
            oldFacesSketch = rootComp.sketches.add(face)

            # Get the SketchCircles collection from an existing sketch.
            circles = oldFacesSketch.sketchCurves.sketchCircles

            # Call an add method on the collection to create a new circle.
            circle = circles.addByCenterRadius(
                oldFacesSketch.modelToSketchSpace(face.centroid), branchWidth)
            # adsk.core.Point3D.create(0, 0, 0), branchWidth)

            # Get the first profile from the sketch, which will be the profile defined by the circle in this case.
            prof = oldFacesSketch.profiles.item(1)

            # Create a extrude input object that defines the input for a extrude feature.
            # When creating the input object, required settings are provided as arguments.
            #revInput = revolves.createInput(prof, axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            extInput = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

            # extrude the cirlce by treeheight amount
            dist = adsk.core.ValueInput.createByReal(branchWidth*3)
            extInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
                dist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
            extInput.isSolid = True

            # Create a start extent that starts from a brep face with an offset of 10 mm.
            # CURRENTLY DOESNT ATT THE DISTANCE BECAUSE FOR SOME REASON THE CIRCLE ON THE SKETCH IS ALREADY SO FAR AWAY
            abstand = adsk.core.ValueInput.createByReal(branchWidth*3)
            start_from = adsk.fusion.FromEntityStartDefinition.create(
                face, abstand)
            extInput.startExtent = start_from

            # Create the extrude by calling the add method on the ExtrudeFeatures collection and passing it the ExtrudeInput object.
            ext = extrudes.add(extInput)

            # just get the current brach that we just extruded
            branchbody = ext.bodies.item(0)
            #print("in recursion branchbody objecttype")
            # print(branchbody.objectType)

            # color branch
            branchbody.appearance = yellowAppear

            # Create a collection of entities for move
            # OR IS IT HERE, IS OBJECTCOLLECTION GLOBAL?
            bodies = adsk.core.ObjectCollection.create()
            bodies.add(branchbody)

            # Create a transform to do move
            #fromVector = adsk.core.Vector3D.create(0.0, 00.0, 1.0)
            #toVector = adsk.core.Vector3D.create(1.0, 1.0, 1.0)
            transform = adsk.core.Matrix3D.create()
            #yAxis = adsk.core.Vector3D.create(0.0,1.0,0.0)
            #transform.setWithCoordinateSystem(face.centroid, xAxis, yAxis, zAxis)

            # ROTATION ANGLE CAN ALSO BE RANDOMIZED OR SHOULD MAYBE BE ADJUSTED ACCORDING TO HOW MANY DEPTH STEPS THERE WILL BE
            #branchAngle = random.uniform(0.5, 1.0)
            transform.setToRotation(branchingAngle + random.uniform(-0.03*chaosValue,0.03*chaosValue) , 
                                    axis, 
                                    face.centroid)
            # transform.setToRotateTo(0.25,, face.centroid)

            # Create a move feature
            # moveFeats = adsk.fusion.MoveFeature.
            moveFeats = rootComp.features.moveFeatures
            moveFeatureInput = moveFeats.createInput(bodies, transform)
            moveFeats.add(moveFeatureInput)

            # just get the current brach that we just moved
            #branchbody = moveFeats.bodies.item(0)
            #print("in recursion branchbody objecttype")
            # print(branchbody.objectType)

            # create face and sketch for next iteration
            # I THINK THIS IS WHERE THE RECURSION IS FAILING; THE TOPFACE IS ALWAYS THE SAME ITEM THEN
            topFace = branchbody.faces.item(1)
            #
            # print(topFace.objectType)
            #newSketch = rootComp.sketches.add(topFace)

            # Create loft feature input
            loftFeats = rootComp.features.loftFeatures
            loftInput = loftFeats.createInput(
                adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            loftSectionsObj = loftInput.loftSections

            path1 = adsk.fusion.Path.create(face.edges.item(
                0), adsk.fusion.ChainedCurveOptions.noChainedCurves)
            section1 = loftSectionsObj.add(path1)
            section1.setTangentEndCondition(
                adsk.core.ValueInput.createByReal(1.0))

            #section2 = loftSectionsObj.add(branchbody.faces.item(2))
            path2 = adsk.fusion.Path.create(branchbody.edges.item(
                1), adsk.fusion.ChainedCurveOptions.noChainedCurves)
            section2 = loftSectionsObj.add(path2)
            section2.setTangentEndCondition(
                adsk.core.ValueInput.createByReal(1.0))

            loftInput.isSolid = True

            # Create loft feature
            loftbodies = loftFeats.add(loftInput)

            # color loft
            loftbody = loftbodies.bodies.item(0)
            loftbody.appearance = yellowAppear

            callSplit(topFace, branchWidth,
                      depth, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

            # print("Depth")
            # print(depth)
            # print("completed")

            # call recusrively
            #recursiveBranching(topFace, branchWidth*0.6, axis, depth-1, yellowAppear)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# actually makes the recursive calls for the function and
# calculates the random values and angles
# if branchFactor == 0, it will select a random between 3, 4 and 5
def callSplit(face, branchWidth, depth, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue):
    app = adsk.core.Application.get()
    ui = app.userInterface
    #ui.messageBox('in createDonuts')

    #If progress dialog is cancelled, stop drawing.
    if progressDialog.wasCancelled:
        return

    try:
        branchDecision = branchFactor

        if depth == 0:
            leavSize = branchWidth*5
            addLeaves(face, leavSize, yellowAppear, progressDialog, chaosValue)
        else:

            if branchFactor == 0:
                branchDecision = random.randint(3, 5)

            if branchDecision == 3:
                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, 1.0, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

                #thickFactor = random.uniform(0.5, 0.8)
                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(1.0, -0.577, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(-1, -0.577, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

            if branchDecision == 4:
                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(axis1, 0.0, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, axis1, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, -axis1, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(-axis1, 0.0, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

            if branchDecision == 5:
                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, 1.0, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(1.0, 0.325, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(-1, 0.325, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.727, -1.0, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

                thickFactor = 0.65 + random.uniform(-0.03*chaosValue, 0.03*chaosValue)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(-0.727, -1, 0.0)
                recursiveBranching(face, branchWidth *
                                   thickFactor, axis, depth-1, yellowAppear, branchFactor, branchingAngle, progressDialog, chaosValue)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def addLeaves(face, leavesRadius, yellowAppear, progressDialog, chaosValue):
    app = adsk.core.Application.get()
    ui = app.userInterface
    #ui.messageBox('in createDonuts')

    #If progress dialog is cancelled, stop drawing.
    if progressDialog.wasCancelled:
        return

    try:
        # get the design  //selfmade
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('No active Fusion 360 design', 'No Design')
            return
        else:
            # Get the root component of the active design.
            rootComp = design.rootComponent
            # prepares the sphere, using only the centerpoint of the surface though.
            bodies = rootComp.bRepBodies
            # maybe possible with permanent?
            tBrep = adsk.fusion.TemporaryBRepManager.get()
            centerPoint = face.centroid
            sphereBody = tBrep.createSphere(centerPoint, leavesRadius)

            # Create a base feature
            baseFeats = rootComp.features.baseFeatures
            baseFeat = baseFeats.add()

            # adds the sphere. we lose reference to the cylinder though it seems. at least in the UI
            # reference was lost because of the edit state. once its done we see the cylinder again

            baseFeat.startEdit()

            body = bodies.add(sphereBody, baseFeat)

            # Create a copy of the existing appearance.
            newAppear = design.appearances.addByCopy(
                yellowAppear, 'Color ' + str(random.randint(0, 10000000000)))

            # Edit the "Color" property by setting it to a green color.
            colorProp = adsk.core.ColorProperty.cast(
                newAppear.appearanceProperties.itemByName('Color'))
            red = random.randint(0, 30)
            green = random.randint(100, 200)
            blue = random.randint(0, 30)
            colorProp.value = adsk.core.Color.create(
                red, green, blue, 1)  # use green for leaves

            # get the current body
            # leavestocolor = rootComp.bRepBodies.item(i+1)
            # get the current sphere to color
            leavestocolor = body

            # and color the sphere with this new material
            #print("body object type is")
            # print(body.objectType)
            # print(newAppear.appearanceProperties.itemByName('Color'))
            leavestocolor.appearance = newAppear

            #circleTest(leavestocolor, leavesRadius, centerPoint)

            baseFeat.finishEdit()

            global progresscounter
            progresscounter = progresscounter + 1
            print(str(progresscounter) + '/' + str(forProgressTotal))


            # ---------------------------
            # Update progress value of progress dialog
            progressDialog.progressValue = progresscounter
            # ---------------------------



    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def circleTest(sphere, sphereRad, center):
    app = adsk.core.Application.get()
    ui = app.userInterface
    try:
        design = adsk.fusion.Design.cast(app.activeProduct)
        root = adsk.fusion.Component.cast(design.rootComponent)

        sk = adsk.fusion.Sketch.cast(
            root.sketches.add(root.xYConstructionPlane))
        circles = adsk.fusion.SketchCircles.cast(sk.sketchCurves.sketchCircles)

        latitude = -math.pi * 0.25
        longitude = 0
        #sphereRad = 5
        circleRad = 1
        height = math.sqrt(math.pow(sphereRad, 2) - math.pow(circleRad, 2))
        #center = adsk.core.Point3D.create(0, 0, 0)

        for lat_step in range(8):
            for long_step in range(3):
                # Create a circle on the X-Y plane centered at the origin
                circ = circles.addByCenterRadius(
                    adsk.core.Point3D.create(0, 0, 0), circleRad)

                # Convert the latitude and longitude to XYZ (ECEF)
                # https://en.wikipedia.org/wiki/Geographic_coordinate_conversion
                radSquare = math.pow(sphereRad, 2)
                nlat = radSquare / math.sqrt(radSquare * math.pow(
                    math.cos(latitude), 2) + radSquare * math.pow(math.sin(latitude), 2))
                nlat = 0
                x = (nlat + height) * math.cos(latitude) * math.cos(longitude)
                y = (nlat + height) * math.cos(latitude) * math.sin(longitude)
                z = (nlat + height) * math.sin(latitude)

                # Create the Z vector along the vector defined by sphere center to the point.
                pnt = adsk.core.Point3D.create(x, y, z)
                zVec = center.vectorTo(pnt)
                zVec.normalize()

                # Create an arbitrary X axis that is not paralle with the Z axis.
                xVec = adsk.core.Vector3D.create(1, .05, 0.05)

                # Create the Y axis by crossing the Z and X vectors.
                yVec = zVec.crossProduct(xVec)
                yVec.normalize()

                # Create the good X axis by crossing the Y and Z vectors.
                xVec = yVec.crossProduct(zVec)
                xVec.normalize()

                # Create a matrix using the origin and vectors computed.
                mat = adsk.core.Matrix3D.create()
                mat.setWithCoordinateSystem(pnt, xVec, yVec, zVec)

                # Move the circle using the defined matrix.
                objs = adsk.core.ObjectCollection.create()
                objs.add(circ)
                sk.move(objs, mat)

                # Adjust the longitude for the next circle
                longitude = longitude + (math.pi * 0.25)

            # Reset the longitude angle.
            longitude = -math.pi * 0.25

            # Adjust the latitude for the set of longitude circles
            latitude = latitude + (math.pi * 0.25)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
