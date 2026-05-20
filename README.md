# PD42S1 Motor Control Library

通用 PD42S1 闭环步进电机控制库，使用原生串口协议（0xC5...0x5C 格式）。

可用于显微镜自动对焦、精密位移台、机器人关节等场景。

## 特性

- **纯 Python**，仅依赖 `pyserial`
- **原生协议** — 基于手册第4章的自定义协议，支持全部命令
- **CLI 接口** — 设计为 LLM 可直接调用的形式
- **即插即用** — `pip install` 即可使用

## 安装

```bash
pip install pyserial
# 或从源码
pip install .
```

## 用法

### Python API

```python
from pd42s1_motor import MotorController

motor = MotorController()
motor.connect("COM3", 115200)
motor.enable()

# 读取位置
pos = motor.get_position()
print(f"当前位置: {pos}")

# 相对移动 (+1 圈，假设 51200 步/圈)
motor.move_relative(51200)

# 读取全部状态
status = motor.read_all_status()
print(f"电压: {status['voltage']:.1f}V")
print(f"电流: {status['current']}mA")
print(f"速度: {status['speed']}RPM")

motor.stop()
motor.disconnect()
```

### CLI (推荐 LLM 调用)

```bash
# 列出串口
pd42s1-cli ports

# 连接测试
pd42s1-cli connect COM3

# 读取全部状态 (JSON)
pd42s1-cli status COM3

# 移动
pd42s1-cli move-rel COM3 51200
pd42s1-cli move-abs COM3 100000

# 停止 / 使能
pd42s1-cli stop COM3
pd42s1-cli enable COM3
pd42s1-cli disable COM3

# 设置原点
pd42s1-cli home COM3

# 设置电流
pd42s1-cli set-current COM3 200

# 发送原始命令 (调试用)
pd42s1-cli raw COM3 "C5 01 F4 BA 5C"
```

CLI 输出为单行 JSON，方便 LLM 解析：

```json
{"ok": true, "port": "COM3", "baud": 115200, "position": 51200}
```

## 协议说明

PD42S1 原生协议格式（手册第4章）：

| 头部 | 地址 | 命令 | 数据 | 校验和 | 尾部 |
|------|------|------|------|--------|------|
| 0xC5 | 0x01 | cmd  | ...  | SUM&0xFF | 0x5C |

- 校验和 = (0xC5 + 地址 + 命令 + 所有数据字节) & 0xFF
- 读命令：无数据字节，直接 `C5 01 <cmd> <chk> 5C`
- 写命令：`C5 01 <cmd> 01 <值...> <chk> 5C`（Byte1=0x01 表示写入）

## 命令映射

### 系统参数 (§4.3)

| 命令码 | 功能 | 函数 |
|--------|------|------|
| 0x20 | 读取固件版本 | `read_firmware_version()` |
| 0x21 | 读取磁链 (mWb) | `read_flux()` |
| 0x22 | 读取电阻/电感 | `read_resistance_inductance()` |
| 0x23 | 读取电流 (mA) | `read_current()` |
| 0x24 | 读取电压 (V) | `read_voltage()` |
| 0x25~0x27 | PID 参数 | `read_pid_float()` / `write_pid_uint32()` |
| 0x28 | 编码器分辨率 | `read_encoder_resolution()` |
| 0x29 | 读取转速 (RPM) | `read_speed_rpm()` |
| 0x2A | 读取位置 | `read_position()` |
| 0x2B | 写入位置 | `write_position(pos)` |
| 0x2C~0x2D | 控制模式 | `read/write_control_mode()` |
| 0x2E~0x2F | 运行电流 | `read/write_run_current()` |
| 0x30 | 使能状态 | `read_enable_state()` |
| 0x31 | 全部状态 (41字节) | `read_all_status()` |
| 0x32 | 电机参数 (45字节) | `read/write_motor_params()` |
| 0x60 | 设备地址 | `read/write_device_address()` |
| 0x61 | 多轴同步组 | `read/write_sync_group()` |
| 0x62 | 串口波特率索引 | `read/write_baudrate()` |
| 0x63 | 速度环 PID | `read/write_velocity_pid()` |
| 0x64 | 电流限制 | `read/write_current_limit()` |
| 0x65 | 微步分辨率 | `read/write_microstep()` |
| 0x66 | 保持电流 | `read/write_holding_current()` |
| 0x67 | 串口波特率 (数值) | `read/write_serial_baudrate()` |
| 0x68 | CAN 波特率 | `read/write_can_baudrate()` |
| 0x6D | 运动方向 | `read/write_direction()` |
| 0x6E | 使能模式 | `read/write_enable_mode()` |
| 0x6F | 保存参数到 Flash | `save_params()` |
| 0x70 | 复位电机 | `reset_motor()` |
| 0x71 | 恢复出厂设置 | `restore_defaults()` |
| 0x72 | IO 控制 | `read/write_io()` |
| 0x73 | 位置环 PID | `read/write_position_pid()` |

