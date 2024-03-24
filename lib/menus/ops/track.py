from bpy.props import IntProperty, StringProperty
from bpy.types import Operator


# add tag to track
class AC_AddTag(Operator):
    """Add tag to track"""
    bl_idname = "ac.add_tag"
    bl_label = "Add Tag"
    bl_options = {'REGISTER'}
    tag: StringProperty(
        name="Tag",
        default="New Tag",
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        track = settings.track
        tag = track.tags.add()
        tag.value = self.tag
        return {'FINISHED'}

# remove tag from track
class AC_RemoveTag(Operator):
    """Remove tag from track"""
    bl_idname = "ac.remove_tag"
    bl_label = "Remove Tag"
    bl_options = {'REGISTER'}
    index: IntProperty(
        name="Index",
        default=-1,
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        track = settings.track
        if self.index >= 0 and self.index < len(track.tags):
            track.tags.remove(self.index)
        return {'FINISHED'}


# add tag to track
class AC_AddGeoTag(Operator):
    """Add geotag to track"""
    bl_idname = "ac.add_geo_tag"
    bl_label = "Add GeoTag"
    bl_options = {'REGISTER'}
    tag: StringProperty(
        name="Tag",
        default="New Tag",
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        track = settings.track
        tag = track.geotags.add()
        tag.value = self.tag
        return {'FINISHED'}

# remove tag from track
class AC_RemoveGeoTag(Operator):
    """Remove geotag from track"""
    bl_idname = "ac.remove_geo_tag"
    bl_label = "Remove GeoTag"
    bl_options = {'REGISTER'}
    index: IntProperty(
        name="Index",
        default=-1,
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        track = settings.track
        if self.index >= 0 and self.index < len(track.geotags):
            track.geotags.remove(self.index)
        return {'FINISHED'}

class AC_ToggleTag(Operator):
    """Toggle tag"""
    bl_idname = "ac.toggle_tag"
    bl_label = "Toggle Tag"
    bl_options = {'REGISTER'}
    target: StringProperty(
        name="Target",
        default="",
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        settings.track.show_tags = not settings.track.show_tags
        return {'FINISHED'}

class AC_ToggleGeoTag(Operator):
    """Toggle geotag"""
    bl_idname = "ac.toggle_geo_tag"
    bl_label = "Toggle GeoTag"
    bl_options = {'REGISTER'}
    target: StringProperty(
        name="Target",
        default="",
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        settings.track.show_geotags = not settings.track.show_geotags
        return {'FINISHED'}
