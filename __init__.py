"""
PD42S1 Motor Control Library

General-purpose library for controlling PD42S1 closed-loop stepper motor
via its native serial protocol (0xC5 ... 0x5C format).

Usage:
    from pd42s1_motor import MotorController

    motor = MotorController()
    motor.connect("COM3", 115200)
    motor.enable()
    print(motor.get_position())
    motor.move_relative(51200)
    motor.disconnect()
"""

from .protocol import hex_str, parse_response
from .commands import (
    # Position & status
    read_position, read_all_status, read_voltage, read_current,
    read_speed_rpm, read_flux, read_resistance_inductance,
    # Movement
    cmd_move_relative, cmd_move_absolute, cmd_stop,
    cmd_enable, cmd_disable, cmd_set_origin,
    cmd_position_io_mode, cmd_position_mode_rel, cmd_position_mode_abs,
    # PWM servo mapping
    cmd_stp_pwm_position, cmd_stp_pwm_current, cmd_stp_pwm_speed,
    # Current & microstep
    write_run_current, write_microstep,
    # PID
    read_pid_float, read_pid_uint32, write_pid_uint32,
    read_position_pid, read_velocity_pid,
    # Sync group
    read_sync_group, write_sync_group,
    # System
    read_firmware_version, read_device_address, write_device_address,
    read_baudrate, write_baudrate,
    save_params, reset_motor, restore_defaults,
    read_enable_mode, write_enable_mode,
    read_direction, write_direction,
    read_encoder_resolution, read_holding_current, write_holding_current,
    read_io, write_io,
    read_control_mode, write_control_mode,
    read_enabled, write_enabled,
    read_current_limit, write_current_limit,
)  # fmt: skip
from .controller import MotorController, PD42S1Error

__all__ = [
    "MotorController",
    "PD42S1Error",
    "hex_str",
]
