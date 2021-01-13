import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import math


def roll(field):
    #  shift items in an array by one in right to left direction
    #  that first element becomes the last
    #  example: roll([0, 1, 2, 3])  returns: [1, 2, 3, 0]
    #  field:  array of elements to be shifted
    #  retruns: shifted

    new_field = []
    for idx, item in enumerate(field):
        if idx == 0:
            continue
        new_field.append(item)
    new_field.append(field[0])
    return new_field


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        product = app.activeProduct
        design = adsk.fusion.Design.cast(product)

        rootComp = design.rootComponent

        # star data

        inner_radius = 3
        outer_radius = 6
        num_of_pikes = 3
        z_height = 3
        angle = math.pi/num_of_pikes
        points = []

        trigger = True
        for n in range(2*num_of_pikes):
            current_angle = n*angle
            if trigger:
                l = inner_radius
                trigger = False
            else:
                l = outer_radius
                trigger = True
            x = l * math.cos(current_angle)
            y = l * math.sin(current_angle)
            z = 0
            points.append([x, y, z])

        # Create a new sketch on the xy plane.

        sketches = rootComp.sketches
        xyPlane = rootComp.xYConstructionPlane
        sketch0 = sketches.add(xyPlane)

        # Draw some circles.
        lines = sketch0.sketchCurves.sketchLines

        p0 = adsk.core.Point3D.create(points[0][0], points[0][1], points[0][2])
        p1 = adsk.core.Point3D.create(points[1][0], points[1][1], points[1][2])
        line0 = lines.addByTwoPoints(p0, p1)

        for xyz in roll(points):
            line1 = lines.addByTwoPoints(
                line0.endSketchPoint, adsk.core.Point3D.create(xyz[0], xyz[1], xyz[2]))
            line0 = line1

        # create offset construction plane
        #
        # Get construction planes
        # Get the profile defined by the circle
        sketch_profile0 = sketch0.profiles.item(0)

        planes = rootComp.constructionPlanes
        # Create construction plane input
        planeInput = planes.createInput()
        # Add construction plane by offset
        offsetValue = adsk.core.ValueInput.createByReal(z_height)
        planeInput.setByOffset(sketch_profile0, offsetValue)
        planeOne = planes.add(planeInput)

        sketch1 = sketches.add(planeOne)

        # circle
        # sketch1_circles = sketch1.sketchCurves.sketchCircles
        # sketch1_circles.addByCenterRadius(adsk.core.Point3D.create(0,0,0), 0.0001)
        # point
        sketch1_points = sketch1.sketchPoints
        top_point = sketch1_points.add(adsk.core.Point3D.create(0, 0, 0))

        # sketch_profile1 = sketch1.profiles.item(0)

        # Create an extrusion input
        loftFeature = rootComp.features.loftFeatures
        loftInput = loftFeature.createInput(
            adsk.fusion.FeatureOperations.NewBodyFeatureOperation)
        loftSectionsObjects = loftInput.loftSections
        loftSectionsObjects.add(sketch_profile0)
        loftSectionsObjects.add(top_point)
        loftInput.isSolid = True

        # Create loft feature
        loftFeature.add(loftInput)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
