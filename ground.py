import bpy
import math
import random

class Ground:
    """Class defining the ground.
    The ground is caracterized by its radius and by its altitude
    in function of x and y."""
    
    
    def __init__(self, radius=100, altitude_f=[], noise_amplitude=5,
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
        bpy.ops.mesh.primitive_plane_add(radius=radius,
                                         location=(0,0,0))
        
        # recover infos
        self.scene = bpy.context.scene
        self.object = bpy.context.object
        self.mesh = self.object.data
        
        # subdivide it
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.subdivide(number_cuts=number_cuts)
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # define altitude_f if needed
        if altitude_f == []:
            altitude_f = lambda x, y, radius: 0
        
        # change altitude
        for vertice in self.mesh.vertices:
            vertice.co.z = (altitude_f(vertice.co.x, vertice.co.y,
                                       radius)
                + noise_amplitude * random.uniform(-1,1))
        
        # smooth it
        bpy.ops.object.modifier_add(type='SUBSURF')
        bpy.context.object.modifiers["Subsurf"].levels = 2
        bpy.context.object.modifiers["Subsurf"].render_levels = 3
        bpy.ops.object.modifier_apply(apply_as='DATA')
        
        # update
        self.mesh.update()
    
    
    def __del__(self):
        """Cleanly delete the object"""
        
        # unlink the ground from the scene (if not done)
        if self.object in self.scene.objects.values():
            if self.object.select: # object mode needed
                bpy.ops.object.mode_set(mode='OBJECT')
            self.scene.objects.unlink(self.object)
        
        # destroy the ground (if not done)
        if self.object in bpy.data.objects.values():
            bpy.data.objects.remove(self.object)
        
        # destroy the mesh (if not done)
        if self.mesh in bpy.data.meshes.values():
            bpy.data.meshes.remove(self.mesh)
    
    
    @staticmethod
    def mound_altitude_f(altitude=20, sharpening=5):
        """Create a function giving an altitude that give a mound."""
        return (lambda x, y, radius:
            altitude*math.exp(-sharpening*(x**2+y**2)/radius**2))