### 电机控制 (§4.4)

| 命令码 | 功能 | 函数 |
|--------|------|------|
| 0xF0 | 力矩模式 | `cmd_torque_mode()` |
| 0xF1 | 速度模式 | `cmd_speed_mode()` |
| 0xF2 | 绝对定位 | `cmd_move_absolute()` |
| 0xF3 | 相对定位 | `cmd_move_relative()` |
| 0xF4 | 急停 | `cmd_stop()` |
| 0xF5 | STP PWM 位置映射 | `cmd_stp_pwm_position()` |
| 0xF6 | STP PWM 电流映射 | `cmd_stp_pwm_current()` |
| 0xF7 | STP PWM 速度映射 | `cmd_stp_pwm_speed()` |
| 0xF8 | 使能电机 | `cmd_enable()` |
| 0xF9 | 失能电机 | `cmd_disable()` |
| 0xFA | 使能状态读写 | `read/write_enabled()` |
| 0xFB | 设为零位 | `cmd_set_origin()` |
| 0xFC | 清除报警 | `cmd_clear_alarm()` |
| 0xE0 | 位置模式绝对 | `cmd_position_mode_abs()` |
| 0xE1 | 位置模式相对 | `cmd_position_mode_rel()` |
| 0xE2 | IO 触发定位 | `cmd_position_io_mode()` |
| 0xE3 | 位置模式停止 | `cmd_position_mode_stop()` |
| 0xE4 | IO 速度模式 | `cmd_io_speed_mode()` |

### 高级功能 (§4.5)

| 命令码 | 功能 | 函数 |
|--------|------|------|
| 0x90 | 编码器偏移 | `read/write_encoder_offset()` |
| 0x91 | PID 自整定 | `cmd_auto_pid_tune()` |
| 0x92 | PID 模式 | `read/write_pid_mode()` |
| 0x93 | 保存用户参数 | `cmd_save_user_params()` |
| 0x94 | 位置跟踪 | `read_position_tracking()` |
| 0x95 | 超时设置 | `read/write_timeout()` |
| 0x96 | 读取报警状态 | `read_alarm_state()` |
| 0x97 | 清除报警 (v2) | `cmd_clear_alarm_v2()` |
| 0x98 | 目标位置 | `read/write_target_position()` |
| 0x99 | 编码器方向 | `read/write_encoder_dir()` |

完整命令见 `pd42s1_motor/commands.py`（共 **60+** 命令，覆盖手册全部功能）。

## 项目结构

```
pd42s1_motor/
├── __init__.py      # 公开 API
├── __main__.py      # python -m pd42s1_motor
├── protocol.py      # 帧打包/解析/校验和 + 协议常量
├── unpack.py        # 响应数据解包 (float/int16/int32)
├── commands/        # 全部命令构建器 (按手册章节拆分)
│   ├── __init__.py
│   ├── system.py    # §4.3 系统参数 (0x20-0x73)
│   ├── motor.py     # §4.4 电机控制 (0xF0-0xFC, 0xE0-0xE4)
│   └── advanced.py  # §4.5 高级功能 (0x90-0x99)
├── controller.py    # 高层控制器
├── cli.py           # CLI 入口 (LLM 调用)
└── pyproject.toml   # 包配置
```
