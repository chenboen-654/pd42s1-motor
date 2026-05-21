"""PD42S1 command builders — re-exports from all submodules."""
# fmt: off
from .system import (
    read_firmware_version, read_flux, read_resistance_inductance,
    read_current, read_voltage,
    read_speed_rpm, read_position,
    read_motor_status, read_enabled_state,
    read_all_status, read_motor_params, write_motor_params,
    read_device_address, write_device_address,
    read_sync_group, write_sync_group,
    read_work_mode, write_work_mode,
    write_position_pid,
    read_microstep, write_microstep,
    write_run_current,
    read_serial_baudrate, write_serial_baudrate,
    read_can_baudrate, write_can_baudrate,
    read_direction, write_direction,
    read_enable_mode, write_enable_mode,
)
from .motor import (
    cmd_torque_mode, cmd_speed_mode,
    cmd_move_relative, cmd_move_absolute,
    cmd_pulse_mode,
    cmd_stp_pwm_position, cmd_stp_pwm_current, cmd_stp_pwm_speed,
    cmd_clear_position, cmd_release_stall,
    cmd_enable, cmd_disable,
    cmd_clear_status, cmd_immediate_stop,
)

# ── Backward-compatible aliases ──
cmd_stop = cmd_immediate_stop         # was 0xF4→0xFC
cmd_set_origin = cmd_clear_position   # was 0xFB→0xF8
cmd_clear_alarm = cmd_clear_status    # was 0xFC→0xFB
read_enabled = read_enabled_state     # was 0xFA→0x2F
