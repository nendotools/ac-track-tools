from bpy.types import Operator
from bpy.props import StringProperty, IntProperty

class AC_AddAudioSource(Operator):
    """Add audio source to track"""
    bl_idname = "ac.add_audio_source"
    bl_label = "Add AudioSource"
    bl_options = {'REGISTER'}
    name: StringProperty(
        name="Name",
        default="New Audio Source",
    )
    def execute(self, context):
        settings = context.scene.AC_Settings # type: ignore
        reverbs = [a for a in settings.audio_sources if a.audio_type == "REVERB"]
        audio_source = settings.audio_sources.add()
        audio_source.name = f"REVERB_{len(reverbs)}"
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
