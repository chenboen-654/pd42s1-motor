"""PD42S1 advanced function commands (§4.5)."""

from __future__ import annotations

import struct

from ..protocol import pack_frame


# ── 4.5.1  0x90  Read/write encoder offset ──
def read_encoder_offset() -> bytes:
    return pack_frame(0x90)

def write_encoder_offset(offset: int) -> bytes:
    return pack_frame(0x90, struct.pack(">i", offset))


# ── 4.5.2  0x91  Auto PID tune ──
def cmd_auto_pid_tune(mode: int, enable: int, speed_rpm: int, current_ma: int) -> bytes:
    data = struct.pack(">BBHi", mode, enable,
                       speed_rpm, current_ma)
    return pack_frame(0x91, data)


# ── 4.5.3  0x92  Read/write PID mode ──
def read_pid_mode() -> bytes:
    return pack_frame(0x92, bytes([0x01]))

def write_pid_mode(mode: int) -> bytes:
    data = bytes([0x01, mode])
    return pack_frame(0x92, data)


# ── 4.5.4  0x93  Save user parameters ──
def cmd_save_user_params() -> bytes:
    return pack_frame(0x93)


# ── 4.5.5  0x94  Read position tracking ──
def read_position_tracking() -> bytes:
    return pack_frame(0x94)


# ── 4.5.6  0x95  Read/write timeout ──
def read_timeout() -> bytes:
    return pack_frame(0x95)

def write_timeout(timeout_ms: int) -> bytes:
    return pack_frame(0x95, struct.pack(">I", timeout_ms))


# ── 4.5.7  0x96  Read alarm state ──
def read_alarm_state() -> bytes:
    return pack_frame(0x96)


# ── 4.5.8  0x97  Clear alarm (v2) ──
def cmd_clear_alarm_v2() -> bytes:
    return pack_frame(0x97, bytes([0x01]))


# ── 4.5.9  0x98  Read/write target position ──
def read_target_position() -> bytes:
    return pack_frame(0x98)

def write_target_position(pos: int) -> bytes:
    return pack_frame(0x98, struct.pack(">i", pos))


# ── 4.5.10 0x99  Read/write encoder direction ──
def read_encoder_dir() -> bytes:
    return pack_frame(0x99, bytes([0x01]))

def write_encoder_dir(dir_: int) -> bytes:
    data = bytes([0x01, dir_])
    return pack_frame(0x99, data)
