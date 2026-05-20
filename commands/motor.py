"""PD42S1 motor control commands (§4.4).

Corrected per user manual V1.2:
  0xF0 = 力矩模式 (方向 + 电流)
  0xF1 = 速度模式 (方向 + 加速度 + 速度)
  0xF2 = 绝对位置模式 (方向 + 加速度 + 速度 + 绝对位置)
  0xF3 = 相对位置模式 (方向 + 加速度 + 速度 + 相对步数)
"""

from __future__ import annotations

import struct

from ..protocol import pack_frame


# ── 4.4.1  0xF0  力矩模式 ──
def cmd_torque_mode(direction: int, current_ma: int) -> bytes:
    """direction: 0=正转, 1=反转; current_ma: 0~3000 mA"""
    data = struct.pack(">BH", direction, current_ma)
    return pack_frame(0xF0, data)


# ── 4.4.2  0xF1  速度模式 ──
def cmd_speed_mode(direction: int, accel: int, speed_rpm: float) -> bytes:
    """direction: 0=正转, 1=反转; accel: 0~200; speed_rpm: 0.1~6000 RPM (float32)"""
    data = struct.pack(">BBf", direction, accel, speed_rpm)
    return pack_frame(0xF1, data)


# ── 4.4.3  0xF2  绝对位置模式 ──
def cmd_move_absolute(direction: int, accel: int, speed_rpm: int, position: int) -> bytes:
    """direction: 0=正转, 1=反转; accel: 0~200; speed_rpm: 0~6000; position: uint32 (51200/转)"""
    data = struct.pack(">BBHI", direction, accel, speed_rpm, position)
    return pack_frame(0xF2, data)


# ── 4.4.4  0xF3  相对位置模式 ──
def cmd_move_relative(direction: int, accel: int, speed_rpm: int, steps: int) -> bytes:
    """direction: 0=正转, 1=反转; accel: 0~200; speed_rpm: 0~6000; steps: uint32 (51200/转)"""
    data = struct.pack(">BBHI", direction, accel, speed_rpm, steps)
    return pack_frame(0xF3, data)


# ── 4.4.5  0xF4  Stop ──
def cmd_stop() -> bytes:
    return pack_frame(0xF4)


# ── 4.4.6  0xF5  STP PWM position mode ──
def cmd_stp_pwm_position(pulse_on: int, pulse_off: int,
                         pos_at_pulse_on: int, pos_at_pulse_off: int) -> bytes:
    data = struct.pack(">HHii",
                       pulse_on, pulse_off,
                       pos_at_pulse_on, pos_at_pulse_off)
    return pack_frame(0xF5, data)


# ── 4.4.7  0xF6  STP PWM current mode ──
def cmd_stp_pwm_current(pulse_low: int, pulse_high: int,
                        current_low: int, current_high: int) -> bytes:
    data = struct.pack(">HHii",
                       pulse_low, pulse_high,
                       current_low, current_high)
    return pack_frame(0xF6, data)


# ── 4.4.8  0xF7  STP PWM speed mode ──
def cmd_stp_pwm_speed(pulse_low: int, pulse_high: int,
                      speed_low: int, speed_high: int) -> bytes:
    data = struct.pack(">HHii",
                       pulse_low, pulse_high,
                       speed_low, speed_high)
    return pack_frame(0xF7, data)


# ── 4.4.9  0xF8  Enable motor ──
def cmd_enable() -> bytes:
    return pack_frame(0xF8)


# ── 4.4.10 0xF9  Disable motor ──
def cmd_disable() -> bytes:
    return pack_frame(0xF9)


# ── 4.4.11 0xFA  Read/write enable state ──
def read_enabled() -> bytes:
    return pack_frame(0xFA, bytes([0x01]))

def write_enabled(state: int) -> bytes:
    return pack_frame(0xFA, bytes([0x01, state]))


# ── 4.4.12 0xFB  Set origin ──
def cmd_set_origin() -> bytes:
    return pack_frame(0xFB)


# ── 4.4.13 0xFC  Clear alarm ──
def cmd_clear_alarm() -> bytes:
    return pack_frame(0xFC)


# ── 4.4.14 0xE0  Position mode absolute ──
def cmd_position_mode_abs(direction: int, accel: int, speed_rpm: float) -> bytes:
    data = struct.pack(">BBf", direction, accel, speed_rpm)
    return pack_frame(0xE0, data)


# ── 4.4.15 0xE1  Position mode relative ──
def cmd_position_mode_rel(direction: int, accel: int, speed_rpm: int, steps: int) -> bytes:
    data = struct.pack(">BBHI", direction, accel, speed_rpm, steps)
    return pack_frame(0xE1, data)


# ── 4.4.16 0xE2  Position IO mode ──
def cmd_position_io_mode(direction: int, accel: int, speed_rpm: int, position: int) -> bytes:
    data = struct.pack(">BBHI", direction, accel, speed_rpm, position)
    return pack_frame(0xE2, data)


# ── 4.4.17 0xE3  Stop (position mode) ──
def cmd_position_mode_stop() -> bytes:
    return pack_frame(0xE3)


# ── 4.4.18 0xE4  IO speed mode ──
def cmd_io_speed_mode(direction: int, accel: int, speed_rpm: float) -> bytes:
    data = struct.pack(">BBf", direction, accel, speed_rpm)
    return pack_frame(0xE4, data)
