"""PD42S1 system parameter commands (§4.3)."""

from __future__ import annotations

import struct

from ..protocol import pack_frame


# ── 4.3.1  0x20  Read firmware version ──
def read_firmware_version() -> bytes:
    return pack_frame(0x20)

# ── 4.3.2  0x21  Read flux (mWb) ──
def read_flux() -> bytes:
    return pack_frame(0x21)

# ── 4.3.3  0x22  Read resistance & inductance ──
def read_resistance_inductance() -> bytes:
    return pack_frame(0x22)

# ── 4.3.4  0x23  Read current (mA) ──
def read_current() -> bytes:
    return pack_frame(0x23)

# ── 4.3.5  0x24  Read voltage (V) ──
def read_voltage() -> bytes:
    return pack_frame(0x24)

# ── 4.3.6  0x25  Read PID (float) ──
def read_pid_float() -> bytes:
    return pack_frame(0x25)

# ── 4.3.7  0x26  Read PID (uint32) ──
def read_pid_uint32() -> bytes:
    return pack_frame(0x26)

# ── 4.3.8  0x27  Write PID (uint32) ──
def write_pid_uint32(pid_p: int, pid_i: int, pid_d: int) -> bytes:
    data = bytes([0x01]) + struct.pack(">III", pid_p, pid_i, pid_d)
    return pack_frame(0x27, data)

# ── 4.3.9  0x28  Read encoder resolution ──
def read_encoder_resolution() -> bytes:
    return pack_frame(0x28)

# ── 4.3.10 0x29  Read speed (RPM) ──
def read_speed_rpm() -> bytes:
    return pack_frame(0x29)

# ── 4.3.11 0x2A  Read position ──
def read_position() -> bytes:
    return pack_frame(0x2A)

# ── 4.3.12 0x2B  Write position ──
def write_position(pos: int) -> bytes:
    data = bytes([0x01]) + struct.pack(">i", pos)
    return pack_frame(0x2B, data)

# ── 4.3.13 0x2C  Read control mode ──
def read_control_mode() -> bytes:
    return pack_frame(0x2C)

# ── 4.3.14 0x2D  Write control mode ──
def write_control_mode(mode: int) -> bytes:
    data = bytes([0x01, mode])
    return pack_frame(0x2D, data)

# ── 4.3.15 0x2E  Read run current ──
def read_run_current() -> bytes:
    return pack_frame(0x2E)

# ── 4.3.16 0x2F  Write run current (mA) ──
def write_run_current(current_ma: int) -> bytes:
    data = struct.pack(">Bh", 0x01, current_ma)
    return pack_frame(0x2F, data)

# ── 4.3.17 0x30  Read enable state ──
def read_enable_state() -> bytes:
    return pack_frame(0x30)

# ── 4.3.18 0x31  Read all status ──
def read_all_status() -> bytes:
    return pack_frame(0x31)

# ── 4.3.19 0x32  Read/write motor parameters (45 bytes) ──
def read_motor_params() -> bytes:
    return pack_frame(0x32)

def write_motor_params(params: bytes) -> bytes:
    data = bytes([0x01]) + params
    return pack_frame(0x32, data)

# ── 4.3.20 0x60  Read/write device address ──
def read_device_address() -> bytes:
    return pack_frame(0x60, bytes([0x01]))

def write_device_address(addr: int) -> bytes:
    data = bytes([0x01, addr])
    return pack_frame(0x60, data)

# ── 4.3.21 0x61  Read/write multi-axis sync group ──
def read_sync_group() -> bytes:
    return pack_frame(0x61, bytes([0x02]))

def write_sync_group(group: int) -> bytes:
    data = bytes([0x01, group])
    return pack_frame(0x61, data)

# ── 4.3.22 0x62  Read/write serial baudrate (index) ──
def read_baudrate() -> bytes:
    return pack_frame(0x62, bytes([0x01]))

def write_baudrate(baud_index: int) -> bytes:
    data = bytes([0x01, baud_index])
    return pack_frame(0x62, data)

# ── 4.3.23 0x63  Read/write PID (velocity) ──
def read_velocity_pid() -> bytes:
    return pack_frame(0x63)

def write_velocity_pid(pid_p: int, pid_i: int, pid_d: int) -> bytes:
    data = bytes([0x01]) + struct.pack(">III", pid_p, pid_i, pid_d)
    return pack_frame(0x63, data)

# ── 4.3.24 0x64  Read/write current limit ──
def read_current_limit() -> bytes:
    return pack_frame(0x64, bytes([0x00]))

def write_current_limit(current_ma: int) -> bytes:
    data = struct.pack(">H", current_ma)
    return pack_frame(0x64, data)

# ── 4.3.25 0x65  Read/write microstep resolution ──
def read_microstep() -> bytes:
    return pack_frame(0x65, bytes([0x00]))

def write_microstep(divisor: int) -> bytes:
    data = struct.pack(">BH", 0x01, divisor)
    return pack_frame(0x65, data)

# ── 4.3.26 0x66  Read/write holding current ──
def read_holding_current() -> bytes:
    return pack_frame(0x66, bytes([0x00]))

def write_holding_current(current_ma: int) -> bytes:
    data = struct.pack(">h", current_ma)
    return pack_frame(0x66, data)

# ── 4.3.27 0x67  Read/write serial baudrate (value) ──
def read_serial_baudrate() -> bytes:
    return pack_frame(0x67, bytes([0x00]))

def write_serial_baudrate(baud: int) -> bytes:
    data = struct.pack(">BI", 0x01, baud)
    return pack_frame(0x67, data)

# ── 4.3.28 0x68  Read/write CAN baudrate ──
def read_can_baudrate() -> bytes:
    return pack_frame(0x68, bytes([0x01]))

def write_can_baudrate(kbps: int) -> bytes:
    data = struct.pack(">BH", 0x01, kbps)
    return pack_frame(0x68, data)

# ── 4.3.33 0x6D  Read/write direction ──
def read_direction() -> bytes:
    return pack_frame(0x6D, bytes([0x01]))

def write_direction(dir_: int) -> bytes:
    data = bytes([0x01, dir_])
    return pack_frame(0x6D, data)

# ── 4.3.34 0x6E  Read/write enable mode ──
def read_enable_mode() -> bytes:
    return pack_frame(0x6E, bytes([0x01]))

def write_enable_mode(mode: int) -> bytes:
    data = bytes([0x01, mode])
    return pack_frame(0x6E, data)

# ── 4.3.35 0x6F  Save parameters to flash ──
def save_params() -> bytes:
    return pack_frame(0x6F, bytes([0x01]))

# ── 4.3.36 0x70  Reset motor ──
def reset_motor() -> bytes:
    return pack_frame(0x70, bytes([0x01]))

# ── 4.3.37 0x71  Restore factory defaults ──
def restore_defaults() -> bytes:
    return pack_frame(0x71, bytes([0x01]))

# ── 4.3.38 0x72  IO control ──
def read_io() -> bytes:
    return pack_frame(0x72, bytes([0x01]))

def write_io(state: int) -> bytes:
    data = bytes([0x01, state])
    return pack_frame(0x72, data)

# ── 4.3.39 0x73  Read/write PID (position) ──
def read_position_pid() -> bytes:
    return pack_frame(0x73)

def write_position_pid(pid_p: int, pid_i: int, pid_d: int) -> bytes:
    data = bytes([0x01]) + struct.pack(">III", pid_p, pid_i, pid_d)
    return pack_frame(0x73, data)
