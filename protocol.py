"""
PD42S1 native protocol — low-level frame packing/unpacking.

Protocol format (Section 4 of the manual):
  Request:  [0xC5][addr][cmd][data...][checksum][0x5C]
  Response: [0xC5][addr][cmd][data...][checksum][0x5C]

  - checksum = sum(all bytes before checksum) & 0xFF
  - footer   = 0x5C

Read commands (no data bytes):
  -> C5 01 <cmd> <checksum> 5C

Write commands (Byte1 = 0x01 = write):
  -> C5 01 <cmd> 01 <data...> <checksum> 5C

Response (Byte1 = status, 0x01 = success):
  <- C5 01 <cmd> 01 <data...> <checksum> 5C
"""

from __future__ import annotations

from typing import Optional

# Re-export unpack helpers for backward compatibility
from .unpack import (
    unpack_float_be, unpack_int16_be, unpack_uint16_be,
    unpack_int32_be, unpack_uint32_be, hex_str,
)


PROTOCOL_HEADER = 0xC5
PROTOCOL_FOOTER = 0x5C
PROTOCOL_ADDR = 0x01  # default device address

# ── Status / error codes (from manual §4.2.1) ──
STATUS_OK = 0x01
STATUS_LENGTH_ERR = 0xE1          #  frame length insufficient
STATUS_HEADER_ERR = 0xE2          #  header error (not 0xC5)
STATUS_FOOTER_ERR = 0xE3          #  footer error (not 0x5C)
STATUS_CHECKSUM_ERR = 0xE4        #  checksum error
STATUS_UNSUPPORTED = 0xE5         #  unsupported function code
STATUS_INVALID_DATA = 0xE6        #  invalid data

# ── Control mode constants (§4.3.22, 0x62) ──
MODE_OPEN_LOOP = 0
MODE_CLOSED_LOOP = 1
MODE_TORQUE = 2

# ── Motor status constants (§4.3.13, 0x2C) ──
MOTOR_STOPPED    = 0  # 停止状态
MOTOR_COMPLETED  = 1  # 完成任务状态
MOTOR_RUNNING    = 2  # 正在运行
MOTOR_OVERLOAD   = 3  # 过载状态
MOTOR_STALLED    = 4  # 堵转状态
MOTOR_UNDERVOLT  = 5  # 欠压状态

# ── Direction constants ──
DIR_CW = 0   # clockwise (or positive)
DIR_CCW = 1  # counter-clockwise (or negative)

# ── Enable mode constants (§4.3.34) ──
EN_ALWAYS = 0
EN_ON_CMD = 1
EN_ON_PULSE = 2

# ── Microstep divisor presets ──
MICROSTEP_1 = 1
MICROSTEP_2 = 2
MICROSTEP_4 = 4
MICROSTEP_8 = 8
MICROSTEP_16 = 16
MICROSTEP_32 = 32
MICROSTEP_64 = 64
MICROSTEP_128 = 128
MICROSTEP_256 = 256

# ── Baud rate index map (§4.3.22) ──
BAUD_INDEX_MAP = {
    9600: 0, 19200: 1, 38400: 2, 57600: 3,
    115200: 4, 230400: 5, 460800: 6, 921600: 7,
}
BAUD_RATE_MAP = {v: k for k, v in BAUD_INDEX_MAP.items()}


# ── Checksum ──────────────────────────────────────────────────────

def calc_checksum(data: bytes) -> int:
    """8-bit checksum: sum of all bytes & 0xFF."""
    return sum(data) & 0xFF


# ── Frame packing ─────────────────────────────────────────────────

def pack_frame(cmd: int, data: bytes = b"", addr: int = PROTOCOL_ADDR) -> bytes:
    """Build a complete PD42S1 command frame.

    Args:
        cmd:    Command code (e.g. 0xF2 for absolute move).
        data:   Payload bytes (empty for read commands).
        addr:   Device address (default 0x01).

    Returns:
        Complete frame bytes including header, checksum, and footer.

    Example:
        Read position (0x2A):
          >>> pack_frame(0x2A).hex()
          'c5012af05c'

        Absolute move to position 51200 (+1 rev, 1000 RPM):
          >>> pack_frame(0xF2, bytes([0, 100, 0x03, 0xE8, 0x00, 0x01, 0x00, 0x00]))
    """
    header = bytes([PROTOCOL_HEADER, addr & 0xFF, cmd & 0xFF])
    payload = header + data
    checksum = calc_checksum(payload)
    return payload + bytes([checksum, PROTOCOL_FOOTER])


# ── Frame parsing ─────────────────────────────────────────────────

class PD42S1Frame:
    """Parsed PD42S1 response frame.

    Properties:
        valid:      True if checksum and framing are correct.
        addr:       Device address.
        cmd:        Command echo.
        status:     Status byte (0x01 = OK, 0xE1..0xE6 = error).
        data:       Payload bytes after status byte.
        is_error:   True if status indicates an error.
        error_name: Human-readable error description.
    """

    ERROR_NAMES = {
        0xE1: "Frame length insufficient",
        0xE2: "Header error (not 0xC5)",
        0xE3: "Footer error (not 0x5C)",
        0xE4: "Checksum error",
        0xE5: "Unsupported function code",
        0xE6: "Invalid data",
    }

    def __init__(self, raw: bytes):
        self.raw = raw
        self.valid = False
        self.addr: int = 0
        self.cmd: int = 0
        self.status: int = 0
        self.data: bytes = b""
        self._parse()

    @property
    def is_error(self) -> bool:
        return self.valid and self.status in (
            STATUS_LENGTH_ERR, STATUS_HEADER_ERR, STATUS_FOOTER_ERR,
            STATUS_CHECKSUM_ERR, STATUS_UNSUPPORTED, STATUS_INVALID_DATA,
        )

    @property
    def error_name(self) -> str:
        return self.ERROR_NAMES.get(self.status, f"Unknown error 0x{self.status:02X}")

    def _parse(self):
        if len(self.raw) < 4:
            return
        if self.raw[0] != PROTOCOL_HEADER:
            return
        if self.raw[-1] != PROTOCOL_FOOTER:
            return
        self.addr = self.raw[1]
        self.cmd = self.raw[2]
        # data is between byte 3 and checksum byte
        chk_idx = len(self.raw) - 2
        self.data = self.raw[3:chk_idx]
        # verify checksum
        expected_chk = calc_checksum(self.raw[:chk_idx])
        actual_chk = self.raw[chk_idx]
        if expected_chk != actual_chk:
            return
        if len(self.data) >= 1:
            self.status = self.data[0]
        self.valid = True

    def __repr__(self) -> str:
        return (f"PD42S1Frame(valid={self.valid}, addr=0x{self.addr:02X}, "
                f"cmd=0x{self.cmd:02X}, status=0x{self.status:02X}, "
                f"data={self.data.hex()})")


def parse_response(raw: bytes) -> Optional[PD42S1Frame]:
    """Parse a raw response frame, returning None on failure."""
    frame = PD42S1Frame(raw)
    return frame if frame.valid else None
