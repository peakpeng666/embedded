# 本地工具

从仓库根目录执行。Python 工具依赖 `requirements.txt`；连接操作针对本次 STM32L496 实板和其匹配的 ATK 探针。

| 文件 | 用途 |
| --- | --- |
| `board_access.py` | 查看或临时授权 USB / 串口设备访问权限 |
| `console.sh` | 115200 串口终端，Ctrl+] 退出 |
| `listen_serial.py` | 限时被动监听，不发送命令 |
| `inspect_board.py` | 读取芯片信息；`--backup` 读取内部 Flash 到本地备份 |
| `lab1_observe.py` | 同步记录 UART、按键电平和 RGB 输出，不驱动 GPIO |
| `lab1_flash.py` | 固定镜像与两个应用页的写入 / 原程序恢复 |
| `check_serial.py` | 只适用于恢复后的 RT-Thread 原演示，查询 `version` |

旧串口诊断和临时测试程序已归档在本机 `.local_archive/`，不作为当前实验工具上传。

## 固定范围烧录与回退

```bash
.venv/bin/python tools/lab1_flash.py plan
.venv/bin/python tools/lab1_flash.py apply
.venv/bin/python tools/lab1_flash.py restore
```

`plan` 只做本地文件与范围检查；`apply` 会写入 `firmware/lab1.bin`；`restore` 恢复原程序的两个改动页。代码固定目标 MCU、原始备份 SHA-256、发布镜像 SHA-256 和 `0x08010000–0x08010FFF` 范围。整片擦除、自动解除保护和选项字节编程均未使用。写入后全 512 KiB 读回比对，再验证串口启动。

烧录和恢复使用两项未上传的本地文件：

- `backups/stm32l4_internal_flash_20261020T154711+0900.bin`：这块实板的原始 512 KiB 备份。
- `.toolchains/Keil.STM32L4xx_DFP.3.1.0.pack`：本次校验过的设备包。

它们仍保存在原工作目录中。新克隆的仓库不包含原固件备份，烧录工具会在访问硬件前停止。换一块板不能直接复用原备份校验配置，需要先独立备份并核对芯片与内存布局。

## PDF 生成

报告已在 `docs/lab1_design.pdf`，通常无需重建。需要重建时：

```bash
.venv/bin/pip install -r tools/requirements-docs.txt
.venv/bin/python lab1/create_report.py
```

生成器使用系统 DroidSansFallbackFull、DejaVuSans 字体；Ubuntu 上对应字体文件位于 `/usr/share/fonts/truetype/`。构建镜像信息来自 `lab1/build/validation.json`，实测摘要来自 `docs/hardware_validation.json`；两者 SHA-256 不匹配时，不复用旧实测结论。
