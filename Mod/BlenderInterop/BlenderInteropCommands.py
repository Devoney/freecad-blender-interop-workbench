import FreeCAD
import FreeCADGui
import Part
import Mesh
import MeshPart
import os
import subprocess
import tempfile
import BlenderMeshProcessor

class Solidify:
    def GetResources(self):
        return {
            # 'Pixmap': 'path/to/your/icon.png',  # Optional, path to an icon file
            'MenuText': 'Solidify',
            'ToolTip': 'Solidify modifier'
        }
    def GetResources(self):
        # Assuming this script is in the MyWorkbench folder
        icon_path = os.path.join(os.path.dirname(__file__), 'Icons', 'Solidify.png')
        return {
            'MenuText': 'Solidify',
            'ToolTip': 'Solidify modifier',
            'Pixmap': icon_path
        }

    def Activated(self):
        FreeCAD.Console.PrintMessage("BlenderInterop.Solidify Activated\n")
        doc = FreeCAD.ActiveDocument
        selected_part = FreeCADGui.Selection.getSelection()[0]

        processor = BlenderMeshProcessor.createBlenderMeshProcessor('solidify.py', 'Solidify', 1, selected_part)  # Default thickness is set to 1
        FreeCAD.ActiveDocument.recompute()
        FreeCAD.Console.PrintMessage("BlenderInterop.Solidify Done\n")

    def IsActive(self):
        return True

FreeCADGui.addCommand('Solidify', Solidify())
