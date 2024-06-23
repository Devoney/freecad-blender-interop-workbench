import bpy
import sys

def process(new_mesh_path, export_path, thickness_amount):
    # Delete all objects in the scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    
    # Import the new mesh
    bpy.ops.import_mesh.stl(filepath=new_mesh_path)
    new_mesh = bpy.context.selected_objects[0]
    
    # Apply offset modifier to the new mesh
    mod = new_mesh.modifiers.new(name='Solidify', type='SOLIDIFY')
    mod.thickness = thickness_amount
    mod.offset = 0

    # Apply the modifier
    bpy.context.view_layer.objects.active = new_mesh
    bpy.ops.object.modifier_apply(modifier=mod.name)
    
    # Export the new mesh as an STL file
    bpy.ops.export_mesh.stl(filepath=export_path)

# Get the new mesh path, export path, and offset amount from the command line arguments
args = sys.argv[sys.argv.index('--') + 1:]  # The paths and offset amount are passed after '--' argument
new_mesh_path = args[0]
export_path = args[1]
thickness_amount = float(args[2])

process(new_mesh_path, export_path, thickness_amount)
