bl_info = {
    "name": "City Generator",
    "author": "Guillaume Dauphin & Antoine Dujardin",
    "category": "Add Mesh"
}

# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "bpy" in locals():
    import imp
    imp.reload(city)
    imp.reload(const)
    imp.reload(parcel)
    imp.reload(park_block)
    imp.reload(resources)
else:
    from city_generator import city
    from city_generator import const
    from city_generator import parcel
    from city_generator import park_block
    from city_generator import resources


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
        row.prop(scene, 'relief_complexity')
        row = layout.row()
        row.prop(scene, 'relief_amplitude')
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
        row.prop(scene, 'size_var')
        row = layout.row()
        row.prop(scene, 'center_radius')
        row = layout.row()
        row.prop(scene, 'park_proba')
        row = layout.row()
        row.prop(scene, 'elem_density')
        row = layout.row()
        row.prop(scene, 'lamp_distance')
        row = layout.row()
        row.prop(scene, 'day')
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
        
        if scene.city_x_size < scene.min_block_size \
            or scene.city_y_size < scene.min_block_size:
            self.report({'ERROR_INVALID_INPUT'},
                        "X and Y size should be at least equal to " \
                            + "Min block size")
            return {'CANCELLED'}
        elif scene.max_block_size < (2*scene.min_block_size +
                                    const.min_road_size):
            self.report({'ERROR_INVALID_INPUT'},
                        "Max block size should be at least equal to " \
                            "two times Min block size + {}".format(
                                const.min_road_size))
            return {'CANCELLED'}
        
        # Remove previous city (if any)
        bpy.ops.city.delete()
        
        # Load the resources
        resources.load_all()
        parcel.Parcel.load_buildings()
        park_block.ParkBlock.load_parks()
        
        # Create the city
        city_instance = city.City(scene.city_x_size,
                                  scene.city_y_size,
                                  scene.min_block_size,
                                  scene.max_block_size,
                                  scene.road_size,
                                  scene.size_var,
                                  scene.center_radius,
                                  scene.park_proba,
                                  scene.elem_density,
                                  scene.day,
                                  scene.relief_complexity,
                                  scene.relief_amplitude,
                                  scene.lamp_distance,
                                  scene)
        
        return {'FINISHED'}


class OBJECT_OT_DeleteCity(bpy.types.Operator):
    bl_idname = "city.delete"
    bl_label = "Delete"
    bl_description = "Delete the city"
 
    def execute(self, context):
        global city_instance
        scene = context.scene
        
        # delete city and python objects
        if city_instance != None:
            del city_instance
            city_instance = None
        
        # delect all
        if bpy.context.object:
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT') 
        
        # unlink objects
        for key, object in scene.objects.items():
            if key.startswith("C_"):
                scene.objects.unlink(object)
        
        # erase the objects
        for key, object in bpy.data.objects.items():
            if key.startswith("C_"):
                bpy.data.objects.remove(object)
                del object
        
        # erase the meshes
        for key, mesh in bpy.data.meshes.items():
            if key.startswith("C_"):
                bpy.data.meshes.remove(mesh)
                del mesh
        
        # erase the materials
        for key, material in bpy.data.materials.items():
            if key.startswith("C_"):
                bpy.data.materials.remove(material)
                del material

        # erase the textures
        for key, texture in bpy.data.textures.items():
            if key.startswith("C_"):
                bpy.data.textures.remove(texture)
                del texture
    
        return {'FINISHED'}


def register():
    bpy.utils.register_module(__name__)
    
    bpy.types.Scene.relief_complexity = bpy.props.IntProperty(
        name="Relief complexity",
        description="Relief complexity index: 0 (no relief), " \
            + "1 (single mound), 2 (several mounds)",
        default=1,
        min=0,
        max=2
    )
    bpy.types.Scene.relief_amplitude = bpy.props.FloatProperty(
        name="Relief_amplitude",
        description="Approximation of the maximum amplitude",
        default=3,
        min=0,
        max=5,
        precision=1,
        step=10
    )
    bpy.types.Scene.city_x_size = bpy.props.FloatProperty(
        name="X size",
        description="City size in the x axis",
        default=30.0,
        min=1.0,
        max=100.0,
        precision=1,
        step=50
    )
    bpy.types.Scene.city_y_size = bpy.props.FloatProperty(
        name="Y size",
        description="City size in the z axis",
        default=30.0,
        min=1.0,
        max=100.0,
        precision=1,
        step=50
    )
    bpy.types.Scene.min_block_size = bpy.props.FloatProperty(
        name="Min block size",
        description="Minimal size for the blocks",
        default=3.0,
        min=2.0,
        max=10.0,
        precision=1,
        step=10
    )
    bpy.types.Scene.max_block_size = bpy.props.FloatProperty(
        name="Max block size",
        description="Maximal size for the blocks",
        default=10.0,
        min=3.0,
        max=30.0,
        precision=1,
        step=10
    )
    bpy.types.Scene.road_size = bpy.props.FloatProperty(
        name="Road size",
        description="Size of the main roads",
        default=2.0,
        min=const.min_road_size,
        max=5.0
    )
    bpy.types.Scene.size_var = bpy.props.FloatProperty(
        name="Size variance",
        description="Relative variance for element heights and sizes",
        default=.05,
        min=0,
        max=.1,
        step=1
    )
    bpy.types.Scene.center_radius = bpy.props.FloatProperty(
        name="Center relative radius",
        description="Relative radius of the city center",
        default = .2,
        min=0,
        max=1,
        step=1
    )
    bpy.types.Scene.park_proba = bpy.props.FloatProperty(
        name="Park probability",
        description="Probability of a block being a park",
        default=.1,
        min=0,
        max=.3
    )
    bpy.types.Scene.elem_density = bpy.props.FloatProperty(
        name="Element density",
        description="Density of elements like trees",
        default=.2,
        min=0,
        max=.5
    )
    bpy.types.Scene.lamp_distance = bpy.props.FloatProperty(
        name="Lamp distance",
        description="Distance between consecutive road lamps",
        default=1,
        min=.5,
        max=10
    )
    bpy.types.Scene.day = bpy.props.BoolProperty(
        name="Day",
        description="Day or night",
        default=True
    )


def unregister():
    bpy.utils.unregister_module(__name__)
    del bpy.types.Scene.relief_amplitude
    del bpy.types.Scene.relief_complexity
    del bpy.types.Scene.city_x_size
    del bpy.types.Scene.city_y_size
    del bpy.types.Scene.min_block_size
    del bpy.types.Scene.max_block_size
    del bpy.types.Scene.road_size
    del bpy.types.Scene.size_var
    del bpy.types.Scene.center_radius
    del bpy.types.Scene.park_proba
    del bpy.types.Scene.elem_density
    del bpy.types.Scene.lamp_distance
    del bpy.types.Scene.day


if __name__ == "__main__":
    register()
