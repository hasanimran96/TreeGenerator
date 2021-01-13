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


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        #ui.messageBox('In run function')

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('NewButtonDefIdPython',
                                                   'EnviroGen',
                                                   'Generate new enviromental assets, such as trees with the ease of a click',
                                                   './resources/Button')

        # Connect to the command created event.
        sampleCommandCreated = SampleCommandCreatedEventHandler()
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


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('NewButtonDefIdPython')
        if cmdDef:
            cmdDef.deleteMe()

        addinsPanel = ui.allToolbarPanels.itemById('SolidCreatePanel')
        cntrl = addinsPanel.controls.itemById('NewButtonDefIdPython')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler for the commandCreated event.
class SampleCommandCreatedEventHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandCreatedEventArgs.cast(args)
        cmd = eventArgs.command

        # Get the CommandInputs collection to create new command inputs.
        inputs = cmd.commandInputs

        # Create a selection input.
        selectionInput = inputs.addSelectionInput(
            'surfaceInput', 'Select', 'Basic select command input')
        selectionInput.setSelectionLimits(0, 1)
        selectionInput.addSelectionFilter('Faces')
        # selectionInput.addSelectionFilter('ConstructionPlanes')

        # Create the value input to get the bbase size of the Tree
        baseSize = inputs.addIntegerSpinnerCommandInput(
            'baseSize', 'Tree size', 5, 30, 1, 10)

        # Create a check box to get if high cusomizability is desired
        highCustomizability = inputs.addBoolValueInput('highCustomizability', 'Customize tree',
                                                       True, '', False)

        # Create the slider to get the thickness setting the range of the slider to
        # be 10 to 20 of whatever the current document unit is.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)

        minVal = des.unitsManager.convert(
            10, des.unitsManager.defaultLengthUnits, 'mm')
        maxVal = des.unitsManager.convert(
            20, des.unitsManager.defaultLengthUnits, 'mm')
        thickness = inputs.addIntegerSliderCommandInput('thickness',
                                                        'Trunk thickness',

                                                        10, 20, True)
        thickness.isVisible = False

        # Create the slider to get the length setting the range of the slider to
        # be 100 to 200 of whatever the current document unit is.
        minVal = des.unitsManager.convert(
            100, des.unitsManager.defaultLengthUnits, 'mm')
        maxVal = des.unitsManager.convert(
            200, des.unitsManager.defaultLengthUnits, 'mm')
        treeHeight = inputs.addIntegerSliderCommandInput('height',
                                                         'Trunk height',

                                                         100, 200, True)
        # des.unitsManager.defaultLengthUnits,
        treeHeight.isVisible = False

        print("created the length slider")
        print(inputs.count)

        # Create the slider to get the treetop size range of the slider to
        # be 30 to 60 of whatever the current document unit is.
        minVal = des.unitsManager.convert(
            10, des.unitsManager.defaultLengthUnits, 'mm')
        maxVal = des.unitsManager.convert(
            20, des.unitsManager.defaultLengthUnits, 'mm')
        treetops = inputs.addIntegerSliderCommandInput('treetops',
                                                       'Treetop diameter',

                                                       30, 60, True)
        treetops.isVisible = False

        # Connect to the execute event.
        onExecute = SampleCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)

        # Connect to the inputChanged event.
        onInputChanged = SampleCommandInputChangedHandler()
        cmd.inputChanged.add(onInputChanged)
        handlers.append(onInputChanged)


