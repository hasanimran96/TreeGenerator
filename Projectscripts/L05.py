# Author-
# Description-

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

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions

        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('MyButtonDefIdPython',
                                                   'Python Sample Button',
                                                   'Sample button tooltip',
                                                   './Resources/Sample')

        # Connect to the command created event.
        sampleCommandCreated = SampleCommandCreatedEventHandler()
        buttonSample.commandCreated.add(sampleCommandCreated)
        handlers.append(sampleCommandCreated)

        # Get the ADD-INS panel in the model workspace.
        addInsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')

        # Add the button to the bottom of the panel.
        buttonControl = addInsPanel.controls.addCommand(buttonSample)

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
        ui.messageBox('In command execute event handler.')

        readyForDonuts()


def stop(context):
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # Clean up the UI.
        cmdDef = ui.commandDefinitions.itemById('MyButtonDefIdPython')
        if cmdDef:
            cmdDef.deleteMe()

        addinsPanel = ui.allToolbarPanels.itemById('SolidScriptsAddinsPanel')
        cntrl = addinsPanel.controls.itemById('MyButtonDefIdPython')
        if cntrl:
            cntrl.deleteMe()
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def readyForDonuts():
    app = adsk.core.Application.get()
    ui = app.userInterface
    ui.messageBox('Ready for Donuts?')
    design = adsk.fusion.Design.cast(app.activeProduct)
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

    anzahlringe = random.randint(4, 9)
    i = 0
    while i <= anzahlringe:

        # new donut
        # Call an add method on the collection to create a new circle.
        circle1 = circles.addByCenterRadius(
            adsk.core.Point3D.create(5*i, 0, 0), 2)

        # Call an add method on the collection to create a new line.
        axis = lines.addByTwoPoints(adsk.core.Point3D.create(
            5*i-1, -4, 0), adsk.core.Point3D.create(5*i+1, -4, 0))

        # Get the first profile from the sketch, which will be the profile defined by the circle in this case.
        prof = sketch.profiles.item(i)

        # Create a revolve input object that defines the input for a revolve feature.
        # When creating the input object, required settings are provided as arguments.
        revInput = revolves.createInput(
            prof, axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

        # Define a full revolve by specifying 2 pi as the revolve angle.
        angle = adsk.core.ValueInput.createByReal(
            math.pi * 2 * ((i+1)/(anzahlringe+1)))
        revInput.setAngleExtent(False, angle)

        # Create the revolve by calling the add method on the RevolveFeatures collection and passing it the RevolveInput object.
        rev = revolves.add(revInput)

        i = i+1
