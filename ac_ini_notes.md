## notes

### structure

map.png : the map of the track

/ai : contains various configuration files for the AI

/texture : contains various texture files for the track

/ui : contains various configuration files for the user interface

- ui_track.json : defines details for the track selection screen
  - name (string) : the name of the track
  - description (string) : the description of the track
  - tags (string[]) : tags to describe the track (location, modes, features, etc.)
  - geotags (string[]) : geographical tags to describe the track (lat, lon, etc.)
  - country (string) : the country of the track
  - city (string) : the city of the track
  - length (float) : the length of the track
  - width (float) : the width of the track lanes
  - pitboxes (int) : the number of pitboxes available
  - run (string) : the run direction of the track (clockwise, anticlockwise, etc.)
- outline.png : the outline of the track
- preview.png : the preview image of the track

/data : contains various configuration files and generic data

- surfaces.ini : contains data for custom surface definitions
  - [SURFACE_NAME]
    - KEY (string) : the label expected in the object name to trigger the surface
    - FRICTION (float) : the friction coefficient (how well the object maintains control on the surface)
    - DAMPING (float) : the damping coefficient (how much energy is lost when colliding with the surface)
    - WAV (string) : the sound file to play when colliding with the surface (optional)
    - WAV_PITCH (float) : the pitch of the sound file to play when colliding with the surface (optional)
    - FF_EFFECT (string | NULL) : the force feedback effect to play when colliding with the surface (optional)
    - DIRT_ADDITIVE (float) : the dirt additive texture to apply when colliding with the surface (optional)
    - IS_VALID_TRACK (tinyint) : whether the surface is a valid track surface (optional)
    - BLACK_FLAG_TIME (float) : the time in seconds before a black flag is triggered when driving on the surface (optional)
    - SIN_HEIGHT (float) : the height of the sine wave to apply to the surface (optional)
    - SIN_LENGTH (float) : the length of the sine wave to apply to the surface (optional)
    - IS_PITLANE (tinyint) : whether the surface is a pitlane surface (optional)
    - VIBRATION_GAIN (float) : the gain of the vibration to apply when colliding with the surface (optional)
    - VIBRATION_LENGTH (float) : the length of the vibration to apply when colliding with the surface (optional)
