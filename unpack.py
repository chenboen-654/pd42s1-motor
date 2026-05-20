"""
PD42S1 response data unpack helpers.

Provides typed accessors for big-endian binary data embedded in
PD42S1 response frames (float32, int16, uint16, int32, uint32).
"""

from __future__ import annotations

import struct


def unpack_float_be(buf: bytes, offset: int = 0) -> float:
    """4 bytes → float (big-endian, STM32 format)."""
    return struct.unpack(">f", buf[offset:offset + 4])[0]


def unpack_int16_be(buf: bytes, offset: int = 0) -> int:
    """2 bytes → signed 16-bit int (big-endian)."""
    return struct.unpack(">h", buf[offset:offset + 2])[0]


def unpack_uint16_be(buf: bytes, offset: int = 0) -> int:
    """2 bytes → unsigned 16-bit int."""
    return struct.unpack(">H", buf[offset:offset + 2])[0]


def unpack_int32_be(buf: bytes, offset: int = 0) -> int:
    """4 bytes → signed 32-bit int (big-endian)."""
    return struct.unpack(">i", buf[offset:offset + 4])[0]


def unpack_uint32_be(buf: bytes, offset: int = 0) -> int:
    """4 bytes → unsigned 32-bit int."""
    return struct.unpack(">I", buf[offset:offset + 4])[0]


def hex_str(data: bytes) -> str:
    """Bytes → space-separated uppercase hex, for UI display."""
    return " ".join(f"{b:02X}" for b in data)
