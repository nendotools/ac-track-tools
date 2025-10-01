import bpy

from .configs.audio_source import AC_AudioSource
from .configs.kn5 import (AC_MaterialSettings, AC_ShaderProperty,
                          AC_TextureSettings)
from .configs.layout import (AC_LayoutCollection, AC_LayoutSettings,
                             AC_TrackLayout)
from .configs.lighting import (AC_DirectionList, AC_GlobalLighting, AC_Light,
                               AC_Lighting, AC_MaterialList, AC_MeshList,
                               AC_PositionList, AC_SunSettings)
from .configs.surface import AC_Surface
from .configs.track import AC_Track
from .gizmos.pitbox import (AC_GizmoGate, AC_GizmoGroup,
                            AC_GizmoPitbox, AC_GizmoStartPos, AC_SelectGizmoObject)
from .menus.context import (WM_MT_AssignSurface, WM_MT_ObjectSetup, pit_menu,
                            start_menu, surface_menu, utility_menu)
from .menus.ops.audio import AC_AddAudioSource, AC_ToggleAudio
from .menus.ops.extensions import (AC_AddGlobalExtension,
                                   AC_AddGlobalExtensionItem,
                                   AC_RemoveGlobalExtension,
                                   AC_RemoveGlobalExtensionItem,
                                   AC_ToggleGlobalExtension)
from .menus.ops.object_setup import (AC_AutoSetupObjects, AC_SetupAsGrass,
                                     AC_SetupAsStandard, AC_SetupAsTree)
from .menus.ops.image_generation import (AC_CreatePreviewCamera,
                                         AC_GenerateMap, AC_GeneratePreview)
from .menus.ops.layout import (AC_AddLayout, AC_RefreshLayoutCollections,
                               AC_RemoveLayout, AC_RemoveLayoutByIndex, AC_SetActiveLayout,
                               AC_ToggleLayoutCollection, AC_ToggleLayoutExpand)
from .menus.ops.project import (AC_AddABFinishGate, AC_AddABStartGate,
                                AC_AddAudioEmitter, AC_AddHotlapStart,
                                AC_AddPitbox, AC_AddStart, AC_AddTimeGate,
                                AC_AutofixPreflight, AC_ExportTrack,
                                AC_LoadSettings, AC_SaveSettings)
from .menus.ops.surface import (AC_AddSurface, AC_AddSurfaceExt,
                                AC_AssignPhysProp, AC_AssignSurface,
                                AC_AssignWall, AC_DeleteSurfaceExt,
                                AC_InitSurfaces, AC_RemoveSurface,
                                AC_SelectAllSurfaces, AC_ToggleSurface)
from .menus.ops.track import (AC_AddGeoTag, AC_AddTag, AC_RemoveGeoTag,
                              AC_RemoveTag, AC_SelectByName, AC_ToggleGeoTag,
                              AC_ToggleTag)
from .menus.panels import (AC_AddShaderProperty, AC_RemoveShaderProperty,
                           AC_UL_ShaderProperties, NODE_PT_AC_Texture,
                           PROPERTIES_PT_AC_Material)
from .menus.sidebar import (AC_UL_Extensions, AC_UL_LayoutCollections,
                            AC_UL_SurfaceExtensions, AC_UL_Tags,
                            VIEW3D_PT_AC_Sidebar_Audio,
                            VIEW3D_PT_AC_Sidebar_Extensions,
                            VIEW3D_PT_AC_Sidebar_Layouts,
                            VIEW3D_PT_AC_Sidebar_Lighting,
                            VIEW3D_PT_AC_Sidebar_Project,
                            VIEW3D_PT_AC_Sidebar_Surfaces,
                            VIEW3D_PT_AC_Sidebar_Track)
from .settings import AC_Settings, ExportSettings, KN5_MeshSettings

