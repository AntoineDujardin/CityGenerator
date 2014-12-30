# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "City" in locals():
    import imp
    imp.reload(block)
    imp.reload(ground)
else:
    from city_generator import block, ground


import bpy

class City:
    """Class managing the creation of the whole city."""
    
    def __init__(self, city_x_size, city_y_size, min_block_size,
                 max_block_size, road_size, scene):
        """Create the city"""
        
        # save the values
        self.city_x_size = city_x_size
        self.city_y_size = city_y_size
        self.min_block_size = min_block_size
        self.max_block_size = max_block_size
        self.road_size = road_size
        self.scene = scene
        
        # initialize
        self.blocks = set()
        self.roads = set()
        
        # create the ground
        self.ground = ground.Ground(city_x_size, city_y_size)
        
        # make the block decomposition
        block.Block(-self.city_x_size/2, self.city_x_size,
                    -self.city_y_size/2, self.city_y_size, road_size,
                    self)
    
    
    def __del__(self):
        """Cleanly delete the city"""
        
        # delete ground
        del self.ground
        
        # delete blocks
        for block in self.blocks:
            del block
        
        # delete roads
        for road in self.roads:
            del road