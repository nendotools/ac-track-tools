import bpy
from bpy.types import PropertyGroup, Volume
from bpy.props import (
    StringProperty,
    IntProperty,
    FloatProperty,
    BoolProperty,
    EnumProperty
)

from utils.files import verify_local_file

##
## Audio Sources can support playing sounds when driving in range of the source node
## or they can be used to apply reverb effects to sounds triggered within the effect range.
##
class AC_AudioSource(PropertyGroup):
    ##
    ## Global Properties
    ##
    audo_type: EnumProperty(
        name="Audio Type",
        description="Type of audio source",
        items=[
            ('SFX', "Sound Effect", "Sound effect to play"),
            ('REVERB', "Reverb", "Reverb effect settings")
        ],
        default='SFX'
    )
    # Node can be named anything for reverbs, but sound effects must use the
    # correct audio source naming convention: "AC_AUDIO_$"
    node: StringProperty(
        name="Node",
        description="Node to attach the audio source to",
        default=""
    )

    ##
    ## Sound Effect Properties
    ##
    filename: StringProperty(
        name="Filename",
        description="Filename of the audio source",
        subtype='FILE_PATH',
        default="",
        update= lambda s,c: s.ensure_local_file(c)
    )
    volume: FloatProperty(
        name="Volume",
        description="Volume of the audio source",
        default=0.9,
        min=0,
        max=3,
        precision=2
    )
    volume_scale: IntProperty(
        name="Volume Scale",
        description="Volume scale of the audio source",
        default=20,
        min=1,
        max=100
    )

    ##
    ## Reverb Properties
    ##
    enabled: BoolProperty(
        name="Enabled",
        description="Is the audio source enabled",
        default=True
    )
    preset: EnumProperty(
        name="Preset",
        description="Reverb preset to use",
        items=[
            ('NONE', "None", "No reverb effect"),
            ('SMALL', "Small Room", "Small room reverb"),
            ('MEDIUM', "Medium Room", "Medium room reverb"),
            ('LARGE', "Large Room", "Large room reverb"),
            ('HALL', "Hall", "Hall reverb"),
            ('PLATE', "Plate", "Plate reverb"),
            ('CUSTOM', "Custom", "Custom reverb settings")
        ],
        default='NONE'
    )
    min_distance: IntProperty(
        name="Min Distance",
        description="Minimum distance for the reverb effect",
        default=10,
        min=1,
        max=500
    )
    max_distance: IntProperty(
        name="Max Distance",
        description="Maximum distance for the reverb effect",
        default=100,
        min=1,
        max=500
    )
    decay_time: IntProperty(
        name="Decay Time",
        description="Decay time in milliseconds for the reverb effect",
        default=1000,
        min=0,
        max=20000,
    )
    early_delay: IntProperty(
        name="Early Delay",
        description="Early delay in milliseconds for the reverb effect",
        default=50,
        min=0,
        max=500,
    )
    late_delay: IntProperty(
        name="Late Delay",
        description="Late delay in milliseconds for the reverb effect",
        default=250,
        min=0,
        max=500,
    )
    hf_reference: IntProperty(
        name="HF Reference",
        description="High frequency reference for the reverb effect",
        default=4500,
        min=20,
        max=20000,
    )
    hf_decay_ratio: IntProperty(
        name="HF Decay Ratio",
        description="High frequency decay ratio for the reverb effect",
        default=75,
        min=0,
        max=100,
    )
    diffusion: IntProperty(
        name="Diffusion",
        description="Diffusion for the reverb effect",
        default=100,
        min=0,
        max=100,
    )
    density: IntProperty(
        name="Density",
        description="Density for the reverb effect",
        default=100,
        min=0,
        max=100,
    )
    low_shelf_frequency: IntProperty(
        name="Low Shelf Frequency",
        description="Low shelf frequency for the reverb effect",
        default=250,
        min=20,
        max=1000,
    )
    lw_shelf_gain: IntProperty(
        name="Low Shelf Gain",
        description="Low shelf gain for the reverb effect",
        default=0,
        min=-36,
        max=12,
    )
    high_cut: IntProperty(
        name="High Cut",
        description="High cut for the reverb effect",
        default=4000,
        min=20,
        max=20000,
    )
    early_late_mix: IntProperty(
        name="Early Late Mix",
        description="Early late mix for the reverb effect",
        default=50,
        min=0,
        max=100,
    )
    wet_level: FloatProperty(
        name="Wet Level",
        description="Wet level for the reverb effect",
        default=-6,
        min=-80.0,
        max=20.0,
    )

    def ensure_local_file(self, context):
        if self.filename:
            self.filename = verify_local_file(self.filename, '/content/sfx/')
        return None

    def from_preset(self, preset: str):
        if preset in REVERB_PRESETS:
            self.preset = preset
            for i, key in enumerate(REVERB_PRESETS['MAPPING']):
                setattr(self, key.lower().replace(' ', '_'), REVERB_PRESETS[preset][i])

