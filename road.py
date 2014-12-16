import bpy

class Road:
    """Class managing the roads. Roads are represented by their central
    line as a curve and their size."""
    
    def __init__(self, vertices, scene):
        """Create a roads whose centrale line is defined by the list of
        vertices that is given."""
        
        # save the values
        self.vertices = vertices
        self.scene = scene
        
        # draw
        self.draw()
    
    
    def __del__(self):
        """Cleanly delete the road."""
        
        # erase, if drawn
        self.erase()
    
    
    def draw(self):
        """Drawn the central line curve."""
        
        # define the edges
        edges = [(i, i+1) for i in range(0,len(self.vertices)-1)]
        
        # create the mesh
        self.mesh = bpy.data.meshes.new("Road")
        self.mesh.from_pydata(self.vertices, edges, [])
        self.mesh.update()
        
        # create the block as an object
        self.object = bpy.data.objects.new("Road", self.mesh)
        
        # link the block to the scene
        self.scene.objects.link(self.object)
        
        # transform into curve
        #bpy.ops.object.convert(target='CURVE')
        
        # mention the drawing
        self.is_drawn = True
    
    
    def erase(self):
        """Erase the drawn block."""
        
        # assert drawing
        if not self.is_drawn:
            return
        
        # unlink the block from the scene (if not done)
        if self.object in self.scene.objects.values():
            if self.object.select: # object mode needed
                bpy.ops.object.mode_set(mode='OBJECT')
            self.scene.objects.unlink(self.object)
        
        # destroy the block (if not done)
        if self.object in bpy.data.objects.values():
            bpy.data.objects.remove(self.object)
        
        # destroy the mesh (if not done)
        if self.mesh in bpy.data.meshes.values():
            bpy.data.meshes.remove(self.mesh)
    
