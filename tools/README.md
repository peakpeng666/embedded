# 本地工具

从仓库根目录执行。Python 工具依赖 `requirements.txt`；连接操作针对本次 STM32L496 实板和其匹配的 ATK 探针。

| 文件 | 用途 |
| --- | --- |
| `board_access.py` | 查看或临时授权 USB / 串口设备访问权限 |
| `console.sh` / `console.py` | Linux Bash / Windows 与 Linux Python 串口终端 |
| `build_firmware.py` | Windows/Linux 原生 Python 构建固件，不访问硬件 |
| `verify_handoff.py` | 校验解压后的交接包文件清单 |
| `listen_serial.py` | 限时被动监听，不发送命令 |
| `inspect_board.py` | 读取芯片信息；`--backup` 读取内部 Flash 到本地备份 |
| `lab1_observe.py` | 同步记录 UART、按键电平和 RGB 输出，不驱动 GPIO |
| `lab1_flash.py` | 固定镜像与两个应用页的写入 / 原程序恢复 |
| `check_serial.py` | 只适用于恢复后的 RT-Thread 原演示，查询 `version` |

旧串口诊断和临时测试程序归档于 `.local_archive/`，随 Release 快照保留，不作为当前实验工具入口。

## 固定范围烧录与回退

```bash
.venv/bin/python tools/lab1_flash.py plan
.venv/bin/python tools/lab1_flash.py apply
.venv/bin/python tools/lab1_flash.py restore
```

`plan` 只做本地文件与范围检查；`apply` 会写入 `firmware/lab1.bin`；`restore` 恢复原程序的两个改动页。代码固定目标 MCU、原始备份 SHA-256、发布镜像 SHA-256 和 `0x08010000–0x08010FFF` 范围。整片擦除、自动解除保护和选项字节编程均未使用。写入后全 512 KiB 读回比对，再验证串口启动。

烧录和恢复使用两项随 Release 的 Windows 交接包提供的文件：

- `backups/stm32l4_internal_flash_20261020T154711+0900.bin`：这块实板的原始 512 KiB 备份。
- `.toolchains/Keil.STM32L4xx_DFP.3.1.0.pack`：本次校验过的设备包。

单独克隆 Git 文件树不包含它们；按 [Windows 指南](../docs/windows.md) 叠加解压交接包即可恢复对应路径。缺少原固件备份时，工具在访问硬件前停止。换一块板不能直接复用原备份校验配置，需要先独立备份并核对芯片与内存布局。

## PDF 生成

报告已在 `docs/lab1_design.pdf`，通常无需重建。需要重建时：

```bash
.venv/bin/pip install -r tools/requirements-docs.txt
.venv/bin/python lab1/create_report.py
```

生成器在 Ubuntu 使用 DroidSansFallbackFull、DejaVuSans，在 Windows 使用系统宋体和 Arial。构建镜像信息来自 `lab1/build/validation.json`，实测摘要来自 `docs/hardware_validation.json`；两者 SHA-256 不匹配时，不复用旧实测结论。
