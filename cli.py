#!/usr/bin/env python3
"""
PD42S1 CLI — designed for LLM calling.

Each command is a stateless one-shot operation:
  pd42s1-cli connect <port> [baud]
  pd42s1-cli status <port> [baud]
  pd42s1-cli move-rel <port> <steps> [speed]
  pd42s1-cli move-abs <port> <position> [speed]
  pd42s1-cli stop <port>
  pd42s1-cli enable <port>
  pd42s1-cli disable <port>
  pd42s1-cli home <port>
  pd42s1-cli get-pos <port>
  pd42s1-cli set-current <port> <ma>
  pd42s1-cli info <port>         # read all status registers
  pd42s1-cli ports               # list available ports

Output is newline-delimited JSON for easy LLM parsing.
"""

from __future__ import annotations

import json
import sys
import time
from typing import Optional

from .controller import MotorController


def _open(motor: MotorController, port: str, baud: int = 115200,
          timeout: float = 2.0) -> Optional[str]:
    """Connect to motor and return error string, or None on success."""
    if not motor.connect(port, baud):
        return f"Failed to connect to {port} @ {baud}"
    time.sleep(0.3)  # let the serial link stabilize
    return None


def cmd_connect(port: str, baud: int = 115200):
    """Test connection by reading position."""
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    pos = motor.get_position()
    motor.disconnect()
    return {"ok": True, "port": port, "baud": baud, "position": pos}


def cmd_status(port: str, baud: int = 115200):
    """Read all status registers."""
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    status = motor.read_all_status()
    motor.disconnect()
    if status is None:
        return {"ok": False, "error": "No response / invalid frame"}
    return {"ok": True, **status}


def cmd_move_relative(port: str, steps: int, speed_rpm: Optional[int] = None,
                      baud: int = 115200):
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    if speed_rpm:
        motor.set_speed(speed_rpm)
    ok = motor.move_relative(steps)
    pos = motor.get_position()
    motor.disconnect()
    return {"ok": ok, "steps": steps, "position": pos}


def cmd_move_absolute(port: str, position: int, speed_rpm: Optional[int] = None,
                      baud: int = 115200):
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    if speed_rpm:
        motor.set_speed(speed_rpm)
    ok = motor.move_absolute(position)
    pos = motor.get_position()
    motor.disconnect()
    return {"ok": ok, "target": position, "position": pos}


def cmd_stop(port: str, baud: int = 115200):
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    ok = motor.stop()
    pos = motor.get_position()
    motor.disconnect()
    return {"ok": ok, "position": pos}


def cmd_enable(port: str, baud: int = 115200):
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    ok = motor.enable()
    motor.disconnect()
    return {"ok": ok}


def cmd_disable(port: str, baud: int = 115200):
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    ok = motor.disable()
    motor.disconnect()
    return {"ok": ok}


def cmd_home(port: str, baud: int = 115200):
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    ok = motor.set_origin()
    pos = motor.get_position()
    motor.disconnect()
    return {"ok": ok, "position": pos}


def cmd_get_position(port: str, baud: int = 115200):
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    pos = motor.get_position()
    motor.disconnect()
    return {"ok": pos is not None, "position": pos}


def cmd_set_current(port: str, current_ma: int, baud: int = 115200):
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    ok = motor.set_current(current_ma)
    motor.disconnect()
    return {"ok": ok, "current_ma": current_ma}


def cmd_ports():
    ports = MotorController.available_ports()
    return {"ok": True, "ports": ports}


def cmd_raw(port: str, hex_str: str, baud: int = 115200):
    """Send raw hex bytes (e.g. \"C5 01 F4 BA 5C\") and return response."""
    motor = MotorController()
    err = _open(motor, port, baud)
    if err:
        return {"ok": False, "error": err}
    raw_bytes = bytes.fromhex(hex_str.replace(" ", ""))
    reply = motor.send_raw(raw_bytes)
    motor.disconnect()
    from .protocol import hex_str as fmt_hex
    return {"ok": reply is not None, "request": hex_str,
            "response": fmt_hex(reply) if reply else None}


# ── CLI dispatcher ────────────────────────────────────────────────

COMMANDS = {
    "connect":    cmd_connect,
    "status":     cmd_status,
    "move-rel":   cmd_move_relative,
    "move-abs":   cmd_move_absolute,
    "stop":       cmd_stop,
    "enable":     cmd_enable,
    "disable":    cmd_disable,
    "home":       cmd_home,
    "get-pos":    cmd_get_position,
    "set-current": cmd_set_current,
    "ports":      cmd_ports,
    "raw":        cmd_raw,
}


def print_result(result: dict):
    """Print result as single-line JSON."""
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0 if result.get("ok") else 1)


def main():
    if len(sys.argv) < 2 or sys.argv[1] in ("-h", "--help", "help"):
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(0)

    cmd_name = sys.argv[1]
    args = sys.argv[2:]

    func = COMMANDS.get(cmd_name)
    if func is None:
        print(json.dumps({"ok": False, "error": f"Unknown command: {cmd_name}"}),
              file=sys.stderr)
        print(__doc__.strip(), file=sys.stderr)
        sys.exit(1)

    try:
        if cmd_name == "ports":
            result = cmd_ports()
        elif cmd_name == "connect":
            result = cmd_connect(*args)
        elif cmd_name in ("status", "stop", "enable", "disable", "home", "get-pos"):
            port = args[0] if len(args) > 0 else "COM1"
            baud = int(args[1]) if len(args) > 1 else 115200
            result = COMMANDS[cmd_name](port, baud)
        elif cmd_name in ("move-rel", "move-abs"):
            port = args[0] if len(args) > 0 else "COM1"
            val = int(args[1]) if len(args) > 1 else 0
            speed = int(args[2]) if len(args) > 2 else None
            result = COMMANDS[cmd_name](port, val, speed)
        elif cmd_name == "set-current":
            port = args[0] if len(args) > 0 else "COM1"
            ma = int(args[1]) if len(args) > 1 else 150
            result = COMMANDS[cmd_name](port, ma)
        elif cmd_name == "raw":
            port = args[0] if len(args) > 0 else "COM1"
            hex_str = args[1] if len(args) > 1 else ""
            result = COMMANDS[cmd_name](port, hex_str)
        else:
            result = {"ok": False, "error": f"Unhandled command: {cmd_name}"}
    except Exception as e:
        result = {"ok": False, "error": str(e)}

    print_result(result)


if __name__ == "__main__":
    main()
