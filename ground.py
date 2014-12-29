import bpy
import math
import random

class Ground:
    """Class defining the ground.
    The ground is caracterized by its radius and by its altitude
    in function of x and y."""
    
    def __init__(self, x_size, y_size, altitude_f=[], noise_amplitude=5,
                 number_cuts=10):
        """Create a new ground with its size and altitude.
        The altitude function is defined such that z = f(x, y, radius).
        It is modified by a noise determined by noise_amplitude.
        The parameter number_cuts is the one used in the subdivision
        process."""
        
        # leave EDIT mode if needed
        if bpy.context.object:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # create a plane
        bpy.ops.mesh.primitive_plane_add(radius=0.5, location=(0,0,0))
        
        # recover infos
        self.scene = bpy.context.scene
        self.object = bpy.context.object
        self.mesh = self.object.data
        
        # rename
        self.object.name = "C_Ground"
        self.mesh.name = "C_Ground"
        
        # scale it
        self.object.scale[0] = x_size
        self.object.scale[1] = y_size
        
        # subdivide it
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=number_cuts)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # define altitude_f if needed
        if altitude_f == []:
            altitude_f = lambda x, y: 0
        
        # change altitude
        for vertex in self.mesh.vertices:
            vertex.co.z = (altitude_f(vertex.co.x, vertex.co.y)
                + noise_amplitude * random.uniform(-1,1))
        
        # smooth it
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 2
        bpy.context.object.modifiers["Subsurf"].render_levels = 3
        bpy.ops.object.modifier_apply(apply_as='DATA')
        
        # update
        self.mesh.update()

    
    @staticmethod
    def mound_altitude_f(altitude=20, sharpening=0.025):
        """Create a function giving an altitude that give a mound."""
        return (lambda x, y:
            altitude*math.exp(-sharpening*(x**2+y**2)))
