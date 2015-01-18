# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "Road" in locals():
    import imp
    imp.reload(car)
    imp.reload(const)
else:
    from city_generator import car, const


import bpy
import random

class Road:
    """Class managing the roads."""

    def __init__(self, x_start, x_size, y_start, y_size, orientation,
                 city):
        """Create a new road with the given coordinates.
        Orientation is 0 (1) for a road parallel to the x-axis (y)."""
        
        # save the values
        self.x_start = x_start
        self.x_size = x_size
        self.y_start = y_start
        self.y_size = y_size
        self.orientation = orientation
        self.city = city
        
        # draw itself
        self.draw()
        
        # add cars
        self.add_cars()
    
    
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
        self.object.name = "C_Road.000"
        self.mesh.name = "C_Road.000"
        
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
        self.material = bpy.data.materials.new("C_Road.000")
        self.mesh.materials.append(self.material)
        self.material.diffuse_color = (0, 0, 0)

        # add the texture
        m_tex = self.material.texture_slots.add()
        m_tex.texture_coords = 'ORCO'
        if self.orientation:
            m_tex.texture = bpy.data.textures["vert_road"].copy()
            m_tex.texture.name = "C_vert_road"
            m_tex.texture.extension = 'REPEAT'
            m_tex.texture.repeat_y = round(self.y_size)
        else:
            m_tex.texture = bpy.data.textures["hor_road"].copy()
            m_tex.texture.name = "C_hor_road"
            m_tex.texture.extension = 'REPEAT'
            m_tex.texture.repeat_x = round(self.x_size)
        
        # update
        self.mesh.update()
        
        # parent
        self.object.parent = self.city.roads_object


    def add_cars(self):
        """Add cars to the road."""
        
        if self.orientation: # vertical
            if self.y_size < 12:
                return
            car.Car(self.x_start + self.x_size/4, self.y_start + 1, 0,
                    10, self)
        else: # horizontal
            if self.x_size < 12:
                return
            car.Car(self.x_start + 1, self.y_start + self.y_size/4, 3,
                    10, self)
