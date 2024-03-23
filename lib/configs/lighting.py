from bpy.types import PropertyGroup
from bpy.props import IntProperty, FloatProperty, FloatVectorProperty, BoolProperty, PointerProperty, CollectionProperty

class AC_SunSettings(PropertyGroup):
    sun_pitch_angle: IntProperty(
        name="Sun Pitch Angle",
        description="The pitch angle of the sun (sunrise <-> noon)",
        default=45,
        min=0,
        max=180
    )

    sun_heading_angle: IntProperty(
        name="Sun Heading Angle",
        description="The heading angle of the sun (cardinal direction)",
        default=0,
        min=-180,
        max=180
    )

class AC_GlobalLighting(PropertyGroup):
    enable_trees_lighting: BoolProperty(
        name="Enable Trees Lighting",
        description="If all your trees are not very close to a track, you can improve performance a lot by disabling trees lighting completely",
        default=True
    )

    use_track_ambient_ground_mult: BoolProperty(
        name="Use Track Ambient Ground Multiplier",
        description="Override default ambient ground lighting (affects surfaces facing down)",
        default=False
    )
    track_ambient_ground_mult: FloatProperty(
        name="Track Ambient Ground Multiplier",
        description="Allows to redefine ambient multiplier for surfaces facing down",
        default=0.5,
        min=0,
        max=1
    )

    use_multipliers: BoolProperty(
        name="Use Multipliers",
        default=False
    )
    lit_mult: FloatProperty(
        name="Lit Multiplier",
        description="Multiplier for dynamic lights affecting the track",
        default=1,
        min=0,
        max=4
    )

    specular_mult: FloatProperty(
        name="Specular Multiplier",
        description="Multiplier for speculars",
        default=1,
        min=0,
        max=4
    )

    car_lights_lit_mult: FloatProperty(
        name="Car Lights Lit Multiplier",
        description="Multiplier for dynamic lights affecting cars on the track",
        default=1,
        min=0,
        max=4
    )

    use_bounced_light_mult: BoolProperty(
        name="Use Bounced Light Multiplier",
        default=False
    )
    bounced_light_mult: FloatVectorProperty(
        name="Bounced Light Multiplier",
        description="Multiplier for bouncing light (set to 0 if track is black, for example)",
        default=(1, 1, 1, 1),
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR'
    )

    use_terrain_shadows_threshold: BoolProperty(
        name="Use Terrain Shadows Threshold",
        default=False
    )
    terrain_shadows_threshold: FloatProperty(
        name="Terrain Shadows Threshold",
        description="Terrain shadows threshold",
        default=0,
        min=0,
        max=1
    )

    def from_dict(self, data: dict):
        self.enable_trees_lighting = True if "enable_trees_lighting" in data and data["enable_trees_lighting"] == 1 else False
        self.use_track_ambient_ground_mult = True if "track_ambient_ground_mult" in data else False
        self.track_ambient_ground_mult = float(data.get("track_ambient_ground_mult", 0.5))
        self.use_multipliers = True if "lit_mult" in data else False
        self.lit_mult = float(data.get("lit_mult", 1))
        self.specular_mult = float(data.get("specular_mult", 1))
        self.car_lights_lit_mult = float(data.get("car_lights_lit_mult", 1))
        self.use_bounced_light_mult = True if "bounced_light_mult" in data else False
        self.bounced_light_mult = data.get("bounced_light_mult", (1, 1, 1, 1))
        self.use_terrain_shadows_threshold = True if "terrain_shadows_threshold" in data else False 
        self.terrain_shadows_threshold = float(data.get("terrain_shadows_threshold", 0))

    def to_dict(self) -> dict:
        data = {}
        data["enable_trees_lighting"] = 1 if self.enable_trees_lighting else 0
        if self.use_track_ambient_ground_mult:
            data["track_ambient_ground_mult"] = self.track_ambient_ground_mult
        if self.use_multipliers:
            data["lit_mult"] = self.lit_mult
            data["specular_mult"] = self.specular_mult
            data["car_lights_lit_mult"] = self.car_lights_lit_mult
        if self.use_bounced_light_mult:
            data["bounced_light_mult"] = self.bounced_light_mult
        if self.use_terrain_shadows_threshold:
            data["terrain_shadows_threshold"] = self.terrain_shadows_threshold
        return data


class AC_Light(PropertyGroup):
    pass

class AC_LightSeries(PropertyGroup):
    pass


class AC_Lighting(PropertyGroup):
    sun: PointerProperty(
        type=AC_SunSettings,
        name="Sun Settings"
    )

    global_lighting: PointerProperty(
        type=AC_GlobalLighting,
        name="Global Lighting"
    )

    lights: CollectionProperty(
        type=AC_Light,
        name="Lights"
    )

    light_series: CollectionProperty(
        type=AC_LightSeries,
        name="Light Series"
    )

    def from_dict(self, data: dict):
        self.sun.sun_pitch_angle = data.get("sun_pitch_angle", 45)
        self.sun.sun_heading_angle = data.get("sun_heading_angle", 0)

    def to_dict(self) -> dict:
        return {
            "sun_pitch_angle": self.sun.sun_pitch_angle,
            "sun_heading_angle": self.sun.sun_heading_angle
        }
