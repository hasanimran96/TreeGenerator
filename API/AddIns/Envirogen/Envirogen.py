import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import math
import random

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('In run function')

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('NewButtonDefIdPython',
                                                   'Tree',
                                                   'Sample button tooltip',
                                                   './resources/Button')

        # Connect to the command created event.
        sampleCommandCreated = SampleCommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)

        # Get the ADD-INS panel in the model workspace.
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')

        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(buttonSample)

        # Make the button available in the panel.
        buttonControl.isPromotedByDefault = True
        buttonControl.isPromoted = True
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

        # Create a check box to get if it should be a random number.
        isRandom = inputs.addBoolValueInput('isRandom', 'Random # of Rings',
                                            True, '', False)

        # Create the value input to get the number of rings.
        fixedNrOfRings = inputs.addIntegerSpinnerCommandInput(
            'fixedNrOfRings', '# of Rings', 1, 100, 1, 1)
        # Create the slider to get the thickness setting the range of the slider to
        # be 10 to 24 of whatever the current document unit is.
        app = adsk.core.Application.get()
        des = adsk.fusion.Design.cast(app.activeProduct)

        minVal = des.unitsManager.convert(
            10, des.unitsManager.defaultLengthUnits, 'cm')
        maxVal = des.unitsManager.convert(
            24, des.unitsManager.defaultLengthUnits, 'cm')
        thickness = inputs.addFloatSliderCommandInput('thickness',
                                                      'Thickness',
                                                      des.unitsManager.defaultLengthUnits,
                                                      minVal, maxVal, False)

        # Connect to the execute event.
        onExecute = SampleCommandExecuteHandler()
        cmd.execute.add(onExecute)
        handlers.append(onExecute)


# Event handler for the execute event.
class SampleCommandExecuteHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()

    def notify(self, args):
        eventArgs = adsk.core.CommandEventArgs.cast(args)

        # Code to react to the event.
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Ready for a Tree?')

        # Get the values from the command inputs.
        inputs = eventArgs.command.commandInputs

        isRandomAmount = inputs.itemById('isRandom').value
        fixedAamountOfDonuts = inputs.itemById('fixedNrOfRings').value
        donutThickness = inputs.itemById('thickness').valueOne

        # depending on the choice assign the amount of rings
        if isRandomAmount:
            amountOfDonuts = random.randint(5, 10)
        else:
            amountOfDonuts = fixedAamountOfDonuts

        # call the method to create the rings
        createDonuts(amountOfDonuts, donutThickness)


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('NewButtonDefIdPython')
        if cmdDef:
            cmdDef.deleteMe()

        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('NewButtonDefIdPython')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# This method contains the actual code to create the rings
# arguments
# amountOfDonuts int how many rings to create
# donutThickness radius of the rings
def createDonuts(amountOfDonuts, donutThickness):
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




        # loop requested amount of times
        #anzahlringe = random.randint(4, 9)
        i = 0
        while i <= (amountOfDonuts-1):

            # new donut
            # Call an add method on the collection to create a new circle.
            circle1 = circles.addByCenterRadius(
                adsk.core.Point3D.create(5*i, 0, 0), donutThickness)

            # Call an add method on the collection to create a new line.
            axis = lines.addByTwoPoints(adsk.core.Point3D.create(
                5*i-1, -4, 0), adsk.core.Point3D.create(5*i+1, -4, 0))

            # Get the first profile from the sketch, which will be the profile defined by the circle in this case.
            prof = sketch.profiles.item(i)

            # Create a revolve input object that defines the input for a revolve feature.
            # When creating the input object, required settings are provided as arguments.
            #revInput = revolves.createInput(prof, axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
            # NEW
            extInput = extrudes.createInput(
                prof, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

            # Define a revolve by specifying fractions of 2 pi(full circle) as the revolve angle.
            #angle = adsk.core.ValueInput.createByReal(math.pi * 2 * ((i+1)/amountOfDonuts) )
            #revInput.setAngleExtent(False, angle)
            # NEW
            dist = adsk.core.ValueInput.createByReal(5)
            extInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
                dist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
            extInput.isSolid = True

            # Create the revolve by calling the add method on the RevolveFeatures collection and passing it the RevolveInput object.
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
            bodytocolor = rootComp.bRepBodies.item(i)

            # Create a copy of the existing appearance.
            newAppear = design.appearances.addByCopy(
                yellowAppear, 'Color ' + str(i+1))

            # Edit the "Color" property by setting it to a random color.
            colorProp = adsk.core.ColorProperty.cast(
                newAppear.appearanceProperties.itemByName('Color'))
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            colorProp.value = adsk.core.Color.create(139,69,19, 1)  #use brown for trunk

            # and color the body with this new material
            bodytocolor.appearance = newAppear

            # Get one face and edge of the extrusion body
            #face = extrudes.endFaces.item(0)
            # print("extrudes")
            # print(face.objectType)
            # exttudes has no endfaces
            #face = extInput.endFaces.item(0)
            # print("extInput")
            # print(face.objectType)
            # has no endfaces
            #adds the sketch. sometimes however face is the cylinder instead of the flat face. maybe use endFace istead ::: face = ext.faces.item(1) :::this worked
            face = ext.endFaces.item(0)
            print("ext")
            print(face.objectType)
            print(face.area)
            print(face.geometry)
            print(face.evaluator)
            print(face.body)
            print(face.attributes)
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
            #adds the sketch. sometimes however face is the cylinder instead of the flat face. maybe use endFace istead 
            sk = rootComp.sketches.add(face)
            #neueSphere = adsk.core.Sphere.create(centerPoint, 10)

            #prepares the sphere, using only the centerpoint of the surface though.
            bodies = rootComp.bRepBodies
            #maybe possible with permanent?
            tBrep = adsk.fusion.TemporaryBRepManager.get()
            centerPoint = face.centroid
            sphereBody = tBrep.createSphere(centerPoint, 3)
                
            # Create a base feature
            baseFeats = rootComp.features.baseFeatures
            baseFeat = baseFeats.add()
            
            #adds the sphere. we lose reference to the cylinder though it seems. at least in the UI
            baseFeat.startEdit()


            body = bodies.add(sphereBody, baseFeat)
            baseFeat.finishEdit()


            # Create a copy of the existing appearance.
            newAppear = design.appearances.addByCopy(
                yellowAppear, 'Color ' + str(i+1))

            # Edit the "Color" property by setting it to a random color.
            colorProp = adsk.core.ColorProperty.cast(
                newAppear.appearanceProperties.itemByName('Color'))
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            colorProp.value = adsk.core.Color.create(0,100,0, 1)  #use green for leaves

            # get the current body
            leavestocolor = rootComp.bRepBodies.item(i+1)

            # and color the sphere with this new material
            print("body object type is")
            print(body.objectType)
            print(newAppear.appearanceProperties.itemByName('Color'))
            leavestocolor.appearance = newAppear

            i = i+1

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
