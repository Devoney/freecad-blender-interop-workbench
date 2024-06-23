import FreeCAD
import FreeCADGui
import Part
import Mesh
import MeshPart
import os
import subprocess
import tempfile

class BlenderMeshProcessor:
    def __init__(self, obj, script_file, thickness=1):  # Default thickness value
        self.script_file = script_file
        self.thickness = thickness
        obj.Proxy = self
        self.init_properties(obj)
        self.intermediate_objects = []

    def init_properties(self, obj):
        # TODO MDK: Finish here using param defs as suggested by ChatGPT: https://chatgpt.com/c/20a810bd-eab5-4865-b272-be62f2264be9
        if not hasattr(obj, "Part"):
            obj.addProperty("App::PropertyLink", "Part", "Blender", "Part to process with Blender")
        if not hasattr(obj, "Thickness"):
            obj.addProperty("App::PropertyString", "Thickness", "Blender", "Thickness to apply to the part")
            obj.Thickness = str(self.thickness)  # Set initial thickness value
        if not hasattr(obj, "RemeshBefore"):
            obj.addProperty("App::PropertyBool", "RemeshBefore", "Blender", "Whether to apply the remesh modifier beforehand to prevent a result with self intersection.")
            obj.RemeshBefore = False
    
    def execute(self, obj):
        # Do not trigger recomputes when in sketch mode or so.
        # if FreeCADGui.ActiveDocument.getInEdit():
        #    obj.touch()
        #    return
        
        # Ensure the properties are updated
        part = obj.Part
        thickness = obj.Thickness
        remesh_before = obj.RemeshBefore
        FreeCAD.Console.PrintMessage(f"Thickness: {thickness}.\n")

        if not part:
            FreeCAD.Console.PrintMessage("No part linked to process.\n")
            return
        
        # Create temporary files for the STL files
        input_stl_path = tempfile.mktemp(suffix='.stl')
        output_stl_path = tempfile.mktemp(suffix='.stl')

        try:
            # Export the FreeCAD part to STL
            self.export_part_to_stl(part, input_stl_path)
            
            # Call Blender to process the STL file
            self.call_blender(input_stl_path, output_stl_path, thickness, remesh_before)
            
            # Import the resulting STL back into FreeCAD
            imported_mesh = self.import_stl_to_freecad(output_stl_path)

            # Validate imported mesh
            if not imported_mesh:
                raise RuntimeError("Imported mesh object is None.")
            if not hasattr(imported_mesh, 'Mesh'):
                raise RuntimeError("Imported mesh object does not have a 'Mesh' attribute.")
            
            # Create shape from mesh and convert to solid
            shape_obj = self.create_shape_from_mesh(imported_mesh, obj)
            self.create_solid_from_shape(shape_obj, obj)

        finally:
            # Clean up temporary files
            if os.path.exists(input_stl_path):
                os.remove(input_stl_path)
            if os.path.exists(output_stl_path):
                os.remove(output_stl_path)
            
            # Clean up intermediate objects
            self.cleanup_intermediate_objects()

    def export_part_to_stl(self, part, export_path):
        __objs__ = [part]
        Mesh.export(__objs__, export_path)
        FreeCAD.Console.PrintMessage(f"Exported part to STL: {export_path}\n")

    def call_blender(self, input_stl, output_stl, offset, remesh_before):
        blender_executable = "blender"  # Use "blender" assuming it's in your PATH        
        script_path = os.path.join(os.path.dirname(__file__), 'BlenderScripts', self.script_file)
        try:
            cmd = [blender_executable, "--background", "--python", script_path, "--", input_stl, output_stl, str(offset), str(remesh_before)]
            cmdStr = " ".join(cmd)
            FreeCAD.Console.PrintMessage(f"Running command: {cmdStr}\n")
            result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            FreeCAD.Console.PrintMessage(f"Blender output: {result.stdout}\n")
            if result.stderr:
                FreeCAD.Console.PrintMessage(f"Blender errors: {result.stderr}\n")
        except FileNotFoundError:
            FreeCAD.Console.PrintMessage(f"Blender executable not found: {blender_executable}\n")
        except subprocess.CalledProcessError as e:
            FreeCAD.Console.PrintMessage(f"Blender process failed with return code {e.returncode}\n")
            FreeCAD.Console.PrintMessage(f"Error output: {e.stderr}\n")

    def import_stl_to_freecad(self, stl_path):
        if not os.path.exists(stl_path):
            raise RuntimeError(f"File does not exist: {stl_path}\n")
        
        # Insert the mesh
        Mesh.insert(stl_path, FreeCAD.ActiveDocument.Name)
        FreeCAD.Console.PrintMessage(f"Imported processed STL into FreeCAD: {stl_path}\n")
        
        # Extract the name of the mesh from the filename
        mesh_name = os.path.splitext(os.path.basename(stl_path))[0]
        
        # Retrieve the mesh object by iterating over the document objects
        imported_mesh = None
        for obj in FreeCAD.ActiveDocument.Objects:
            if obj.Name == mesh_name and obj.TypeId == 'Mesh::Feature':
                imported_mesh = obj
                self.intermediate_objects.append(imported_mesh.Name)
                break
        
        if imported_mesh is None:
            raise RuntimeError("Imported mesh object could not be found in the document.")
        
        FreeCAD.Console.PrintMessage(f"Imported mesh object: {imported_mesh.Name}\n")
        return imported_mesh

    def create_shape_from_mesh(self, mesh_obj, obj):
        if mesh_obj is None:
            raise RuntimeError("Imported mesh object is None.")
        if not hasattr(mesh_obj, 'Mesh'):
            raise RuntimeError("Imported mesh object does not have a 'Mesh' attribute.")
        
        shape = Part.Shape()
        shape.makeShapeFromMesh(mesh_obj.Mesh.Topology, 0.1, True)
        
        part_feature = FreeCAD.ActiveDocument.addObject("Part::Feature", "PartShape")
        part_feature.Shape = shape
        part_feature.purgeTouched()
        
        self.intermediate_objects.append(part_feature.Name)
        
        FreeCAD.Console.PrintMessage("Created shape from mesh\n")
        return part_feature

    def create_solid_from_shape(self, shape_obj, obj):
        solid = Part.makeSolid(shape_obj.Shape)
        solid_feature = FreeCAD.ActiveDocument.addObject("Part::Feature", "Solid")
        solid_feature.Shape = solid
        solid_feature.purgeTouched()

        self.intermediate_objects.append(solid_feature.Name)
        
        obj.Shape = solid
        FreeCAD.Console.PrintMessage("Created solid from shape\n")
    
    def cleanup_intermediate_objects(self):
        for obj_name in self.intermediate_objects:
            FreeCAD.Console.PrintMessage(f"Attempt to clean up object by name: {obj_name}\n")
            obj = FreeCAD.ActiveDocument.getObject(obj_name)
            if obj:
                objName = obj.Name
                FreeCAD.ActiveDocument.removeObject(objName)
                FreeCAD.Console.PrintMessage(f"Removed intermediate object: {objName}\n")
        self.intermediate_objects.clear()

    def __str__(self):
        return f"BlenderMeshProcessor(thickness={self.thickness})"

class ViewProviderBlenderMeshProcessor:
    def __init__(self, obj):
        obj.Proxy = self

    def attach(self, obj):
        self.Object = obj.Object

    def updateData(self, fp, prop):
        pass

    def onChanged(self, vp, prop):
        pass
        # if prop == "Thickness":
        #    FreeCAD.Console.PrintMessage(f"Thickness changed to: {vp.Thickness}\n")
        #    vp.Object.Proxy.execute(vp.Object)

    def getDisplayModes(self, obj):
        return []

    def getDefaultDisplayMode(self):
        return "Flat Lines"

    def setDisplayMode(self, mode):
        return mode

    def onDelete(self, vp, subelements):
        return True

    def __str__(self):
        return "ViewProviderBlenderMeshProcessor()"

def createBlenderMeshProcessor(script_file, object_type_name, thickness, part):
    doc = FreeCAD.ActiveDocument
    obj = doc.addObject("Part::FeaturePython", f"BlenderInterop{object_type_name}")
    BlenderMeshProcessor(obj, script_file, thickness)
    ViewProviderBlenderMeshProcessor(obj.ViewObject)
    obj.Part = part
    doc.recompute()
    return obj