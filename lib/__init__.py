import bpy

from .configs.audio_source import AC_AudioSource
from .configs.lighting import (AC_DirectionList, AC_GlobalLighting, AC_Light,
                               AC_Lighting, AC_MaterialList, AC_MeshList,
                               AC_PositionList, AC_SunSettings)
from .configs.surface import AC_Surface
from .configs.track import AC_Track
from .menus.context import (WM_MT_AssignSurface, pit_menu, start_menu,
                            surface_menu, utility_menu)
from .menus.ops.audio import AC_AddAudioSource, AC_ToggleAudio
from .menus.ops.extensions import (AC_AddGlobalExtension,
                                   AC_AddGlobalExtensionItem,
                                   AC_RemoveGlobalExtension,
                                   AC_RemoveGlobalExtensionItem,
                                   AC_ToggleGlobalExtension)
from .menus.ops.project import (AC_AddABFinishGate, AC_AddABStartGate,
                                AC_AddAudioEmitter, AC_AddHotlapStart,
                                AC_AddPitbox, AC_AddStart, AC_AddTimeGate,
                                AC_AutofixPreflight, AC_LoadSettings,
                                AC_SaveSettings)
from .menus.ops.surface import (AC_AddSurface, AC_AddSurfaceExt,
                                AC_AssignPhysProp, AC_AssignSurface,
                                AC_AssignWall, AC_DeleteSurfaceExt,
                                AC_InitSurfaces, AC_RemoveSurface,
                                AC_SelectAllSurfaces, AC_ToggleSurface)
from .menus.ops.track import (AC_AddGeoTag, AC_AddTag, AC_RemoveGeoTag,
                              AC_RemoveTag, AC_ToggleGeoTag, AC_ToggleTag)
from .menus.sidebar import (AC_UL_Extenstions, AC_UL_SurfaceExtenstions,
                            AC_UL_Tags, VIEW3D_PT_AC_Sidebar_Audio,
                            VIEW3D_PT_AC_Sidebar_Extensions,
                            VIEW3D_PT_AC_Sidebar_Lighting,
                            VIEW3D_PT_AC_Sidebar_Project,
                            VIEW3D_PT_AC_Sidebar_Surfaces,
                            VIEW3D_PT_AC_Sidebar_Track)
from .settings import AC_Settings

__classes__ = (
    AC_InitSurfaces, AC_AddSurface, AC_RemoveSurface, AC_ToggleSurface, AC_AssignSurface, AC_SelectAllSurfaces, AC_AssignWall, AC_AssignPhysProp,
    AC_AddSurfaceExt, AC_DeleteSurfaceExt,
    AC_AddTag, AC_RemoveTag, AC_AddGeoTag, AC_RemoveGeoTag, AC_ToggleTag, AC_ToggleGeoTag,
    AC_AutofixPreflight,
    AC_SaveSettings, AC_LoadSettings,
    AC_AddAudioSource, AC_ToggleAudio,
    AC_AddGlobalExtension, AC_RemoveGlobalExtension, AC_ToggleGlobalExtension, AC_AddGlobalExtensionItem, AC_RemoveGlobalExtensionItem,
    AC_AddStart, AC_AddHotlapStart, AC_AddPitbox, AC_AddTimeGate, AC_AddABStartGate, AC_AddABFinishGate, AC_AddAudioEmitter, 
    AC_Track, AC_Surface, AC_AudioSource,
    AC_MeshList, AC_MaterialList, AC_PositionList, AC_DirectionList,
    AC_SunSettings, AC_GlobalLighting, AC_Light, AC_Lighting,
    AC_Settings,
    AC_UL_Tags, AC_UL_Extenstions, AC_UL_SurfaceExtenstions,
    VIEW3D_PT_AC_Sidebar_Project, VIEW3D_PT_AC_Sidebar_Track, VIEW3D_PT_AC_Sidebar_Surfaces, VIEW3D_PT_AC_Sidebar_Audio, VIEW3D_PT_AC_Sidebar_Lighting, VIEW3D_PT_AC_Sidebar_Extensions,
    WM_MT_AssignSurface,
)

def register():
    from bpy.utils import register_class
    for cls in __classes__:
        register_class(cls)
    bpy.types.Scene.AC_Settings = bpy.props.PointerProperty(type=AC_Settings)
    bpy.types.VIEW3D_MT_object_context_menu.append(start_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(pit_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(surface_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(utility_menu)

def unregister():
    from bpy.utils import unregister_class
    bpy.types.Scene.AC_Settings = None
    for cls in reversed(__classes__):
        unregister_class(cls)