# Event handler for the execute event.
class SampleCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        # Code to react to the event.
        app = adsk.core.Application.get()
        ui = app.userInterface
        #ui.messageBox('Ready for a Tree?')

        # Get the values from the command inputs.
        inputs = eventArgs.command.commandInputs

        hasHighCustomizability = inputs.itemById('highCustomizability').value

        baseSize = inputs.itemById('baseSize').value
        print("base size")
        print(baseSize)

        donutMinThickness = inputs.itemById('thickness').valueOne
        donutMaxThickness = inputs.itemById('thickness').valueTwo
        print("donutMinThickness")
        print(donutMinThickness)
        print("donutMaxThickness")
        print(donutMaxThickness)

        treeMinHeight = inputs.itemById('height').valueOne
        treeMaxHeight = inputs.itemById('height').valueTwo
        print("got all values except leaves")

        treetopsMin = inputs.itemById('treetops').valueOne
        treetopsMax = inputs.itemById('treetops').valueTwo
        print("got all values and treetops leaves")

        # GETTING THE SURFACE DOESNT WORK, IT JUST DOESNT PRGORSS FROM HERE; WE HAD A SIMILAR PROBLEM BEFORE
       # selectedSurfaceInput = inputs.itemById('surfaceInput')
        # next line is okay, debugging shows that the count is 1 as expected. don't know why next line code stops
       # if selectedSurface.selectionCount == 0:
       #     selectedSurface = selectedSurfaceInput.selection(0).entity
        #flache = input.itemById('surfaceInput').selection(0)
        #print('nach dem input getten')

        forselectioninputs = eventArgs.firingEvent.sender.commandInputs
        selectionInput = forselectioninputs.itemById('surfaceInput')

        # (selectionInput.selection(0).entity.objectType)
        selectedBRepFace = selectionInput.selection(0).entity

        # assign values to random values based on either base size or selected ranges if high customizability is desired
        if hasHighCustomizability:
            donutThickness = random.randint(
                donutMinThickness, donutMaxThickness)
            print("donutThickness")
            print(donutThickness)
            treeHeight = random.randint(treeMinHeight, treeMaxHeight)
            leavesRadius = random.randint(treetopsMin, treetopsMax)
        else:
            donutThickness = baseSize + random.randint(0, round(baseSize/2))
            treeHeight = baseSize*10 + random.randint(0, baseSize*3)
            print("donutThickness")
            print(donutThickness)
            leavesRadius = baseSize*5 + random.randint(0, baseSize)

        # call the method to create the tree
        createDonuts(donutThickness, treeHeight,
                     leavesRadius, selectedBRepFace)

        # ui.messageBox('function createDonuts is completed')

        # call mouseClick method
        # mouseClick()


# Event handler for the inputChanged event.
class SampleCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.InputChangedEventArgs.cast(args)

        # Check the value of the check box.
        changedInput = eventArgs.input
        if changedInput.id == 'highCustomizability':
            inputs = eventArgs.firingEvent.sender.commandInputs
            scaleInput = inputs.itemById('heightScale')

            # get all inputs
            thicknessInput = inputs.itemById('thickness')
            heightInput = inputs.itemById('height')
            treetopInput = inputs.itemById('treetops')

            # Change the visibility of the inputs related to high customizability
            if changedInput.value == True:
                thicknessInput.isVisible = True
                heightInput.isVisible = True
                treetopInput.isVisible = True
            else:
                thicknessInput.isVisible = False
                heightInput.isVisible = False
                treetopInput.isVisible = False

        # for some reason acessing it from here works, but not from the execute command handler or the createDOnuts (if you save it here into a global variable)
        if changedInput.id == 'surfaceInput':
            inputs = eventArgs.firingEvent.sender.commandInputs
            selectionInput = inputs.itemById('surfaceInput')

            print(selectionInput.selection(0).entity.objectType)
            selectedBRepFace = selectionInput.selection(0).entity.objectType


