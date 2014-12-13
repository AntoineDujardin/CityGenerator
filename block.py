import bpy

class Block:
    """Class managing the blocks.
    A blender block is caracterized by its vertices,
    that must be given in positive order."""
    
    def __init__(self, vertices):
        """Create a new block with the vertices.
        The vertices must be in the form: (x, y, z)."""
        
        # define the face
        faces = [range(len(vertices))]
        
        # create the mesh
        self.mesh = bpy.data.meshes.new("Block")
        self.mesh.from_pydata(vertices, [], faces)
        self.mesh.update()
        
        # create the block as an object
        self.object = bpy.data.objects.new("Block", self.mesh)
        
        # link the block to the scene
        self.scene = bpy.context.scene
        self.scene.objects.link(self.object)
    
    
    def __del__(self):
        """Cleanly delete the object"""
        
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
