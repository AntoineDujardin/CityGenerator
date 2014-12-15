bl_info = {
    "name": "City Generator",
    "author": "Guillaume Dauphin & Antoine Dujardin",
    "category": "Add Mesh"
}

# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
    import imp
    imp.reload(block)
    imp.reload(city)
    imp.reload(ground)
else:
    from city_generator import block, city, ground

import bpy

# shared
city_instance = None

class CityGeneratorPanel(bpy.types.Panel):
    bl_label = "City Generator"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'Generators'
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="City Parameters:")
        
        scene = context.scene
        row = layout.row()
        row.prop(scene, 'city_x_size')
        row = layout.row()
        row.prop(scene, 'city_y_size')
        row = layout.row()
        row.prop(scene, 'min_block_size')
        row = layout.row()
        row.prop(scene, 'max_block_size')
        row = layout.row()
        row.prop(scene, 'road_size')
        row = layout.row()
        row.operator('city.generate')
        row.operator('city.delete')


class OBJECT_OT_GenerateCity(bpy.types.Operator):
    bl_idname = "city.generate"
    bl_label = "Generate"
    bl_description = "Generates the city based on the given parameters"
 
    def execute(self, context):
        global city_instance
        scene = context.scene
        
        if (scene.city_x_size < scene.min_block_size or
            scene.city_y_size < scene.min_block_size or
            scene.max_block_size < (2*scene.min_block_size +
                                    scene.road_size)):
            return {'CANCELLED'}
        
        # Remove previous city (if any)
        bpy.ops.city.delete()
        
        city_instance = city.City(scene.city_x_size,
                                  scene.city_y_size,
                                  scene.min_block_size,
                                  scene.max_block_size,
                                  scene.road_size, scene)
        
        return {'FINISHED'}


class OBJECT_OT_DeleteCity(bpy.types.Operator):
    bl_idname = "city.delete"
    bl_label = "Delete"
    bl_description = "Delete the city"
 
    def execute(self, context):
        global city_instance
        scene = context.scene
        
        if city_instance != None:
            del city_instance
            city_instance = None
    
        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.city_x_size = \
        bpy.props.FloatProperty(name="X size", default=75.0, min=1.0,
                                max=200.0)
    bpy.types.Scene.city_y_size = \
        bpy.props.FloatProperty(name="Y size", default=75.0, min=1.0,
                                max=200.0)
    bpy.types.Scene.min_block_size = \
        bpy.props.FloatProperty(name="Min block size", default=3.0,
                                min=1.0, max=10.0)
    bpy.types.Scene.max_block_size = \
        bpy.props.FloatProperty(name="Max block size", default=8.0,
                                min=3.0, max=21.0)
    bpy.types.Scene.road_size = \
        bpy.props.FloatProperty(name="Road size", default=2.0, min=1.0,
                                max=5.0)


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.city_x_size
    del bpy.types.Scene.city_y_size
    del bpy.types.Scene.min_block_size
    del bpy.types.Scene.max_block_size
    del bpy.types.Scene.road_size


if __name__ == "__main__":
    register()
