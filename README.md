# FreeCAD Blender Interop Workbench

This workbench allows you to apply a modifier from Blender on a Part/Body in FreeCAD parametrically. It also works on meshes.
Note that this was created very minimalistically as the 3D offset operation in FreeCAD didn't work for me, but it worked in Blender.
Perhaps I will add support for more modifiers, but currently that is the only modifier supported: Solidify.

# Installation instructions
Copy the contents of the `Mod` folder in this repo to FreeCAD's `Mod` folder.
Then in FreeCAD enable this workbench by going to FreeCAD's menu -> Edit -> Preferences -> Workbenches.

# Usage instructions

YouTube: https://www.youtube.com/watch?v=WJBEbAPwoR4

- Create a mesh, a body or a part.
- Go to the Blender Interop Workbench
- Select the mesh/body/part and click one of the operations in the Blender Interop Workbench (currently only Solidify).
- Wait for FreeCAD to have called Blender (a console window might popup)
- See the Part pop up in the treeview called something like BlenderInterop{Operation} like BlenderInteropSolidify, for instance.
- Click this part and here you can alter its parameters, like Thickness for Solidify.
- See that the operation from Blender is reapplied when the parameter has changed. 
Note: If the Blender operation was applied to a Body created from a sketch, it might be so that after having altered the sketch, the BlenderInterop{Operation} part needs to be recomputed manually.

# Compatibility
It was programmed for FreeCAD 0.21.1 and for Blender 4.0. It could work for other versions too.
