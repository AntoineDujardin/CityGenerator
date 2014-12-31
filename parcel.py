# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "Parcel" in locals():
    import imp
    imp.reload(const)
else:
    from city_generator import const


import bpy
import random
from math import pi

class Parcel:
    """Class managing the parcels."""
    
    def __init__(self, x_center, x_size, y_center, y_size, orientation,
                city):
        """Create a new parcel and subdivide it.
        The orientation represent the orientation of the facade.
        S=0, E=1, N=2, W=3."""
        
        # save the values
        self.x_center = x_center
        self.x_size = x_size
        self.y_center = y_center
        self.y_size = y_size
        self.city = city
        
        # draw
        #self.draw()
        
        # add building
        self.add_building(orientation, city.scene)
    
    
    def add_building(self, orientation, scene):
        """Place a building in the parcel."""
        
        building = bpy.data.objects["residential_house_1"].copy()
        building.name = "C_residential_house.000"
        
        # put the door at the ground level
        x_door = self.x_center
        y_door = self.y_center
        if orientation == 0:
            y_door = self.y_center - self.y_size/2
        elif orientation == 1:
            x_door = self.x_center + self.x_size/2
        elif orientation == 2:
            y_door = self.y_center + self.y_size/2
        else:
            x_door = self.x_center - self.x_size/2
        
        # locate
        building.location = (self.x_center, self.y_center,
            self.city.ground.altitude_f(self.x_center, self.y_center))
        scene.objects.active = building
        building.select = True
        building.rotation_euler = (0, 0, orientation*pi/2)
        building.scale[orientation % 2] = self.x_size
        building.scale[(orientation + 1) % 2] = self.y_size
        self.city.scene.objects.link(building)
    
    
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
        self.object.name = "C_Parcel.000"
        self.mesh.name = "C_Parcel.000"
        
        # scale it
        self.object.scale[0] = self.x_size
        self.object.scale[1] = self.y_size
        bpy.ops.object.transform_apply(scale=True)
        
        # locate it
        self.object.location[0] = self.x_center
        self.object.location[1] = self.y_center
        #altitude_f = self.city.ground.altitude_f
        #self.object.location[2] = altitude_f(self.x_center,
        #                                     self.y_center)
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
                2*const.pavement_thickness
        
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
        self.material = bpy.data.materials.new("C_Parcel.000")
        self.mesh.materials.append(self.material)
        self.material.diffuse_color = (0.2, 0.8, 0.2)
        
        # update
        self.mesh.update()
