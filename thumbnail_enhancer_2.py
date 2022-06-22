"""
This script is still a WIP.
There are 2 major things I still need to tackle (and a few more, but these are the most important ones):
    - Prior to runnig the script, all objects need to be scaled to 0.1x their original size with the 3D cursor as pivot.
    - The materials and node group for shading and compositing still has to be imported from a separate file.
        it would be great if the file itself already contained these, but that has to be applied on a higher level.
    - Script is not resillient to objects with a different name/material
    - Some of the numbers have a darker color than others

-
IMPORTANT: For the script to work, all objects have to be manually scaled to 0.1x size
(with the world origin as pivot point) before running. Don't forget this.
"""

import bpy

# Please define the path to your resources file here
resources = "//resources.blend"

# Initial steps
# - [Manually Scale entire scene down to 0.1x scale, with world origin as pivot point]
bpy.ops.object.select_all(action='DESELECT')
mainCamera = bpy.data.objects["Object"]
mainCamera.location = (0, 0, 10)
mainCamera.data.ortho_scale = 12

# Define objects, functions, etc.
objectZirconia = bpy.data.objects["Object.001"]
supports = []
teeth = []

# Functions
def replace_material(object,old_material,new_material):
    ob = object
    om = bpy.data.materials[old_material]
    nm = bpy.data.materials[new_material]
    for s in ob.material_slots:
        if s.material.name == old_material:
            s.material = nm


# Set initial render engine settings
bpy.context.scene.render.engine = 'CYCLES'
bpy.context.scene.cycles.device = 'GPU'
bpy.context.scene.cycles.samples = 64
bpy.context.scene.cycles.use_denoising = True


# Change Zirconia viewport color
bpy.data.materials["Material.017"].diffuse_color = (0.2, 0.2, 0.2, 1)


# Retrieve pre-made materials from materials.blend, and apply them to their intended objects.
with bpy.data.libraries.load(resources, link=False) as (data_from, data_to):
    data_to.materials = data_from.materials

for obj in bpy.data.objects:
    for slot in obj.material_slots:
        if slot.material == bpy.data.materials["cncPin"]:
            supports.append(obj)    
        if slot.material == bpy.data.materials["model"]:
            teeth.append(obj)
        
for support in supports:
    replace_material(support, "cncPin", "zirconia_supports")

for tooth in teeth:
    replace_material(tooth, "model", "zirconia_highlight")

replace_material(objectZirconia, "cncStock", "zirconia")


# Set up scene lights
light_1_data = bpy.data.lights.new(name="light-data-1", type='AREA')
light_object1 = bpy.data.objects.new(name="light-1", object_data=light_1_data)
light_object1.location = (4.83197, 2.96577, 4.42255)
light_object1.rotation_euler = (-1.0266, 0,  -0.959931)
light_object1.scale = (11.5524, 4.10024, 11.5524)
light_object1.data.size = 1
light_object1.data.energy = 2500

light_2_data = bpy.data.lights.new(name="light-data-2", type='AREA')
light_object2 = bpy.data.objects.new(name="light-2", object_data=light_2_data)
light_object2.location = (-6.75097, -5.11998, 4.94434)
light_object2.rotation_euler = (-0.0145078, 1.09379,  -2.54982)
light_object2.scale = (12.7395, 12.7395, 12.7395)
light_object2.data.size = 1
light_object2.data.energy = 5000

bpy.context.collection.objects.link(light_object1)
bpy.context.collection.objects.link(light_object2)


# Save main scene into variable and rename
mainScene = bpy.context.scene
mainScene.name = 'mainScene'

# Duplicate main scene
bpy.ops.scene.new(type='FULL_COPY')

# Save new scene into variable and rename
shadowScene = bpy.context.scene
shadowScene.name = 'shadowScene'

# Setup lights in shadowScene: remove old lights and add sun
bpy.data.objects['light-1.001'].select_set(True)
bpy.data.objects['light-2.001'].select_set(True)
bpy.ops.object.delete()
shadowSunData = bpy.data.lights.new(name="light-data-2", type='SUN')
shadowSunObject = bpy.data.objects.new(name="light-2", object_data=shadowSunData)
shadowSunObject.rotation_euler = (-0.161174, -0.128633, -0.000813812)
shadowSunObject.data.angle = 0.872665
shadowSunObject.data.energy = 25
bpy.context.collection.objects.link(shadowSunObject)








height = bpy.data.objects['Object.031'].dimensions.z / 2 * -1
bpy.ops.mesh.primitive_plane_add(enter_editmode=False, align='WORLD', location=(0, 0, height), scale=(1, 1, 1))
bpy.ops.transform.resize(value=(16, 16, 16))
bpy.context.object.is_shadow_catcher = True
bpy.context.scene.view_layers["View Layer"].cycles.use_pass_shadow_catcher = True

# Switch back to main scene and prepare for compositing.
bpy.context.window.scene = bpy.data.scenes['mainScene']
with bpy.data.libraries.load(resources, link=False) as (data_from, data_to):
    data_to.node_groups = data_from.node_groups
bpy.context.scene.view_layers["View Layer"].use_pass_cryptomatte_object = True
bpy.context.scene.view_layers["View Layer"].use_pass_cryptomatte_material = True
bpy.context.scene.view_layers["View Layer"].cycles.use_pass_shadow_catcher = True
bpy.context.scene.use_nodes = True


# ------------ COMPOSITING SCRIPT --------------


# Remove all old nodes
compositor = bpy.context.scene.node_tree
scene = bpy.context.scene
for node in compositor.nodes:
    compositor.nodes.remove(node)

# Place new nodes
Composite = compositor.nodes.new(type='CompositorNodeComposite')
renderLayerMain = compositor.nodes.new(type='CompositorNodeRLayers')
renderLayerShadow = compositor.nodes.new(type='CompositorNodeRLayers')
customNodeGroup = compositor.nodes.new('CompositorNodeGroup')
customNodeGroup.node_tree = bpy.data.node_groups['Composite-Zirconia-Top']

# Organize new nodes (not necessary, purely visual)
Composite.location = (1000, 200)
renderLayerMain.location = (-300, 200)
renderLayerShadow.location = (0, -200)
customNodeGroup.location = (400, 200)
renderLayerShadow.scene = bpy.data.scenes[2]

# Connect all nodes
compositor.links.new(renderLayerMain.outputs["Image"], customNodeGroup.inputs["Image"])
compositor.links.new(renderLayerMain.outputs["Alpha"], customNodeGroup.inputs["Fac"])
compositor.links.new(renderLayerShadow.outputs["Alpha"], customNodeGroup.inputs["Alpha"])
compositor.links.new(renderLayerShadow.outputs["Shadow Catcher"], customNodeGroup.inputs["Shadow Catcher"])
compositor.links.new(customNodeGroup.outputs["Image"], Composite.inputs["Image"])

# Ta-daa! :)