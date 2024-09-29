bl_info = {
    "name": "Light Render AI",
    "blender": (2, 80, 0),  # Update version as necessary
    "category": "Object",
}

import bpy
import os
import mathutils
import json
import random

# Folder to save renders and metadata (make sure this path exists)
output_dir = "D:/Lightrenderai"
lighting_data_file = os.path.join(output_dir, "lighting_data.json")
progress_log_file = os.path.join(output_dir, "progress_log.json")

# Load or initialize lighting data
def load_data():
    try:
        with open(lighting_data_file, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []
    except IOError as e:
        print(f"Error loading data: {e}")
        return []

# Save data to a file
def save_data(data):
    try:
        with open(lighting_data_file, "w") as file:
            json.dump(data, file, indent=4)
    except IOError as e:
        print(f"Error saving data: {e}")

# Save progress log
def save_progress_log(log):
    try:
        with open(progress_log_file, "w") as file:
            json.dump(log, file, indent=4)
    except IOError as e:
        print(f"Error saving progress log: {e}")

# Function to get a simplified shape representation of the object
def get_final_shape(obj):
    shape_info = {
        "type": obj.type,
        "scale": obj.scale[:],
    }
    if obj.type == 'MESH':
        shape_info["num_vertices"] = len(obj.data.vertices)
        shape_info["num_faces"] = len(obj.data.polygons)
    else:
        shape_info["num_vertices"] = 0
        shape_info["num_faces"] = 0
    return shape_info

# Function to learn from ratings
def learn_from_ratings(shape_data, lighting_settings, lighting_rating, camera_rating, predicted_lighting_rating, predicted_camera_rating):
    if shape_data['type'] == 'LIGHT':
        return  # Skip lights

    data = load_data()
    data.append({
        "shape_data": shape_data,
        "lighting_settings": lighting_settings,
        "lighting_rating": lighting_rating,
        "camera_rating": camera_rating,
        "predicted_lighting_rating": predicted_lighting_rating,
        "predicted_camera_rating": predicted_camera_rating
    })
    save_data(data)

    lighting_success = 1 if lighting_rating == predicted_lighting_rating else 0
    camera_success = 1 if camera_rating == predicted_camera_rating else 0
    progress_log.append({
        "actual_lighting_rating": lighting_rating,
        "predicted_lighting_rating": predicted_lighting_rating,
        "lighting_success": lighting_success,
        "actual_camera_rating": camera_rating,
        "predicted_camera_rating": predicted_camera_rating,
        "camera_success": camera_success
    })

    save_progress_log(progress_log)

# Function to add lights based on AI predictions
def add_lights_with_ai(obj, num_lights=10, light_distance=1.0, brightness=1.0):
    lights_info = []
    obj_dimensions = obj.dimensions
    max_distance = max(obj_dimensions) * 0.5 + light_distance

    light_color = (1.0, 1.0, 1.0) if not bpy.context.scene.use_colored_lights else (random.random(), random.random(), random.random())

    for _ in range(num_lights):
        light_data = bpy.data.lights.new(name="AI_Light", type='POINT')
        light_object = bpy.data.objects.new(name="AI_Light", object_data=light_data)
        bpy.context.collection.objects.link(light_object)
        light_object.location = [
            obj.location.x + random.uniform(-max_distance, max_distance),
            obj.location.y + random.uniform(-max_distance, max_distance),
            obj.location.z + random.uniform(-max_distance, max_distance)
        ]
        light_data.energy = random.uniform(500, 1500) * brightness
        light_data.color = light_color
        lights_info.append({'location': list(light_object.location), 'energy': light_data.energy})

    return lights_info

def delete_all_lights():
    for obj in bpy.data.objects:
        if obj.type == 'LIGHT':
            bpy.data.objects.remove(obj)

def save_render_and_data(obj, lights_info):
    scene_name = f"scene_{random.randint(1000, 9999)}"
    image_path = os.path.join(output_dir, scene_name + ".png")
    metadata_path = os.path.join(output_dir, scene_name + ".txt")

    bpy.context.scene.render.filepath = image_path
    bpy.ops.render.render(write_still=True)

    with open(metadata_path, 'w') as file:
        file.write(f"Object: {obj.name}\n")
        file.write(f"Location: {obj.location}\n")
        file.write(f"Scale: {obj.scale}\n")

        for light_info in lights_info:
            file.write(f"Light Location: {light_info['location']}\n")
            file.write(f"Light Energy: {light_info['energy']}\n")

        file.write(f"Lighting Rating: {lighting_rating}\n")
        file.write(f"Camera Rating: {camera_rating}\n")

def position_camera_near_object(obj, max_distance=20.0):
    if "Camera" in bpy.data.objects:
        cam = bpy.data.objects["Camera"]
    else:
        bpy.ops.object.camera_add()
        cam = bpy.context.active_object

    cam.location = obj.location + mathutils.Vector((random.uniform(-max_distance, max_distance),
                                                     random.uniform(-max_distance, max_distance),
                                                     random.uniform(1.0, max_distance)))

    direction = cam.location - obj.location
    rot_quat = direction.to_track_quat('Z', 'Y')
    cam.rotation_euler = rot_quat.to_euler()
    bpy.context.scene.camera = cam

lighting_rating = None
camera_rating = None
progress_log = []

def save_current_scene_data():
    obj = bpy.context.active_object
    lights_info = [dict(location=list(light.location), energy=light.data.energy)
                   for light in bpy.data.objects if light.type == 'LIGHT']

    save_render_and_data(obj, lights_info)

    shape_data = get_final_shape(obj)

    predicted_lighting_rating = random.randint(1, 10)
    predicted_camera_rating = random.randint(1, 10)

    lighting_settings = {
        "location": list(lights_info[0]['location']) if lights_info else [0, 0, 0],
        "energy": lights_info[0]['energy'] if lights_info else 1000,
        "color": (1.0, 1.0, 1.0)
    }
    
    learn_from_ratings(shape_data, lighting_settings, lighting_rating, camera_rating, predicted_lighting_rating, predicted_camera_rating)

def create_scene_with_ai(max_camera_distance=20.0, light_distance=1.0, max_lights=10, brightness=1.0):
    delete_all_lights()
    global lighting_rating, camera_rating
    lighting_rating = None
    camera_rating = None
    objects = [obj for obj in bpy.context.scene.objects if obj.type == 'MESH']
    if objects:
        for obj in objects:
            lights_info = add_lights_with_ai(obj, num_lights=max_lights, light_distance=light_distance, brightness=brightness)
            position_camera_near_object(obj, max_camera_distance)
            save_current_scene_data()

class WM_OT_rate_lighting(bpy.types.Operator):
    bl_idname = "wm.rate_lighting"
    bl_label = "Rate Lighting"
    rating: bpy.props.IntProperty()

    def execute(self, context):
        global lighting_rating
        lighting_rating = self.rating
        if camera_rating is not None:
            save_current_scene_data()
        return {'FINISHED'}

class WM_OT_rate_camera(bpy.types.Operator):
    bl_idname = "wm.rate_camera"
    bl_label = "Rate Camera"
    rating: bpy.props.IntProperty()

    def execute(self, context):
        global camera_rating
        camera_rating = self.rating
        if lighting_rating is not None:
            save_current_scene_data()
        return {'FINISHED'}

class WM_OT_generate_scene(bpy.types.Operator):
    bl_idname = "wm.generate_scene"
    bl_label = "Generate New Scene"

    def execute(self, context):
        create_scene_with_ai(max_camera_distance=context.scene.max_camera_distance, 
                              light_distance=context.scene.light_distance, 
                              max_lights=context.scene.max_number_of_lights,
                              brightness=context.scene.brightness)
        return {'FINISHED'}

class WM_PT_scene_generator(bpy.types.Panel):
    bl_label = "Scene Generator"
    bl_idname = "WM_PT_scene_generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Scene Gen"

    def draw(self, context):
        layout = self.layout
        layout.operator("wm.generate_scene", text="Generate New Scene")
        layout.prop(context.scene, "max_camera_distance")
        layout.prop(context.scene, "light_distance")
        layout.prop(context.scene, "max_number_of_lights")
        layout.prop(context.scene, "use_colored_lights")
        layout.prop(context.scene, "brightness")

# Register properties and classes
def register():
    bpy.types.Scene.max_camera_distance = bpy.props.FloatProperty(
        name="Max Camera Distance", 
        default=20.0, 
        min=1.0, 
        max=1000.0
    )
    bpy.types.Scene.light_distance = bpy.props.FloatProperty(
        name="Light Distance", 
        default=1.0, 
        min=0.0, 
        max=1000.0
    )
    bpy.types.Scene.max_number_of_lights = bpy.props.IntProperty(
        name="Max Number of Lights", 
        default=10, 
        min=1, 
        max=100
    )
    bpy.types.Scene.use_colored_lights = bpy.props.BoolProperty(name="Use Colored Lights", default=True)
    bpy.types.Scene.brightness = bpy.props.FloatProperty(
        name="Brightness", 
        default=1.0, 
        min=0.0, 
        max=10.0
    )

    bpy.utils.register_class(WM_OT_rate_lighting)
    bpy.utils.register_class(WM_OT_rate_camera)
    bpy.utils.register_class(WM_OT_generate_scene)
    bpy.utils.register_class(WM_PT_scene_generator)
    global progress_log
    progress_log = []

def unregister():
    bpy.utils.unregister_class(WM_PT_scene_generator)
    bpy.utils.unregister_class(WM_OT_generate_scene)
    bpy.utils.unregister_class(WM_OT_rate_camera)
    bpy.utils.unregister_class(WM_OT_rate_lighting)
    del bpy.types.Scene.max_camera_distance
    del bpy.types.Scene.light_distance
    del bpy.types.Scene.max_number_of_lights
    del bpy.types.Scene.use_colored_lights
    del bpy.types.Scene.brightness

if __name__ == "__main__":
    register()
