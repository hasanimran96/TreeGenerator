# Author-
# Description-

import adsk.core
import adsk.fusion
import adsk.cam
import traceback
import math


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface
        ui.messageBox('Hello script')

        circleTest(context)

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


def circleTest(context):
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
        sphereRad = 5
        circleRad = 1
        height = math.sqrt(math.pow(sphereRad, 2) - math.pow(circleRad, 2))
        center = adsk.core.Point3D.create(0, 0, 0)

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
