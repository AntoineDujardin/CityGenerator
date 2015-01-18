import bpy
import os

def load_all():
    """Append all elements from the addon blender file with the
    sources."""
    
    # ensure the data is not already loaded
    if load_all.called == True:
        return
    
    load_all.called = True
    
    s = os.sep
    dirname = os.path.dirname(__file__)
    path = s.join((dirname, "resources/resources.blend"))

    with bpy.data.libraries.load(path) as (data_from, data_to):
        data_to.materials.extend(data_from.materials)
        data_to.textures.extend(data_from.textures)
        data_to.objects.extend(data_from.objects)

load_all.called = False
