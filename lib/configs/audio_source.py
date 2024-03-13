import re
from bpy.types import Context, Object
from bpy.types import PropertyGroup
from bpy.props import (
    PointerProperty,
    StringProperty,
    IntProperty,
    FloatProperty,
    BoolProperty,
    EnumProperty
)

from ...utils.constants import (
    AC_TIME_L_REGEX,
    AC_TIME_R_REGEX,
    FINISH_AB_L_REGEX,
    FINISH_AB_R_REGEX,
    PIT_BOX_REGEX,
    START_AB_L_REGEX,
    START_AB_R_REGEX,
    START_CIRCUIT_REGEX,
    START_HOTLAP_REGEX
)

##
## Audio Sources can support playing sounds when driving in range of the source node
## or they can be used to apply reverb effects to sounds triggered within the effect range.
##
class AC_AudioSource(PropertyGroup):
    ##
    ## Global Properties
    ##
    name: StringProperty(
        name="Name",
        description="Name of the audio source",
        default="New Audio Source"
    )
    audio_type: EnumProperty(
        name="Audio Type",
        description="Type of audio source",
        items=[
            ('SFX', "Sound Effect", "Sound effect to play"),
            ('REVERB', "Reverb", "Reverb effect settings")
        ],
        default='REVERB',
        update= lambda s,c: s.refit_name(c)
    )
    # Node can be any AC_ node in the scene for reverb effects.
    # For sounds, the node should follow the convention of 'AC_AUDIO_${name}'.
    # ${name} can be any number (default) or standard string name without spaces.
    node: StringProperty(
        name="Node",
        description="Node to attach the audio source to",
        default=""
    )
    node_pointer: PointerProperty(
        name="Node Pointer",
        description="Pointer to the node to attach the audio source to",
        type=Object,
        poll= lambda s,o: o.name.startswith('AC_') if s.audio_type == 'REVERB' else re.match(r"AC_AUDIO_\d+",o.name),
        update= lambda s,c: s.assert_name(c)
    )
    expand: BoolProperty(
        name="Expand",
        description="Expand the audio source properties",
        default=False
    )

    ##
    ## Sound Effect Properties
    ##
    filename: StringProperty(
        name="Filename",
        description="WAV file must be a reference to a sound bank to work",
        default="",
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
    # TODO: This should be a reference field. It cannot be updated on attribute change without triggering light recursion.
    #       It should always be saved to the INI as CUSTOM.
    preset: EnumProperty(
        name="Preset",
        description="Reverb preset to use as base",
        items= [
            ('NONE', "None", "No reverb effect"),
            ('GENERIC', "Generic", "Generic reverb effect"),
            ('PADDEDCELL', "Padded Cell", "Padded Cell reverb effect"),
            ('ROOM', "Room", "Room reverb effect"),
            ('BATHROOM', "Bathroom", "Bathroom reverb effect"),
            ('LIVINGROOM', "Living Room", "Living Room reverb effect"),
            ('STONEROOM', "Stone Room", "Stone Room reverb effect"),
            ('AUDITORIUM', "Auditorium", "Auditorium reverb effect"),
            ('CONCERTHALL', "Concert Hall", "Concert Hall reverb effect"),
            ('CAVE', "Cave", "Cave reverb effect"),
            ('ARENA', "Arena", "Arena reverb effect"),
            ('HANGAR', "Hangar", "Hangar reverb effect"),
            ('CARPETEDHALLWAY', "Carpeted Hallway", "Carpeted Hallway reverb effect"),
            ('HALLWAY', "Hallway", "Hallway reverb effect"),
            ('STONECORRIDOR', "Stone Corridor", "Stone Corridor reverb effect"),
            ('ALLEY', "Alley", "Alley reverb effect"),
            ('FOREST', "Forest", "Forest reverb effect"),
            ('CITY', "City", "City reverb effect"),
            ('MOUNTAINS', "Mountains", "Mountains reverb effect"),
            ('QUARRY', "Quarry", "Quarry reverb effect"),
            ('PLAIN', "Plain", "Plain reverb effect"),
            ('PARKINGLOT', "Parking Lot", "Parking Lot reverb effect"),
            ('SEWERPIPE', "Sewer Pipe", "Sewer Pipe reverb effect"),
            ('UNDERWATER', "Underwater", "Underwater reverb effect"),
        ],
        default='NONE',
        update= lambda s,c: s.from_preset(c)
    )
    min_distance: IntProperty(
        name="Min Distance",
        description="Minimum distance for the reverb effect",
        default=150,
        min=1,
        max=500,
        update= lambda s,c: s.modified(c)
    )
    max_distance: IntProperty(
        name="Max Distance",
        description="Maximum distance for the reverb effect",
        default=250,
        min=1,
        max=500,
        update= lambda s, c: s.modified(c)
    )
    decay_time: IntProperty(
        name="Decay Time",
        description="Duration a sound will persist in the reverb effect (in milliseconds)",
        default=1500,
        min=0,
        max=20000,
        update= lambda s, c: s.modified(c)
    )
    early_delay: IntProperty(
        name="Early Delay",
        description="Early delay for the reverb effect (in milliseconds)",
        default=300,
        min=0,
        max=1000,
        update= lambda s, c: s.modified(c)
    )
    late_delay: IntProperty(
        name="Late Delay",
        description="Late delay for the reverb effect (in milliseconds)",
        default=100,
        min=0,
        max=1000,
        update= lambda s, c: s.modified(c)
    )
    hf_reference: IntProperty(
        name="HF Reference",
        description="High frequency reference for the reverb effect",
        default=4500,
        min=20,
        max=20000,
        update= lambda s, c: s.modified(c)
    )
    hf_decay_ratio: IntProperty(
        name="HF Decay Ratio",
        description="Rate of decay for high frequencies in the reverb effect",
        default=75,
        min=0,
        max=100,
        update= lambda s, c: s.modified(c)
    )
    diffusion: IntProperty(
        name="Diffusion",
        description="Size/spacing of the reflections for the reverb effect",
        default=100,
        min=0,
        max=100,
        update= lambda s, c: s.modified(c)
    )
    density: IntProperty(
        name="Density",
        description="Density of the reflections for the reverb effect",
        default=100,
        min=0,
        max=100,
        update= lambda s, c: s.modified(c)
    )
    low_shelf_frequency: IntProperty(
        name="Low Shelf Frequency",
        description="Low shelf frequency for the reverb effect",
        default=250,
        min=20,
        max=1000,
        update= lambda s, c: s.modified(c)
    )
    low_shelf_gain: IntProperty(
        name="Low Shelf Gain",
        description="Low shelf gain for the reverb effect",
        default=0,
        min=-50,
        max=50,
        update= lambda s, c: s.modified(c)
    )
    high_cut: IntProperty(
        name="High Cut",
        description="High cut for the reverb effect",
        default=4000,
        min=20,
        max=20000,
        update= lambda s, c: s.modified(c)
    )
    early_late_mix: IntProperty(
        name="Early Late Mix",
        description="Early late mix for the reverb effect",
        default=50,
        min=0,
        max=100,
        update= lambda s, c: s.modified(c)
    )
    wet_level: FloatProperty(
        name="Wet Level",
        description="Wet level for the reverb effect",
        default=-6,
        min=-100.0,
        max=100.0,
        update= lambda s, c: s.modified(c)
    )

    def modified(self, _:Context):
        # self.preset = 'CUSTOM'
        pass

    def assert_name(self, context: Context):
        name_rules = [
            lambda n: n.startswith('AC_AUDIO_'),
        ]
        if self.audio_type == 'REVERB':
            name_rules = [
                lambda n: n.startswith('AC_AUDIO_'),
                lambda n: re.match(r'AC_AUDIO_\d+', n),
                lambda n: re.match(START_CIRCUIT_REGEX, n),
                lambda n: re.match(START_HOTLAP_REGEX, n),
                lambda n: re.match(START_AB_L_REGEX, n),
                lambda n: re.match(START_AB_R_REGEX, n),
                lambda n: re.match(FINISH_AB_L_REGEX, n),
                lambda n: re.match(FINISH_AB_R_REGEX, n),
                lambda n: re.match(AC_TIME_L_REGEX, n),
                lambda n: re.match(AC_TIME_R_REGEX, n),
                lambda n: re.match(PIT_BOX_REGEX, n),
            ]
        if not self.node_pointer:
            self.node = ""
            return

        if not any([rule(self.node_pointer.name) for rule in name_rules]):
            self.node = ""
            self.node_pointer = None
            return

        if self.node_pointer:
            self.node = self.node_pointer.name
            if self.audio_type == 'SFX':
                self.name = self.node_pointer.name

    def refit_name(self, context: Context):
        settings = context.scene.AC_Settings
        sfx = []
        reverb = []
        for audio in settings.audio_sources:
            if audio.audio_type == 'SFX' and not audio.node_pointer:
                audio.name = f"AC_AUDIO_{1 + len(sfx)}"
                sfx.append(audio.name)
            else:
                audio.name = f"REVERB_{len(reverb)}"
                reverb.append(audio.name)

    def from_preset(self, _:Context):
        preset = self.preset
        if(preset == 'CUSTOM'):
            return
        if preset in REVERB_PRESETS:
            for i, key in enumerate(REVERB_PRESETS['MAPPING']):
                setattr(self, key.lower().replace(' ', '_'), REVERB_PRESETS[preset][i])

    def to_dict(self) -> dict:
        if self.audio_type == 'SFX':
            return {
                'NAME': self.name,
                'FILENAME': self.filename,
                'VOLUME': self.volume,
                'VOLUME_SCALE': self.volume_scale
            }
        return {
            'NAME': self.name,
            'ENABLED': 1 if self.enabled else 0,
            'NODE': self.node,
            'PRESET': 'CUSTOM',
            'MIN_DISTANCE': self.min_distance,
            'MAX_DISTANCE': self.max_distance,
            'DECAY_TIME': self.decay_time,
            'EARLY_DELAY': self.early_delay,
            'LATE_DELAY': self.late_delay,
            'HF_REFERENCE': self.hf_reference,
            'HF_DECAY_RATIO': self.hf_decay_ratio,
            'DIFFUSION': self.diffusion,
            'DENSITY': self.density,
            'LOW_SHELF_FREQUENCY': self.low_shelf_frequency,
            'LOW_SHELF_GAIN': self.low_shelf_gain,
            'HIGH_CUT': self.high_cut,
            'EARLY_LATE_MIX': self.early_late_mix,
            'WET_LEVEL': self.wet_level
        }

    def from_dict(self, audio: dict):
        self.name = audio['NAME']
        if 'filename' in audio:
            self.audio_type = 'SFX'
            self.filename = audio['FILENAME']
            self.volume = float(audio['VOLUME'])
            self.volume_scale = float(audio['VOLUME_SCALE'])
        else:
            self.audio_type = 'REVERB'
            self.enabled = True if audio['ENABLED'] else False
            self.node = audio['NODE']
            self.presets = 'NONE'
            self.min_distance = int(audio['MIN_DISTANCE'])
            self.max_distance = int(audio['MAX_DISTANCE'])
            self.decay_time = int(audio['DECAY_TIME'])
            self.early_delay = int(audio['EARLY_DELAY'])
            self.late_delay = int(audio['LATE_DELAY'])
            self.hf_reference = int(audio['HF_REFERENCE'])
            self.hf_decay_ratio = int(audio['HF_DECAY_RATIO'])
            self.diffusion = int(audio['DIFFUSION'])
            self.density = int(audio['DENSITY'])
            self.low_shelf_frequency = int(audio['LOW_SHELF_FREQUENCY'])
            self.low_shelf_gain = int(audio['LOW_SHELF_GAIN'])
            self.high_cut = int(audio['HIGH_CUT'])
            self.early_late_mix = int(audio['EARLY_LATE_MIX'])
            self.wet_level = float(audio['WET_LEVEL'])


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