- overlays.ini : contains data for checkpoint regions of the track
  - [MAIN] : the main configuration settings
    - OVERLAYS_COUNT (int) : the number of overlays to define
  - [CHECKPOINT_#]
    - WORLD_POSITION (float[]) : the world position of the checkpoint
    - OFFSET (float[]) : the offset of the checkpoint
    - WIDTH (float) : the width of the checkpoint
    - HEIGHT (float) : the height of the checkpoint
    - ORIENTATION (float) : the orientation of the checkpoint
- sections.ini : contains data related to track section labels
  - [SECTION_#]
    - IN (float) : the start position of the section banner by percentage of the track length
    - OUT (float) : the end position of the section banner by percentage of the track length
    - TEXT (string) : the text to display for the section
- lighting.ini : contains data related to the track lighting
  - [LIGHTING]
    - SUN_PITCH_ANGLE (int) : the pitch angle of the sun
    - SUN_HEADING_ANGLE (int) : the heading angle of the sun
- crew.ini : contains data related to the pit crew
  - [HEADER]
    - SIDE (int) : the side of the pit crew (1 = left, -1 = right)
- cameras.ini : contains data related to the cameras during a session
  - [HEADER]
    - VERSION (int) : the version of the cameras
    - CAMERAS_COUNT (int) : the number of cameras to define
    - SET_NAME (string) : the name of the camera set to identify what screen the cameras are for
  - [CAMERA_#]
    - NAME (string) : the name of the camera
    - POSITION (float[]) : the position of the camera
    - FORWARD (float[]) : the forward vector of the camera
    - UP (float[]) : the up vector of the camera
    - MIN_FOV (float) : the minimum field of view of the camera
    - MAX_FOV (float) : the maximum field of view of the camera
    - IN_POINT (float) : the in point of the camera by percentage of the track length
    - OUT_POINT (float) : the out point of the camera by percentage of the track length
    - SHADOW_SPLIT# (float) : the shadow split of the camera
    - NEAR_PLANE (float) : the near plane of the camera
    - FAR_PLANE (float) : the far plane of the camera
    - MIN_EXPOSURE (float) : the minimum exposure of the camera
    - MAX_EXPOSURE (float) : the maximum exposure of the camera
    - DOF_FACTOR (float) : the depth of field factor of the camera
    - DOF_RANGE (float) : the depth of field range of the camera
    - DOF_FOCUS (float) : the depth of field focus of the camera
    - DOF_MANUAL (tinyint) : whether the depth of field focus is manual or automatic
    - SPLINE (csv) : the spline data of the camera
    - SPLIE_ANIMATION_LENGTH (float) : the spline animation length of the camera
      -IS_FIXED (tinyint) : whether the camera is fixed or not
- camera_facing.ini : contains data related to billboards that always face the camera
  - [CAMERA_FACING_#]
    - SURFACE (string) : the surface to apply the billboards to
    - ELEMENTS (int) : the number of elements to spawn on the surface
    - SIZE (float[]) : the size of the billboards
    - TEXTURE (string) : the texture of the billboards
    - TEXTURE_ROWS (int) : the number of rows of to create
    - TEXTURE_COLUMNS (int) : the number of columns to create
    - SHADED (tinyint) : whether the billboards are shaded or not
    - DIFFUSE (float[]) : the diffuse color of the billboards
    - AMBIENT (float[]) : the ambient color of the billboards
- audio_sources.ini : contains data related to audio emitters and sound modifiers
  - [(EFFECT)_#] : (ie: REVERB)
    - ENABLED (tinyint) : whether the effect is enabled or not
    - NODE (string) : the node to apply the effect to
    - MINDISTANCE (int) : the minimum distance of the effect to be audible
    - MAXDISTANCE (int) : the maximum distance of the effect to be audible
    - PRESET (string) : the preset to apply to the effect
    - DECAY_TIME (int) : the decay time of the effect
    - EARLY_DELAY (int) : the early delay of the effect
    - LATE_DELAY (int) : the late delay of the effect
    - DIFFUSION (int) : the diffusion of the effect
    - DENSITY (int) : the density of the effect
    - LOW_SHELF_FREQUENCY (int) : the low shelf frequency of the effect
    - LOW_SHELF_GAIN (int) : the low shelf gain of the effect
    - HIGH_CUT (int) : the high cut of the effect
    - EARLY_LATE_MIX (int) : the early late mix of the effect
    - WET_LEVEL (int) : the wet level of the effect

### Element Naming Conventions

> Assets within a map should be named based on their purpose. General graphic
> elements do no require and special names, but anything intended for collision,
> impacting driving, or triggering some aspect of the race logic should be named
> according to the following conventions:

- 3D Asset naming convention: `ID``TYPE``_OPTIONAL`
  - ID (int) : a unique identifier for the asset
  - TYPE (string) : the type of asset (ie: WALL, ROAD, GRASS, etc.)
  - \_OPTIONAL (string) : any optional data to help identify the asset (ie: house, tree, fence, flag, traffic_light, etc.)
- Spawn and Race Logic naming conventions:
  - `AC_START_#` : the starting grid positions
  - `AC_PIT_#` : the pitlane positions
  - `AC_HOTLAP_START_#` : the hotlap starting positions
  - `AC_TIME_#_L` : the time trial starting positions (left)
  - `AC_TIME_#_R` : the time trial starting positions (right)
  - `AC_AB_START_L` : the starting positions for the AB challenge (left)
  - `AC_AB_START_R` : the starting positions for the AB challenge (right)
  - `AC_AB_FINISH_L` : the finishing positions for the AB challenge (left)
  - `AC_AB_FINISH_R` : the finishing positions for the AB challenge (right)
- Goodies:
  - `AC_POBJECT_SUFFIX` : defines the object as a physics object
    - suffix is optional, but helps to define unique names
    - it's recommended to limit the number of physics objects as much as possible
  - `AC_AUDIO_SUFFIX` : defines the object as an audio emitter
    - suffix is optional, but helps define the type of sound to emit
    - audio emitters should be configured in the `audio_sources.ini` file

#### Default Types

- `WALL` : a solid barrier, typically used to define the track boundaries, shoul be simple and low poly
- `ROAD` : the main driving surface of the track, should be smooth and have a high (0.95+) friction coefficient
- `GRASS` : the off-road surface of the track, should be bumpy and have a mid (0.6+) friction coefficient
- `SAND` : the off-road surface of the track, should be bumpy and have a low (0.4+) friction coefficient
- `KERB` : the raised edge of the track, should be smooth and have a high (0.9+) friction coefficient

Additional types can be added to the `surfaces.ini` file to define custom surfaces. A default PIT surface is not provided.
So, it would be best to define a custom surface for the pitlane for every project in the `surfaces.ini` file.

#### Race Logic Nodes

All logic nodes should be placed a 1 or 2 meters above the ground to avoid any issues with the collision detection.

It's important to remember that the local rotation of the nodes is used to determine the forward direction of the node.
In the case of the starting grid, the forward direction is used to determine the direction of the grid slot.
In the case of the pitlane, the forward direction is used to determine the direction of the pitlane slot as well as the
position of the pit crew.

For nodes with either L or R, the forward direction is asserted based on the position of the nodes.

It's best to use empty nodes for race logic nodes since they should not be visible in the game.

### Exporting

When exporting a track, it's important to use the following settings to ensure compatibility with Assetto Corsa:

- Geometry Settings:
  - triangulate faces
- Units: meters
- Axis Conversion:
  - up: +Y
  - forward: +Z
- Format: FBX
