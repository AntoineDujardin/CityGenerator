import bpy
import os

def load_all():
    load("Texture", "vert_road_text")
    load("Texture", "hor_road_text")

def load(ofolder, oname):
    """Append an element based on a resource in blender ;
    ofolder is the subfolder in the blender file, oname is the
    object name"""
    
    # append the resource
    s = os.sep
    opath = "//resources.blend\\{}\\{}".format(ofolder, oname)
    dpath = bpy.utils.script_paths()[1] + \
        "{0}addons{0}city_generator{0}resources{0}resources.blend\\{1}\\".format(s, ofolder)
    
    bpy.ops.wm.link_append(filepath=opath,
                           filename=oname,
                           directory=dpath,
                           filemode=1,
                           link=False,
                           relative_path=True)
