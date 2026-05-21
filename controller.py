"""
PD42S1 high-level motor controller.

Wraps the raw protocol commands into a convenient Python API.
Handles serial communication, response parsing, and error handling.
"""

from __future__ import annotations

import struct
import logging
from typing import Optional, Any

import serial

from .protocol import (
    parse_response, PROTOCOL_ADDR, PROTOCOL_HEADER, PROTOCOL_FOOTER,
)
from .unpack import (
    unpack_float_be, unpack_int16_be,
    unpack_int32_be, unpack_uint16_be, unpack_uint32_be,
    hex_str,
)
from . import commands as C

logger = logging.getLogger(__name__)


# ── Default serial parameters (from manual: 115200, 8, 1, N) ──
SERIAL_DEFAULTS = {
    "baudrate": 115200,
    "bytesize": 8,
    "parity": "N",
    "stopbits": 1,
    "timeout": 0.5,
}


class PD42S1Error(Exception):
    """Motor communication or operation error."""


class MotorController:
    """High-level controller for PD42S1 stepper motor.

    Usage:
        motor = MotorController()
        motor.connect("COM3", 115200)
        motor.enable()
        pos = motor.get_position()
        motor.move_relative(51200)  # +1 revolution
        motor.stop()
        motor.disconnect()
    """

    def __init__(self, port: str = "COM1", baudrate: int = 115200):
        self.port = port
        self.baudrate = baudrate
        self.serial: Optional[serial.Serial] = None
        self._connected = False
        self._addr = PROTOCOL_ADDR
        # 显微镜 Z 轴默认参数 (平稳且响应及时)
        self._accel = 50          # 适中加速度 (手册范围 0~200, 0=直接启动)
        self._speed_rpm = 200     # 安全低速 (0~6000 RPM)
        self._current_ma = 150    # 默认电流 (0~3000 mA)

    # ── Properties ──

    @property
    def is_connected(self) -> bool:
        return self._connected and self.serial is not None and self.serial.is_open

    # ── Connection management ──

    def connect(self, port: Optional[str] = None,
                baudrate: Optional[int] = None) -> bool:
        """Open serial connection to the motor driver."""
        if port:
            self.port = port
        if baudrate:
            self.baudrate = baudrate
        try:
            self.serial = serial.Serial(
                port=self.port,
                baudrate=self.baudrate,
                bytesize=SERIAL_DEFAULTS["bytesize"],
                parity=SERIAL_DEFAULTS["parity"],
                stopbits=SERIAL_DEFAULTS["stopbits"],
                timeout=SERIAL_DEFAULTS["timeout"],
            )
            self._connected = True
            logger.info(f"PD42S1 connected: {self.port} @ {self.baudrate}")
            return True
        except serial.SerialException as e:
            logger.error(f"PD42S1 connection failed: {e}")
            self._connected = False
            return False

    def disconnect(self):
        """Close serial connection."""
        if self.serial and self.serial.is_open:
            try:
                self.serial.close()
            except Exception:
                pass
        self._connected = False
        logger.info("PD42S1 disconnected")

    # ── Low-level send / receive ──

    def send(self, cmd_bytes: bytes) -> Optional[dict]:
        """Send a PD42S1 frame and parse the response.

        Returns:
            Parsed response dict with keys: addr, cmd, status, data, raw
            Or None on timeout / invalid response.
        """
        if not self.is_connected:
            raise PD42S1Error("Motor not connected")
        try:
            self.serial.reset_input_buffer()
            self.serial.write(cmd_bytes)
            logger.debug(f"TX: {hex_str(cmd_bytes)}")

            # RS485 半双工需要收发切换时间，循环读取直到收到有效帧
            for attempt in range(3):
                raw = self.serial.read(64)
                if not raw:
                    if attempt < 2:
                        continue
                    logger.warning(f"No response for: {hex_str(cmd_bytes)}")
                    return None

                # 在缓冲区中定位帧: 从最后一个 0xC5 头到最后一个 0x5C 尾
                header_idx = raw.rfind(bytes([PROTOCOL_HEADER]))
                footer_idx = raw.rfind(bytes([PROTOCOL_FOOTER]))
                if header_idx == -1 or footer_idx == -1 or footer_idx <= header_idx:
                    continue  # 无效帧，重试
                raw = raw[header_idx:footer_idx + 1]

                # 帧太短 (header + addr + cmd + status + checksum + footer 至少 6 字节)
                if len(raw) < 6:
                    continue

                logger.debug(f"RX: {hex_str(raw)}")
                frame = parse_response(raw)
                if frame is None:
                    continue

                return {
                    "addr": frame.addr,
                    "cmd": frame.cmd,
                    "status": frame.status,
                    "data": frame.data,
                    "raw": raw,
                }

            logger.warning(f"Invalid response after retries: {hex_str(cmd_bytes)}")
            return None
        except serial.SerialException as e:
            raise PD42S1Error(f"Serial error: {e}")

    def _check_ok(self, reply: Optional[dict]) -> bool:
        """Check if response indicates success (status == 0x01)."""
        return reply is not None and reply.get("status") == 0x01

    # ── High-level operations ──

    # -- Speed / accel / current settings --

    def set_accel(self, accel: int):
        """Set acceleration for move commands (0~200, 0=direct start)."""
        self._accel = accel

    def set_speed(self, speed_rpm: int):
        """Set default speed for move commands (0~6000 RPM)."""
        self._speed_rpm = speed_rpm

    def set_current(self, current_ma: int):
        """Set target current in mA (0x66)."""
        reply = self.send(C.write_run_current(current_ma))
        if self._check_ok(reply):
            self._current_ma = current_ma
            return True
        return False

    # -- Enable / disable --

    def enable(self) -> bool:
        """Enable motor driver."""
        reply = self.send(C.cmd_enable())
        return self._check_ok(reply)

    def disable(self) -> bool:
        """Disable motor driver."""
        reply = self.send(C.cmd_disable())
        return self._check_ok(reply)

    def set_enabled(self, state: bool) -> bool:
        if state:
            return self.enable()
        else:
            return self.disable()

    def is_enabled(self) -> Optional[bool]:
        reply = self.send(C.read_enabled_state())
        if reply and len(reply["data"]) >= 2:
            return reply["data"][1] == 0  # 0=enabled, 1=disabled
        return None

    # -- Stop / emergency --

    def stop(self) -> bool:
        """Emergency stop (0xFC immediate brake)."""
        reply = self.send(C.cmd_immediate_stop())
        return self._check_ok(reply)

    # -- Position read --

    def get_position(self) -> Optional[int]:
        """Read current absolute position (internal units)."""
        reply = self.send(C.read_position())
        if reply and len(reply["data"]) >= 5:
            return unpack_int32_be(reply["data"], 1)
        return None

    # -- Movement --

    def is_moving(self) -> Optional[bool]:
        """Check if motor is currently in motion."""
        status = self.read_all_status()
        if status is None:
            return None
        return bool(status.get("motion", 0))

    def move_relative(self, steps: int, speed_rpm: Optional[int] = None) -> bool:
        """Move relative by `steps` (positive = forward, negative = reverse).

        Uses 0xF3 relative position mode. Speed range 0~6000 RPM.
        """
        speed = speed_rpm if speed_rpm is not None else self._speed_rpm
        direction = 0 if steps >= 0 else 1
        cmd = C.cmd_move_relative(direction, self._accel, speed, abs(steps))
        reply = self.send(cmd)
        return self._check_ok(reply)

    def move_absolute(self, position: int, speed_rpm: Optional[int] = None) -> bool:
        """Move to absolute `position` (0xF2 absolute position mode)."""
        speed = speed_rpm if speed_rpm is not None else self._speed_rpm
        cmd = C.cmd_move_absolute(0, self._accel, speed, position)
        reply = self.send(cmd)
        return self._check_ok(reply)

    def jog(self, steps: int, speed_rpm: int = None) -> bool:
        """Jog (point) by `steps`. Positive = forward, negative = reverse."""
        return self.move_relative(steps, speed_rpm)

    # -- Status / telemetry --

    def read_all_status(self) -> Optional[dict]:
        """Read all motor status registers (voltage, current, position, etc.).

        Returns a dict with keys matching the manual section 4.3.18,
        or None on failure.
        """
        reply = self.send(C.read_all_status())
        if not reply or len(reply["data"]) < 41:
            return None
        d = reply["data"]
        # Byte1 = status already parsed
        return {
            "voltage":      unpack_float_be(d, 1),        # V
            "current":      unpack_int16_be(d, 5),        # mA
            "flux":         unpack_float_be(d, 7),        # mWb
            "torque":       unpack_float_be(d, 11),       # N・m ?
            "inductance":   unpack_float_be(d, 15),       # mH
            "speed":        unpack_int16_be(d, 19),       # RPM
            "target_pos":   unpack_int32_be(d, 21),       # internal units
            "actual_pos":   unpack_int32_be(d, 25),
            "encoder_pos":  unpack_int32_be(d, 29),
            "pulse_count":  unpack_uint32_be(d, 33),
            "io_state":     d[37],
            "direction":    d[38],
            "enabled":      d[39],
            "motion":       d[40],  # 0=stopped, 1=moving
        }

    def get_speed(self) -> Optional[int]:
        """Read current speed in RPM."""
        reply = self.send(C.read_speed_rpm())
        if reply and len(reply["data"]) >= 3:
            return unpack_int16_be(reply["data"], 1)
        return None

    def get_voltage(self) -> Optional[float]:
        """Read bus voltage in V."""
        reply = self.send(C.read_voltage())
        if reply and len(reply["data"]) >= 5:
            return unpack_float_be(reply["data"], 1)
        return None

    def get_current_reading(self) -> Optional[int]:
        """Read actual motor current in mA."""
        reply = self.send(C.read_current())
        if reply and len(reply["data"]) >= 3:
            return unpack_int16_be(reply["data"], 1)
        return None

    # -- Multi-axis sync group --

    def set_sync_group(self, group: int) -> bool:
        """Set multi-axis synchronization group (1~255, 0=standalone)."""
        reply = self.send(C.write_sync_group(group))
        return self._check_ok(reply)

    def get_sync_group(self) -> Optional[int]:
        """Read current sync group ID."""
        reply = self.send(C.read_sync_group())
        if reply and len(reply["data"]) >= 2:
            return reply["data"][1]
        return None

    # -- Set origin / home --

    def set_origin(self) -> bool:
        """Clear current position/angle to zero (0xF8)."""
        reply = self.send(C.cmd_clear_position())
        return self._check_ok(reply)

    # -- Microstep --

    def set_microstep(self, divisor: int) -> bool:
        """Set microstep resolution (1~256, e.g. 16 = 1/16 step)."""
        reply = self.send(C.write_microstep(divisor))
        return self._check_ok(reply)

    def get_microstep(self) -> Optional[int]:
        reply = self.send(C.read_microstep())
        if reply and len(reply["data"]) >= 2:
            return unpack_uint16_be(reply["data"], 0)
        return None

    # -- PID tuning for microscope (soft, smooth) --

    def tune_pid_soft(self) -> bool:
        """设置显微镜 Z 轴适用的柔和位置环 PID 参数 (0x63)。

        降低 P 增益、增大 D 阻尼，减少闭环过冲和微震。
        """
        soft_p, soft_i, soft_d = 500, 50, 200
        reply = self.send(C.write_position_pid(soft_p, soft_i, soft_d))
        ok = self._check_ok(reply)
        if ok:
            logger.info(f"Position PID set to soft: P={soft_p} I={soft_i} D={soft_d}")
        return ok

    # -- Utility --

    @staticmethod
    def available_ports() -> list[dict]:
        """List available serial ports with descriptions.

        Returns:
            List of dicts with keys: device, description, vid, pid.
        """
        import serial.tools.list_ports
        return [
            {
                "device": p.device,
                "description": p.description,
                "vid": p.vid,
                "pid": p.pid,
            }
            for p in serial.tools.list_ports.comports()
        ]

    def send_raw(self, cmd_bytes: bytes) -> Optional[bytes]:
        """Send raw bytes and return raw response (for debugging / custom commands)."""
        if not self.is_connected:
            raise PD42S1Error("Motor not connected")
        self.serial.reset_input_buffer()
        self.serial.write(cmd_bytes)
        raw = self.serial.read(64)
        if not raw:
            return None
        # 从最后一个 0xC5 头到最后一个 0x5C 尾
        h = raw.rfind(b"\xC5")
        f = raw.rfind(b"\x5C")
        return raw[h:f + 1] if h != -1 and f != -1 and f > h else raw
