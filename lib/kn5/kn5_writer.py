from __future__ import annotations

import struct
from typing import BinaryIO

ENCODING = 'utf-8'


class KN5Writer:
    """Base class for writing KN5 binary format primitives."""

    def __init__(self, file: BinaryIO):
        self.file = file

    def write_string(self, string: str) -> None:
        """Write length-prefixed UTF-8 string."""
        string_bytes = string.encode(ENCODING)
        self.write_uint(len(string_bytes))
        self.file.write(string_bytes)

    def write_blob(self, blob: bytes) -> None:
        """Write length-prefixed binary blob."""
        self.write_uint(len(blob))
        self.file.write(blob)

    def write_uint(self, int_val: int) -> None:
        """Write unsigned 32-bit integer."""
        self.file.write(struct.pack("I", int_val))

    def write_int(self, int_val: int) -> None:
        """Write signed 32-bit integer."""
        self.file.write(struct.pack("i", int_val))

    def write_ushort(self, short: int) -> None:
        """Write unsigned 16-bit integer."""
        self.file.write(struct.pack("H", short))

    def write_byte(self, byte: int) -> None:
        """Write unsigned 8-bit integer."""
        self.file.write(struct.pack("B", byte))

    def write_bool(self, bool_val: bool) -> None:
        """Write boolean as single byte."""
        self.file.write(struct.pack("?", bool_val))

    def write_float(self, f: float) -> None:
        """Write 32-bit float."""
        self.file.write(struct.pack("f", f))

    def write_vector2(self, vector2: tuple[float, float]) -> None:
        """Write 2D vector (2 floats)."""
        self.file.write(struct.pack("2f", *vector2))

    def write_vector3(self, vector3: tuple[float, float, float]) -> None:
        """Write 3D vector (3 floats)."""
        self.file.write(struct.pack("3f", *vector3))

    def write_vector4(self, vector4: tuple[float, float, float, float]) -> None:
        """Write 4D vector (4 floats)."""
        self.file.write(struct.pack("4f", *vector4))

    def write_matrix(self, matrix) -> None:
        """
        Write 4x4 matrix in column-major order.

        Args:
            matrix: Blender Matrix object (4x4)
        """
        for row in range(4):
            for col in range(4):
                self.write_float(matrix[col][row])
