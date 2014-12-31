import bpy
import math
import random

class Ground:
    """Class defining the ground.
    The ground is caracterized by its size and by its altitude
    in function of x and y."""
    
    def __init__(self, x_size, y_size):
        """Create a new ground with its size and altitude."""
        
        # save the values
        self.x_size = x_size
        self.y_size = y_size
        
        # define altitude_f
        self.altitude_f = Ground.mound_altitude_f()
        
        # draw it
        #self.draw()
    
    
    def draw(self):
        """Draw the ground."""
        
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
        self.object.scale[0] = self.x_size
        self.object.scale[1] = self.y_size
        bpy.ops.object.transform_apply(scale=True)
        
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
        for vertex in self.mesh.vertices:
            vertex.co.z = self.altitude_f(vertex.co.x, vertex.co.y)
        
        # update
        self.mesh.update()

    
    @staticmethod
    def mound_altitude_f(altitude=2, sharpening=0.003):
        """Create a function giving an altitude that give a mound."""
        return (lambda x, y:
            altitude*math.exp(-sharpening*(x**2+y**2)))
