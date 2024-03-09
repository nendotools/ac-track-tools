import bpy
from .menus.ops.surface import (
    AC_InitSurfaces,
    AC_AddSurface,
    AC_RemoveSurface,
    AC_ToggleSurface,
    AC_AssignSurface,
    AC_AssignWall
)
from .menus.ops.project import (
    AC_AddHotlapStart,
    AC_AddPitbox,
    AC_SaveSettings,
    AC_LoadSettings,
    AC_AddStart
)
from .menus.ops.track import (
    AC_AddTag,
    AC_RemoveTag,
    AC_ToggleTag,
    AC_AddGeoTag,
    AC_RemoveGeoTag,
    AC_ToggleGeoTag
)
from .menus.sidebar import (
    VIEW3D_PT_AC_Sidebar_Project,
    VIEW3D_PT_AC_Sidebar_Track,
    AC_UL_Tags,
    VIEW3D_PT_AC_Sidebar_Surfaces
)
from .menus.context import WM_MT_AssignSurface, pit_menu, start_menu, surface_menu
from .configs.surface import AC_Surface
from .configs.track import AC_Track
from .settings import AC_Settings

__classes__ = (
    AC_InitSurfaces, AC_AddSurface, AC_RemoveSurface, AC_ToggleSurface, AC_AssignSurface, AC_AssignWall,
    AC_AddTag, AC_RemoveTag, AC_AddGeoTag, AC_RemoveGeoTag, AC_ToggleTag, AC_ToggleGeoTag,
    AC_SaveSettings, AC_LoadSettings, AC_AddStart, AC_AddHotlapStart, AC_AddPitbox,
    AC_Surface, AC_Track, AC_Settings,
    AC_UL_Tags,
    VIEW3D_PT_AC_Sidebar_Project, VIEW3D_PT_AC_Sidebar_Track, VIEW3D_PT_AC_Sidebar_Surfaces,
    WM_MT_AssignSurface,
)

def register():
    from bpy.utils import register_class
    for cls in __classes__:
        print('registering', cls.__name__)
        register_class(cls)
    bpy.types.Scene.AC_Settings = bpy.props.PointerProperty(type=AC_Settings)
    bpy.types.VIEW3D_MT_object_context_menu.append(start_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(pit_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(surface_menu)

def unregister():
    from bpy.utils import unregister_class
    bpy.types.Scene.AC_Settings = None
    for cls in reversed(__classes__):
        unregister_class(cls)