REVERB_PRESETS = {
    'DEFINITION': ('Decay Time', 'Early Delay', 'Late Delay', 'HF Reference', 'HF Decay Ratio', 'Diffusion', 'Density', 'Low Shelf Frequency', 'Low Shelf Gain', 'High Cut', 'Early Late Mix', 'Wet Level'),
    'MAPPING': ('decay_time', 'early_delay', 'late_delay', 'hf_reference', 'hf_decay_ratio', 'diffusion', 'density', 'low_shelf_frequency', 'lw_shelf_gain', 'high_cut', 'early_late_mix', 'wet_level'),
    'NONE': (1000, 7, 11, 5000, 100, 100, 100, 250, 0, 20, 96, -80.0),
    'GENERIC': (1500, 7, 11, 5000, 83, 100, 100, 250, 0, 14500, 96, -8.0),
    'PADDEDCELL': (170, 1, 2, 5000, 10, 100, 100, 250, 0, 160, 84, -7.8),
    'ROOM': (400, 2, 3, 5000, 83, 100, 100, 250, 0, 6050, 88, -9.4),
    'BATHROOM': (1500, 7, 11, 5000, 54, 100, 60, 250, 0, 2900, 83, -0.5),
    'LIVINGROOM': (500, 3, 4, 5000, 10, 100, 100, 250, 0, 160, 58, -19.0),
    'STONEROOM': (2300, 12, 17, 5000, 64, 100, 100, 250, 0, 7800, 71, -8.5),
    'AUDITORIUM': (4300, 20, 30, 5000, 30, 100, 100, 250, 0, 5850, 64, -11.7),
    'CONCERTHALL': (3900, 20, 29, 5000, 30, 100, 100, 250, 0, 5650, 80, -9.8),
    'CAVE': (2900, 15, 22, 5000, 100, 100, 100, 250, 0, 20000, 59, -11.3),
    'ARENA': (7200, 20, 30, 5000, 33, 100, 100, 250, 0, 4500, 80, -9.6),
    'HANGAR': (10000, 20, 30, 5000, 23, 100, 100, 250, 0, 3400, 72, -7.4),
    'CARPETEDHALLWAY': (300, 2, 30, 5000, 10, 100, 100, 250, 0, 500, 56, -24.0),
    'HALLWAY': (1500, 7, 11, 5000, 59, 100, 100, 250, 0, 7800, 87, -5.5),
    'STONECORRIDOR': (270, 13, 20, 5000, 79, 100, 100, 250, 0, 9000, 86, -6.0),
    'ALLEY': (1500, 7, 11, 5000, 86, 100, 100, 250, 0, 8300, 80, -9.8),
    'FOREST': (1500, 162, 88, 5000, 54, 79, 100, 250, 0, 760, 94, -12.3),
    'CITY': (1500, 7, 11, 5000, 67, 50, 100, 250, 0, 4050, 66, -26.0),
    'MOUNTAINS': (1500, 300, 100, 5000, 21, 27, 100, 250, 0, 1220, 82, -24.0),
    'QUARRY': (1500, 61, 25, 5000, 83, 100, 100, 250, 0, 3400, 100, -5.0),
    'PLAIN': (1500, 179, 100, 5000, 50, 21, 100, 250, 0, 1670, 65, -28.0),
    'PARKINGLOT': (1700, 8, 12, 5000, 100, 100, 100, 250, 0, 20000, 56, -19.5),
    'SEWERPIPE': (2800, 14, 21, 5000, 14, 80, 60, 250, 0, 3400, 66, 1.2),
    'UNDERWATER': (1500, 7, 11, 5000, 10, 100, 100, 250, 0, 500, 92, 7.0),
    'CUSTOM': ()
}
