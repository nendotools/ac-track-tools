# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####
from bpy.utils import register_class, unregister_class

from . import lib
from .lib.preferences import AC_Preferences
from .utils.properties import ExtensionCollection, KeyValuePair

bl_info = {
    "name": "Assetto Corsa Configurator",
    "description":
        "Track configuration tool for easier management of assets, nodes, and"
        "track settings intended to speed up track development",
    "author": "NENDO",
    "version": (0, 4, 3),
    "blender": (2, 93, 0),
    "location": "View3D > Tools > Assetto Corsa: Track",
    "warning": "",
    "doc_url": "",
    "tracker_url": "https://github.com/nendotools/touchview/issues",
    "category": "3D View",
}


def register():
    register_class(AC_Preferences)
    register_class(KeyValuePair)
    register_class(ExtensionCollection)
    lib.register()

def unregister():
    lib.unregister()
    unregister_class(ExtensionCollection)
    unregister_class(KeyValuePair)
    unregister_class(AC_Preferences)
