from os import name
from bpy import context
from bpy.types import PropertyGroup, Object, Material
from bpy.props import (
    IntProperty,
    FloatProperty,
    FloatVectorProperty,
    StringProperty,
    BoolProperty,
    EnumProperty,
    PointerProperty,
    CollectionProperty
)

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
        self.enable_trees_lighting = True if "ENABLE_TREES_LIGHTING" in data and data["ENABLE_TREES_LIGHTING"] == 1 else False
        self.use_track_ambient_ground_mult = True if "TRACK_AMBIENT_GROUND_MULT" in data else False
        self.track_ambient_ground_mult = float(data.get("TRACK_AMBIENT_GROUND_MULT", 0.5))
        self.use_multipliers = True if "LIT_MULT" in data else False
        self.lit_mult = float(data.get("LIT_MULT", 1))
        self.specular_mult = float(data.get("SPECULAR_MULT", 1))
        self.car_lights_lit_mult = float(data.get("CAR_LIGHTS_LIT_MULT", 1))
        self.use_bounced_light_mult = True if "BOUNCED_LIGHT_MULT" in data else False
        self.bounced_light_mult = data.get("BOUNCED_LIGHT_MULT", (1, 1, 1, 1))
        self.use_terrain_shadows_threshold = True if "TERRAIN_SHADOWS_THRESHOLD" in data else False 
        self.terrain_shadows_threshold = float(data.get("TERRAIN_SHADOWS_THRESHOLD", 0))

    def to_dict(self) -> dict:
        data = {}
        data["ENABLE_TREES_LIGHTING"] = 1 if self.enable_trees_lighting else 0
        if self.use_track_ambient_ground_mult:
            data["TRACK_AMBIENT_GROUND_MULT"] = self.track_ambient_ground_mult
        if self.use_multipliers:
            data["LIT_MULT"] = self.lit_mult
            data["SPECULAR_MULT"] = self.specular_mult
            data["CAR_LIGHTS_LIT_MULT"] = self.car_lights_lit_mult
        if self.use_bounced_light_mult:
            data["BOUNCED_LIGHT_MULT"] = self.bounced_light_mult
        if self.use_terrain_shadows_threshold:
            data["TERRAIN_SHADOWS_THRESHOLD"] = self.terrain_shadows_threshold
        return data


