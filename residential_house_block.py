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

class ResidentialHousesBlock(block.Block):
    """Class managing the blocks of residential houses."""
    
    def __init__(self, x_start, x_size, y_start, y_size, city):
        """Create a new block of residential houses."""
        
        block.Block.__init__(self, x_start, x_size, y_start, y_size,
                             city)
        
        self.draw()
        self.draw_grass()
        self.parcel()
    
    def parcel(self):
        """Cut it into parcels.
        We first create the corner buildings. Then, we fill the road
        sides with buildings in such a way that they don't collide."""
        
        # create the corner buildings
        min_corner_size = const.min_residential_houses_size
        max_corner_size = min(self.parcels_x_size/3,
                              self.parcels_y_size/3,
                              const.max_residential_houses_size)
        corner_building_sizes = list((0, 0, 0, 0))
        for i in range(4):
            corner_building_sizes[i] = random.uniform(min_corner_size,
                                                      max_corner_size)
        # S-W corner
        parcel.Parcel(self.parcels_x_start, corner_building_sizes[0],
                      self.parcels_y_start, corner_building_sizes[0],
                      0, self.city)
        # S-E corner
        parcel.Parcel(self.parcels_x_start + self.parcels_x_size \
                        - corner_building_sizes[1],
                      corner_building_sizes[1],
                      self.parcels_y_start,
                      corner_building_sizes[1], 1, self.city)
        # N-E corner
        parcel.Parcel(self.parcels_x_start + self.parcels_x_size \
                        - corner_building_sizes[2],
                      corner_building_sizes[2],
                      self.parcels_y_start + self.parcels_y_size \
                      - corner_building_sizes[2],
                      corner_building_sizes[2], 2, self.city)
        # N-W corner
        parcel.Parcel(self.parcels_x_start,
                      corner_building_sizes[3],
                      self.parcels_y_start + self.parcels_y_size \
                        - corner_building_sizes[3],
                      corner_building_sizes[3], 3, self.city)
        
        # create the other buildings
        # S face
        parcels_side_x_sizes = self.cut_length(
            self.parcels_x_size - corner_building_sizes[0] \
                - corner_building_sizes[1],
            const.min_residential_houses_size,
            const.max_residential_houses_size
        )
        parcels_side_x_starts = list(parcels_side_x_sizes)
        temp_x_start = self.parcels_x_start + corner_building_sizes[0]
        for i in range(len(parcels_side_x_sizes)):
            parcels_side_x_starts[i] = temp_x_start
            temp_x_start = temp_x_start + parcels_side_x_sizes[i]
            parcel_y_size = random.uniform(
                const.min_residential_houses_size,
                min(parcels_side_x_starts[i] - self.parcels_x_start,
                    self.parcels_x_start + self.parcels_x_size \
                        - (parcels_side_x_starts[i] +
                            parcels_side_x_sizes[i]),
                    self.parcels_y_size/2,
                    const.max_residential_houses_size))
            parcel.Parcel(parcels_side_x_starts[i],
                          parcels_side_x_sizes[i],
                          self.parcels_y_start,
                          parcel_y_size, 0, self.city)
        # E face
        parcels_side_y_sizes = self.cut_length(
            self.parcels_y_size - corner_building_sizes[1] \
                - corner_building_sizes[2],
            const.min_residential_houses_size,
            const.max_residential_houses_size
        )
        parcels_side_y_starts = list(parcels_side_y_sizes)
        temp_y_start = self.parcels_y_start + corner_building_sizes[1]
        for i in range(len(parcels_side_y_sizes)):
            parcels_side_y_starts[i] = temp_y_start
            temp_y_start = temp_y_start + parcels_side_y_sizes[i]
            parcel_x_size = random.uniform(
                const.min_residential_houses_size,
                min(parcels_side_y_starts[i] - self.parcels_y_start,
                    self.parcels_y_start + self.parcels_y_size \
                        - (parcels_side_y_starts[i] +
                            parcels_side_y_sizes[i]),
                    self.parcels_x_size/2,
                    const.max_residential_houses_size))
            parcel.Parcel(self.parcels_x_start + self.parcels_x_size \
                              - parcel_x_size,
                          parcel_x_size,
                          parcels_side_y_starts[i],
                          parcels_side_y_sizes[i], 1, self.city)
        # N face
        parcels_side_x_sizes = self.cut_length(
            self.parcels_x_size - corner_building_sizes[2] \
                - corner_building_sizes[3],
            const.min_residential_houses_size,
            const.max_residential_houses_size
        )
        parcels_side_x_starts = list(parcels_side_x_sizes)
        temp_x_start = self.parcels_x_start + corner_building_sizes[3]
        for i in range(len(parcels_side_x_sizes)):
            parcels_side_x_starts[i] = temp_x_start
            temp_x_start = temp_x_start + parcels_side_x_sizes[i]
            parcel_y_size = random.uniform(
                const.min_residential_houses_size,
                min(parcels_side_x_starts[i] - self.parcels_x_start,
                    self.parcels_x_start + self.parcels_x_size \
                        - (parcels_side_x_starts[i] +
                            parcels_side_x_sizes[i]),
                    self.parcels_y_size/2,
                    const.max_residential_houses_size))
            parcel.Parcel(parcels_side_x_starts[i],
                          parcels_side_x_sizes[i],
                          self.parcels_y_start + self.parcels_y_size \
                              - parcel_y_size,
                          parcel_y_size, 2, self.city)
        # W face
        parcels_side_y_sizes = self.cut_length(
            self.parcels_y_size - corner_building_sizes[3] \
                - corner_building_sizes[0],
            const.min_residential_houses_size,
            const.max_residential_houses_size
        )
        parcels_side_y_starts = list(parcels_side_y_sizes)
        temp_y_start = self.parcels_y_start + corner_building_sizes[0]
        for i in range(len(parcels_side_y_sizes)):
            parcels_side_y_starts[i] = temp_y_start
            temp_y_start = temp_y_start + parcels_side_y_sizes[i]
            parcel_x_size = random.uniform(
                const.min_residential_houses_size,
                min(parcels_side_y_starts[i] - self.parcels_y_start,
                    self.parcels_y_start + self.parcels_y_size \
                        - (parcels_side_y_starts[i] +
                            parcels_side_y_sizes[i]),
                    self.parcels_x_size/2,
                    const.max_residential_houses_size))
            parcel.Parcel(self.parcels_x_start,
                          parcel_x_size,
                          parcels_side_y_starts[i],
                          parcels_side_y_sizes[i], 3, self.city)
