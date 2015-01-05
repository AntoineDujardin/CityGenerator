# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "ResidentialHousesBlock" in locals():
    import imp
    imp.reload(block)
    imp.reload(const)
    imp.reload(parcel)
else:
    from city_generator import block, const, parcel


import bpy
import random

class BusinessTowerBlock(block.Block):
    """Class managing the blocks of business towers."""
    
    def __init__(self, x_start, x_size, y_start, y_size, city):
        """Create a new block of business towers."""
        
        block.Block.__init__(self, x_start, x_size, y_start, y_size,
                             city)
        
        self.draw()
        self.parcel()


    def parcel(self):
        """Cut it into parcels."""
        
        # decompose in x
        parcels_x_sizes = self.cut_length(self.x_size,
                                          const.min_business_tower_size,
                                          const.max_business_tower_size)
        len_x = len(parcels_x_sizes)
        parcels_x_starts = list((0,)) * len_x
        temp_x_start = self.parcels_x_start
        for i in range(len_x):
            parcels_x_starts[i] = temp_x_start
            temp_x_start = temp_x_start + parcels_x_sizes[i]
        
        # decompose in y
        parcels_y_sizes = self.cut_length(self.y_size,
                                          const.min_business_tower_size,
                                          const.max_business_tower_size)
        len_y = len(parcels_y_sizes)
        parcels_y_starts = list((0,)) * len_y
        temp_y_start = self.parcels_y_start
        for i in range(len_y):
            parcels_y_starts[i] = temp_y_start
            temp_y_start = temp_y_start + parcels_y_sizes[i]
        

        # create all the towers
        for i in range(len_x):
            parcel.Parcel(parcels_x_starts[i], parcels_x_sizes[i],
                          parcels_y_starts[0], parcels_y_sizes[0],
                          0, self.city, "business_tower")
        if len_y >= 2:
            for i in range(len_x):
                parcel.Parcel(parcels_x_starts[i], parcels_x_sizes[i],
                              parcels_y_starts[-1], parcels_y_sizes[-1],
                              2, self.city, "business_tower")
            for j in range(1, len_y-1):
                parcel.Parcel(parcels_x_starts[0], parcels_x_sizes[0],
                              parcels_y_starts[j], parcels_y_sizes[j],
                              3, self.city, "business_tower")
                parcel.Parcel(parcels_x_starts[-1], parcels_x_sizes[-1],
                              parcels_y_starts[j], parcels_y_sizes[j],
                              1, self.city, "business_tower")
