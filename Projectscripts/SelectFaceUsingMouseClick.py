import adsk.core
import adsk.fusion
import traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        design = app.activeProduct
        rootComp = design.rootComponent
        sketches: adsk.fusion.Sketches = rootComp.sketches

        # select PlanarFaces
        try:
            returnValue: adsk.core.Selections = ui.selectEntity(
                'Select Face', 'PlanarFaces')
        except:
            return

        # Selected surface
        surf: adsk.fusion.BRepFace = returnValue.entity

        # Create Sketch
        skt: adsk.fusion.Sketch = sketches.add(surf)

        # Click Point
        pnt: adsk.core.Point3D = returnValue.point

        # Get the difference between the RootComponent and the origin of the sketch.
        mat: adsk.core.Matrix3D = skt.transform

        # Inverts this matrix.
        mat.invert()

        # Convert the difference
        pnt.transformBy(mat)

        # Draw Sketch
        radius = 2.0
        circles: adsk.fusion.SketchCircles = skt.sketchCurves.sketchCircles
        circles.addByCenterRadius(pnt, radius)
    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
