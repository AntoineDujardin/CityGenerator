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
        
        # make the block decomposition (also add camera)
        self.cut_blocks(-self.x_size/2, self.x_size,
                        -self.y_size/2, self.y_size,
                        road_size, True)
        
        # lighting
        self.set_environment_lightning(day)
        self.add_sun_moon(day)
        
        # configure animation
        bpy.data.scenes["Scene"].frame_start = 1
        bpy.data.scenes["Scene"].frame_end = 100
        
    
    def add_static_camera(self):
        """Add a camera to the scene."""
        
        bpy.ops.object.camera_add()
        camera = bpy.context.object
        camera.name = "C_camera"
        camera.location = (0, -1.1*self.y_size, self.y_size)
        camera.rotation_euler = (math.pi/4, 0, 0)
        
    
    def add_dynamic_camera(self, co_list, start_orientation):
        """Add a camera that follows a path given as a list of
        coordinates (x, y, z, w) and a starting orientation
        (0 for south->north, 1 for west-east)."""
        
        # add camera
        bpy.ops.object.camera_add()
        camera = bpy.context.object
        camera.name = "C_camera"
        camera.location = co_list[0][0:3]
        camera.rotation_euler = (math.pi/2, 0,
                                 -math.pi/2 * start_orientation)
        
        # add path
        path_data = bpy.data.curves.new("C_camera_path", 'CURVE')    
        path_data.dimensions = '3D'    
        
        path = bpy.data.objects.new("C_camera_path", path_data)
        path.location = (0,0,0)
        bpy.context.scene.objects.link(path)    
        
        line = path_data.splines.new('NURBS')    
        line.points.add(len(co_list)-1)    
        for i in range(len(co_list)):    
            line.points[i].co = co_list[i]
        
        line.order_u = len(line.points)-1  
        line.use_endpoint_u = True
        
        # link camera to path
        bpy.ops.object.select_all(action="DESELECT")
        camera.select = True
        path.select = True
        bpy.context.scene.objects.active = path
        bpy.context.scene.update
        bpy.ops.object.parent_set(type="FOLLOW")

        
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


    def cut_blocks(self, x_start, x_size, y_start, y_size, road_size,
                   add_camera=False):
        """Separate the city in blocks, recurcively, with the
        coordinates."""
        
        # subdivide
        if (x_size <= self.max_block_size
            and y_size <= self.max_block_size):
            # block should not be cutted further, create it
            self.create_block(x_start, x_size, y_start, y_size,
                              add_camera)
        
        elif (x_size <= self.max_block_size):
            # y cut
            self.cut_y_axis(x_start, x_size, y_start, y_size, road_size,
                            add_camera)
        
        elif (y_size <= self.max_block_size):
            # x cut
            self.cut_x_axis(x_start, x_size, y_start, y_size, road_size,
                            add_camera)
        
        else:
            # double cut
            self.double_cut(x_start, x_size, y_start, y_size, road_size,
                            add_camera)

    
    def create_block(self, x_start, x_size, y_start, y_size,
                     add_camera):
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
        
        if add_camera:
            self.add_static_camera()
    

    def cut_y_axis(self, x_start, x_size, y_start, y_size, road_size,
                   add_camera):
        """Cut in y."""
        
        # cut
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
        
        # add camera
        if add_camera:
            xs = [x_start-1] + \
                list(frange(x_start, x_start+x_size, min(2, x_size/2)))
            ln = len(xs)
            ys = [y_start+y_cut+y_road_size/2] * ln
            zs = list((0,)) * ln
            cos = list((0,)) * ln
            for i in range(ln):
                zs[i] = self.ground.altitude_f(xs[i], ys[i]) \
                    + const.camera_z_offset
            zs[0] = zs[1] # matches the path with camera orientation
            for i in range(ln):
                cos[i] = (xs[i], ys[i], zs[i], 1)
            self.add_dynamic_camera(cos, 1)
    
    
    def cut_x_axis(self, x_start, x_size, y_start, y_size, road_size,
                   add_camera):
        """Cut in x."""
        
        # cut
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
        
        # add camera
        if add_camera:
            ys = [y_start-1] + \
                list(frange(y_start, y_start+y_size, min(2, y_size/2)))
            ln = len(ys)
            xs = [x_start+x_cut+x_road_size/2] * ln
            zs = list((0,)) * ln
            cos = list((0,)) * ln
            for i in range(ln):
                zs[i] = self.ground.altitude_f(xs[i], ys[i]) \
                    + const.camera_z_offset
            zs[0] = zs[1] # matches the path with camera orientation
            for i in range(ln):
                cos[i] = (xs[i], ys[i], zs[i], 1)
            self.add_dynamic_camera(cos, 0)
    
    
    def double_cut(self, x_start, x_size, y_start, y_size, road_size,
                   add_camera):
        """Cut in x and y."""
        
        # cut
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
                        
        # add camera
        if add_camera:
            # enter from south, go north until main crossroads
            ys_begin = [y_start-1] + \
                list(frange(y_start, y_start+y_cut, min(2, y_cut/2)))
            xs_begin = [x_start+x_cut+x_road_size/2] * len(ys_begin)
            ws_begin = [1] * (len(ys_begin)-1) + [10]
            
            # turn right
            xs_end = list(frange(x_start+x_cut+x_road_size,
                                 x_start+x_size,
                                 min(2, (x_size-x_cut-x_road_size)/2)))
            ys_end = [y_start+y_cut+y_road_size/2] * len(xs_end)
            ws_end = [10] + [1] * (len(xs_end)-1)
            
            # fuse
            xs = xs_begin + xs_end
            ys = ys_begin + ys_end
            ws = ws_begin + ws_end # 10s are for the crossroads
            ln = len(xs)
            zs = list((0,)) * ln
            cos = list((0,)) * ln
            for i in range(ln):
                zs[i] = self.ground.altitude_f(xs[i], ys[i]) \
                    + const.camera_z_offset
            zs[0] = zs[1] # matches the path with camera orientation
            for i in range(ln):
                cos[i] = (xs[i], ys[i], zs[i], ws[i])
            self.add_dynamic_camera(cos, 0)


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
        

def frange(start, stop, step):
    """Equivalent of range generator, not limited to int."""
    while start < stop:
        yield start
        start += step
