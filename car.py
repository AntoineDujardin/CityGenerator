if "Car" in locals():
    import imp
    imp.reload(const)
else:
    from city_generator import const


import bpy
import random
from math import pi

class Car:
    """Class managing the cars."""
    
    def __init__(self, x_start, y_start, orientation, distance, road):
        """Create a car starting in x_start, y_start, running to the
        given orientation (0=S->N, 1=E->W, 2=N-S, 3=W->E) the given
        distance during the frame time."""
        
        # recover city
        city = road.city
        
        # back to object mode
        bpy.ops.object.mode_set(mode='OBJECT')
        
        # choose car model
        car_model = random.choice(Car.cars)
        
        # create the car
        alt = city.ground.altitude_f
        car = car_model.copy()
        car.name = "C_car.000"
        car.location = (x_start, y_start,
                        alt(x_start, y_start) +
                        const.pavement_thickness)
        car.rotation_euler = (0, 0, (orientation-2)*pi/2)
        
        # link
        bpy.context.scene.objects.link(car)
        
        # recover infos
        scene = bpy.context.scene
        mesh = car.data
        
        # select
        bpy.ops.object.select_all(action="DESELECT")
        car.select = True
        bpy.context.scene.objects.active = car
        
        # frame
        bpy.context.scene.frame_current = 0
        bpy.ops.anim.keyframe_insert_menu(type='Location')
        N = 10
        x = x_start
        y = y_start
        z = alt(x, y)
        for i in range(1, N+1):
            bpy.context.scene.frame_current = round(100 * i / N)
            if orientation % 2:
                old_x = x
                x += (orientation-2) * distance / N
                old_z = z
                z = alt(x, y)
                bpy.ops.transform.translate(
                    value=(x-old_x, 0, z-old_z)
                )
            else:
                old_y = y
                y += (1-orientation) * distance / N
                old_z = z
                z = alt(x, y)
                bpy.ops.transform.translate(
                    value=(0, y-old_y, z-old_z)
                )
            bpy.ops.anim.keyframe_insert_menu(type='Location')
            
        # parent
        car.parent = road.object


    @classmethod
    def load_cars(self):
        Car.cars = list()
        
        for key, object in bpy.data.objects.items():
            if key.startswith("car"):
                Car.cars.append(object)
