"""PD42S1 motor control commands (§4.4).

Function code map (verified against manual V1.2 §4.4):
  0xF0-0xF3  Closed-loop motion modes
  0xF4       Pulse mode control
  0xF5-0xF7  PWM mapping modes
  0xF8       Clear position/angle to zero
  0xF9       Release stall protection
  0xFA       Motor enable control
  0xFB       Clear status (stall, brake, disable)
  0xFC       Immediate stop (brake)
  0xE0-0xE4  Open-loop / IO modes (not used in this project)
"""

from __future__ import annotations

import struct

from ..protocol import pack_frame


# ── 4.4.1  0xF0  力矩模式 ──
def cmd_torque_mode(direction: int, current_ma: int) -> bytes:
    """direction: 0=正转, 1=反转; current_ma: 0~3000 mA"""
    data = struct.pack(">Bh", direction, current_ma)
    return pack_frame(0xF0, data)


# ── 4.4.2  0xF1  速度模式 ──
def cmd_speed_mode(direction: int, accel: int, speed_rpm: float) -> bytes:
    """direction, accel (0~200), speed_rpm (0.1~6000, float32)"""
    data = struct.pack(">BBf", direction, accel, speed_rpm)
    return pack_frame(0xF1, data)


# ── 4.4.3  0xF2  绝对位置模式 ──
def cmd_move_absolute(direction: int, accel: int, speed_rpm: int, position: int) -> bytes:
    """direction, accel (0~200), speed_rpm (0~6000), position (51200/rev)"""
    data = struct.pack(">BBHI", direction, accel, speed_rpm, position)
    return pack_frame(0xF2, data)


# ── 4.4.4  0xF3  相对位置模式 ──
def cmd_move_relative(direction: int, accel: int, speed_rpm: int, steps: int) -> bytes:
    """direction, accel (0~200), speed_rpm (0~6000), steps (51200/rev)"""
    data = struct.pack(">BBHI", direction, accel, speed_rpm, steps)
    return pack_frame(0xF3, data)


# ── 4.4.5  0xF4  脉冲模式控制 ──
def cmd_pulse_mode() -> bytes:
    return pack_frame(0xF4)


# ── 4.4.6  0xF5  STP PWM position mode ──
def cmd_stp_pwm_position(pulse_on: int, pulse_off: int,
                         pos_at_pulse_on: int, pos_at_pulse_off: int) -> bytes:
    data = struct.pack(">HHii", pulse_on, pulse_off,
                       pos_at_pulse_on, pos_at_pulse_off)
    return pack_frame(0xF5, data)


# ── 4.4.7  0xF6  STP PWM current mode ──
def cmd_stp_pwm_current(pulse_low: int, pulse_high: int,
                        current_low: int, current_high: int) -> bytes:
    data = struct.pack(">HHii", pulse_low, pulse_high,
                       current_low, current_high)
    return pack_frame(0xF6, data)


# ── 4.4.8  0xF7  STP PWM speed mode ──
def cmd_stp_pwm_speed(pulse_low: int, pulse_high: int,
                      speed_low: int, speed_high: int) -> bytes:
    data = struct.pack(">HHii", pulse_low, pulse_high,
                       speed_low, speed_high)
    return pack_frame(0xF7, data)


# ── 4.4.9  0xF8  将当前位置角度清零 ──
def cmd_clear_position() -> bytes:
    """Clear current position/angle and accumulated pulse count to zero."""
    return pack_frame(0xF8)


# ── 4.4.10 0xF9  解除堵转保护 ──
def cmd_release_stall() -> bytes:
    """Release stall protection after motor stall."""
    return pack_frame(0xF9)


# ── 4.4.11 0xFA  电机使能控制 ──
def cmd_enable() -> bytes:
    """Enable motor."""
    return pack_frame(0xFA, bytes([0x00]))

def cmd_disable() -> bytes:
    """Disable motor."""
    return pack_frame(0xFA, bytes([0x01]))


# ── 4.4.12 0xFB  清除状态（堵转、刹车，失能） ──
def cmd_clear_status() -> bytes:
    """Clear stall, brake, and disable status flags."""
    return pack_frame(0xFB)


# ── 4.4.13 0xFC  立即停止（刹车） ──
def cmd_immediate_stop() -> bytes:
    """Immediate stop / brake. WARNING: motor heats up after braking!"""
    return pack_frame(0xFC)
