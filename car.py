import bpy

class Car:
    """Class managing the cars."""
    
    def __init__(self, x_start, y_start, orientation, distance, city):
        """Create a car starting in x_start, y_start, running to the
        given orientation (0=S->N, 1=E->W, 2=N-S, 3=W->E) the given
        distance during the frame time."""
        
        # leave EDIT mode if needed
        if bpy.context.object:
            bpy.ops.object.mode_set(mode='OBJECT')
        
        # create a plane
        alt = city.ground.altitude_f
        bpy.ops.mesh.primitive_cube_add(
            radius=.1, 
            location=(x_start, y_start, alt(x_start, y_start) + .1)
        )
        
        # recover infos
        scene = bpy.context.scene
        object = bpy.context.object
        mesh = object.data
        
        # rename
        object.name = "".join(("C_car.000"))
        mesh.name = "".join(("C_car.000"))
        
        # frame
        bpy.data.scenes["Scene"].frame_current = 1
        bpy.ops.anim.keyframe_insert_menu(type='Location')
        N = 10
        x = x_start
        y = y_start
        z = alt(x, y)
        for i in range(1, N+1):
            bpy.data.scenes["Scene"].frame_current = round(100 * i / N)
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
