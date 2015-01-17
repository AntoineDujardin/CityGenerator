# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "Block" in locals():
    import imp
    imp.reload(const)
    imp.reload(drawer)
else:
    from city_generator import const, drawer, parcel


import bpy
import random

class Block:
    """Class managing the blocks."""
    
    def __init__(self, x_start, x_size, y_start, y_size, city):
        """Create a new block of buildings."""
        
        # save the values
        self.x_start = x_start
        self.x_size = x_size
        self.y_start = y_start
        self.y_size = y_size
        self.city = city
        
        # get the coordinates without pavement
        self.parcels_x_start = self.x_start + const.pavement_size
        self.parcels_x_size = self.x_size - 2*const.pavement_size
        self.parcels_y_start = self.y_start + const.pavement_size
        self.parcels_y_size = self.y_size - 2*const.pavement_size
        
        # add details (lamps)
        self.add_details()
        
    
    def draw(self, gravel_texture=False):
        """Draw the block.
        Use pavement texture, exept if gravel is asked."""
        
        # draw the plane
        object = drawer.draw_relief_plane(self.x_start, self.x_size,
            self.y_start, self.y_size, "Block",
            self.city.ground.altitude_f,
            const.pavement_thickness)
        
        # add the material
        mesh = object.data
        material = bpy.data.materials.new("C_Pavement.000")
        mesh.materials.append(material)
        material.diffuse_color = (0.2, 0.2, 0.2)

        # add the regular texture
        m_tex = material.texture_slots.add()
        if gravel_texture:
            m_tex.texture = bpy.data.textures["gravel"].copy()
        else:
            m_tex.texture = bpy.data.textures["pavement_regular"].copy()
        m_tex.texture.name = "C_pavement"
        m_tex.texture_coords = 'ORCO'
        m_tex.texture.extension = 'REPEAT'
        m_tex.texture.repeat_x = round(10*self.x_size)
        m_tex.texture.repeat_y = round(10*self.y_size)
        
        if not gravel_texture:
            # add the normal displacement texture
            m_tex = material.texture_slots.add()
            m_tex.texture = bpy.data.textures["pavement_nrm"].copy()
            m_tex.texture.name = "C_pavement_nrm"
            m_tex.texture_coords = 'ORCO'
            m_tex.texture.extension = 'REPEAT'
            m_tex.texture.repeat_x = round(10*self.x_size)
            m_tex.texture.repeat_y = round(10*self.y_size)
            m_tex.use_map_color_diffuse = False
            m_tex.use_map_normal = True
            m_tex.normal_factor = 5
        
        # update
        mesh.update()
        
        
    def draw_grass(self):
        """Draw the block grass."""
        
        # draw the plane
        object = drawer.draw_relief_plane(self.parcels_x_start, 
            self.parcels_x_size, self.parcels_y_start,
            self.parcels_y_size, "Grass_Block",
            self.city.ground.altitude_f,
            2*const.pavement_thickness
        )
        
        # add the material
        mesh = object.data
        material = bpy.data.materials["grass"].copy()
        material.name = "C_grass"
        mesh.materials.append(material)
        
        # update
        mesh.update()
    
    
    def cut_length(self, length, min_l, max_l):
        """From one length, give an array of lengths between min_l and
        max_l. The latter should be at least twice as big as the
        first."""
        
        if length <= max_l:
            return [length]
        else:
            a = random.uniform(min_l, length - min_l)
            return self.cut_length(a, min_l, max_l) + \
                self.cut_length(length - a, min_l, max_l)


    def add_details(self):
        """Add some details, like the lamps."""
        
        offset = const.pavement_size / 3
        cut = lambda d: [offset] + \
            self.cut_length(d - 2*offset, self.city.lamp_distance,
                            2*self.city.lamp_distance)
        dist = 0
        for delta_dist in cut(self.x_size):
            dist += delta_dist
            self.add_lamp(self.x_start + dist,
                           self.y_start + offset)
            self.add_lamp(self.x_start + dist,
                           self.y_start + self.y_size - offset)
        dist = 0
        for delta_dist in cut(self.y_size)[1:-1]:
            # don't do the corners twice
            dist += delta_dist
            self.add_lamp(self.x_start + offset,
                           self.y_start + dist)
            self.add_lamp(self.x_start + self.x_size - offset,
                           self.y_start + dist)
    
    
    def add_lamp(self, x, y):
        """Add some lamps at the given coordinates."""
        
        lamp = bpy.data.objects["ramplamp"].copy()
        lamp.name = "C_Lamp.000"
        lamp.location = (x, y,
            self.city.ground.altitude_f(x, y))
        self.city.scene.objects.link(lamp)
