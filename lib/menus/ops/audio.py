from bpy.props import StringProperty
from bpy.types import Operator


class AC_AddAudioSource(Operator):
    """Add audio source to track"""
    bl_idname = "ac.add_audio_source"
    bl_label = "Add AudioSource"
    bl_options = {'REGISTER'}
    audio_type: StringProperty(
        name="Audio Type",
        default="REVERB",
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        audio_source = settings.audio_sources.add()
        audio_source.name = "REVERB_1" if self.audio_type == "REVERB" else "AC_AUDIO_1"
        audio_source.audio_type = self.audio_type
        audio_source.refit_name(context)
        return {'FINISHED'}

class AC_ToggleAudio(Operator):
    """Toggle audio source"""
    bl_idname = "ac.toggle_audio"
    bl_label = "Toggle AudioSource"
    bl_options = {'REGISTER'}
    target: StringProperty(
        name="Target",
        default="",
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        audio_source = settings.audio_sources[self.target]
        audio_source.expand = not audio_source.expand
        return {'FINISHED'}
