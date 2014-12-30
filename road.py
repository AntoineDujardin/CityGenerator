import bpy

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
        
        # add itself to the city roads
        self.city.roads.add(self)
        
        # draw itself
        self.draw()

    
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

        # add the material
        self.material = bpy.data.materials.new("Mat")
        self.mesh.materials.append(self.material)

        # add the texture
        m_tex = self.material.texture_slots.add()
        if self.orientation:
            m_tex.texture = bpy.data.textures["vert_road_text"].copy()
            m_tex.texture.repeat_y = round(self.y_size)
        else:
            m_tex.texture = bpy.data.textures["hor_road_text"].copy()
            m_tex.texture.repeat_x = round(self.x_size)
        
        # update
        self.mesh.update()
