import FreeCAD
import FreeCADGui

class BlenderInteropWorkbench(FreeCADGui.Workbench):
    MenuText = "Blender Interop Workbench"
    ToolTip = "An integration with Blender for mesh operations FreeCAD does not have."
    Icon = """
    /* XPM */
    static const char * BlenderInteropWorkbench_xpm[] = {
    "16 16 4 1",
    "  c None",
    ". c #000000",
    "+ c #FFFFFF",
    "@ c #FF0000",
    "                ",
    "                ",
    "                ",
    "                ",
    "                ",
    "                ",
    "     ......     ",
    "     ......     ",
    "     ......     ",
    "     ......     ",
    "                ",
    "                ",
    "                ",
    "                ",
    "                ",
    "                "};
    """

    def Initialize(self):
        import BlenderInteropCommands
        self.appendToolbar("Blender Interop Tools", ["Solidify"])

    def GetClassName(self):
        return "Gui::PythonWorkbench"

FreeCADGui.addWorkbench(BlenderInteropWorkbench)
