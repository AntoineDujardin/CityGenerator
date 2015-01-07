# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "Parcel" in locals():
    import imp
    imp.reload(const)
else:
    from city_generator import const


import bpy
import math
import random
from math import pi

class Parcel:
    """Class managing the parcels."""
    
    def __init__(self, x_start, x_size, y_start, y_size, orientation,
                 city, building_type):
        """Create a new parcel and subdivide it.
        The orientation represent the orientation of the facade.
        S=0, E=1, N=2, W=3.
        The building_type can be:
        - "business_tower";
        - "residential_building";
        - "residential_house".
        """
        
        # save the values
        self.x_center = x_start + x_size/2
        self.x_size = x_size
        self.y_center = y_start + y_size/2
        self.y_size = y_size
        self.building_type = building_type
        self.city = city
        
        # add building
        self.add_building(orientation, building_type, city.scene)
    
    
    def add_building(self, orientation, building_type, scene):
        """Place a building in the parcel."""
        
        # because of the rotation, x and y index may be interverted
        x_index = orientation % 2
        y_index = (orientation + 1) % 2
        
        # select one building: the one that fits as good as possible
        target_buildings = Parcel.buildings[building_type]
        stretchings = [0] * len(target_buildings)
        for i, house in enumerate(target_buildings):
            dimensions = target_buildings[i].dimensions
            # get the stretching degree:
            # the closest to zero, the fittest.
            stretchings[i] = (
                math.log(dimensions[x_index] / self.x_size)**2
                + math.log(dimensions[y_index] / self.y_size)**2)
        best_strech = min(stretchings)
        arg_best = list()
        for i, value in enumerate(stretchings):
            # find the best one and other that are close
            if value <= 1.1 * best_strech:
                arg_best.append(i)
        chosen_model = target_buildings[random.choice(arg_best)]
        building = chosen_model.copy()
        building.name = "".join(("C_", building_type, ".000"))
        
        # put the door at the ground level
        x_door = self.x_center
        y_door = self.y_center
        if orientation == 0:
            y_door = self.y_center - self.y_size/2
        elif orientation == 1:
            x_door = self.x_center + self.x_size/2
        elif orientation == 2:
            y_door = self.y_center + self.y_size/2
        else:
            x_door = self.x_center - self.x_size/2
        
        # locate
        building.location = (
            self.x_center,
            self.y_center,
            self.city.ground.altitude_f(self.x_center, self.y_center)
        )
        scene.objects.active = building
        building.select = True
        building.rotation_euler = (0, 0, orientation*pi/2)
        building.scale[x_index] = self.x_size \
            / building.dimensions[x_index] \
            * Parcel.buildings_ratio[building_type]
        building.scale[y_index] = self.y_size \
            / building.dimensions[y_index] \
             * Parcel.buildings_ratio[building_type]
        building.scale[2] = max(
            0.7,
            random.gauss(1, self.city.building_z_var)
        )
        self.city.scene.objects.link(building)


    @classmethod
    def load_buildings(self):
        Parcel.buildings = {
            "residential_house": list(),
            "business_tower": list(),
            "residential_building": list()
        }
        
        for key, object in bpy.data.objects.items():
            if key.startswith("residential_house"):
                Parcel.buildings["residential_house"].append(object)
            elif key.startswith("business_tower"):
                Parcel.buildings["business_tower"].append(object)
            elif key.startswith("residential_building"):
                Parcel.buildings["residential_building"].append(object)
        
        Parcel.buildings_ratio = {
            "residential_house": .8,
            "business_tower": .7,
            "residential_building": .6
        }
