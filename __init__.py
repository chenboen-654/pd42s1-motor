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
    read_position, read_all_status, read_motor_status,
    read_voltage, read_current,
    read_speed_rpm, read_flux, read_resistance_inductance,
    read_enabled_state,
    # Movement
    cmd_move_relative, cmd_move_absolute,
    cmd_clear_position, cmd_release_stall,
    cmd_enable, cmd_disable,
    cmd_clear_status, cmd_immediate_stop,
    # PWM servo mapping
    cmd_stp_pwm_position, cmd_stp_pwm_current, cmd_stp_pwm_speed,
    # Work mode & current & microstep
    read_work_mode, write_work_mode,
    write_run_current, write_microstep,
    # PID
    write_position_pid,
    # Sync group
    read_sync_group, write_sync_group,
    # System
    read_firmware_version, read_device_address, write_device_address,
    read_serial_baudrate, write_serial_baudrate,
    read_can_baudrate, write_can_baudrate,
    read_direction, write_direction,
    read_enable_mode, write_enable_mode,
    read_microstep,
)  # fmt: skip
from .controller import MotorController, PD42S1Error

__all__ = [
    "MotorController",
    "PD42S1Error",
    "hex_str",
]
