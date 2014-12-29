# To support reload properly, try to access a package var, 
# if it's there, reload everything
#if "Parcel" in locals():
    #import imp
    #imp.reload(road)
#else:
    #from city_generator import road


import bpy
import random

class Parcel:
    """Class managing the parcels.
    A blender parcel is caracterized by its vertices,
    that must be given in positive order."""
    
    def __init__(self, x_start, x_size, y_start, y_size,
                 min_building_size, buildings, roads, scene):
        """Create a new parcel and subdivide it.
        If end subdivision, put itself in the parcels set. Add roads
        in the roads set."""
        
        # save the values
        self.x_start = x_start
        self.x_size = x_size
        self.y_start = y_start
        self.y_size = y_size
        self.min_building_size
        self.scene = scene
        
        # subdivide
        if (random.uniform(0, 1) >= 0.5):
            # create it (big)
            self.create(buildings)
        
        if (x_size >= 2*min_building_size and
            y_size >= 2*min_building_size):
            # double cut
            self.double_cut(blocks, roads)
        
        elif (x_size >= 2*min_building_size):
            # y cut
            self.cut_y_axis(blocks, roads)
        
        elif (y_size >= 2*min_building_size):
            # x cut
            self.cut_x_axis(blocks, roads)
        
        else:
            # create it
            self.create(blocks)
    
    
    def create(self, blocks):
        """Properly create the block."""
        
        blocks.add(self)
        self.draw()
    
    
    def cut_y_axis(self, blocks, roads):
        """Cut in y."""
        
        y_road_size = self.corrected_road_size(self.y_size)
        y_cut = random.uniform(self.min_block_size,
            self.y_size-2*self.min_block_size-y_road_size)
        Block(self.x_start, self.x_size, self.y_start, y_cut,
              self.decreased(y_road_size), self.min_block_size,
              self.max_block_size, blocks, roads, self.scene)
        roads.add(road.Road([
            (self.x_start, self.y_start+y_cut+y_road_size/2, 0),
            (self.x_start+self.x_size, self.y_start+y_cut+y_road_size/2,
             0)
        ], self.scene))
        Block(self.x_start, self.x_size, self.y_start+y_cut+y_road_size,
              self.y_size-y_cut-y_road_size,
              self.decreased(y_road_size), self.min_block_size,
              self.max_block_size, blocks, roads, self.scene)
    
    
    def cut_x_axis(self, blocks, roads):
        """Cut in x."""
        
        x_road_size = self.corrected_road_size(self.x_size)
        x_cut = random.uniform(self.min_block_size,
            self.x_size-2*self.min_block_size-x_road_size)
        Block(self.x_start, x_cut, self.y_start, self.y_size,
              self.decreased(x_road_size), self.min_block_size,
              self.max_block_size, blocks, roads, self.scene)
        roads.add(road.Road([
            (self.x_start+x_cut+x_road_size/2, self.y_start, 0),
            (self.x_start+x_cut+x_road_size/2, self.y_start+self.y_size,
             0)
        ], self.scene))
        Block(self.x_start+x_cut+x_road_size,
              self.x_size-x_cut-x_road_size, self.y_start, self.y_size,
              self.decreased(x_road_size), self.min_block_size,
              self.max_block_size, blocks, roads, self.scene)
    
    
    def double_cut(self, blocks, roads):
        """Cut in x and y."""
        
        x_road_size = self.corrected_road_size(self.x_size)
        y_road_size = self.corrected_road_size(self.y_size)
        next_road_size = self.decreased(min(x_road_size, y_road_size))
        x_cut = random.uniform(self.min_block_size,
            self.x_size-2*self.min_block_size-x_road_size)
        y_cut = random.uniform(self.min_block_size,
            self.y_size-2*self.min_block_size-y_road_size)
        
        Block(self.x_start, x_cut, self.y_start, y_cut, next_road_size,
              self.min_block_size, self.max_block_size, blocks, roads,
              self.scene)
        roads.add(road.Road([
            (self.x_start+x_cut+x_road_size/2, self.y_start, 0),
            (self.x_start+x_cut+x_road_size/2, self.y_start+y_cut, 0)
        ], self.scene))
        Block(self.x_start+x_cut+x_road_size,
              self.x_size-x_cut-x_road_size, self.y_start, y_cut,
              next_road_size, self.min_block_size,
              self.max_block_size, blocks, roads, self.scene)
        
        roads.add(road.Road([
            (self.x_start, self.y_start+y_cut+y_road_size/2, 0),
            (self.x_start+self.x_size, self.y_start+y_cut+y_road_size/2,
             0)
        ], self.scene))
        
        Block(self.x_start, x_cut, self.y_start+y_cut+y_road_size,
              self.y_size-y_cut-y_road_size, next_road_size,
              self.min_block_size, self.max_block_size, blocks, roads,
              self.scene)
        roads.add(road.Road([
            (self.x_start+x_cut+x_road_size/2,
             self.y_start+y_cut+y_road_size, 0),
            (self.x_start+x_cut+x_road_size/2, self.y_start+self.y_size,
             0)
        ], self.scene))
        Block(self.x_start+x_cut+x_road_size,
              self.x_size-x_cut-x_road_size,
              self.y_start+y_cut+y_road_size,
              self.y_size-y_cut-y_road_size, next_road_size,
              self.min_block_size, self.max_block_size, blocks, roads,
              self.scene)
    
    
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
        self.scene.objects.link(self.object)
    
    
    def corrected_road_size(self, block_size):
        """Return the road_size after correction with regard to the
        block_size : if the road is too big, decrease it."""
        
        return min(self.road_size, block_size-2*self.min_block_size)
    
    
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
