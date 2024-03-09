# directories
DATA_DIR = 'data/'
UI_DIR = 'ui/'

# Surface Regex
SURFACE_REGEX = r"^(\d*)([A-Z]+)_?(.*)$"
SURFACE_OBJECT_REGEX = r"^\d*[A-Z]+_?(.*)$"
SURFACE_VALID_KEY = r"^[A-Z_]+$"

# Physics Regex
WALL_REGEX = r"^\d+WALL_(.*)$"
PHYSICS_OBJECT_REGEX = r"^AC_POBJECT_(.*)$"
AUDIO_SOURCE_REGEX = r"^AC_AUDIO_(.*)$"

# Race Logic Regex
START_CIRCUIT_REGEX = r"^AC_START_\d+$"
START_AB_L_REGEX = r"^AC_AB_START_L$"
START_AB_R_REGEX = r"^AC_AB_START_R$"
FINISH_AB_L_REGEX = r"^AC_AB_FINISH_L$"
FINISH_AB_R_REGEX = r"^AC_AB_FINISH_R$"
PIT_BOX_REGEX = r"^AC_PIT_\d+$"
AC_TIME_L_REGEX = r"^AC_TIME_\d+_L$"
AC_TIME_R_REGEX = r"^AC_TIME_\d+_R$"