__classes__ = (
    AC_InitSurfaces, AC_AddSurface, AC_RemoveSurface, AC_ToggleSurface, AC_AssignSurface, AC_SelectAllSurfaces, AC_AssignWall, AC_AssignPhysProp,
    AC_AddSurfaceExt, AC_DeleteSurfaceExt,
    AC_AddTag, AC_RemoveTag, AC_AddGeoTag, AC_RemoveGeoTag, AC_ToggleTag, AC_ToggleGeoTag,
    AC_AutofixPreflight, AC_ExportTrack,
    AC_SaveSettings, AC_LoadSettings,
    AC_SelectByName,
    AC_SelectGizmoObject, AC_GizmoPitbox, AC_GizmoStartPos, AC_GizmoGate, AC_GizmoGroup,
    AC_AddAudioSource, AC_ToggleAudio,
    AC_AddGlobalExtension, AC_RemoveGlobalExtension, AC_ToggleGlobalExtension, AC_AddGlobalExtensionItem, AC_RemoveGlobalExtensionItem,
    AC_AddStart, AC_AddHotlapStart, AC_AddPitbox, AC_AddTimeGate, AC_AddABStartGate, AC_AddABFinishGate, AC_AddAudioEmitter,
    AC_SetupAsTree, AC_SetupAsGrass, AC_SetupAsStandard, AC_AutoSetupObjects,
    AC_AddShaderProperty, AC_RemoveShaderProperty,
    AC_GenerateMap, AC_GeneratePreview, AC_CreatePreviewCamera,
    AC_AddLayout, AC_RemoveLayout, AC_RemoveLayoutByIndex, AC_ToggleLayoutCollection, AC_SetActiveLayout, AC_RefreshLayoutCollections, AC_ToggleLayoutExpand,
    AC_LayoutCollection, AC_TrackLayout, AC_LayoutSettings,
    AC_Track, AC_Surface, AC_AudioSource,
    AC_MeshList, AC_MaterialList, AC_PositionList, AC_DirectionList,
    AC_SunSettings, AC_GlobalLighting, AC_Light, AC_Lighting,
    AC_ShaderProperty, AC_MaterialSettings, AC_TextureSettings,
    KN5_MeshSettings, ExportSettings, AC_Settings,
    AC_UL_Tags, AC_UL_Extensions, AC_UL_SurfaceExtensions, AC_UL_LayoutCollections, AC_UL_ShaderProperties,
    VIEW3D_PT_AC_Sidebar_Project, VIEW3D_PT_AC_Sidebar_Track, VIEW3D_PT_AC_Sidebar_Layouts, VIEW3D_PT_AC_Sidebar_Surfaces, VIEW3D_PT_AC_Sidebar_Audio, VIEW3D_PT_AC_Sidebar_Lighting, VIEW3D_PT_AC_Sidebar_Extensions,
    PROPERTIES_PT_AC_Material, NODE_PT_AC_Texture,
    WM_MT_AssignSurface, WM_MT_ObjectSetup,
)

def register():
    from bpy.utils import register_class
    for cls in __classes__:
        register_class(cls)
    bpy.types.Scene.AC_Settings = bpy.props.PointerProperty(type=AC_Settings)
    bpy.types.Object.AC_KN5 = bpy.props.PointerProperty(type=KN5_MeshSettings)
    bpy.types.Material.AC_Material = bpy.props.PointerProperty(type=AC_MaterialSettings)
    bpy.types.ShaderNodeTexImage.AC_Texture = bpy.props.PointerProperty(type=AC_TextureSettings)
    bpy.types.VIEW3D_MT_object_context_menu.append(start_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(pit_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(surface_menu)
    bpy.types.VIEW3D_MT_object_context_menu.append(utility_menu)

def unregister():
    from bpy.utils import unregister_class
    del bpy.types.ShaderNodeTexImage.AC_Texture
    del bpy.types.Material.AC_Material
    del bpy.types.Object.AC_KN5
    del bpy.types.Scene.AC_Settings
    for cls in reversed(__classes__):
        unregister_class(cls)
