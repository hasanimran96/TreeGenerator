import adsk.core, adsk.fusion, adsk.cam, traceback, math, random

# Global list to keep all event handlers in scope.
# This is only needed with Python.
handlers = []

def run(context):
    ui = None
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        ui.messageBox('In run function')

        # Get the CommandDefinitions collection.
        cmdDefs = ui.commandDefinitions
        
        # Create a button command definition.
        buttonSample = cmdDefs.addButtonDefinition('MyButtonDefIdPython', 
                                                   'Python Sample Button', 
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
        ui  = app.userInterface
        ui.messageBox('Ready for Donuts?')
        createDonuts()
        ui.messageBox('Ready for Donuts!!!')



def stop(context):
    try:
        app = adsk.core.Application.get()
        ui  = app.userInterface
        
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

def inFunction():
        ui.messageBox('in inFUnction')

def createDonuts():
    ui.messageBox('in createDonuts')
    try:
        #get the design  //selfmade
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

        #1st

        # Create a new ObjectCollection.
        objColl = adsk.core.ObjectCollection.create()

        #2nd

        # Get the SketchCircles collection from an existing sketch.
        circles = sketch.sketchCurves.sketchCircles

        # Get the SketchLines collection from an existing sketch.
        lines = sketch.sketchCurves.sketchLines

        # Get the RevolveFeatures collection.
        revolves = rootComp.features.revolveFeatures

        # Get a reference to an appearance in the library.
        lib = app.materialLibraries.itemByName('Fusion 360 Appearance Library')
        libAppear = lib.appearances.itemByName('Plastic - Matte (Yellow)')

        #copy material into the design
        libAppear.copyTo(design)
        yellowAppear = design.appearances.itemByName(libAppear.name)


        #loop 5 to 10 times
        anzahlringe = random.randint(4, 9)
        i=0
        while i <= anzahlringe:

            #new donut
            # Call an add method on the collection to create a new circle.
            circle1 = circles.addByCenterRadius(adsk.core.Point3D.create(5*i,0,0), 2)
            
            # Call an add method on the collection to create a new line.
            axis = lines.addByTwoPoints(adsk.core.Point3D.create(5*i-1,-4,0), adsk.core.Point3D.create(5*i+1,-4,0))

            # Get the first profile from the sketch, which will be the profile defined by the circle in this case.
            prof = sketch.profiles.item(i)

            # Create a revolve input object that defines the input for a revolve feature.
            # When creating the input object, required settings are provided as arguments.
            revInput = revolves.createInput(prof, axis, adsk.fusion.FeatureOperations.NewBodyFeatureOperation)

            # Define a revolve by specifying fractions of 2 pi(full circle) as the revolve angle.
            angle = adsk.core.ValueInput.createByReal(math.pi * 2 * ((i+1)/(anzahlringe+1)) )
            revInput.setAngleExtent(False, angle)
                    
            # Create the revolve by calling the add method on the RevolveFeatures collection and passing it the RevolveInput object.
            rev = revolves.add(revInput)

            #get component collection
            #comp = rev.parentComponent

            #used for debugging
            #print(rev.objectType)
            #print(libAppear.objectType)
            #print(libAppear.name)

            #get the current body
            bodytocolor = rootComp.bRepBodies.item(i)

            # Create a copy of the existing appearance.
            newAppear = design.appearances.addByCopy(yellowAppear, 'Color ' + str(i+1))


            # Edit the "Color" property by setting it to a random color.
            colorProp = adsk.core.ColorProperty.cast(newAppear.appearanceProperties.itemByName('Color'))
            red = random.randint(0,255)
            green = random.randint(0,255)
            blue = random.randint(0,255)
            colorProp.value = adsk.core.Color.create(red, green, blue, 1)   

            #and color the body with this new material
            bodytocolor.appearance = newAppear


            i=i+1


    except:
        if ui:
            ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))