# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "ParkBlock" in locals():
    import imp
    imp.reload(block)
    imp.reload(const)
else:
    from city_generator import block, const


import bpy
import math
import random

class ParkBlock(block.Block):
    """Class managing the parks."""
    
    def __init__(self, x_start, x_size, y_start, y_size, city):
        """Create a new park."""
        
        block.Block.__init__(self, x_start, x_size, y_start, y_size,
                             city)
        
        self.park_x_start = x_start + const.pavement_size
        self.park_x_size = x_size - 2*const.pavement_size
        self.park_y_start = y_start + const.pavement_size
        self.park_y_size = y_size - 2*const.pavement_size
        
        self.draw(gravel_texture=True)
        self.place_park()
    
    
    def place_park(self):
        """Place the park."""
        
        # select one park: the one that fits as good as possible
        stretchings = [0] * len(ParkBlock.parks)
        for i, park in enumerate(ParkBlock.parks):
            dimensions = ParkBlock.parks[i].dimensions
            # get the stretching degree:
            # the closest to zero, the fittest.
            stretchings[i] = (
                math.log(dimensions[0] / self.park_x_size)**2
                + math.log(dimensions[1] / self.park_y_size)**2)
        best_strech = min(stretchings)
        arg_best = list()
        for i, value in enumerate(stretchings):
            # find the best one and other that are close
            if value <= 1.1 * best_strech:
                arg_best.append(i)
        chosen_model = ParkBlock.parks[random.choice(arg_best)]
        park = chosen_model.copy()
        park.data = park.data.copy()
        park.name = "C_park.000"
        park.data.name = "C_park.000"
        
        # link
        self.city.scene.objects.link(park)
        
        # add children (lakes)
        for child_model in chosen_model.children:
            child = child_model.copy()
            child.name = "C_park_child.000"
            child.parent = park
            self.city.scene.objects.link(child)
        
        # scale
        self.city.scene.objects.active = park
        park.select = True
        park.scale[0] = self.park_x_size \
            / park.dimensions[0]
        park.scale[1] = self.park_y_size \
            / park.dimensions[1]
        bpy.ops.object.transform_apply(scale=True)
        
        # locate
        park.location = (
            self.park_x_start + self.park_x_size/2,
            self.park_y_start + self.park_y_size/2,
            2*const.pavement_thickness
        )
        bpy.ops.object.transform_apply(location=True)
        
        # change altitude
        altitude_function = self.city.ground.altitude_f
        for vertex in park.data.vertices:
            vertex.co.z += altitude_function(vertex.co.x, vertex.co.y)
        for child in park.children:
            # child are moved without deformation
            child.location[2] += altitude_function(child.location[0],
                                                   child.location[1])
        
        # add trees
        self.place_trees([v.co for v in park.data.vertices])
    
    
    def place_trees(self, coordinates_list):
        """Place trees one some of the given coordinates."""
        
        for co in coordinates_list:
            if random.uniform(0, 1) <= self.city.elem_density:
                self.place_tree(co)
    
    
    def place_tree(self, coordinates):
        """Place a tree at the given coordinates."""
        
        # choose tree model
        tree_model = random.choice(ParkBlock.trees)
        
        # create the tree
        tree = tree_model.copy()
        tree.name = "C_tree.000"
        
        # add the leafs
        leafs = tree_model.children[0].copy()
        leafs.name = "C_leafs.000"
        leafs.parent = tree
        
        # locate
        tree.location = coordinates
        
        # scale
        scale = random.uniform(1-self.city.size_var,
                               1+self.city.size_var)
        tree.scale = (scale, scale, scale)
        
        # link
        self.city.scene.objects.link(tree)
        self.city.scene.objects.link(leafs)
        

    @classmethod
    def load_parks(self):
        ParkBlock.parks = list()
        ParkBlock.trees = list()
        
        for key, object in bpy.data.objects.items():
            if key.startswith("park") or key.startswith("lake_park"):
                ParkBlock.parks.append(object)
            elif key.startswith("tree"):
                ParkBlock.trees.append(object)
