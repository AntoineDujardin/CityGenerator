# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "City" in locals():
    import imp
    imp.reload(block)
    imp.reload(business_tower_block)
    imp.reload(const)
    imp.reload(crossroads)
    imp.reload(ground)
    imp.reload(joint_house_block)
    imp.reload(park_block)
    imp.reload(residential_building_block)
    imp.reload(residential_house_block)
    imp.reload(road)
else:
    from city_generator import block
    from city_generator import business_tower_block
    from city_generator import const
    from city_generator import crossroads
    from city_generator import ground
    from city_generator import joint_house_block
    from city_generator import park_block
    from city_generator import residential_building_block
    from city_generator import residential_house_block
    from city_generator import road


import bpy
import math
import random

class City:
    """Class managing the creation of the whole city."""
    
    def __init__(self, city_x_size, city_y_size, min_block_size,
                 max_block_size, road_size, size_var,
                 center_radius, park_proba, elem_density, day,
                 relief_complexity, relief_amplitude, scene):
        """Create the city"""
        
        # save the values
        self.x_size = city_x_size
        self.y_size = city_y_size
        self.min_block_size = min_block_size
        self.max_block_size = max_block_size
        self.road_size = road_size
        self.size_var = size_var
        self.center_radius = center_radius
        self.park_proba = park_proba
        self.elem_density = elem_density
        self.day = day
        self.scene = scene
        
        # calculate the radius
        self.radius = math.hypot(self.x_size, self.y_size)/2
        
        # create the ground
        self.ground = ground.Ground(city_x_size, city_y_size,
                                    relief_complexity,
                                    relief_amplitude)
        
        # make the block decomposition
        self.cut_blocks(-self.x_size/2, self.x_size,
                        -self.y_size/2, self.y_size,
                        road_size)
        
        # lighting
        self.set_environment_lightning(day)
        self.add_sun_moon(day)
        
        # camera
        self.add_camera()
        
    
    def add_camera(self):
        """Add a camera to the scene."""
        
        bpy.ops.object.camera_add()
        camera = bpy.context.object
        camera.name = "C_camera"
        camera.location = (0, -1.1*self.y_size, self.y_size)
        camera.rotation_euler = (math.pi/4, 0, 0)
        
        
    def set_environment_lightning(self, day):
        """Set the environment lightning of the scene."""
        
        bpy.data.worlds["World"].light_settings.use_environment_light \
            = True
        bpy.data.worlds["World"].light_settings.environment_energy \
            = day + .1
            
        bpy.data.worlds["World"].light_settings.use_indirect_light \
            = True
        
        bpy.data.worlds["World"].light_settings.gather_method \
            = "APPROXIMATE"
        
        if day:
            bpy.data.worlds["World"].horizon_color = (.1, .3, .5)
        else:
            bpy.data.worlds["World"].horizon_color = (0, 0, .05)
    
    
    def add_sun_moon(self, day):
        """Add a sun or a moon, depending on the day parameter."""
        
        bpy.ops.object.lamp_add(type='SUN', location=(0, 0, 20))
        sun = bpy.context.object
        sun.name = "C_Sun"
        sun.rotation_euler = (math.pi/4, math.pi/4, 0)
        sun.data.energy = day + .1
        
        if day:
            sun.data.color = (1, 1, .7)
        else:
            sun.data.color = (1, 1, 1)


    def cut_blocks(self, x_start, x_size, y_start, y_size, road_size):
        """Separate the city in blocks."""
        
        # subdivide
        if (x_size <= self.max_block_size
            and y_size <= self.max_block_size):
            # block should not be cutted further, create it
            self.create_block(x_start, x_size, y_start, y_size)
        
        elif (x_size <= self.max_block_size):
            # y cut
            self.cut_y_axis(x_start, x_size, y_start, y_size, road_size)
        
        elif (y_size <= self.max_block_size):
            # x cut
            self.cut_x_axis(x_start, x_size, y_start, y_size, road_size)
        
        else:
            # double cut
            self.double_cut(x_start, x_size, y_start, y_size, road_size)

    
    def create_block(self, x_start, x_size, y_start, y_size):
        """Create the block."""
        coef = self.central_coef(x_start, x_size, y_start, y_size)
        
        if random.uniform(0, 1) <= self.park_proba:
            park_block.ParkBlock(x_start, x_size, y_start, y_size, self)
        elif coef <= self.center_radius:
            business_tower_block.BusinessTowerBlock(x_start, x_size,
                                                    y_start, y_size,
                                                    self)
        elif coef <= 2*self.center_radius:
            residential_building_block.ResidentialBuildingBlock(x_start,
                                                                x_size,
                                                                y_start,
                                                                y_size,
                                                                self)
        elif coef <= 3*self.center_radius:
            joint_house_block.JointHouseBlock(x_start, x_size, y_start,
                                              y_size, self)
        else:
            residential_house_block.ResidentialHouseBlock(x_start,
                                                          x_size,
                                                          y_start,
                                                          y_size, self)
        
    

    def cut_y_axis(self, x_start, x_size, y_start, y_size, road_size):
        """Cut in y."""
        
        y_road_size = self.corrected_road_size(road_size, y_size)
        y_cut = random.uniform(self.min_block_size,
            y_size-self.min_block_size-y_road_size)
        self.cut_blocks(x_start, x_size, y_start, y_cut,
                        self.decreased(y_road_size))
        road.Road(x_start, x_size, y_start+y_cut,
                  y_road_size, 0, self)
        self.cut_blocks(x_start, x_size, y_start+y_cut+y_road_size,
                        y_size-y_cut-y_road_size,
                        self.decreased(y_road_size))
    
    
    def cut_x_axis(self, x_start, x_size, y_start, y_size, road_size):
        """Cut in x."""
        
        x_road_size = self.corrected_road_size(road_size, x_size)
        x_cut = random.uniform(self.min_block_size,
            x_size-self.min_block_size-x_road_size)
        self.cut_blocks(x_start, x_cut, y_start, y_size,
                        self.decreased(x_road_size))
        road.Road(x_start+x_cut, x_road_size, y_start,
                  y_size, 1, self)
        self.cut_blocks(x_start+x_cut+x_road_size,
                        x_size-x_cut-x_road_size, y_start, y_size,
                        self.decreased(x_road_size))
    
    
    def double_cut(self, x_start, x_size, y_start, y_size, road_size):
        """Cut in x and y."""
        
        x_road_size = self.corrected_road_size(road_size, x_size)
        y_road_size = self.corrected_road_size(road_size, y_size)
        next_road_size = self.decreased(min(x_road_size, y_road_size))
        x_cut = random.uniform(self.min_block_size,
            x_size-self.min_block_size-x_road_size)
        y_cut = random.uniform(self.min_block_size,
            y_size-self.min_block_size-y_road_size)
        
        self.cut_blocks(x_start, x_cut, y_start, y_cut, next_road_size)
        road.Road(x_start+x_cut, x_road_size, y_start,
                  y_cut, 1, self)
        self.cut_blocks(x_start+x_cut+x_road_size,
                        x_size-x_cut-x_road_size, y_start, y_cut,
                        next_road_size)
        
        road.Road(x_start, x_cut, y_start+y_cut,
                  y_road_size, 0, self)
        crossroads.Crossroads(x_start+x_cut, x_road_size,
                              y_start+y_cut, y_road_size,
                              self)
        road.Road(x_start+x_cut+x_road_size,
                  x_size-x_cut-x_road_size, y_start+y_cut,
                  y_road_size, 0, self)
        
        self.cut_blocks(x_start, x_cut, y_start+y_cut+y_road_size,
                        y_size-y_cut-y_road_size, next_road_size)
        road.Road(x_start+x_cut, x_road_size,
                  y_start+y_cut+y_road_size,
                  y_size-y_cut-y_road_size, 1, self)
        self.cut_blocks(x_start+x_cut+x_road_size,
                        x_size-x_cut-x_road_size,
                        y_start+y_cut+y_road_size,
                        y_size-y_cut-y_road_size, next_road_size)


    def corrected_road_size(self, road_size, block_size):
        """Return the road_size after correction with regard to the
        block_size : if the road is too big, decrease it."""
        
        return min(road_size, block_size-2*self.min_block_size)
    
    
    def decreased(self, size):
        """Return a decreased size, for the roads (size >= 1)."""
        
        return (size + const.min_road_size)/2


    def central_coef(self, x_start, x_size, y_start,
                                 y_size):
        """Return a coefficient of centralisation, between 0 and 1.
        The closer to 0, the closer to the center."""
        
        x_center = x_start + x_size/2
        y_center = y_start + y_size/2
        block_dist = math.hypot(x_center, y_center)
        
        return block_dist/self.radius