# This method contains the actual code to create the tree
# arguments
# donutThickness radius of the rings
# treeHeight height of the tree
# leavesRadius radius of the treetop
def createDonuts(donutThickness, treeHeight, leavesRadius, selectedBRepFace):
    app = adsk.core.Application.get()
    ui = app.userInterface
    #ui.messageBox('in createDonuts')

    try:
        # get the design  //selfmade
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('No active Fusion 360 design', 'No Design')
            return

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

        # NEW
        # Get the ExtrudeFeatures collection.
        extrudes = rootComp.features.extrudeFeatures

        # Get a reference to an appearance in the library.
        lib = app.materialLibraries.itemByName('Fusion 360 Appearance Library')
        libAppear = lib.appearances.itemByName('Plastic - Matte (Yellow)')

        # copy material into the design
        libAppear.copyTo(design)
        yellowAppear = design.appearances.itemByName(libAppear.name)

        # only one tree
        i = 0
        while i <= (0):

            pointForTreestart = selectedBRepFace.centroid

            # new tree
            # Call an add method on the collection to create a new circle.
            circle = circles.addByCenterRadius(
                # adsk.core.Point3D.create(5*i, 0, 0), donutThickness)
                pointForTreestart, donutThickness)

            # Call an add method on the collection to create a new line.
            axis = lines.addByTwoPoints(adsk.core.Point3D.create(
                5*i-1, -4, 0), adsk.core.Point3D.create(5*i+1, -4, 0))

            # Get the first profile from the sketch, which will be the profile defined by the circle in this case.
            prof = sketch.profiles.item(i)

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
            trunkBody = ext.bodies.item(i)

            # Create a copy of the existing appearance.
            newAppear = design.appearances.addByCopy(
                yellowAppear, 'Color ' + str(i+1))

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

            # add the base for the trunk
            trunkBaseSketch = sketches.add(xyPlane)

            # Get the SketchCircles collection from an existing sketch.
            trunkBaseCircles = trunkBaseSketch.sketchCurves.sketchCircles

            # circle on sketch
            trunkBase = trunkBaseCircles.addByCenterRadius(
                pointForTreestart, 2*donutThickness)
            # get profile
            trunkBaseProf = trunkBaseSketch.profiles.item(i)
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
            trunkBaseBody = trunkBaseExt.bodies.item(i)

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

            chamferSize = adsk.core.ValueInput.createByReal(0.6*donutThickness)
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

            i = i+1

        totalDepth = 4

        global forProgressTotal
        forProgressTotal = 4**(totalDepth)

        branchFactor = 0

        callSplit(face, donutThickness, axis, totalDepth, newAppear, branchFactor)

        # in the end combine objects to one
        # color the bodys by actual reference instead of getting the number from the total bodies. will create issues with existing bodies
        # close program and start again. does fusion keep the material names that we created last time or does it store them internally
        # to create unique handle if needed: combination of all random values
        # hasan: color to body itself
        # simon: randomize integration with ui

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def recursiveBranching(face,  branchWidth, axis, depth, yellowAppear, branchFactor):
    app = adsk.core.Application.get()
    ui = app.userInterface
    #ui.messageBox('in createDonuts')

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
            branchAngle = random.uniform(0.5, 1.0)
            transform.setToRotation(branchAngle, axis, face.centroid)
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



            callSplit(topFace, branchWidth, axis, depth, yellowAppear, branchFactor)

            # print("Depth")
            # print(depth)
            # print("completed")

            # call recusrively
            #recursiveBranching(topFace, branchWidth*0.6, axis, depth-1, yellowAppear)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))



#actually makes the recursive calls for the function and 
#calculates the random values and angles 
#if branchFactor == 0, it will select a random between 3, 4 and 5
def callSplit(face, branchWidth, axis, depth, yellowAppear, branchFactor):
    app = adsk.core.Application.get()
    ui = app.userInterface
    #ui.messageBox('in createDonuts')

    try:
        branchDecision = branchFactor

        if depth == 0:
            leavSize = branchWidth*10
            addLeaves(face, leavSize, yellowAppear)
        else:        

            if branchFactor == 0:
                branchDecision = random.randint(3,5)

            if branchDecision == 3:
                thickFactor = random.uniform(0.5, 0.8)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, 1.0, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

                thickFactor = random.uniform(0.5, 0.8)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(1.0, -0.577, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

                thickFactor = random.uniform(0.5, 0.8)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(-1, -0.577, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

            if branchDecision == 4:
                thickFactor = random.uniform(0.5, 0.8)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(axis1, 0.0, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

                thickFactor = random.uniform(0.5, 0.8)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, axis1, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

                thickFactor = random.uniform(0.5, 0.8)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, -axis1, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

                thickFactor = random.uniform(0.5, 0.8)
                axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(-axis1, 0.0, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

            if branchDecision == 5:
                thickFactor = random.uniform(0.5, 0.8)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.0, 1.0, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

                thickFactor = random.uniform(0.5, 0.8)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(1.0, 0.325, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

                thickFactor = random.uniform(0.5, 0.8)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(-1, 0.325, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

                thickFactor = random.uniform(0.5, 0.8)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(0.727, -1.0, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)

                thickFactor = random.uniform(0.5, 0.8)
                #axis1 = random.uniform(0.7, 1.3)
                axis = adsk.core.Vector3D.create(-0.727, -1, 0.0)
                recursiveBranching(face, branchWidth *
                                    thickFactor, axis, depth-1, yellowAppear, branchFactor)


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))






def addLeaves(face, leavesRadius, yellowAppear):
    app = adsk.core.Application.get()
    ui = app.userInterface
    #ui.messageBox('in createDonuts')

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

            baseFeat.finishEdit()

            global progresscounter
            progresscounter = progresscounter + 1
            print(str(progresscounter) + '/' + str(forProgressTotal))

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))