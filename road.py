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
    
    
    def draw(self):
        """Drawn the central line curve."""
        
        # define the edges
        edges = [(i, i+1) for i in range(0,len(self.vertices)-1)]
        
        # create the mesh
        self.mesh = bpy.data.meshes.new("C_Road")
        self.mesh.from_pydata(self.vertices, edges, [])
        self.mesh.update()
        
        # create the road as an object
        self.object = bpy.data.objects.new("C_Road", self.mesh)
        
        # link the block to the scene
        self.scene.objects.link(self.object)
        
        # transform into curve
        self.object.select = True
        self.scene.objects.active = self.object
        bpy.ops.object.convert(target='CURVE')
