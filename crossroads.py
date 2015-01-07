# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "Crossroads" in locals():
    import imp
    imp.reload(const)
else:
    from city_generator import const


import bpy
from math import pi

class Crossroads:
    """Class managing the crossroads."""

    
    def __init__(self, x_start, x_size, y_start, y_size, city):
        """Create a new crossroad with the given coordinates."""
        
        # save the values
        self.x_start = x_start
        self.x_size = x_size
        self.y_start = y_start
        self.y_size = y_size
        self.city = city
        
        # draw itself
        self.draw()
        
        # add details
        self.add_details()


    def add_details(self):
        """Add some details, like the traffic lights."""
        
        offset = const.pavement_size / 2
        self.add_traffic_lights(self.x_start - offset,
                                self.y_start - offset,
                                -pi/2)
        self.add_traffic_lights(self.x_start + self.x_size + offset,
                                self.y_start - offset,
                                0)
        self.add_traffic_lights(self.x_start + self.x_size + offset,
                                self.y_start + self.y_size + offset,
                                pi/2)
        self.add_traffic_lights(self.x_start - offset,
                                self.y_start + self.y_size + offset,
                                pi)
    
    
    def add_traffic_lights(self, x, y, angle):
        """Add some traffic_lights at the given coordinates.
        The (z-)angle should be in radians."""
        
        traffic_lights = bpy.data.objects["traffic_lights"].copy()
        traffic_lights.name = "C_Traffic_lights.000"
        traffic_lights.location = (x, y,
            self.city.ground.altitude_f(x, y))
        traffic_lights.rotation_euler = (0, 0, angle)
        self.city.scene.objects.link(traffic_lights)

    
    def draw(self):
        """Draw the road."""
        
        # leave EDIT mode if needed
        if bpy.context.object:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # create a plane
        bpy.ops.mesh.primitive_plane_add(radius=0.5, location=(0, 0, 0))
        
        # recover infos
        self.scene = bpy.context.scene
        self.object = bpy.context.object
        self.mesh = self.object.data
        
        # rename
        self.object.name = "C_Crossroads.000"
        self.mesh.name = "C_Crossroads.000"
        
        # scale it
        self.object.scale[0] = self.x_size
        self.object.scale[1] = self.y_size
        bpy.ops.object.transform_apply(scale=True)
        
        # locate it
        self.object.location[0] = self.x_start + self.x_size / 2
        self.object.location[1] = self.y_start + self.y_size / 2
        bpy.ops.object.transform_apply(location=True)
        
        # subdivide it
        if (self.x_size >= 2 * self.y_size
            or self.y_size >= 2 * self.x_size):
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.select_all(action = 'DESELECT')
            bpy.context.tool_settings.mesh_select_mode = [False, True,
                                                          False]
            bpy.ops.object.mode_set(mode='OBJECT')
            for vert in self.mesh.vertices:
                vert.select = True
            if self.x_size > self.y_size:
                self.mesh.edges[0].select = True
                self.mesh.edges[1].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.subdivide(number_cuts=int(self.x_size
                                                       / self.y_size))
            else:
                self.mesh.edges[2].select = True
                self.mesh.edges[3].select = True
                bpy.ops.object.mode_set(mode='EDIT')
                bpy.ops.mesh.subdivide(number_cuts=int(self.y_size
                                                       / self.x_size))
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.subdivide(number_cuts=int(min(self.x_size,
                                                   self.y_size)))
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # change altitude
        altitude_f = self.city.ground.altitude_f
        for vertex in self.mesh.vertices:
            vertex.co.z = altitude_f(vertex.co.x, vertex.co.y)

        # extrude
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action = 'SELECT')
        bpy.ops.mesh.extrude_region_move( \
            MESH_OT_extrude_region={"mirror":False},
            TRANSFORM_OT_translate={
                "value":(0, 0, -const.planes_thickness),
                "constraint_axis":(False, False, True),
                "constraint_orientation":'NORMAL',
                "mirror":False,
                "proportional":'DISABLED',
                "proportional_edit_falloff":'SMOOTH',
                "proportional_size":1,
                "snap":False,
                "snap_target":'CLOSEST',
                "snap_point":(0, 0, 0),
                "snap_align":False,
                "snap_normal":(0, 0, 0),
                "texture_space":False,
                "remove_on_cancel":False,
                "release_confirm":False
            })
        bpy.ops.mesh.dissolve_limited()
        bpy.ops.object.mode_set(mode='OBJECT')

        # add the material
        self.material = bpy.data.materials.new("C_Crossroads.000")
        self.mesh.materials.append(self.material)
        self.material.diffuse_color = (0, 0, 0)

        # add the texture
        m_tex = self.material.texture_slots.add()
        m_tex.texture = bpy.data.textures["crossroads"].copy()
        m_tex.texture.name = "C_crossroads"
        m_tex.texture_coords = 'ORCO'
        m_tex.texture.extension = 'CLIP'
        
        # update
        self.mesh.update()
