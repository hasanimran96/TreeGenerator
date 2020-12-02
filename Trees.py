# Author-
# Description-

import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import random
import math


app = adsk.core.Application.get()
ui = app.userInterface


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Tree script')

        # get the design  //selfmade
        design = adsk.fusion.Design.cast(app.activeProduct)
        if not design:
            ui.messageBox('No active Fusion 360 design', 'No Design')
            return

        # Get the root component of the active design.
        rootComp = design.rootComponent

        radius = 2

        create_bond2(rootComp, radius)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def create_bond2(rootComp, radius):

    # Create a new sketch on the xy plane.
    sketches = rootComp.sketches
    xyPlane = rootComp.xYConstructionPlane
    sketch1 = rootComp.sketches.add(xyPlane)
    circles = sketch1.sketchCurves.sketchCircles
    circle1 = circles.addByCenterRadius(
        adsk.core.Point3D.create(0, 0, 0), radius)

    # Create the End Loft Sketch Profile
    profile0 = sketch1.profiles.item(0)

    # Create loft feature input
    extFeats = adsk.fusion.ExtrudeFeatures.cast(
        rootComp.features.extrudeFeatures)
    dist = adsk.core.ValueInput.createByReal(5)
    extInput = extFeats.createInput(
        profile0, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
    extInput.setOneSideExtent(adsk.fusion.DistanceExtentDefinition.create(
        dist), adsk.fusion.ExtentDirections.PositiveExtentDirection)
    extInput.isSolid = False

    try:    # Create extrude feature
        extFeats.add(extInput)
    except:
        ui.messageBox("couldn't extrude")
        # print(traceback.format_exc())