class AC_Light(PropertyGroup):
    active: BoolProperty(
        name="Active",
        default=True
    )
    description: StringProperty(
        name="Description",
        default=""
    )

    light_type: EnumProperty(
        name="Light Type",
        items=[
            ("SPOT", "Spot", "Spotlight source"),
            ("MESH", "Mesh", "Mesh light source"),
            ("LINE", "Line", "Line light source"),
            ("SERIES", "Series", "Series light source")
        ],
        default="SPOT"
    )
    mesh: PointerProperty(
        name="Mesh",
        description="Mesh object to use as light source",
        type=Object
    )
    # if mesh is None, name is 'position', else name this to 'offset' on export/import
    # reset to (0, 0, 0) when mesh is set/removed
    position: FloatVectorProperty(
        name="Position",
        description="Light position",
        default=(0, 0, 0),
        subtype="XYZ"
    )
    # default direction is down: 0, -1, 0
    direction: FloatVectorProperty(
        name="Direction",
        description="Light direction",
        default=(0, -1, 0),
        subtype="DIRECTION"
    )
    direction_mode: EnumProperty(
        name="Direction Mode",
        description="Direction mode",
        items=[
            ("NORMAL", "Normal", "Use normal direction"),
            ("FIXED", "Fixed", "Use fixed direction")
        ],
    )
    direction_alter: FloatVectorProperty(
        name="Direction Alter",
        description="Light direction alter",
        default=(0, 0, 0),
        subtype='DIRECTION'
    )
    direction_offset: FloatVectorProperty(
        name="Direction Offset",
        description="Light direction offset",
        default=(0, 0, 0),
        subtype='DIRECTION'
    )

    # line settings
    line_from: FloatVectorProperty(
        name="Line From",
        description="Line light source start position",
        default=(0, 0, 0),
    )
    color_from: FloatVectorProperty(
        name="Color From",
        description="Line light source start color",
        default=(1, 1, 1, 1), # TODO: verify output: expects #RRGGBB, INT
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR'
    )
    line_from_helper: PointerProperty(
        name="Line From Helper",
        description="Line light source start helper",
        type=Object
    )
    line_to: FloatVectorProperty(
        name="Line To",
        description="Line light source end position",
        default=(0, 0, 0),
    )
    color_to: FloatVectorProperty(
        name="Color To",
        description="Line light source end color",
        default=(1, 1, 1, 1),
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR'
    )
    line_to_helper: PointerProperty(
        name="Line To Helper",
        description="Line light source end helper",
        type=Object
    )

    meshes: CollectionProperty(
        type=PointerProperty(
            type=Object
        ),
        name="Meshes",
        description="List of meshes to use as light source"
    )
    materials: CollectionProperty(
        type=PointerProperty(
            type=Material
        ),
        name="Materials",
        description="List of materials to use as light source"
    )
    positions: CollectionProperty(
        type=FloatVectorProperty,
        name="Positions",
        description="List of light positions"
    )
    directions: CollectionProperty(
        type=FloatVectorProperty,
        name="Directions",
        description="List of light directions"
    )

    # shape settings
    modify_shape: BoolProperty(
        name="Modify Shape",
        description="Enable to modify shape",
        default=True
    )
    spot: IntProperty(
        name="Spot",
        description="Spotlight angle",
        default=120,
        min=0,
        max=180
    )
    spot_sharpness: FloatProperty(
        name="Spot Sharpness",
        description="Sharpness of spotlight edge",
        default=0.3,
        precision=3,
        min=0,
        max=1
    )
    range: FloatProperty(
        name="Range",
        description="Light casting distance in meters",
        default=40,
        min=0,
        max=1000
    )
    range_gradient_offset: FloatProperty(
        name="Range Gradient Offset",
        description="light fade out starting distance",
        default=0.2,
        min=0,
        max=1
    )

    # performance settings
    fade_at: IntProperty(
        name="Fade At",
        description="Initial fade out distance where brightness has 50% intensity",
        default=400,
        min=0,
        max=1000
    )
    fade_smooth: IntProperty(
        name="Fade Smooth",
        description="Fade out smoothness",
        default=50,
        min=0,
        max=100
    )


    # color settings
    modify_color: BoolProperty(
        name="Modify Color",
        description="Enable to modify color",
        default=False
    )
    color: FloatVectorProperty(
        name="Color",
        description="Light color",
        default=(1, 1, 1, 1), # 255, 255, 255, 1.0 on export
        min=0.0,
        max=1.0,
        size=4,
        subtype='COLOR'
    )
    specular_multiplier: FloatProperty(
        name="Specular Multiplier",
        description="Specular multiplier",
        default=0,
        min=0,
        max=4
    )
    single_frequency: BoolProperty(
        name="Single Frequency",
        description="Use single frequency for light",
        default=False
    )
    diffuse_concentration: FloatProperty(
        name="Diffuse Concentration",
        description="Diffuse concentration",
        default=0.88,
        precision=3,
        min=0,
        max=1
    )

    # condition settings, to be implemented with global definitions later
    use_condition: BoolProperty(
        name="Use Condition",
        description="Enable condition trigger",
        default=False
    )
    condition: StringProperty(
        name="Condition",
        description="Condition trigger to control brightness and color",
        default=""
    )
    condition_offset: StringProperty(
        name="Condition Offset",
        description="(optional) offset condition flashing",
        default=""
    )

    # extras
    volumetric_light: BoolProperty(
        name="Volumetric Light",
        description="Enable volumetric light (expensive)",
        default=False
    )
    long_specular: BoolProperty(
        name="Long Specular",
        description="Enable long specular (used to create wet look, cannot cast shadows)",
        default=False
    )
    skip_light_map: BoolProperty(
        name="Skip Light Map",
        description="Enable this to exclude light from contributing to bounced lighting FX",
        default=False
    )
    disable_with_bounced_light: BoolProperty(
        name="Disable With Bounced Light",
        description="Disable light when bounced light is enabled",
        default=False
    )

    # shadow settings
    cast_shadows: BoolProperty(
        name="Shadows",
        description="Cast shadows",
        default=False
    )
    shadows_static: BoolProperty(
        name="Shadows Static",
        description="Static shadows",
        default=True
    )
    shadows_half_res: BoolProperty(
        name="Shadows Half Res",
        description="Half resolution shadows",
        default=False
    )
    shadows_spot_angle: IntProperty(
        name="Shadows Spot Angle",
        description="Shadow spotlight angle",
        default=0, # 0 to unset the value
        min=0,
        max=180
    )
    shadows_range: FloatProperty(
        name="Shadows Range",
        description="Shadow casting distance",
        default=0, # 0 to unset the value
        min=0,
        max=1000
    )
    shadows_dir: FloatVectorProperty(
        name="Shadows Direction",
        description="Shadow direction",
        default=(0, 0, 0), # 0 to unset the value
        min=-1,
        max=1,
        size=3,
        subtype="DIRECTION"
    )
    shadows_offset: FloatVectorProperty(
        name="Shadows Offset",
        description="Shadow offset position (limited to 5m)",
        default=(0, 0, 0), # 0 to unset the value
        precision=3,
        min=-5,
        max=5,
        size=3,
        subtype="TRANSLATION"
    )
    shadows_boost: FloatProperty(
        name="Shadows Boost",
        description="Shadow boost",
        default=0, # 0 to unset the value
        min=0,
        max=4
    )
    shadows_clip_plane: FloatProperty(
        name="Shadows Clip Plane",
        description="Shadow clip plane distance",
        default=0.5, # 0.5 to unset the value
        min=0,
        max=100
    )
    shadows_clip_sphere: FloatProperty(
        name="Shadows Clip Sphere",
        description="Shadow clip sphere radius",
        default=0.5, # 0.5 to unset the value
        min=0,
        max=100
    )
    shadows_exp_factor: IntProperty(
        name="Shadow Exp Factor",
        description="Shadow exponent factor",
        default=20,
        min=0,
        max=100
    )
    shadows_extra_blur: BoolProperty(
        name="Shadow Extra Blur",
        description="Shadow extra blur",
        default=False
    )

    def from_dict(self, data: dict, is_series: bool = False):
        self.active = True if "active" in data and data["active"] == 1 else False
        self.description = data.get("description", "")
        if not is_series:
            self.mesh = data.get("mesh", None)
            position = data.get("position", (0, 0, 0))
            offset = data.get("offset", (0, 0, 0))
            self.position = offset if self.mesh else position
            if "line_from" in data:
                self.light_type = "LINE"
                self.line_from = data["line_from"]
                self.line_to = data["line_to"]
            elif "mesh" in data:
                self.light_type = "MESH"
                mesh = context.scene.objects.get(data["mesh"])
                if mesh:
                    self.mesh = mesh
                else:
                    self.mesh = None
            else:
                self.light_type = "SPOT"
        else:
            self.light_type = "SERIES"
            # TODO: handle series lights

        #shape settings
        self.modify_shape = True if "SPOT" in data else False
        self.spot = int(data.get("SPOT", 120))
        self.spot_sharpness = float(data.get("SPOT_SHARPNESS", 0.3))
        self.range = float(data.get("RANGE", 40))
        self.range_gradient_offset = float(data.get("RANGE_GRADIENT_OFFSET", 0.2))

        # color settings
        self.color = data.get("COLOR", (1, 1, 1, 1))
        self.specular_multiplier = float(data.get("SPECULAR_MULTIPLIER", 0))
        self.single_frequency = True if "SINGLE_FREQUENCY" in data and data["SINGLE_FREQUENCY"] == 1 else False
        self.diffuse_concentration = float(data.get("DIFFUSE_CONCENTRATION", 0.88))
        self.fade_at = int(data.get("FADE_AT", 400))
        self.fade_smooth = int(data.get("FADE_SMOOTH", 50))

        # condition settings
        self.condition = data.get("CONDITION", "")
        self.condition_offset = data.get("CONDITION_OFFSET", "")

        # extras
        self.volumetric_light = True if "VOLUMETRIC_LIGHT" in data and data["VOLUMETRIC_LIGHT"] == 1 else False
        self.long_specular = True if "LONG_SPECULAR" in data and data["LONG_SPECULAR"] == 1 else False
        self.skip_light_map = True if "SKIP_LIGHT_MAP" in data and data["SKIP_LIGHT_MAP"] == 1 else False
        self.disable_with_bounced_light = True if "DISABLE_WITH_BOUNCED_LIGHT" in data and data["DISABLE_WITH_BOUNCED_LIGHT"] == 1 else False
 
        # shadow settings
        self.shadows = True if "SHADOWS" in data and data["SHADOWS"] == 1 else False
        self.shadows_static = True if "SHADOWS_STATIC" in data and data["SHADOWS_STATIC"] == 1 else False
        self.shadows_half_res = True if "SHADOWS_HALF_RES" in data and data["SHADOWS_HALF_RES"] == 1 else False
        self.shadows_spot_angle = int(data.get("SHADOWS_SPOT_ANGLE", 0))
        self.shadows_range = float(data.get("SHADOWS_RANGE", 0))
        self.shadows_dir = data.get("SHADOWS_DIR", (0, 0, 0))
        self.shadows_offset = data.get("SHADOWS_OFFSET", (0, 0, 0))
        self.shadows_boost = float(data.get("SHADOWS_BOOST", 0))
        self.shadows_clip_plane = float(data.get("SHADOWS_CLIP_PLANE", 0.5))
        self.shadows_clip_sphere = float(data.get("SHADOWS_CLIP_SPHERE", 0.5))
        self.shadows_exp_factor = int(data.get("SHADOW_EXP_FACTOR", 20))
        self.shadows_extra_blur = True if "SHADOW_EXTRA_BLUR" in data and data["SHADOW_EXTRA_BLUR"] == 1 else False

    def to_dict(self) -> dict:
        data = {
            "ACTIVE": 1 if self.active else 0,
            "DESCRIPTION": self.description
        }
        if self.light_type == "SPOT":
            data["POSITION"] = self.position
        if self.light_type == "MESH":
            data["MESH"] = self.mesh
            data["OFFSET"] = self.position
        if self.light_type == "LINE":
            data["LINE_FROM"] = self.line_from if not self.line_from_helper else self.line_from_helper.location
            data["LINE_TO"] = self.line_tt if not self.line_to_helper else self.line_to_helper.location
        if self.light_type == "SERIES":
            if self.meshes:
                data["MESHES"] = [mesh.name for mesh in self.meshes]
                data['DIRECTION'] = self.direction if self.direction_mode == "FIXED" else 'NORMAL'
                if self.direction_alter:
                    data['DIRECTION_ALTER'] = self.direction_alter
                if self.direction_offset:
                    data['DIRECTION_OFFSET'] = self.direction_offset
            elif self.materials:
                data["MATERIALS"] = [material.name for material in self.materials]
            else:
                for i, position in enumerate(self.positions):
                    data[f"POSITION_{i}"] = position
                    data[f"DIRECTION_{i}"] = self.directions[i] if len(self.directions) > i else (0, -1, 0)
            data['OFFSET'] = self.position
        else:
            data["DIRECTION"] = self.direction
        if self.modify_shape:
            data["SPOT"] = self.spot
            data["SPOT_SHARPNESS"] = self.spot_sharpness
            data["RANGE"] = self.range
            data["RANGE_GRADIENT_OFFSET"] = self.range_gradient_offset
        if self.modify_color:
            data["COLOR"] = self.color
            data["SPECULAR_MULTIPLIER"] = self.specular_multiplier
            data["SINGLE_FREQUENCY"] = 1 if self.single_frequency else 0
            data["DIFFUSE_CONCENTRATION"] = self.diffuse_concentration
            data["FADE_AT"] = self.fade_at
            data["FADE_SMOOTH"] = self.fade_smooth
        if self.use_condition:
            data["CONDITION"] = self.condition
            data["CONDITION_OFFSET"] = self.condition_offset

        if self.volumetric_light:
            data["VOLUMETRIC_LIGHT"] = 1
        if self.long_specular:
            data["LONG_SPECULAR"] = 1
        if self.skip_light_map:
            data["SKIP_LIGHT_MAP"] = 1
        if self.disable_with_bounced_light:
            data["DISABLE_WITH_BOUNCED_LIGHT"] = 1

        if self.cast_shadows:
            data["SHADOWS"] = 1
            data["SHADOWS_STATIC"] = 1 if self.shadows_static else 0
            data["SHADOWS_HALF_RES"] = 1 if self.shadows_half_res else 0
            data["SHADOWS_SPOT_ANGLE"] = self.shadows_spot_angle
            data["SHADOWS_RANGE"] = self.shadows_range
            data["SHADOWS_DIR"] = self.shadows_dir
            data["SHADOWS_OFFSET"] = self.shadows_offset
            data["SHADOWS_BOOST"] = self.shadows_boost
            data["SHADOWS_CLIP_PLANE"] = self.shadows_clip_plane
            data["SHADOWS_CLIP_SPHERE"] = self.shadows_clip_sphere
            data["SHADOWS_EXP_FACTOR"] = self.shadows_exp_factor
            data["SHADOWS_EXTRA_BLUR"] = 1 if self.shadows_extra_blur else 0
        return data



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

    def from_dict(self, data: dict):
        self.sun.sun_pitch_angle = data.get("SUN_PITCH_ANGLE", 45)
        self.sun.sun_heading_angle = data.get("SUN_HEADING_ANGLE", 0)

    def to_dict(self) -> dict:
        return {
            "SUN_PITCH_ANGLE": self.sun.sun_pitch_angle,
            "SUN_HEADING_ANGLE": self.sun.sun_heading_angle
        }
