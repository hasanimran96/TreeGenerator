# Fusion360API python
import adsk.core
import adsk.fusion
import traceback


def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui = app.userInterface

        # click
        msg = 'Click on the surface'
        sel = ui.selectEntity(msg, 'Faces')
        if sel is None:
            return
        clickPoint = sel.point

        # sketch
        root = adsk.fusion.Component.cast(app.activeProduct.rootComponent)
        skt = root.sketches.add(root.xYConstructionPlane)
        skt.sketchPoints.add(clickPoint)

        ui.messageBox('done')

    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
