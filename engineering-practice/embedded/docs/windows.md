# Windows 接续指南

## 2026-10-21 本机实测更新

已在 Windows 完成 GitHub 工程接续，并实际使用 Keil、STM32CubeIDE、MobaXterm 连板。Keil 原生工程、快捷键、CubeIDE 附加配置、验证记录与录像时间轴见 [Keil 本机开发说明](../keil/README.md)。CubeMX 的引脚配置和 Proteus 的独立 LCD 仿真也已打开验证。

配套 [嘉立创 EDA 原生图纸与核对说明](../hardware/README.md) 包含四页最小系统、电路和实际代码流程图，以及原厂资料冲突、实测边界、网表与引脚核对结果。

本机 Python 为 `C:\Python312\python.exe`；可直接使用工程的 `.venv\Scripts\python.exe`。以下早期交接命令中的 `py -3.12` 如不可用，可换成 `python`。

## 取得全部资料

仓库：[peakpeng666/embedded](https://github.com/peakpeng666/embedded)。

完整交接下载位于 [v1.0.0 Release](https://github.com/peakpeng666/embedded/releases/tag/v1.0.0)：

- `embedded-windows.zip`：Windows 接续用工程，含源码、图纸、已测试固件、原固件备份、设备包、历史记录和文件校验清单；不包含无法在 Windows 直接运行的 Linux Python 环境/编译器。
- `embedded-linux-workspace.tar.gz`：清理前整个 Linux 工作目录的完整快照，含 `.git`、`.venv`、`.toolchains`、原固件、全部日志、缓存、临时文件和历史版本。
- `SHA256SUMS.txt`：两个压缩包和清单的 SHA-256。
- `windows-manifest.json`、`linux-manifest.json`：逐项文件清单和校验值。

GitHub 自动生成的 `Source code (zip)` 仅包含 Git 跟踪文件，不含原固件备份；用于接续时请下载上面命名的交接包。

### 最新 main / full-archive 开发

当前 Git 工程位于仓库内的 `engineering-practice/embedded`，不是仓库根目录。以下命令进入当前工程：

```powershell
git clone https://github.com/peakpeng666/embedded.git C:\Projects\embedded
cd C:\Projects\embedded\engineering-practice\embedded
```

若已克隆 `full-archive`，同样进入其 `engineering-practice/embedded` 子目录；两分支的工程相对路径一致。下文 Python、编译、串口命令均在该工程目录执行。

不要把 v1.0.0 旧交接包覆盖到最新仓库根目录或当前工程中。旧包采用根级 `tools/`、`lab1/` 布局，与当前仓库布局不同；叠加会产生两份工程，可能误用旧源码。

### 固定 v1.0.0 恢复 / 旧交接包验证

需要原固件备份或复现旧交接时，将 `embedded-windows.zip` 解压到一个新的独立目录，不与 Git 克隆目录重合：

```powershell
Expand-Archive -LiteralPath "$env:USERPROFILE\Downloads\embedded-windows.zip" -DestinationPath C:\Projects\embedded-v1.0.0
cd C:\Projects\embedded-v1.0.0\embedded
py -3.12 tools\verify_handoff.py
```

该目录用于固定 v1.0.0 的备份、验证和恢复；不代表当前 main / full-archive 的 Keil/CubeIDE 新增内容。交接包包含 `HANDOFF_MANIFEST.json`，普通 Git 克隆不含该清单，不应直接在克隆中执行交接包校验。

## Python 环境

先明确本次操作目标：开发最新版本时回到 `C:\Projects\embedded\engineering-practice\embedded`；验证或恢复旧交接时留在 `C:\Projects\embedded-v1.0.0\embedded`。下面的虚拟环境与构建命令只在所选目录执行，不在两个目录间共用 `.venv`。上面的旧包示例目录仅在解压后确实包含 `embedded\tools\verify_handoff.py` 时适用；若压缩包目录层级不同，先找到同时包含 `HANDOFF_MANIFEST.json` 和 `tools\verify_handoff.py` 的工程目录，再执行校验，不猜测路径继续恢复。

安装 Python 3.12 的 64 位 Windows 版本。重新创建 Windows 虚拟环境，不复用完整 Linux 快照中的 `.venv`：

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r tools\requirements-windows.txt
```

命令直接调用虚拟环境里的 Python，无需修改 PowerShell 执行策略或激活脚本。pyOCD 会安装 Windows 对应的 HID 后端依赖。

## 编译

安装 Windows 版 Arm GNU Toolchain，目标选择 `arm-none-eabi`，把它的 `bin` 目录加入 PATH。使用原生 Python 构建，不需要 GNU Make：

```powershell
arm-none-eabi-gcc --version
.\.venv\Scripts\python.exe tools\build_firmware.py
.\.venv\Scripts\python.exe lab1\verify_image.py
```

如果工具链没有加入 PATH，可指定实际目录：

```powershell
.\.venv\Scripts\python.exe tools\build_firmware.py --toolchain-dir "C:\ArmGNU\bin"
```

输出仍在 `lab1/build/`，不会自动覆盖 `firmware/` 中已实测的发布镜像。不同编译器版本可能产生不同二进制校验值；烧录工具不会自动采纳重编译的任意镜像。电脑端带 ASan/UBSan 的 GCC 行为测试可继续在 WSL/Linux 运行：`make -C lab1 test`。

## 串口与后续连接

板上当前固件：KEY0 启动七色轮闪，KEY1 全灭，再按 KEY0 从红色重新开始。重新插入时连接 USB_COM，保留两只 USART1 跳线。

```powershell
.\.venv\Scripts\python.exe -m serial.tools.list_ports -v
.\.venv\Scripts\python.exe tools\console.py
```

可显式选择端口：

```powershell
.\.venv\Scripts\python.exe tools\console.py --port COM5
```

串口参数为 115200/8N1，无流控。输入 `status` 或 `help`；Ctrl+] 退出。

该探针是 CMSIS-DAP v1 HID。pyOCD 使用 Windows HID 后端；Linux 的 `board_access.py`、sudo 和 udev 权限处理不用于 Windows。串口 COM 号以设备管理器和上面的列举结果为准。

## 回退到原 LCD/温湿度演示

仅在上文独立解压并通过清单校验的 v1.0.0 工程目录执行本节恢复命令，不在新 Git 工程目录执行。

Windows 交接包包含 `backups/` 原备份和 `.toolchains/Keil.STM32L4xx_DFP.3.1.0.pack`，路径已经与工具匹配。先关闭串口终端，再执行：

```powershell
.\.venv\Scripts\python.exe tools\lab1_flash.py plan
.\.venv\Scripts\python.exe tools\lab1_flash.py restore
```

`plan` 是离线检查；`restore` 会实际恢复应用区两个页面。原始备份、设备包、芯片身份与固定范围不匹配时，工具停止，不会自动解除保护。恢复只适用于本次这块板。

## 验证边界与来源

原交接版本在 Linux 编译并完成实板验收。2026-10-21 又在本机 Windows/Python 3.12 实测：Keil AC5 构建与下载校验通过；CubeIDE 自带 GCC 构建为 0 错误、0 警告；两款 IDE 均完成 CMSIS-DAP 硬件调试；MobaXterm 在 COM3 收到 `STATUS mode=COLOR`。Keil 下载前后完成 512 KiB Flash 读回比较，两个应用页面之外均未改变。Windows 主机逻辑测试六组通过，未在 Windows 执行 ASan/UBSan。历史 Linux 验收记录和本次 Windows 记录分别保留。

PDF 已预生成。Windows 重新生成报告时使用系统宋体和 Arial；没有这些字体时直接阅读 `docs/lab1_design.pdf` 即可。

- [Python Windows 下载](https://www.python.org/downloads/windows/)
- [Arm GNU Toolchain 官方入口](https://developer.arm.com/Tools%20and%20Software/GNU%20Toolchain)
- [Arm 官方 Windows 安装说明](https://learn.arm.com/install-guides/gcc/arm-gnu/)
- [pyOCD 安装](https://pyocd.io/docs/installing)
- [pyOCD USB 后端说明](https://pyocd.io/docs/env_vars.html)

