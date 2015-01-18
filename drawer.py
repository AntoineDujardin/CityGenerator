"""Group of fonctions used for drawings."""

# To support reload properly, try to access a package var, 
# if it's there, reload everything
if "Block" in locals():
    import imp
    imp.reload(const)
else:
    from city_generator import const


import bpy

def draw_relief_plane(x_start, x_size, y_start, y_size, name,
                      altitude_function, altitude_offset=0):
    """Draw a plane with relief.
    The altitude function is a function of x and y. The offset is a
    constant value that is added to the altitude.
    Return the created object."""
    
    # leave EDIT mode if needed
    if bpy.context.object:
        bpy.ops.object.mode_set(mode='OBJECT')
    
    # create a plane
    bpy.ops.mesh.primitive_plane_add(radius=0.5, location=(0, 0, 0))
    
    # recover infos
    scene = bpy.context.scene
    object = bpy.context.object
    mesh = object.data
    
    # rename
    object.name = "".join(("C_", name, ".000"))
    mesh.name = "".join(("C_", name, ".000"))
    
    # scale it
    object.scale[0] = x_size
    object.scale[1] = y_size
    bpy.ops.object.transform_apply(scale=True)
    
    # locate it
    object.location[0] = x_start + x_size / 2
    object.location[1] = y_start + y_size / 2
    bpy.ops.object.transform_apply(location=True)
    
    # subdivide it
    # note: edges indexing on primitive plane depends on Blender version
    if bpy.app.version < (2, 70):
        (ix1, ix2, iy1, iy2) = (0, 1, 2, 3)
    else:
        (ix1, ix2, iy1, iy2) = (1, 3, 0, 2)
    if (x_size >= 2 * y_size or y_size >= 2 * x_size):
        bpy.ops.object.mode_set(mode='EDIT')
        bpy.ops.mesh.select_all(action = 'DESELECT')
        bpy.context.tool_settings.mesh_select_mode = [False, True,
                                                      False]
        bpy.ops.object.mode_set(mode='OBJECT')
        for vert in mesh.vertices:
            vert.select = True
        if x_size > y_size:
            mesh.edges[ix1].select = True
            mesh.edges[ix2].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.subdivide(number_cuts=int(x_size / y_size))
        else:
            mesh.edges[iy1].select = True
            mesh.edges[iy2].select = True
            bpy.ops.object.mode_set(mode='EDIT')
            bpy.ops.mesh.subdivide(number_cuts=int(y_size / x_size))
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action = 'SELECT')
    bpy.ops.mesh.subdivide(number_cuts=int(min(x_size, y_size)))
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # change altitude
    for vertex in mesh.vertices:
        vertex.co.z = altitude_function(vertex.co.x, vertex.co.y) \
            + altitude_offset
    
    # extrude
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action = 'SELECT')
    bpy.ops.mesh.extrude_region_move( \
        MESH_OT_extrude_region={"mirror":False},
        TRANSFORM_OT_translate={
            "value":(0, 0, -const.planes_thickness),
            "constraint_axis":(False, False, True),
            "constraint_orientation":'NORMAL',
            "mirror":False,
            "proportional":'DISABLED',
            "proportional_edit_falloff":'SMOOTH',
            "proportional_size":1,
            "snap":False,
            "snap_target":'CLOSEST',
            "snap_point":(0, 0, 0),
            "snap_align":False,
            "snap_normal":(0, 0, 0),
            "texture_space":False,
            "remove_on_cancel":False,
            "release_confirm":False
        })
    bpy.ops.mesh.dissolve_limited()
    bpy.ops.object.mode_set(mode='OBJECT')
    
    return object
