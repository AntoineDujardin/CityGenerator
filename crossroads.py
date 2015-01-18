# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "Crossroads" in locals():
    import imp
    imp.reload(const)
    imp.reload(drawer)
else:
    from city_generator import const, drawer


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
        
        offset = 2*const.pavement_size / 3
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
        traffic_lights.parent = self.object

    
    def draw(self):
        """Draw the road."""
        
        # draw the plane
        self.object = drawer.draw_relief_plane(
            self.x_start, self.x_size, self.y_start, self.y_size,
            "Crossroads", self.city.ground.altitude_f)
        self.mesh = self.object.data

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
        
        # parent
        self.object.parent = self.city.roads_object
