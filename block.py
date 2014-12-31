# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "Block" in locals():
    import imp
    imp.reload(const)
    imp.reload(crossroads)
    imp.reload(parcel)
    imp.reload(road)
else:
    from city_generator import const, crossroads, parcel, road


import bpy
import random

class Block:
    """Class managing the blocks."""
    
    def __init__(self, x_start, x_size, y_start, y_size, road_size,
                 city):
        """Create a new block of building and subdivide it."""
        
        # save the values
        self.x_start = x_start
        self.x_size = x_size
        self.y_start = y_start
        self.y_size = y_size
        self.road_size = road_size
        self.city = city
        
        # subdivide
        if (x_size <= city.max_block_size
            and y_size <= city.max_block_size):
            # block should not be cutted further, create it
            self.create()
        
        elif (x_size <= city.max_block_size):
            # y cut
            self.cut_y_axis()
        
        elif (y_size <= city.max_block_size):
            # x cut
            self.cut_x_axis()
        
        else:
            # double cut
            self.double_cut()
    
    
    def cut_y_axis(self):
        """Cut in y."""
        
        y_road_size = self.corrected_road_size(self.y_size)
        y_cut = random.uniform(self.city.min_block_size,
            self.y_size-self.city.min_block_size-y_road_size)
        Block(self.x_start, self.x_size, self.y_start, y_cut,
              self.decreased(y_road_size), self.city)
        road.Road(self.x_start, self.x_size, self.y_start+y_cut,
                  y_road_size, 0, self.city)
        Block(self.x_start, self.x_size, self.y_start+y_cut+y_road_size,
              self.y_size-y_cut-y_road_size,
              self.decreased(y_road_size), self.city)
    
    
    def cut_x_axis(self):
        """Cut in x."""
        
        x_road_size = self.corrected_road_size(self.x_size)
        x_cut = random.uniform(self.city.min_block_size,
            self.x_size-self.city.min_block_size-x_road_size)
        Block(self.x_start, x_cut, self.y_start, self.y_size,
              self.decreased(x_road_size), self.city)
        road.Road(self.x_start+x_cut, x_road_size, self.y_start,
                  self.y_size, 1, self.city)
        Block(self.x_start+x_cut+x_road_size,
              self.x_size-x_cut-x_road_size, self.y_start, self.y_size,
              self.decreased(x_road_size), self.city)
    
    
    def double_cut(self):
        """Cut in x and y."""
        
        x_road_size = self.corrected_road_size(self.x_size)
        y_road_size = self.corrected_road_size(self.y_size)
        next_road_size = self.decreased(min(x_road_size, y_road_size))
        x_cut = random.uniform(self.city.min_block_size,
            self.x_size-self.city.min_block_size-x_road_size)
        y_cut = random.uniform(self.city.min_block_size,
            self.y_size-self.city.min_block_size-y_road_size)
        
        Block(self.x_start, x_cut, self.y_start, y_cut, next_road_size,
              self.city)
        road.Road(self.x_start+x_cut, x_road_size, self.y_start,
                  y_cut, 1, self.city)
        Block(self.x_start+x_cut+x_road_size,
              self.x_size-x_cut-x_road_size, self.y_start, y_cut,
              next_road_size,
              self.city)
        
        road.Road(self.x_start, x_cut, self.y_start+y_cut,
                  y_road_size, 0, self.city)
        crossroads.Crossroads(self.x_start+x_cut, x_road_size,
                              self.y_start+y_cut, y_road_size,
                              self.city)
        road.Road(self.x_start+x_cut+x_road_size,
                  self.x_size-x_cut-x_road_size, self.y_start+y_cut,
                  y_road_size, 0, self.city)
        
        Block(self.x_start, x_cut, self.y_start+y_cut+y_road_size,
              self.y_size-y_cut-y_road_size, next_road_size,
              self.city)
        road.Road(self.x_start+x_cut, x_road_size,
                  self.y_start+y_cut+y_road_size,
                  self.y_size-y_cut-y_road_size, 1, self.city)
        Block(self.x_start+x_cut+x_road_size,
              self.x_size-x_cut-x_road_size,
              self.y_start+y_cut+y_road_size,
              self.y_size-y_cut-y_road_size, next_road_size,
              self.city)
    
    
    def draw(self):
        """Draw the block."""
        
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
        self.object.name = "C_Block.000"
        self.mesh.name = "C_Block.000"
        
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
            vertex.co.z = altitude_f(vertex.co.x, vertex.co.y) + \
                const.pavement_thickness
        
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
        self.material = bpy.data.materials.new("C_Pavement.000")
        self.mesh.materials.append(self.material)
        self.material.diffuse_color = (0.2, 0.2, 0.2)

        # add the regular texture
        m_tex = self.material.texture_slots.add()
        m_tex.texture = bpy.data.textures["pavement_regular"].copy()
        m_tex.texture.repeat_x = round(10*self.x_size)
        m_tex.texture.repeat_y = round(10*self.y_size)
        
        # add the normal displacement texture
        m_tex = self.material.texture_slots.add()
        m_tex.texture = bpy.data.textures["pavement_nrm"].copy()
        m_tex.texture.repeat_x = round(10*self.x_size)
        m_tex.texture.repeat_y = round(10*self.y_size)
        m_tex.use_map_color_diffuse = False
        m_tex.use_map_normal = True
        m_tex.normal_factor = 5
        
        # update
        self.mesh.update()
    
    
    def corrected_road_size(self, block_size):
        """Return the road_size after correction with regard to the
        block_size : if the road is too big, decrease it."""
        
        return min(self.road_size,
                   block_size-2*self.city.min_block_size)
    
    
    def decreased(self, size):
        """Return a decreased size, for the roads (size >= 1)."""
        
        return (size + const.min_road_size)/2
    
    
    def create(self):
        """Properly create the block."""
        
        self.city.blocks.add(self)
        
        # draw it
        self.draw()
        
        # parcel it
        self.parcel()
        
    def parcel(self):
        """Cut it into parcels."""
        
        # get the coordinates without pavement
        parcels_x_start = self.x_start + const.pavement_size
        parcels_x_size = self.x_size - 2*const.pavement_size
        parcels_y_start = self.y_start + const.pavement_size
        parcels_y_size = self.y_size - 2*const.pavement_size
        
        # create the corner buildings
        min_corner_size = const.min_building_size
        max_corner_size = min(parcels_x_size/3,
                              parcels_y_size/3,
                              const.max_building_size)
        corner_building_sizes = list((0, 0, 0, 0))
        for i in range(4):
            corner_building_sizes[i] = random.uniform(min_corner_size,
                                                      max_corner_size)
        # S-W corner
        parcel.Parcel(parcels_x_start + corner_building_sizes[0]/2,
                      corner_building_sizes[0],
                      parcels_y_start + corner_building_sizes[0]/2,
                      corner_building_sizes[0], 0, self.city)
        # S-E corner
        parcel.Parcel(parcels_x_start + parcels_x_size \
                        - corner_building_sizes[1]/2,
                      corner_building_sizes[1],
                      parcels_y_start + corner_building_sizes[1]/2,
                      corner_building_sizes[1], 1, self.city)
        # N-E corner
        parcel.Parcel(parcels_x_start + parcels_x_size \
                        - corner_building_sizes[2]/2,
                      corner_building_sizes[2],
                      parcels_y_start + parcels_y_size \
                      - corner_building_sizes[2]/2,
                      corner_building_sizes[2], 2, self.city)
        # N-W corner
        parcel.Parcel(parcels_x_start + corner_building_sizes[3]/2,
                      corner_building_sizes[3],
                      parcels_y_start + parcels_y_size \
                        - corner_building_sizes[3]/2,
                      corner_building_sizes[3], 3, self.city)
        
        # create the other buildings
        # S face
        parcels_side_x_sizes = self.cut_parcels_side(
            parcels_x_size - corner_building_sizes[0] \
                - corner_building_sizes[1])
        parcels_side_x_starts = list(parcels_side_x_sizes)
        temp_x_start = parcels_x_start + corner_building_sizes[0]
        for i in range(len(parcels_side_x_sizes)):
            parcels_side_x_starts[i] = temp_x_start
            temp_x_start = temp_x_start + parcels_side_x_sizes[i]
            parcel_y_size = random.uniform(
                const.min_building_size,
                min(parcels_side_x_starts[i] - parcels_x_start,
                    parcels_x_start + parcels_x_size \
                        - (parcels_side_x_starts[i] +
                            parcels_side_x_sizes[i]),
                    parcels_y_size/2,
                    const.max_building_size))
            parcel.Parcel(parcels_side_x_starts[i] \
                          + parcels_side_x_sizes[i]/2,
                          parcels_side_x_sizes[i],
                          parcels_y_start + parcel_y_size/2,
                          parcel_y_size, 0, self.city)
        # E face
        parcels_side_y_sizes = self.cut_parcels_side(
            parcels_y_size - corner_building_sizes[1] \
                - corner_building_sizes[2])
        parcels_side_y_starts = list(parcels_side_y_sizes)
        temp_y_start = parcels_y_start + corner_building_sizes[1]
        for i in range(len(parcels_side_y_sizes)):
            parcels_side_y_starts[i] = temp_y_start
            temp_y_start = temp_y_start + parcels_side_y_sizes[i]
            parcel_x_size = random.uniform(
                const.min_building_size,
                min(parcels_side_y_starts[i] - parcels_y_start,
                    parcels_y_start + parcels_y_size \
                        - (parcels_side_y_starts[i] +
                            parcels_side_y_sizes[i]),
                    parcels_x_size/2,
                    const.max_building_size))
            parcel.Parcel(parcels_x_start + parcels_x_size \
                              - parcel_x_size/2,
                          parcel_x_size,
                          parcels_side_y_starts[i] \
                          + parcels_side_y_sizes[i]/2,
                          parcels_side_y_sizes[i], 0, self.city)
        # N face
        parcels_side_x_sizes = self.cut_parcels_side(
            parcels_x_size - corner_building_sizes[2] \
                - corner_building_sizes[3])
        parcels_side_x_starts = list(parcels_side_x_sizes)
        temp_x_start = parcels_x_start + corner_building_sizes[3]
        for i in range(len(parcels_side_x_sizes)):
            parcels_side_x_starts[i] = temp_x_start
            temp_x_start = temp_x_start + parcels_side_x_sizes[i]
            parcel_y_size = random.uniform(
                const.min_building_size,
                min(parcels_side_x_starts[i] - parcels_x_start,
                    parcels_x_start + parcels_x_size \
                        - (parcels_side_x_starts[i] +
                            parcels_side_x_sizes[i]),
                    parcels_y_size/2,
                    const.max_building_size))
            parcel.Parcel(parcels_side_x_starts[i] \
                          + parcels_side_x_sizes[i]/2,
                          parcels_side_x_sizes[i],
                          parcels_y_start + parcels_y_size \
                              - parcel_y_size/2,
                          parcel_y_size, 0, self.city)
        # E face
        parcels_side_y_sizes = self.cut_parcels_side(
            parcels_y_size - corner_building_sizes[3] \
                - corner_building_sizes[0])
        parcels_side_y_starts = list(parcels_side_y_sizes)
        temp_y_start = parcels_y_start + corner_building_sizes[0]
        for i in range(len(parcels_side_y_sizes)):
            parcels_side_y_starts[i] = temp_y_start
            temp_y_start = temp_y_start + parcels_side_y_sizes[i]
            parcel_x_size = random.uniform(
                const.min_building_size,
                min(parcels_side_y_starts[i] - parcels_y_start,
                    parcels_y_start + parcels_y_size \
                        - (parcels_side_y_starts[i] +
                            parcels_side_y_sizes[i]),
                    parcels_x_size/2,
                    const.max_building_size))
            parcel.Parcel(parcels_x_start + parcel_x_size/2,
                          parcel_x_size,
                          parcels_side_y_starts[i] \
                          + parcels_side_y_sizes[i]/2,
                          parcels_side_y_sizes[i], 0, self.city)
    
    
    def cut_parcels_side(self, length):
        """From one length, give an array of length in such a way that
        the sum stay constant and each as a standard building size."""
        if length <= const.max_building_size:
            return [length]
        else:
            a = random.uniform(const.min_building_size,
                               length - const.min_building_size)
            return self.cut_parcels_side(a) + \
                self.cut_parcels_side(length - a)
