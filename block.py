# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "Block" in locals():
    import imp
    imp.reload(road)
else:
    from city_generator import road


import bpy
import random

class Block:
    """Class managing the blocks.
    A blender block is caracterized by its vertices,
    that must be given in positive order."""
    
    def __init__(self, x_start, x_size, y_start, y_size, road_size,
                 city):
        """Create a new block of building and subdivide it.
        If end subdivision, put itself in the blocks set. Add roads in
        the roads set."""
        
        # save the values
        self.x_start = x_start
        self.x_size = x_size
        self.y_start = y_start
        self.y_size = y_size
        self.road_size = road_size
        self.city = city
        
        # subdivide
        if (x_size <= city.max_block_size
            and y_size <= city.max_block_size):
            # block should not be cutted further, create it
            self.create()
        
        elif (x_size <= city.max_block_size):
            # y cut
            self.cut_y_axis()
        
        elif (y_size <= city.max_block_size):
            # x cut
            self.cut_x_axis()
        
        else:
            # double cut
            self.double_cut()
    
    
    def create(self):
        """Properly create the block."""
        
        self.city.blocks.add(self)
        self.draw()
    
    
    def cut_y_axis(self):
        """Cut in y."""
        
        y_road_size = self.corrected_road_size(self.y_size)
        y_cut = random.uniform(self.city.min_block_size,
            self.y_size-2*self.city.min_block_size-y_road_size)
        Block(self.x_start, self.x_size, self.y_start, y_cut,
              self.decreased(y_road_size), self.city)
        self.city.roads.add(road.Road([
            (self.x_start, self.y_start+y_cut+y_road_size/2, 0),
            (self.x_start+self.x_size, self.y_start+y_cut+y_road_size/2,
             0)
        ], self.city.scene))
        Block(self.x_start, self.x_size, self.y_start+y_cut+y_road_size,
              self.y_size-y_cut-y_road_size,
              self.decreased(y_road_size), self.city)
    
    
    def cut_x_axis(self):
        """Cut in x."""
        
        x_road_size = self.corrected_road_size(self.x_size)
        x_cut = random.uniform(self.city.min_block_size,
            self.x_size-2*self.city.min_block_size-x_road_size)
        Block(self.x_start, x_cut, self.y_start, self.y_size,
              self.decreased(x_road_size), self.city)
        self.city.roads.add(road.Road([
            (self.x_start+x_cut+x_road_size/2, self.y_start, 0),
            (self.x_start+x_cut+x_road_size/2, self.y_start+self.y_size,
             0)
        ], self.city.scene))
        Block(self.x_start+x_cut+x_road_size,
              self.x_size-x_cut-x_road_size, self.y_start, self.y_size,
              self.decreased(x_road_size), self.city)
    
    
    def double_cut(self):
        """Cut in x and y."""
        
        x_road_size = self.corrected_road_size(self.x_size)
        y_road_size = self.corrected_road_size(self.y_size)
        next_road_size = self.decreased(min(x_road_size, y_road_size))
        x_cut = random.uniform(self.city.min_block_size,
            self.x_size-2*self.city.min_block_size-x_road_size)
        y_cut = random.uniform(self.city.min_block_size,
            self.y_size-2*self.city.min_block_size-y_road_size)
        
        Block(self.x_start, x_cut, self.y_start, y_cut, next_road_size,
              self.city)
        self.city.roads.add(road.Road([
            (self.x_start+x_cut+x_road_size/2, self.y_start, 0),
            (self.x_start+x_cut+x_road_size/2, self.y_start+y_cut, 0)
        ], self.city.scene))
        Block(self.x_start+x_cut+x_road_size,
              self.x_size-x_cut-x_road_size, self.y_start, y_cut,
              next_road_size,
              self.city)
        
        self.city.roads.add(road.Road([
            (self.x_start, self.y_start+y_cut+y_road_size/2, 0),
            (self.x_start+self.x_size, self.y_start+y_cut+y_road_size/2,
             0)
        ], self.city.scene))
        
        Block(self.x_start, x_cut, self.y_start+y_cut+y_road_size,
              self.y_size-y_cut-y_road_size, next_road_size,
              self.city)
        self.city.roads.add(road.Road([
            (self.x_start+x_cut+x_road_size/2,
             self.y_start+y_cut+y_road_size, 0),
            (self.x_start+x_cut+x_road_size/2, self.y_start+self.y_size,
             0)
        ], self.city.scene))
        Block(self.x_start+x_cut+x_road_size,
              self.x_size-x_cut-x_road_size,
              self.y_start+y_cut+y_road_size,
              self.y_size-y_cut-y_road_size, next_road_size,
              self.city)
    
    
    def draw(self):
        """Draw the block in blender."""
        
        # define the vertices
        vertices = [
            (self.x_start, self.y_start, 0),
            (self.x_start+self.x_size, self.y_start, 0),
            (self.x_start+self.x_size, self.y_start+self.y_size, 0),
            (self.x_start, self.y_start+self.y_size, 0)
        ]
        
        # define the face
        faces = [range(len(vertices))]
        
        # create the mesh
        self.mesh = bpy.data.meshes.new("C_Block")
        self.mesh.from_pydata(vertices, [], faces)
        self.mesh.update()
        
        # create the block as an object
        self.object = bpy.data.objects.new("C_Block", self.mesh)
        
        # link the block to the scene
        self.city.scene.objects.link(self.object)
    
    
    def corrected_road_size(self, block_size):
        """Return the road_size after correction with regard to the
        block_size : if the road is too big, decrease it."""
        
        return min(self.road_size,
                   block_size-2*self.city.min_block_size)
    
    
    def decreased(self, size):
        """Return a decreased size, for the roads (size >= 1)."""
        
        return (size+1)/2
    

# test
if __name__ == "__main__":
    # initialize
    blocks = set()
    roads = set()
    
    # make the block decomposition
    Block(-50, 100, -25, 50, 1, 2, 7, blocks, roads)
