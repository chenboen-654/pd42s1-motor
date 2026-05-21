"""PD42S1 system parameter commands.

Function code map (verified against manual V1.2 §4.3):
  0x20-0x3F  Read parameter commands
  0x60-0x7F  Write parameter commands

Only commands actually used by the microscope workflow are kept.
"""

from __future__ import annotations

import struct

from ..protocol import pack_frame


# ── 0x20  Read firmware version ──
def read_firmware_version() -> bytes:
    return pack_frame(0x20)

# ── 0x21  Read flux (mWb) ──
def read_flux() -> bytes:
    return pack_frame(0x21)

# ── 0x22  Read resistance & inductance ──
def read_resistance_inductance() -> bytes:
    return pack_frame(0x22)

# ── 0x23  Read current (mA) ──
def read_current() -> bytes:
    return pack_frame(0x23)

# ── 0x24  Read voltage (V) ──
def read_voltage() -> bytes:
    return pack_frame(0x24)

# ── 0x29  Read speed (RPM) ──
def read_speed_rpm() -> bytes:
    return pack_frame(0x29)

# ── 0x2A  Read position ──
def read_position() -> bytes:
    return pack_frame(0x2A)

# ── 0x2C  Read motor running status ──
def read_motor_status() -> bytes:
    return pack_frame(0x2C)

# ── 0x2F  Read enable state ──
def read_enabled_state() -> bytes:
    return pack_frame(0x2F)

# ── 0x31  Read all system parameters ──
def read_all_status() -> bytes:
    return pack_frame(0x31)

# ── 0x32  Read/write motor drive parameters (45 bytes) ──
def read_motor_params() -> bytes:
    return pack_frame(0x32)

def write_motor_params(params: bytes) -> bytes:
    data = bytes([0x01]) + params
    return pack_frame(0x32, data)

# ── 0x60  Read/write device address ──
def read_device_address() -> bytes:
    return pack_frame(0x60, bytes([0x01]))

def write_device_address(addr: int) -> bytes:
    data = bytes([0x01, addr])
    return pack_frame(0x60, data)

# ── 0x61  Read/write multi-axis sync group ──
def read_sync_group() -> bytes:
    return pack_frame(0x61, bytes([0x02]))

def write_sync_group(group: int) -> bytes:
    data = bytes([0x01, group])
    return pack_frame(0x61, data)

# ── 0x62  Read/write work mode (0=closed-loop pos, 1=open-loop, 2=torque) ──
def read_work_mode() -> bytes:
    return pack_frame(0x62, bytes([0x02]))

def write_work_mode(mode: int) -> bytes:
    data = bytes([0x01, mode])
    return pack_frame(0x62, data)

# ── 0x63  Set position-loop PID parameters ──
def write_position_pid(p: int, i: int, d: int) -> bytes:
    data = struct.pack(">III", p, i, d)
    return pack_frame(0x63, data)

# ── 0x65  Read/write microstep resolution (1~256) ──
def read_microstep() -> bytes:
    return pack_frame(0x65, bytes([0x00]))

def write_microstep(divisor: int) -> bytes:
    data = struct.pack(">H", divisor)
    return pack_frame(0x65, data)

# ── 0x66  Set target current (mA, range -3000~3000) ──
def write_run_current(current_ma: int) -> bytes:
    data = struct.pack(">h", current_ma)
    return pack_frame(0x66, data)

# ── 0x67  Read/write serial baudrate ──
def read_serial_baudrate() -> bytes:
    return pack_frame(0x67, bytes([0x00]))

def write_serial_baudrate(baud: int) -> bytes:
    data = struct.pack(">I", baud)
    return pack_frame(0x67, data)

# ── 0x68  Read/write CAN baudrate ──
def read_can_baudrate() -> bytes:
    return pack_frame(0x68, bytes([0x01]))

def write_can_baudrate(kbps: int) -> bytes:
    data = struct.pack(">H", kbps)
    return pack_frame(0x68, data)

# ── 0x6D  Read/write direction ──
def read_direction() -> bytes:
    return pack_frame(0x6D, bytes([0x01]))

def write_direction(dir_: int) -> bytes:
    data = bytes([0x01, dir_])
    return pack_frame(0x6D, data)

# ── 0x6E  Read/write enable mode ──
def read_enable_mode() -> bytes:
    return pack_frame(0x6E, bytes([0x01]))

def write_enable_mode(mode: int) -> bytes:
    data = bytes([0x01, mode])
    return pack_frame(0x6E, data)
